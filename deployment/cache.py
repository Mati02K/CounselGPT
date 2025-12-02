import redis
import json
import hashlib
import logging
import os
import numpy as np
from typing import Optional, List, Tuple
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ResponseCache:
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        use_semantic: bool = True,
        similarity_threshold: float = 0.95,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize Redis Cache with optional semantic caching
        
        Args:
            redis_url: Redis connection URL
            use_semantic: Enable semantic caching (default: True)
            similarity_threshold: Cosine similarity threshold (0.95 = 95% similar)
            embedding_model: Sentence transformer model for embeddings
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
        
        # Semantic caching setup
        self.use_semantic = use_semantic
        self.similarity_threshold = similarity_threshold
        self.encoder = None
        
        if self.use_semantic:
            try:
                logger.info(f"Loading embedding model: {embedding_model}")
                self.encoder = SentenceTransformer(embedding_model)
                logger.info("✓ Semantic caching enabled")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}. Falling back to exact matching.")
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
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding vector for text
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of embedding or None if encoder not available
        """
        if not self.encoder:
            return None
        
        try:
            embedding = self.encoder.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _find_similar_cached_prompt(
        self, 
        prompt: str, 
        max_tokens: int
    ) -> Optional[Tuple[str, float]]:
        """Find semantically similar cached prompt
        
        Args:
            prompt: User prompt to search for
            max_tokens: Max tokens parameter
            
        Returns:
            Tuple of (cached_response, similarity_score) or None
        """
        if not self.use_semantic or not self.encoder:
            return None
        
        try:
            # Get embedding for current prompt
            current_embedding = self._get_embedding(prompt)
            if current_embedding is None:
                return None
            
            # Search through all cached prompts with same max_tokens
            pattern = f"llama:cache:*"
            best_match = None
            best_similarity = 0.0
            
            for key in self.redis_client.scan_iter(match=pattern, count=100):
                try:
                    # Get metadata for this cache entry
                    metadata_key = f"{key}:metadata"
                    metadata = self.redis_client.get(metadata_key)
                    
                    if not metadata:
                        continue
                    
                    meta = json.loads(metadata)
                    
                    # Check if max_tokens matches
                    if meta.get("max_tokens") != max_tokens:
                        continue
                    
                    # Get stored embedding
                    embedding_str = meta.get("embedding")
                    if not embedding_str:
                        continue
                    
                    stored_embedding = np.array(json.loads(embedding_str))
                    
                    # Calculate similarity
                    similarity = self._cosine_similarity(current_embedding, stored_embedding)
                    
                    # Track best match
                    if similarity > best_similarity and similarity >= self.similarity_threshold:
                        best_similarity = similarity
                        cached_response = self.redis_client.get(key)
                        if cached_response:
                            best_match = (cached_response, similarity)
                            logger.info(
                                f"Semantic match found! Similarity: {similarity:.3f} "
                                f"(threshold: {self.similarity_threshold})"
                            )
                
                except Exception as e:
                    logger.debug(f"Error checking key {key}: {e}")
                    continue
            
            return best_match
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return None
    
    def get(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Get stored cache with semantic matching

        Args:
            prompt (str): Prompt from the user
            max_tokens (int): Max tokens

        Returns:
            str | None: returns the stored value if exact or semantic match is found
        """
        if not self.redis_client:
            return None
        
        try:
            # First try exact match (fastest)
            key = self._generate_key(prompt, max_tokens)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.info(f"Cache HIT (exact) for key: {key[:16]}...")
                return cached
            
            # If no exact match and semantic caching enabled, try semantic search
            if self.use_semantic:
                logger.info(f"Cache MISS (exact), trying semantic search...")
                semantic_match = self._find_similar_cached_prompt(prompt, max_tokens)
                
                if semantic_match:
                    response, similarity = semantic_match
                    logger.info(
                        f"Cache HIT (semantic) with {similarity*100:.1f}% similarity"
                    )
                    return response
            
            logger.info(f"Cache MISS (no matches found)")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, prompt: str, max_tokens: int, response: str, ttl: int = 1800):
        """Cache response with TTL and optional embedding (default 30 mins)

        Args:
            prompt (str): Prompt from the user
            max_tokens (int): Max tokens
            response (str): Response from the model
            ttl (int, optional): Time to Live (30 mins). Defaults to 1800.
        """
        if not self.redis_client:
            return
        
        try:
            key = self._generate_key(prompt, max_tokens)
            
            # Store the response
            self.redis_client.setex(key, ttl, response)
            
            # If semantic caching enabled, store embedding metadata
            if self.use_semantic and self.encoder:
                embedding = self._get_embedding(prompt)
                
                if embedding is not None:
                    metadata = {
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "embedding": json.dumps(embedding.tolist()),
                        "response_length": len(response)
                    }
                    
                    metadata_key = f"{key}:metadata"
                    self.redis_client.setex(metadata_key, ttl, json.dumps(metadata))
                    logger.info(
                        f"Cached response (semantic) for key: {key[:16]}... (TTL: {ttl}s)"
                    )
                else:
                    logger.info(
                        f"Cached response (exact only) for key: {key[:16]}... (TTL: {ttl}s)"
                    )
            else:
                logger.info(f"Cached response for key: {key[:16]}... (TTL: {ttl}s)")
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self, pattern: str = "llama:cache:*"):
        """Clear all cached responses and metadata

        Args:
            pattern (_type_, optional): Basic hash key. Defaults to "llama:cache:*".

        Returns:
            int: returns 0 by default
        """
        if not self.redis_client:
            return 0
        
        try:
            # Clear both cache entries and metadata
            keys = list(self.redis_client.scan_iter(match=pattern))
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"✓ Cleared {deleted} cached responses and metadata")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def stats(self) -> dict:
        """Get cache statistics including semantic caching info"""
        if not self.redis_client:
            return {"status": "disabled"}
        
        try:
            info = self.redis_client.info()
            
            # Count cache entries and metadata entries
            cache_keys = len(list(self.redis_client.scan_iter(match="llama:cache:*", count=1000)))
            metadata_keys = len(list(self.redis_client.scan_iter(match="llama:cache:*:metadata", count=1000)))
            
            stats = {
                "status": "connected",
                "total_keys": self.redis_client.dbsize(),
                "cache_entries": cache_keys - metadata_keys,  # Exclude metadata from count
                "memory_used": info.get("used_memory_human"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "semantic_caching": self.use_semantic,
            }
            
            if self.use_semantic:
                stats["similarity_threshold"] = self.similarity_threshold
                stats["embedding_model"] = "all-MiniLM-L6-v2"
            
            return stats
            
        except Exception as e:
            return {"status": "error", "error": str(e)}