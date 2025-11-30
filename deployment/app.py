from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
import os
import time
from modelclass import CounselGPTModel
from cache import ResponseCache

from metrics import (
    INFERENCE_TIME,
    TOKENS_GENERATED,
    CACHE_HITS,
    CACHE_MISSES,
    add_metrics_middleware
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CounselGPT API", version="1.0")

# Attach Prometheus metrics
add_metrics_middleware(app)

# Initialize model
logger.info("Initializing CounselGPT model...")
model = CounselGPTModel(
    model_path="/models/llama-2-7b-chat.Q4_K_M.gguf",
    n_gpu_layers=35
)

# Initialize cache
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
cache = ResponseCache(redis_url=redis_url)

class InferRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4096)
    max_tokens: int = Field(200, ge=1, le=2048)
    use_cache: bool = Field(True, description="Use cached response if available")

class InferResponse(BaseModel):
    response: str
    prompt_length: int
    response_length: int
    cached: bool = False

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "cache_stats": cache.stats()
    }

@app.post("/infer", response_model=InferResponse)
def infer_text(req: InferRequest):
    try:
        logger.info(f"Received inference request (prompt_len={len(req.prompt)}, max_tokens={req.max_tokens}, use_cache={req.use_cache})")
        
        # Try cache first (if enabled)
        if req.use_cache:
            cached_response = cache.get(req.prompt, req.max_tokens)
            if cached_response:
                CACHE_HITS.inc()
                return InferResponse(
                    response=cached_response,
                    prompt_length=len(req.prompt),
                    response_length=len(cached_response),
                    cached=True
                )
            else:
                CACHE_HITS.inc()
        
        # Cache miss or disabled - run inference
        # Measure inference duration
        start = time.time()
        result = model.infer(req.prompt, req.max_tokens)
        INFERENCE_TIME.observe(time.time() - start)
        
        # Count tokens
        TOKENS_GENERATED.inc(len(result.split()))

        # Cache the result (if cache enabled)
        if req.use_cache:
            cache.set(req.prompt, req.max_tokens, result, ttl=3600)
        
        return InferResponse(
            response=result,
            prompt_length=len(req.prompt),
            response_length=len(result),
            cached=False
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        raise HTTPException(status_code=500, detail="Model inference failed")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/cache/clear")
def clear_cache():
    """Clear all cached responses"""
    deleted = cache.clear()
    return {"message": f"Cleared {deleted} cached responses"}

@app.get("/cache/stats")
def cache_stats():
    """Get cache statistics"""
    return cache.stats()

@app.get("/")
def root():
    return {
        "message": "CounselGPT API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "infer": "/infer (POST)",
            "cache_clear": "/cache/clear (POST)",
            "cache_stats": "/cache/stats (GET)"
        }
    }