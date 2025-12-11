from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
# Lazy import: modelclass only imported when /infer endpoint is called
# This allows RAG endpoints to work without requiring llama-cpp-python
# from modelclass import CounselGPTModel
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

# RAG imports
from rag import get_rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("counselgpt-api")

app = FastAPI(title="CounselGPT API", version="2.1")

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
    messages: Optional[List[Message]] = Field(None, description="Conversation history (preferred over single prompt)")
    # Legacy: single prompt (for backward compatibility)
    prompt: Optional[str] = Field(None, min_length=1, max_length=4096, description="User prompt/question (legacy)")
    max_tokens: int = Field(400, ge=1, le=2048, description="Maximum tokens to generate (default: 400, ~300 words)")
    model_name: str = Field("qwen", description="Model to use: 'qwen' (Qwen2.5-7B with LoRA) or 'llama' (Llama-2-7B)")
    use_gpu: bool = Field(True, description="Use GPU acceleration (recommended)")
    use_cache: bool = Field(True, description="Use Redis cache for faster repeated queries")
    semantic_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional: Override semantic similarity threshold (0.0-1.0)")
    # RAG parameters
    use_rag: bool = Field(False, description="Use RAG to retrieve document context before inference")
    rag_top_k: int = Field(3, ge=1, le=10, description="Number of context chunks to retrieve for RAG")
    document_id: Optional[str] = Field(None, description="Specific document to search (None = default)")


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
    # RAG info
    rag_used: bool = Field(default=False, description="Whether RAG context was used")
    rag_context_length: int = Field(default=0, description="Length of RAG context in characters")


# -----------------------------
# RAG Models
# -----------------------------
class IndexDocumentRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Document text to index")
    document_id: str = Field("default", description="Unique identifier for this document")
    use_semantic_chunking: bool = Field(True, description="Use semantic chunking (better quality, slower)")
    max_chunk_size: int = Field(512, ge=100, le=2000, description="Maximum characters per chunk")
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Threshold for grouping sentences")
    set_as_default: bool = Field(True, description="Set this as the default document for queries")


class IndexDocumentResponse(BaseModel):
    document_id: str
    num_chunks: int
    is_default: bool
    chunking_method: str
    message: str


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query to search for")
    document_id: Optional[str] = Field(None, description="Specific document to search")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    use_reranking: bool = Field(True, description="Apply cross-encoder reranking")


class RAGQueryResponse(BaseModel):
    query: str
    results: List[dict]
    context: str
    document_id: Optional[str]


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
    rag_service = get_rag_service()
    return {
        "status": "healthy",
        "cache": cache.stats(),
        "available_models": ["qwen", "llama"],
        "context_window": 2048,
        "max_tokens_per_request": 2048,
        "rag": {
            "enabled": True,
            "has_default_index": rag_service.has_index(),
            "indexed_documents": len(rag_service.list_documents())
        }
    }


# -----------------------------
# RAG ENDPOINTS
# -----------------------------
@app.post("/rag/index", response_model=IndexDocumentResponse)
def index_document(req: IndexDocumentRequest):
    """
    Index a document for RAG retrieval.
    
    This creates a searchable index from the document text using:
    - Semantic chunking (groups related sentences)
    - BM25 index (keyword search)
    - Dense embeddings (semantic search)
    """
    try:
        rag_service = get_rag_service()
        
        result = rag_service.index_document(
            text=req.text,
            document_id=req.document_id,
            use_semantic_chunking=req.use_semantic_chunking,
            max_chunk_size=req.max_chunk_size,
            similarity_threshold=req.similarity_threshold,
            set_as_default=req.set_as_default
        )
        
        logger.info(f"Indexed document '{req.document_id}' with {result['num_chunks']} chunks")
        
        return IndexDocumentResponse(
            document_id=result["document_id"],
            num_chunks=result["num_chunks"],
            is_default=result["is_default"],
            chunking_method=result["chunking_method"],
            message=f"Successfully indexed document with {result['num_chunks']} chunks"
        )
        
    except Exception as e:
        logger.error(f"Failed to index document: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/rag/query", response_model=RAGQueryResponse)
