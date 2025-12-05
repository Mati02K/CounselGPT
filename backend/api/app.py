from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
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
import logging
import time
import os

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
class Message(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")


class InferRequest(BaseModel):
    # New: conversation history (preferred)
    messages: Optional[list[Message]] = Field(None, description="Conversation history (preferred over single prompt)")
    # Legacy: single prompt (for backward compatibility)
    prompt: Optional[str] = Field(None, min_length=1, max_length=4096, description="User prompt/question (legacy)")
    max_tokens: int = Field(400, ge=1, le=2048, description="Maximum tokens to generate (default: 400, ~300 words)")
    model_name: str = Field("qwen", description="Model to use: 'qwen' (Qwen2.5-7B with LoRA) or 'llama' (Llama-2-7B)")
    use_gpu: bool = Field(True, description="Use GPU acceleration (recommended)")
    use_cache: bool = Field(True, description="Use Redis cache for faster repeated queries")
    semantic_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional: Override semantic similarity threshold (0.0-1.0)")


class InferResponse(BaseModel):
    response: str = Field(..., description="Generated text response")
    prompt_length: int = Field(..., description="Length of input prompt in characters")
    response_length: int = Field(..., description="Length of generated response in characters")
    cached: bool = Field(default=False, description="Whether response was served from cache")
    model_used: str = Field(default="qwen", description="Model that generated the response")
    # New: context tracking
    estimated_tokens: int = Field(default=0, description="Approximate tokens in prompt (chars / 4)")
    context_window: int = Field(default=2048, description="Maximum context window size")
    messages_in_context: int = Field(default=1, description="Number of messages in context")


# -----------------------------
# METRICS ENDPOINT
# -----------------------------
@app.get("/metrics")
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cache": cache.stats(),
        "available_models": ["qwen", "llama"],
        "context_window": 2048,  # Token limit for models
        "max_tokens_per_request": 2048,
    }


# -----------------------------
# INFERENCE ENDPOINT
# -----------------------------
@app.post("/infer", response_model=InferResponse)
def infer(req: InferRequest):
    """
    Perform model inference (Qwen or Llama) with conversation context
    """
    
    # -----------------------------
    # Build Prompt from Messages or Legacy Prompt
    # -----------------------------
    if req.messages:
        # New: conversation history
        conversation_text = ""
        for msg in req.messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            conversation_text += f"{role_label}: {msg.content}\n\n"
        
        # Add final prompt for assistant
        conversation_text += "Assistant:"
        full_prompt = conversation_text
        messages_count = len(req.messages)
    elif req.prompt:
        # Legacy: single prompt
        full_prompt = req.prompt
        messages_count = 1
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'messages' or 'prompt' must be provided"
        )
    
    # Estimate token count (rough: 1 token ≈ 4 chars)
    estimated_tokens = len(full_prompt) // 4
    
    logger.info(
        f"Received infer request model={req.model_name}, "
        f"use_gpu={req.use_gpu}, "
        f"max_tokens={req.max_tokens}, "
        f"use_cache={req.use_cache}, "
        f"threshold={req.semantic_threshold}, "
        f"messages={messages_count}, "
        f"est_tokens={estimated_tokens}"
    )

    # -----------------------------
    # Cache Check
    # -----------------------------
    if req.use_cache:
        cached_response = cache.get(full_prompt, req.max_tokens, threshold=req.semantic_threshold)
        if cached_response:
            CACHE_HITS.inc()
            logger.info(f"Cache hit for prompt (length={len(full_prompt)})")
            return InferResponse(
                response=cached_response,
                prompt_length=len(full_prompt),
                response_length=len(cached_response),
                cached=True,
                model_used=req.model_name,
                estimated_tokens=estimated_tokens,
                context_window=2048,
                messages_in_context=messages_count,
            )
        else:
            CACHE_MISSES.inc()

    # -----------------------------
    # Validate Model Name
    # -----------------------------
    if req.model_name.lower() not in ["qwen", "llama"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model_name: {req.model_name}. Must be 'qwen' or 'llama'"
        )

    # -----------------------------
    # Run Inference Using ModelFactory
    # -----------------------------
    try:
        model = CounselGPTModel(model_name=req.model_name, use_gpu=req.use_gpu)

        start_time = time.time()
        result = model.infer(full_prompt, req.max_tokens)
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
    # Cache Result
    # -----------------------------
    if req.use_cache:
        cache.set(full_prompt, req.max_tokens, result, ttl=3600)

    return InferResponse(
        response=result,
        prompt_length=len(full_prompt),
        response_length=len(result),
        cached=False,
        model_used=req.model_name,
        estimated_tokens=estimated_tokens,
        context_window=2048,
        messages_in_context=messages_count,
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
