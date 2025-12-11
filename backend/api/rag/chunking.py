"""
Semantic Chunking Module

Provides intelligent document chunking strategies:
1. Semantic chunking - Groups sentences by meaning similarity
2. Simple sentence chunking - Sliding window with overlap
"""

import logging
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Lazy-loaded sentence tokenizer
_nltk_initialized = False


def _ensure_nltk():
    """Ensure NLTK data is downloaded (lazy initialization)."""
    global _nltk_initialized
    if not _nltk_initialized:
        import nltk
        import ssl
        
        # Handle SSL certificate issues (common on macOS)
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('punkt_tab', quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download NLTK data: {e}")
                logger.warning("Please run: python -m nltk.downloader punkt punkt_tab")
                raise RuntimeError(
                    "NLTK punkt tokenizer not found. Please run:\n"
                    "  python -c \"import ssl; ssl._create_default_https_context = ssl._create_unverified_context; "
                    "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')\""
                )
        _nltk_initialized = True


def semantic_chunking(
    text: str,
    encoder: SentenceTransformer,
    max_chunk_size: int = 512,
    similarity_threshold: float = 0.5
) -> List[str]:
    """
    Semantic chunking that groups similar consecutive sentences together.
    
    This approach:
    1. Splits text into sentences
    2. Embeds each sentence
    3. Groups consecutive sentences if similarity >= threshold
    4. Respects max_chunk_size limit
    
    Args:
        text: Input document text
        encoder: SentenceTransformer model for embeddings
        max_chunk_size: Maximum characters per chunk
        similarity_threshold: Cosine similarity threshold to group sentences (0-1)
    
    Returns:
        List of semantically coherent chunks
    """
    _ensure_nltk()
    from nltk.tokenize import sent_tokenize
    
    # Handle empty/whitespace input
    if not text or not text.strip():
        return []
    
    # Split into sentences
    sentences = sent_tokenize(text)
    
    if len(sentences) == 0:
        return [text] if text.strip() else []
    
    if len(sentences) == 1:
        return sentences
    
    # Get embeddings for all sentences
    logger.debug(f"Encoding {len(sentences)} sentences for semantic chunking...")
    sentence_embeddings = encoder.encode(sentences, convert_to_numpy=True)
    
    # Group sentences based on similarity
    chunks = []
    current_chunk = [sentences[0]]
    current_embedding = sentence_embeddings[0]
    
    for i in range(1, len(sentences)):
        # Calculate cosine similarity with current chunk's average embedding
        similarity = _cosine_similarity(current_embedding, sentence_embeddings[i])
        
        current_text = " ".join(current_chunk)
        potential_length = len(current_text) + len(sentences[i]) + 1  # +1 for space
        
        # Add to current chunk if similar enough and within size limit
        if similarity >= similarity_threshold and potential_length < max_chunk_size:
            current_chunk.append(sentences[i])
            # Update running average embedding
            chunk_start_idx = i - len(current_chunk) + 1
            current_embedding = np.mean(
                sentence_embeddings[chunk_start_idx:i + 1],
                axis=0
            )
        else:
            # Save current chunk and start new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
            current_embedding = sentence_embeddings[i]
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    logger.info(f"Semantic chunking: {len(sentences)} sentences -> {len(chunks)} chunks")
    return chunks


def simple_sentence_chunking(
    text: str,
    sentences_per_chunk: int = 3,
    overlap: int = 1
) -> List[str]:
    """
    Simple sentence-based chunking with sliding window overlap.
    
    Good fallback if semantic chunking is too slow or encoder unavailable.
    
    Args:
        text: Input document text
        sentences_per_chunk: Number of sentences per chunk
        overlap: Number of overlapping sentences between consecutive chunks
    
    Returns:
        List of chunks
    """
    _ensure_nltk()
    from nltk.tokenize import sent_tokenize
    
    if not text or not text.strip():
        return []
    
    sentences = sent_tokenize(text)
    
    if len(sentences) <= sentences_per_chunk:
        return [text] if text.strip() else []
    
    chunks = []
    step = max(1, sentences_per_chunk - overlap)
    
    for i in range(0, len(sentences), step):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        if chunk_sentences:
            chunks.append(" ".join(chunk_sentences))
    
    logger.info(f"Simple chunking: {len(sentences)} sentences -> {len(chunks)} chunks")
    return chunks


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.dot(vec1, vec2) / (norm1 * norm2))
