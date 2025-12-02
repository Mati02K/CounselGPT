"""
Semantic Embedding Service
Runs alongside Redis to generate embeddings for semantic caching
"""
import os
import numpy as np
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Semantic Embedding Service")

# Load embedding model on startup
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
logger.info(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
logger.info(f"Model loaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}")


class EmbedRequest(BaseModel):
    texts: List[str]


class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimension: int


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "dimension": model.get_sentence_embedding_dimension()
    }


@app.post("/embed", response_model=EmbedResponse)
def embed_texts(request: EmbedRequest):
    """Generate embeddings for input texts"""
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        # Generate embeddings
        embeddings = model.encode(request.texts, convert_to_numpy=True)
        
        # Convert to list of lists for JSON serialization
        embeddings_list = embeddings.tolist()
        
        logger.info(f"Generated {len(embeddings_list)} embeddings")
        
        return EmbedResponse(
            embeddings=embeddings_list,
            model=MODEL_NAME,
            dimension=model.get_sentence_embedding_dimension()
        )
    
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {
        "service": "Semantic Embedding Service",
        "model": MODEL_NAME,
        "dimension": model.get_sentence_embedding_dimension(),
        "endpoints": {
            "/health": "Health check",
            "/embed": "POST - Generate embeddings"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

