import redis
import json
import hashlib
import logging
import os
import httpx
import time
import threading
from typing import Optional, List

logger = logging.getLogger("counselgpt-api.cache")

class ResponseCache:
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        embedding_url: str = "http://counselgpt-redis:8000",
        use_semantic: bool = True,
        similarity_threshold: float = 0.95,
        retry_delay: float = 5.0
    ):
        """Initialize Redis Cache in a non-blocking background thread."""

        logger.setLevel(logging.INFO)
        self.redis_url = redis_url
        self.embedding_url = embedding_url
        self.retry_delay = retry_delay
        self.similarity_threshold = similarity_threshold
        
        # Flags
        self.use_semantic = use_semantic
        self.is_connected = False
        self.embedding_available = False
        
        # Clients (Initially None)
        self.redis_client = None
        self.embedding_client = None

        # Start connection logic in a background thread so app startup isn't blocked
        self._stop_event = threading.Event()
        self._bg_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self._bg_thread.start()
        
        logger.info("ResponseCache initialized (Connection strictly in background)")

    def _background_monitor(self):
        """
        Background loop that attempts to connect and maintain connections.
        This runs forever (daemon) checking health without blocking the main app.
        """
        # Initialize HTTP client once for this thread
        self.embedding_client = httpx.Client(timeout=2.0)

        while not self._stop_event.is_set():
            # 1. Handle Redis Connection
            if not self.redis_client:
                try:
                    client = redis.from_url(self.redis_url, decode_responses=False, socket_timeout=1.0)
                    client.ping()
                    self.redis_client = client
                    self.is_connected = True
                    logger.info("✓ Redis connected successfully (Background)")
                except Exception as e:
                    logger.debug(f"Background Redis connection failed: {e}")
                    self.is_connected = False
            else:
                # Keep-alive check
                try:
                    self.redis_client.ping()
                except Exception:
                    logger.warning("Redis connection lost. Resetting...")
                    self.redis_client = None
                    self.is_connected = False

            # 2. Handle Embedding Service (only if Redis is up and semantic is requested)
            if self.use_semantic and self.is_connected:
                try:
                    resp = self.embedding_client.get(f"{self.embedding_url}/health", timeout=2.0)
                    if resp.status_code == 200:
                        if not self.embedding_available:
                            logger.info("✓ Embedding service connected (Background)")
                        self.embedding_available = True
                    else:
                        self.embedding_available = False
                except Exception:
                    self.embedding_available = False

            # Wait before next check
            time.sleep(self.retry_delay)

    def _generate_key(self, prompt: str, max_tokens: int) -> str:
        content = f"{prompt}:{max_tokens}"
        return f"llama:cache:{hashlib.sha256(content.encode()).hexdigest()}"
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        # Fail fast if service not marked available
        if not self.embedding_available:
            return None
        
        try:
            response = self.embedding_client.post(
                f"{self.embedding_url}/embed",
                json={"texts": [text]},
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()["embeddings"][0]
        except Exception as e:
            logger.error(f"Embedding fetch failed: {e}")
        return None

    def _search_similar(self, embedding: List[float], max_tokens: int) -> Optional[tuple]:
        if not self.is_connected or not self.redis_client:
            return None
        
        try:
            # Note: SCAN is slow for large DBs. 
            best_score = 0.0
            best_key = None
            best_response = None
            
            # Using scan_iter is safer than keys()
            for key in self.redis_client.scan_iter(match="llama:cache:*"):
                try:
                    raw = self.redis_client.get(key)
                    if not raw: continue
                    
                    cached_data = json.loads(raw)
                    if cached_data.get("max_tokens") != max_tokens: continue
                    
                    cached_emb = cached_data.get("embedding")
                    if not cached_emb: continue
                    
                    score = self._cosine_similarity(embedding, cached_emb)
                    if score > best_score:
                        best_score = score
                        best_key = key
                        best_response = cached_data.get("response")
                except (json.JSONDecodeError, TypeError):
                    continue

            if best_score >= self.similarity_threshold:
                return (best_key, best_response, best_score)
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        import math
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            if magnitude1 == 0 or magnitude2 == 0: return 0.0
            return dot_product / (magnitude1 * magnitude2)
        except Exception:
            return 0.0

    def get(self, prompt: str, max_tokens: int) -> Optional[str]:
        """
        Non-blocking Get. Returns None immediately if Redis is down.
        """
        # 1. Fail Fast Check
        if not self.is_connected or not self.redis_client:
            # Do not log here to avoid spamming logs on every request when down
            return None
        
        try:
            # 2. Exact Match
            key = self._generate_key(prompt, max_tokens)
            cached = self.redis_client.get(key)
            
            if cached:
                if isinstance(cached, bytes): cached = cached.decode()
                # Handle JSON wrapper if present
                if cached.startswith("{"):
                    try:
                        data = json.loads(cached)
                        return data.get("response", cached)
                    except:
                        return cached
                return cached
            
            # 3. Semantic Search (only if enabled and available)
            if self.use_semantic and self.embedding_available:
                embedding = self._get_embedding(prompt)
                if embedding:
                    result = self._search_similar(embedding, max_tokens)
                    if result:
                        logger.info(f"Cache HIT (semantic) score={result[2]:.2f}")
                        return result[1]

            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, prompt: str, max_tokens: int, response: str, ttl: int = 1800):
        """
        Non-blocking Set. Does nothing if Redis is down.
        """
        if not self.is_connected or not self.redis_client:
            return
        
        try:
            key = self._generate_key(prompt, max_tokens)
            
            # Try to get embedding, but don't fail operation if embedding service is down
            embedding = None
            if self.use_semantic and self.embedding_available:
                embedding = self._get_embedding(prompt)
            
            if embedding:
                data = {
                    "prompt": prompt, 
                    "max_tokens": max_tokens, 
                    "response": response, 
                    "embedding": embedding
                }
                self.redis_client.setex(key, ttl, json.dumps(data))
            else:
                self.redis_client.setex(key, ttl, response)
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def stats(self) -> dict:
        """
        Safe stats for Health Checks. 
        Returns 'degraded' instead of crashing if Redis is down.
        """
        if not self.is_connected or not self.redis_client:
            return {
                "status": "degraded", 
                "detail": "Redis unavailable - Caching disabled"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "status": "healthy",
                "keys": self.redis_client.dbsize(),
                "memory": info.get("used_memory_human"),
                "semantic_active": self.embedding_available
            }
        except Exception:
            return {"status": "degraded", "detail": "Connection Error"}

    def close(self):
        """Cleanup thread on shutdown"""
        self._stop_event.set()
        if self._bg_thread.is_alive():
            self._bg_thread.join(timeout=1.0)