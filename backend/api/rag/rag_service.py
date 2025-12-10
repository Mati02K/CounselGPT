"""
RAG Service

High-level service that manages RAG functionality:
- Model loading (bi-encoder, cross-encoder)
- Document indexing
- Context retrieval for LLM
"""

import os
import logging
import threading
from typing import Optional, Dict, Any, List

from sentence_transformers import SentenceTransformer, CrossEncoder

from .hybrid_index import HybridRAGIndex

logger = logging.getLogger(__name__)


class RAGService:
    """
    Production-grade RAG service for CounselGPT.
    
    Manages:
    - Model loading (lazy, thread-safe)
    - Document indexing
    - Context retrieval
    - Multiple document support (future)
    """
    
    _instance: Optional["RAGService"] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for RAG service."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        bi_encoder_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        alpha: float = 0.5,
        enable_reranking: bool = True
    ):
        """
        Initialize the RAG service.
        
        Args:
            bi_encoder_model: Model name/path for dense retrieval
            cross_encoder_model: Model name/path for reranking
            alpha: Hybrid search weight (0=BM25 only, 1=Dense only)
            enable_reranking: Whether to load cross-encoder for reranking
        """
        # Skip re-initialization if already done
        if getattr(self, '_initialized', False):
            return
        
        self.bi_encoder_model = bi_encoder_model
        self.cross_encoder_model = cross_encoder_model
        self.alpha = alpha
        self.enable_reranking = enable_reranking
        
        # Models (lazy-loaded)
        self._bi_encoder: Optional[SentenceTransformer] = None
        self._cross_encoder: Optional[CrossEncoder] = None
        
        # Index storage (document_id -> HybridRAGIndex)
        self._indices: Dict[str, HybridRAGIndex] = {}
        
        # Default/active index
        self._default_index: Optional[HybridRAGIndex] = None
        
        # Thread safety
        self._model_lock = threading.Lock()
        self._index_lock = threading.Lock()
        
        self._initialized = True
        logger.info(f"RAGService initialized (bi_encoder={bi_encoder_model}, reranking={enable_reranking})")
    
    @property
    def bi_encoder(self) -> SentenceTransformer:
        """Lazy-load bi-encoder model."""
        if self._bi_encoder is None:
            with self._model_lock:
                if self._bi_encoder is None:
                    logger.info(f"Loading bi-encoder: {self.bi_encoder_model}")
                    self._bi_encoder = SentenceTransformer(self.bi_encoder_model)
                    logger.info("Bi-encoder loaded successfully")
        return self._bi_encoder
    
    @property
    def cross_encoder(self) -> Optional[CrossEncoder]:
        """Lazy-load cross-encoder model (if enabled)."""
        if not self.enable_reranking:
            return None
        
        if self._cross_encoder is None:
            with self._model_lock:
                if self._cross_encoder is None:
                    logger.info(f"Loading cross-encoder: {self.cross_encoder_model}")
                    self._cross_encoder = CrossEncoder(self.cross_encoder_model)
                    logger.info("Cross-encoder loaded successfully")
        return self._cross_encoder
    
    def index_document(
        self,
        text: str,
        document_id: str = "default",
        use_semantic_chunking: bool = True,
        max_chunk_size: int = 512,
        similarity_threshold: float = 0.5,
        set_as_default: bool = True
    ) -> Dict[str, Any]:
        """
        Index a document for RAG retrieval.
        
        Args:
            text: Document text to index
            document_id: Unique identifier for this document
            use_semantic_chunking: Use semantic chunking (slower but better)
            max_chunk_size: Maximum characters per chunk
            similarity_threshold: Threshold for grouping sentences
            set_as_default: Set this as the default index for queries
        
        Returns:
            Dict with indexing stats
        """
        with self._index_lock:
            # Create new index
            index = HybridRAGIndex(
                bi_encoder=self.bi_encoder,
                cross_encoder=self.cross_encoder,
                alpha=self.alpha
            )
            
            # Build the index
            num_chunks = index.build_index(
                text=text,
                document_id=document_id,
                use_semantic_chunking=use_semantic_chunking,
                max_chunk_size=max_chunk_size,
                similarity_threshold=similarity_threshold
            )
            
            # Store the index
            self._indices[document_id] = index
            
            if set_as_default:
                self._default_index = index
            
            logger.info(f"Indexed document '{document_id}' with {num_chunks} chunks")
            
            return {
                "document_id": document_id,
                "num_chunks": num_chunks,
                "is_default": set_as_default,
                "chunking_method": "semantic" if use_semantic_chunking else "simple"
            }
    
    def retrieve_context(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 3,
        use_reranking: bool = True
    ) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User's question
            document_id: Specific document to search (None = default)
            top_k: Number of chunks to retrieve
            use_reranking: Apply cross-encoder reranking
        
        Returns:
            Formatted context string for LLM
        """
        index = self._get_index(document_id)
        
        if index is None:
            logger.warning("No index available for retrieval")
            return ""
        
        return index.get_context_for_llm(query, top_k=top_k, use_reranking=use_reranking)
    
    def retrieve_with_scores(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        use_reranking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with detailed scores.
        
        Args:
            query: User's question
            document_id: Specific document to search (None = default)
            top_k: Number of chunks to retrieve
            use_reranking: Apply cross-encoder reranking
        
        Returns:
            List of result dicts with text, scores, and metadata
        """
        index = self._get_index(document_id)
        
        if index is None:
            logger.warning("No index available for retrieval")
            return []
        
        return index.retrieve(query, top_k=top_k, use_reranking=use_reranking)
    
    def _get_index(self, document_id: Optional[str] = None) -> Optional[HybridRAGIndex]:
        """Get index by ID or return default."""
        if document_id:
            return self._indices.get(document_id)
        return self._default_index
    
    def has_index(self, document_id: Optional[str] = None) -> bool:
        """Check if an index exists."""
        if document_id:
            return document_id in self._indices
        return self._default_index is not None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents."""
        return [
            index.get_stats()
            for index in self._indices.values()
        ]
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document index."""
        with self._index_lock:
            if document_id in self._indices:
                index = self._indices.pop(document_id)
                index.clear()
                
                # Clear default if it was this document
                if self._default_index and self._default_index.document_id == document_id:
                    self._default_index = None
                
                logger.info(f"Deleted document index: {document_id}")
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "models": {
                "bi_encoder": self.bi_encoder_model,
                "bi_encoder_loaded": self._bi_encoder is not None,
                "cross_encoder": self.cross_encoder_model if self.enable_reranking else None,
                "cross_encoder_loaded": self._cross_encoder is not None,
            },
            "indices": {
                "count": len(self._indices),
                "documents": list(self._indices.keys()),
                "default": self._default_index.document_id if self._default_index else None
            },
            "config": {
                "alpha": self.alpha,
                "reranking_enabled": self.enable_reranking
            }
        }


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get the global RAG service instance.
    
    Configuration via environment variables:
    - RAG_BI_ENCODER: Bi-encoder model name/path
    - RAG_CROSS_ENCODER: Cross-encoder model name/path
    - RAG_ALPHA: Hybrid search weight (0-1)
    - RAG_ENABLE_RERANKING: Enable cross-encoder reranking (true/false)
    """
    global _rag_service
    
    if _rag_service is None:
        bi_encoder = os.getenv("RAG_BI_ENCODER", "sentence-transformers/all-MiniLM-L6-v2")
        cross_encoder = os.getenv("RAG_CROSS_ENCODER", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        alpha = float(os.getenv("RAG_ALPHA", "0.5"))
        enable_reranking = os.getenv("RAG_ENABLE_RERANKING", "true").lower() == "true"
        
        _rag_service = RAGService(
            bi_encoder_model=bi_encoder,
            cross_encoder_model=cross_encoder,
            alpha=alpha,
            enable_reranking=enable_reranking
        )
    
    return _rag_service
