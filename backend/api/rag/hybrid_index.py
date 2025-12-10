"""
Hybrid RAG Index

Production-grade RAG index combining:
1. BM25 (keyword-based search) - Good for exact terms, numbers, names
2. Dense retrieval (semantic search) - Good for meaning/paraphrasing
3. Cross-encoder reranking - Precision filtering of results
"""

import re
import logging
import numpy as np
import faiss
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

from .chunking import semantic_chunking, simple_sentence_chunking

logger = logging.getLogger(__name__)


class HybridRAGIndex:
    """
    Production-grade RAG index with hybrid search and cross-encoder reranking.
    
    Features:
    - Semantic chunking for intelligent document splitting
    - BM25 for keyword matching (catches exact terms like $2,150)
    - Dense FAISS for semantic similarity (understands paraphrasing)
    - Cross-encoder reranking for precision
    - Configurable alpha for BM25/dense weighting
    """
    
    def __init__(
        self,
        bi_encoder: SentenceTransformer,
        cross_encoder: Optional[CrossEncoder] = None,
        alpha: float = 0.5
    ):
        """
        Initialize the hybrid RAG index.
        
        Args:
            bi_encoder: SentenceTransformer for dense embeddings
            cross_encoder: Optional CrossEncoder for reranking (if None, skip reranking)
            alpha: Weight for hybrid search (0=BM25 only, 1=Dense only, 0.5=equal)
        """
        self.bi_encoder = bi_encoder
        self.cross_encoder = cross_encoder
        self.alpha = alpha
        
        # Index state (populated by build_index)
        self.chunks: List[str] = []
        self.chunk_embeddings: Optional[np.ndarray] = None
        self.faiss_index: Optional[faiss.IndexFlatIP] = None
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_chunks: List[List[str]] = []
        
        # Metadata
        self.document_id: Optional[str] = None
        self.is_indexed: bool = False
    
    def _tokenize_for_bm25(self, text: str) -> List[str]:
        """Simple tokenization for BM25 (lowercase + alphanumeric tokens)."""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalize scores to [0, 1] range."""
        if len(scores) == 0:
            return scores
        
        min_score = np.min(scores)
        max_score = np.max(scores)
        
        if max_score - min_score == 0:
            return np.ones_like(scores)
        
        return (scores - min_score) / (max_score - min_score)
    
    def build_index(
        self,
        text: str,
        document_id: str = "default",
        use_semantic_chunking: bool = True,
        max_chunk_size: int = 512,
        similarity_threshold: float = 0.5
    ) -> int:
        """
        Build the hybrid index from document text.
        
        Args:
            text: Full document text
            document_id: Identifier for this document
            use_semantic_chunking: Use semantic (True) or simple sentence chunking (False)
            max_chunk_size: Max characters per chunk (for semantic chunking)
            similarity_threshold: Similarity threshold for grouping sentences
        
        Returns:
            Number of chunks created
        """
        self.document_id = document_id
        
        # Step 1: Chunk the document
        logger.info(f"Chunking document '{document_id}'...")
        
        if use_semantic_chunking:
            self.chunks = semantic_chunking(
                text,
                encoder=self.bi_encoder,
                max_chunk_size=max_chunk_size,
                similarity_threshold=similarity_threshold
            )
        else:
            self.chunks = simple_sentence_chunking(text, sentences_per_chunk=3, overlap=1)
        
        if not self.chunks:
            logger.warning(f"No chunks created from document '{document_id}'")
            return 0
        
        logger.info(f"Created {len(self.chunks)} chunks")
        
        # Step 2: Build BM25 index (keyword search)
        logger.info("Building BM25 index...")
        self.tokenized_chunks = [self._tokenize_for_bm25(chunk) for chunk in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_chunks)
        
        # Step 3: Build FAISS index (dense search)
        logger.info("Building dense embeddings...")
        self.chunk_embeddings = self.bi_encoder.encode(
            self.chunks,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True  # Required for Inner Product = Cosine Similarity
        )
        
        # Use Inner Product index (cosine similarity with normalized vectors)
        dim = self.chunk_embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dim)
        self.faiss_index.add(self.chunk_embeddings)
        
        self.is_indexed = True
        logger.info(f"Index built successfully for '{document_id}' ({len(self.chunks)} chunks)")
        
        return len(self.chunks)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        initial_retrieve: int = 20,
        use_reranking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using hybrid search + optional reranking.
        
        Pipeline:
        1. BM25 retrieval (keyword matching)
        2. Dense retrieval (semantic similarity)
        3. Hybrid score fusion (weighted combination)
        4. Cross-encoder reranking (optional, for precision)
        
        Args:
            query: User's question
            top_k: Final number of chunks to return
            initial_retrieve: Candidates for hybrid search before reranking
            use_reranking: Apply cross-encoder reranking (slower but more accurate)
        
        Returns:
            List of dicts with 'text', 'score', 'rank', and score breakdowns
        """
        if not self.is_indexed:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Cap initial_retrieve to number of chunks
        initial_retrieve = min(initial_retrieve, len(self.chunks))
        top_k = min(top_k, len(self.chunks))
        
        # ========== STEP 1: BM25 Retrieval ==========
        query_tokens = self._tokenize_for_bm25(query)
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_scores_normalized = self._normalize_scores(bm25_scores)
        
        # ========== STEP 2: Dense Retrieval ==========
        query_embedding = self.bi_encoder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        dense_scores, dense_indices = self.faiss_index.search(query_embedding, len(self.chunks))
        
        # Align dense scores with chunk indices
        dense_scores_aligned = np.zeros(len(self.chunks))
        for idx, score in zip(dense_indices[0], dense_scores[0]):
            dense_scores_aligned[idx] = score
        dense_scores_normalized = self._normalize_scores(dense_scores_aligned)
        
        # ========== STEP 3: Hybrid Score Fusion ==========
        hybrid_scores = (
            self.alpha * dense_scores_normalized +
            (1 - self.alpha) * bm25_scores_normalized
        )
        
        # Get top candidates
        top_indices = np.argsort(hybrid_scores)[::-1][:initial_retrieve]
        
        # ========== STEP 4: Cross-Encoder Reranking ==========
        if use_reranking and self.cross_encoder and len(top_indices) > 0:
            # Prepare query-document pairs
            pairs = [(query, self.chunks[idx]) for idx in top_indices]
            
            # Get reranking scores
            rerank_scores = self.cross_encoder.predict(pairs)
            
            # Sort by rerank score
            reranked = sorted(
                zip(top_indices, rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Build results
            results = []
            for rank, (idx, score) in enumerate(reranked[:top_k], 1):
                results.append({
                    "text": self.chunks[idx],
                    "score": float(score),
                    "rank": rank,
                    "chunk_index": int(idx),
                    "hybrid_score": float(hybrid_scores[idx]),
                    "bm25_score": float(bm25_scores_normalized[idx]),
                    "dense_score": float(dense_scores_normalized[idx])
                })
            return results
        
        else:
            # No reranking - return hybrid results directly
            results = []
            for rank, idx in enumerate(top_indices[:top_k], 1):
                results.append({
                    "text": self.chunks[idx],
                    "score": float(hybrid_scores[idx]),
                    "rank": rank,
                    "chunk_index": int(idx),
                    "hybrid_score": float(hybrid_scores[idx]),
                    "bm25_score": float(bm25_scores_normalized[idx]),
                    "dense_score": float(dense_scores_normalized[idx])
                })
            return results
    
    def get_context_for_llm(
        self, 
        query: str, 
        top_k: int = 3,
        use_reranking: bool = True
    ) -> str:
        """
        Get formatted context string for LLM consumption.
        
        Args:
            query: User's question
            top_k: Number of chunks to include
            use_reranking: Apply cross-encoder reranking
        
        Returns:
            Formatted context string with chunk markers
        """
        results = self.retrieve(query, top_k=top_k, use_reranking=use_reranking)
        
        context_parts = []
        for r in results:
            context_parts.append(f"[Context {r['rank']}]\n{r['text']}")
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "document_id": self.document_id,
            "is_indexed": self.is_indexed,
            "num_chunks": len(self.chunks),
            "alpha": self.alpha,
            "has_cross_encoder": self.cross_encoder is not None
        }
    
    def clear(self):
        """Clear the index."""
        self.chunks = []
        self.chunk_embeddings = None
        self.faiss_index = None
        self.bm25 = None
        self.tokenized_chunks = []
        self.document_id = None
        self.is_indexed = False
        logger.info("Index cleared")