def query_rag(req: RAGQueryRequest):
    """
    Query the RAG index to retrieve relevant document chunks.
    
    Returns the top-k most relevant chunks with scores.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service.has_index(req.document_id):
            raise HTTPException(
                status_code=400,
                detail=f"No index found for document '{req.document_id or 'default'}'. Index a document first."
            )
        
        results = rag_service.retrieve_with_scores(
            query=req.query,
            document_id=req.document_id,
            top_k=req.top_k,
            use_reranking=req.use_reranking
        )
        
        context = rag_service.retrieve_context(
            query=req.query,
            document_id=req.document_id,
            top_k=req.top_k,
            use_reranking=req.use_reranking
        )
        
        return RAGQueryResponse(
            query=req.query,
            results=results,
            context=context,
            document_id=req.document_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/rag/stats")
def rag_stats():
    """Get RAG service statistics."""
    rag_service = get_rag_service()
    return rag_service.get_stats()


@app.get("/rag/documents")
def list_rag_documents():
    """List all indexed documents."""
    rag_service = get_rag_service()
    return {
        "documents": rag_service.list_documents()
    }


@app.delete("/rag/documents/{document_id}")
def delete_rag_document(document_id: str):
    """Delete a document index."""
    rag_service = get_rag_service()
    
    if rag_service.delete_document(document_id):
        return {"message": f"Deleted document '{document_id}'"}
    else:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found")


# -----------------------------
# INFERENCE ENDPOINT
# -----------------------------
@app.post("/infer", response_model=InferResponse)
def infer(req: InferRequest):
    """
    Perform model inference (Qwen or Llama) with optional RAG context.
    
    If use_rag=True, retrieves relevant document context and includes it
    in the prompt for more accurate, document-grounded responses.
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
        
        # Extract the last user message for RAG query
        last_user_message = None
        for msg in reversed(req.messages):
            if msg.role == "user":
                last_user_message = msg.content
                break
        
        # Add final prompt for assistant
        conversation_text += "Assistant:"
        full_prompt = conversation_text
        messages_count = len(req.messages)
        rag_query = last_user_message or full_prompt
        
    elif req.prompt:
        # Legacy: single prompt
        full_prompt = req.prompt
        messages_count = 1
        rag_query = req.prompt
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'messages' or 'prompt' must be provided"
        )
    
    # -----------------------------
    # RAG Context Retrieval
    # -----------------------------
    rag_context = ""
    rag_used = False
    
    if req.use_rag:
        rag_service = get_rag_service()
        
        if rag_service.has_index(req.document_id):
            try:
                rag_context = rag_service.retrieve_context(
                    query=rag_query,
                    document_id=req.document_id,
                    top_k=req.rag_top_k,
                    use_reranking=True
                )
                rag_used = bool(rag_context)
                logger.info(f"RAG context retrieved: {len(rag_context)} chars")
            except Exception as e:
                logger.warning(f"RAG retrieval failed, proceeding without context: {e}")
        else:
            logger.warning(f"RAG requested but no index found for '{req.document_id or 'default'}'")
    
    # Estimate token count (rough: 1 token ≈ 4 chars)
    total_prompt_length = len(full_prompt) + len(rag_context)
    estimated_tokens = total_prompt_length // 4
    
    logger.info(
        f"Received infer request model={req.model_name}, "
        f"use_gpu={req.use_gpu}, "
        f"max_tokens={req.max_tokens}, "
        f"use_cache={req.use_cache}, "
        f"use_rag={req.use_rag}, "
        f"rag_used={rag_used}, "
        f"threshold={req.semantic_threshold}, "
        f"messages={messages_count}, "
        f"est_tokens={estimated_tokens}"
    )

    # -----------------------------
    # Cache Check (include RAG context in cache key)
    # -----------------------------
    cache_key_prompt = f"{full_prompt}|RAG:{rag_context[:500] if rag_context else 'none'}"
    
    if req.use_cache:
        cached_response = cache.get(cache_key_prompt, req.max_tokens, threshold=req.semantic_threshold)
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
                rag_used=rag_used,
                rag_context_length=len(rag_context),
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
        # Lazy import - only load when /infer endpoint is called
        from modelclass import CounselGPTModel
        model = CounselGPTModel(model_name=req.model_name, use_gpu=req.use_gpu)

        start_time = time.time()
        # Pass RAG context to the model
        result = model.infer(full_prompt, req.max_tokens, rag_context=rag_context)
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
        cache.set(cache_key_prompt, req.max_tokens, result, ttl=3600)

    return InferResponse(
        response=result,
        prompt_length=len(full_prompt),
        response_length=len(result),
        cached=False,
        model_used=req.model_name,
        estimated_tokens=estimated_tokens,
        context_window=2048,
        messages_in_context=messages_count,
        rag_used=rag_used,
        rag_context_length=len(rag_context),
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
        "version": "2.1",
        "features": {
            "rag": "Production-grade RAG with hybrid search and reranking",
            "models": ["qwen (Qwen2.5-7B + LoRA)", "llama (LLaMA-2-7B)"],
            "caching": "Semantic cache with Redis",
        },
        "usage": {
            "/infer": {
                "method": "POST",
                "description": "Run inference with optional RAG context",
                "body": {
                    "prompt": "User prompt",
                    "max_tokens": "1-2048",
                    "model_name": "qwen (default) or llama",
                    "use_gpu": "true/false",
                    "use_cache": "true/false",
                    "use_rag": "true/false (retrieve document context)",
                    "rag_top_k": "1-10 (chunks to retrieve)",
                },
            },
            "/rag/index": {
                "method": "POST",
                "description": "Index a document for RAG",
            },
            "/rag/query": {
                "method": "POST", 
                "description": "Query RAG index directly",
            },
            "/rag/stats": "GET - RAG service statistics",
            "/rag/documents": "GET - List indexed documents",
            "/cache/stats": "GET",
            "/cache/clear": "POST",
            "/health": "GET",
        },
    }
