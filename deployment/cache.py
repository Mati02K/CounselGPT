import redis
import json
import hashlib
import logging
import os
import httpx
from typing import Optional, List

logger = logging.getLogger(__name__)

class ResponseCache:
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        embedding_url: str = "http://counselgpt-redis:8000",
        use_semantic: bool = True,
        similarity_threshold: float = 0.95
    ):
        """Initialize Redis Cache with semantic search support

        Args:
            redis_url: Redis connection URL
            embedding_url: Embedding service URL (sidecar in semantic-cache pod)
            use_semantic: Enable semantic caching (default: True)
            similarity_threshold: Minimum similarity for cache hit (default: 0.95)
        """
        # Redis connection
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()
            logger.info("✓ Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
        
        # Embedding service
        self.embedding_url = embedding_url
        self.use_semantic = use_semantic
        self.similarity_threshold = similarity_threshold
        self.embedding_client = httpx.Client(timeout=5.0) if use_semantic else None
        
        # Test embedding service
        if self.use_semantic and self.redis_client:
            try:
                response = self.embedding_client.get(f"{embedding_url}/health")
                if response.status_code == 200:
                    info = response.json()
                    logger.info(f"✓ Embedding service connected: {info.get('model')} ({info.get('dimension')} dims)")
                else:
                    logger.warning(f"Embedding service unhealthy. Falling back to exact matching.")
                    self.use_semantic = False
            except Exception as e:
                logger.warning(f"Embedding service unavailable: {e}. Falling back to exact matching.")
                self.use_semantic = False
    
    def _generate_key(self, prompt: str, max_tokens: int) -> str:
        """Generate cache key from prompt + params

        Args:
            prompt (str): Prompt from the user
            max_tokens (int): Max tokens allowed

        Returns:
            str: Hashed Key for Redis
        """
        content = f"{prompt}:{max_tokens}"
        return f"llama:cache:{hashlib.sha256(content.encode()).hexdigest()}"
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for text from embedding service

        Args:
            text: Text to embed

        Returns:
            384-dim embedding vector or None if failed
        """
        if not self.use_semantic or not self.embedding_client:
            return None
        
        try:
            response = self.embedding_client.post(
                f"{self.embedding_url}/embed",
                json={"texts": [text]},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["embeddings"][0]
            else:
                logger.error(f"Embedding service error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def _search_similar(self, embedding: List[float], max_tokens: int) -> Optional[tuple]:
        """Search for semantically similar cached prompts

        Args:
            embedding: Query embedding vector
            max_tokens: Max tokens parameter (for filtering)

        Returns:
            Tuple of (cache_key, response, similarity_score) or None
        """
        if not self.redis_client or not embedding:
            return None
        
        try:
            # Search all cache keys for similar vectors
            # Simple approach: scan and compare (for < 10k entries)
            # For production with >10k entries, use Redis VSS (RediSearch)
            
            best_score = 0.0
            best_key = None
            best_response = None
            
            for key in self.redis_client.scan_iter(match="llama:cache:*"):
                try:
                    cached_data = json.loads(self.redis_client.get(key))
                    
                    # Check if same max_tokens
                    if cached_data.get("max_tokens") != max_tokens:
                        continue
                    
                    cached_embedding = cached_data.get("embedding")
                    if not cached_embedding:
                        continue
                    
                    # Compute cosine similarity
                    score = self._cosine_similarity(embedding, cached_embedding)
                    
                    if score > best_score:
                        best_score = score
                        best_key = key.decode() if isinstance(key, bytes) else key
                        best_response = cached_data.get("response")
                
                except Exception as e:
                    continue  # Skip malformed entries
            
            if best_score >= self.similarity_threshold:
                logger.info(f"Semantic match found: similarity={best_score:.3f}")
                return (best_key, best_response, best_score)
            
            return None
        
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        try:
            import math
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
        
        except Exception as e:
            logger.error(f"Cosine similarity error: {e}")
            return 0.0
    
    def get(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Get stored cache (with semantic search if enabled)

        Args:
            prompt: User prompt
            max_tokens: Max tokens parameter

        Returns:
            Cached response or None
        """
        if not self.redis_client:
            return None
        
        try:
            # 1. Try exact match first (fastest)
            key = self._generate_key(prompt, max_tokens)
            cached = self.redis_client.get(key)
            if cached:
                # Handle both string and JSON formats
                if isinstance(cached, bytes):
                    cached = cached.decode()
                if cached.startswith("{"):
                    cached_data = json.loads(cached)
                    response = cached_data.get("response", cached)
                else:
                    response = cached
                
                logger.info(f"Cache HIT (exact) for key: {key[:16]}...")
                return response
            
            # 2. Try semantic search if enabled
            if self.use_semantic:
                embedding = self._get_embedding(prompt)
                if embedding:
                    result = self._search_similar(embedding, max_tokens)
                    if result:
                        _, response, score = result
                        logger.info(f"Cache HIT (semantic) similarity={score:.3f}")
                        return response
            
            # 3. Cache miss
            logger.info(f"Cache MISS for prompt (len={len(prompt)})")
            return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, prompt: str, max_tokens: int, response: str, ttl: int = 1800):
        """Cache response with TTL (default 30 mins)

        Args:
            prompt: User prompt
            max_tokens: Max tokens parameter
            response: Model response
            ttl: Time to live in seconds (default: 30 mins)
        """
        if not self.redis_client:
            return
        
        try:
            key = self._generate_key(prompt, max_tokens)
            
            # Get embedding if semantic caching is enabled
            embedding = None
            if self.use_semantic:
                embedding = self._get_embedding(prompt)
            
            # Store with embedding for semantic search
            if embedding:
                cache_data = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "response": response,
                    "embedding": embedding
                }
                self.redis_client.setex(key, ttl, json.dumps(cache_data))
                logger.info(f"Cached response (semantic) for key: {key[:16]}... (TTL: {ttl}s)")
            else:
                # Fallback: store response only (backward compatible)
                self.redis_client.setex(key, ttl, response)
                logger.info(f"Cached response (exact) for key: {key[:16]}... (TTL: {ttl}s)")
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self, pattern: str = "llama:cache:*"):
        """Clear all cached responses"

        Args:
            pattern (_type_, optional): Basic hash key. Defaults to "llama:cache:*".

        Returns:
            int: returns 0 by default
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = list(self.redis_client.scan_iter(match=pattern))
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"✓ Cleared {deleted} cached responses")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "disabled"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "keys": self.redis_client.dbsize(),
                "memory_used": info.get("used_memory_human"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}