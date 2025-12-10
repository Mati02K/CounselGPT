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

# Test the RAG module directly (no server needed)
print("=" * 60)
print("CounselGPT RAG Local Test")
print("=" * 60)

# Sample lease document
SAMPLE_LEASE = """
RESIDENTIAL LEASE AGREEMENT

This Residential Lease Agreement is entered into on January 1, 2025, by and between
James Wilson (Landlord) and Sarah Thompson (Tenant) for the property located at:
123 Maplewood Drive, Apt 4B, Sunnyvale, California 94086.

1. RENT PAYMENT
The Tenant agrees to pay a monthly rent of $2,150.00 (Rent), due on or before the 1st day of each calendar month.
Payments shall be made via bank transfer or online payment portal designated by the Landlord.

If Rent is not received by the 5th day of the month, a Late Fee of $75.00 shall apply.
If Rent remains unpaid after the 10th day, an additional Late Fee of $10.00 per day may apply.

2. SECURITY DEPOSIT
The Tenant agrees to pay a Security Deposit of $2,500.00 prior to moving in.
The Security Deposit will be held to cover unpaid rent, damages beyond normal wear and tear.
The Security Deposit shall be refunded within 21 days after the Tenant vacates the premises.

3. PETS
Pets are allowed only with written approval from the Landlord and may require an additional 
pet deposit of $300.00. Smoking is strictly prohibited inside the premises.

4. TERMINATION
Either party may terminate the lease at the End Date by providing written notice at least 
30 days prior to expiration. Month-to-month tenancy after the End Date shall result in a 
rental increase of 10%.
"""

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
                # Show first 100 chars of text
                text_preview = r['text'][:100].replace('\n', ' ')
                print(f"       \"{text_preview}...\"")
            
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
    
    BASE_URL = "http://localhost:8000"
    
    print("\n[Testing via HTTP API]")
    print("Make sure server is running: uvicorn app:app --port 8000")
    print("-" * 60)
    
    # Check health
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✓ Server is healthy")
        else:
            print(f"✗ Server returned {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        return False
    
    # Index document
    print("\nIndexing document...")
    resp = requests.post(f"{BASE_URL}/rag/index", json={
        "text": SAMPLE_LEASE,
        "document_id": "test_lease",
        "use_semantic_chunking": True
    })
    print(f"   Response: {resp.json()}")
    
    # Query
    print("\nQuerying: 'What is the monthly rent?'")
    resp = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "What is the monthly rent?",
        "top_k": 3
    })
    result = resp.json()
    print(f"   Found {len(result['results'])} results")
    for r in result['results']:
        print(f"   [{r['rank']}] Score: {r['score']:.3f}")
    
    # Stats
    print("\nRAG Stats:")
    resp = requests.get(f"{BASE_URL}/rag/stats")
    print(json.dumps(resp.json(), indent=2))
    
    return True


if __name__ == "__main__":
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Test via HTTP (requires server)
        test_with_server()
    else:
        # Test module directly (no server needed)
        test_rag_module()
