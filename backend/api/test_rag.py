#!/usr/bin/env python3
"""
Local RAG Testing Script

Run this to test RAG functionality without the full server.

Usage:
    python test_rag.py          # Test RAG module directly (recommended)
    python test_rag.py --http   # Test via HTTP API (requires server + requests library)

Dependencies:
    pip install sentence-transformers faiss-cpu rank_bm25 nltk numpy
    pip install requests  # Only needed for --http mode
"""

import sys
import json
import re
import os

# Test the RAG module directly (no server needed)
print("=" * 60)
print("CounselGPT RAG Local Test")
print("=" * 60)

# Load sample lease document from file
def load_sample_lease():
    """Load the sample lease document from the documents folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lease_file = os.path.join(script_dir, "documents", "sample_lease.txt")
    
    if not os.path.exists(lease_file):
        raise FileNotFoundError(
            f"Sample lease file not found: {lease_file}\n"
            f"Please ensure the file exists in the documents/ folder."
        )
    
    with open(lease_file, 'r', encoding='utf-8') as f:
        return f.read()

# Load the lease document
try:
    SAMPLE_LEASE = load_sample_lease()
    print(f"✓ Loaded sample lease document ({len(SAMPLE_LEASE)} characters)")
except FileNotFoundError as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

TEST_QUERIES = [
    "What is the monthly rent?",
    "What happens if I pay rent late?",
    "Are pets allowed?",
    "How much is the security deposit?",
    "How do I terminate the lease?",
]


def test_rag_module():
    """Test RAG module directly without HTTP server."""
    print("\n[1] Loading RAG Service...")
    
    try:
        from rag import get_rag_service
        rag_service = get_rag_service()
        print("    ✓ RAG Service loaded")
    except Exception as e:
        print(f"    ✗ Failed to load RAG service: {e}")
        return False

    # Index document
    print("\n[2] Indexing sample lease document...")
    try:
        result = rag_service.index_document(
            text=SAMPLE_LEASE,
            document_id="test_lease",
            use_semantic_chunking=True,
            max_chunk_size=512
        )
        print(f"    ✓ Indexed: {result['num_chunks']} chunks created")
    except Exception as e:
        print(f"    ✗ Indexing failed: {e}")
        return False

    # Test queries
    print("\n[3] Testing queries...")
    print("-" * 60)
    
    for query in TEST_QUERIES:
        print(f"\n📝 Query: \"{query}\"")
        
        try:
            # Get results with scores
            results = rag_service.retrieve_with_scores(
                query=query,
                top_k=2,
                use_reranking=True
            )
            
            # Get formatted context
            context = rag_service.retrieve_context(query=query, top_k=2)
            
            print(f"   Found {len(results)} results:")
            for r in results:
                print(f"   [{r['rank']}] Score: {r['score']:.3f} | "
                      f"BM25: {r['bm25_score']:.2f} | "
                      f"Dense: {r['dense_score']:.2f}")
                # Format text as proper sentences - show full text without truncation
                text = r['text'].strip()
                # Clean up excessive whitespace: normalize multiple spaces/newlines to single space
                text = re.sub(r'\s+', ' ', text)
                # Ensure proper spacing after sentence-ending punctuation
                text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
                # Display full text with proper formatting (no truncation, no ellipsis)
                print(f"       {text}")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}")

    # Show stats
    print("\n" + "-" * 60)
    print("\n[4] RAG Service Stats:")
    stats = rag_service.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ RAG Module Test Complete!")
    print("=" * 60)
    
    return True


def test_with_server():
    """Test RAG via HTTP endpoints (requires server running)."""
    import requests
    import os
    
    # Allow BASE_URL to be configured via environment variable
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("\n[Testing via HTTP API]")
    print("Make sure server is running: uvicorn app:app --port 8000")
    print("-" * 60)
    
    # Check health
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        if resp.status_code == 200:
            print("✓ Server is healthy")
        else:
            print(f"✗ Server returned {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        return False
    
    # Index document
    print("\n[2] Indexing sample lease document...")
    try:
        resp = requests.post(f"{BASE_URL}/rag/index", json={
            "text": SAMPLE_LEASE,
            "document_id": "test_lease",
            "use_semantic_chunking": True,
            "max_chunk_size": 512
        }, timeout=120)  # Indexing may take time for large documents
        if resp.status_code != 200:
            print(f"    ✗ Indexing failed: {resp.status_code} - {resp.text}")
            return False
        result = resp.json()
        print(f"    ✓ Indexed: {result['num_chunks']} chunks created")
    except Exception as e:
        print(f"    ✗ Indexing failed: {e}")
        return False
    
    # Test queries
    print("\n[3] Testing queries...")
    print("-" * 60)
    
    for query in TEST_QUERIES:
        print(f"\n📝 Query: \"{query}\"")
        
        try:
            # Query via HTTP
            resp = requests.post(f"{BASE_URL}/rag/query", json={
                "query": query,
                "top_k": 2,
                "use_reranking": True
            }, timeout=30)
            
            if resp.status_code != 200:
                print(f"   ✗ Query failed: {resp.status_code} - {resp.text}")
                continue
                
            result = resp.json()
            results = result.get('results', [])
            context = result.get('context', '')
            
            print(f"   Found {len(results)} results:")
            for r in results:
                # Get scores (handle cases where they might not be present)
                bm25_score = r.get('bm25_score', 0.0)
                dense_score = r.get('dense_score', 0.0)
                score = r.get('score', 0.0)
                
                print(f"   [{r.get('rank', 0)}] Score: {score:.3f} | "
                      f"BM25: {bm25_score:.2f} | "
                      f"Dense: {dense_score:.2f}")
                
                # Format text as proper sentences - show full text without truncation
                text = r.get('text', '').strip()
                # Clean up excessive whitespace: normalize multiple spaces/newlines to single space
                text = re.sub(r'\s+', ' ', text)
                # Ensure proper spacing after sentence-ending punctuation
                text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
                # Display full text with proper formatting (no truncation, no ellipsis)
                print(f"       {text}")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
    
    # Show stats
    print("\n" + "-" * 60)
    print("\n[4] RAG Service Stats:")
    try:
        resp = requests.get(f"{BASE_URL}/rag/stats", timeout=10)
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"   ✗ Failed to get stats: {resp.status_code}")
    except Exception as e:
        print(f"   ✗ Failed to get stats: {e}")
    
    print("\n" + "=" * 60)
    print("✅ RAG HTTP API Test Complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Test via HTTP (requires server)
        test_with_server()
    else:
        # Test module directly (no server needed)
        test_rag_module()
