import redis
import json
import hashlib
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class ResponseCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initalize Redis Cache

        Args:
            redis_url (_type_, optional): Redis URL. Defaults to "redis://localhost:6379".
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    def _generate_key(self, prompt: str, max_tokens: int) -> str:
        """Generate cache key from prompt + params

        Args:
            prompt (str): Prompt from the user
            max_tokens (int): Max tokens allowed

        Returns:
            str: Hashed Key for Redis
        """
        content = f"{prompt}:{max_tokens}"
        return f"llama:cache:{hashlib.sha256(content.encode()).hexdigest()}" # I am creating a cache key using hash
    
    def get(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Get stored cache

        Args:
            prompt (str): Prompt from the user
            max_tokens (int): Max tokens

        Returns:
            str | None: returns the stored value if key is found else returns None
        """
        if not self.redis_client:
            return None
        
        try:
            key = self._generate_key(prompt, max_tokens)
            cached = self.redis_client.get(key)
            if cached:
                logger.info(f"Cache HIT for key: {key[:16]}...")
                return cached
            else:
                logger.info(f"Cache MISS for key: {key[:16]}...")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, prompt: str, max_tokens: int, response: str, ttl: int = 1800):
        """Cache response with TTL (default 30 mins)

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
            self.redis_client.setex(key, ttl, response)
            logger.info(f"Cached response for key: {key[:16]}... (TTL: {ttl}s)")
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