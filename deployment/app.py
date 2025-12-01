from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
import time
import os

from modelclass import CounselGPTModel
from cache import ResponseCache
from metrics import (
    INFERENCE_TIME,
    TOKENS_GENERATED,
    CACHE_HITS,
    CACHE_MISSES,
    add_metrics_middleware
)
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("counselgpt-api")

app = FastAPI(title="CounselGPT API", version="2.0")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Prometheus Metrics
# -----------------------------
add_metrics_middleware(app)

# -----------------------------
# Cache
# -----------------------------
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
cache = ResponseCache(redis_url=redis_url)


# -----------------------------
# Request/Response Models
# -----------------------------
class InferRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4096, description="User prompt/question")
    max_tokens: int = Field(400, ge=1, le=2048, description="Maximum tokens to generate (default: 400, ~300 words)")
    model_name: str = Field("qwen", description="Model to use: 'qwen' (Qwen2.5-7B with LoRA) or 'llama' (Llama-2-7B)")
    use_gpu: bool = Field(True, description="Use GPU acceleration (recommended)")
    use_cache: bool = Field(True, description="Use Redis cache for faster repeated queries")


class InferResponse(BaseModel):
    response: str = Field(..., description="Generated text response")
    prompt_length: int = Field(..., description="Length of input prompt in characters")
    response_length: int = Field(..., description="Length of generated response in characters")
    cached: bool = Field(default=False, description="Whether response was served from cache")
    model_used: str = Field(default="qwen", description="Model that generated the response")


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cache": cache.stats(),
        "available_models": ["qwen", "llama"],
    }


# -----------------------------
# INFERENCE ENDPOINT
# -----------------------------
@app.post("/infer", response_model=InferResponse)
def infer(req: InferRequest):
    """
    Perform model inference (Qwen or Llama)
    """

    logger.info(
        f"Received infer request model={req.model_name}, "
        f"use_gpu={req.use_gpu}, "
        f"max_tokens={req.max_tokens}, "
        f"use_cache={req.use_cache}"
    )

    # -----------------------------
    # 1️⃣ Cache Check
    # -----------------------------
    if req.use_cache:
        cached_response = cache.get(req.prompt, req.max_tokens)
        if cached_response:
            CACHE_HITS.inc()
            logger.info(f"Cache hit for prompt (length={len(req.prompt)})")
            return InferResponse(
                response=cached_response,
                prompt_length=len(req.prompt),
                response_length=len(cached_response),
                cached=True,
                model_used=req.model_name,
            )
        else:
            CACHE_MISSES.inc()

    # -----------------------------
    # 2️⃣ Validate Model Name
    # -----------------------------
    if req.model_name.lower() not in ["qwen", "llama"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model_name: {req.model_name}. Must be 'qwen' or 'llama'"
        )

    # -----------------------------
    # 3️⃣ Run Inference Using ModelFactory
    # -----------------------------
    try:
        model = CounselGPTModel(model_name=req.model_name, use_gpu=req.use_gpu)

        start_time = time.time()
        result = model.infer(req.prompt, req.max_tokens)
        inference_time = time.time() - start_time
        
        INFERENCE_TIME.observe(inference_time)
        TOKENS_GENERATED.inc(len(result.split()))
        
        logger.info(f"Inference completed in {inference_time:.2f}s, generated {len(result)} chars")

    except ValueError as e:
        logger.error(f"Validation Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        logger.error(f"Inference Runtime Error: {e}")
        raise HTTPException(status_code=500, detail="Model inference failed")

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # -----------------------------
    # 4️⃣ Cache Result
    # -----------------------------
    if req.use_cache:
        cache.set(req.prompt, req.max_tokens, result, ttl=3600)

    return InferResponse(
        response=result,
        prompt_length=len(req.prompt),
        response_length=len(result),
        cached=False,
        model_used=req.model_name,
    )


# -----------------------------
# Cache Admin
# -----------------------------
@app.post("/cache/clear")
def clear_cache():
    deleted = cache.clear()
    return {"message": f"Cleared {deleted} cached responses"}


@app.get("/cache/stats")
def cache_stats():
    return cache.stats()


@app.get("/")
def root():
    return {
        "message": "CounselGPT API",
        "version": "2.0",
        "usage": {
            "/infer": {
                "method": "POST",
                "description": "Run inference",
                "body": {
                    "prompt": "User prompt",
                    "max_tokens": "1-2048",
                    "model_name": "qwen (default) or llama",
                    "use_gpu": "true/false",
                    "use_cache": "true/false",
                },
            },
            "/cache/stats": "GET",
            "/cache/clear": "POST",
            "/health": "GET",
        },
    }
