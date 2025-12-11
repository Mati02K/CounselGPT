# RAG Testing Guide

This directory contains testing tools and documentation for the RAG (Retrieval Augmented Generation) system.

## Quick Start

### Option 1: Direct Module Testing (Recommended for Quick Tests)

No server required - tests RAG functionality directly:

```bash
cd backend/api
python test_rag.py
```

### Option 2: HTTP Server Testing (Recommended for Integration Tests)

Tests RAG via HTTP endpoints - requires server:

```bash
# Terminal 1: Start server
cd backend/api
source venv/bin/activate
uvicorn app:app --port 8000

# Terminal 2: Run tests
cd backend/api
source venv/bin/activate
python test_rag.py --http
```

## Documentation

- **`HTTP_SERVER_GUIDE.md`** - Detailed guide for running tests with HTTP server
- **`test_rag_implementation_locally.md`** - Original local testing guide
- **`../RAG_Explanation.md`** - Comprehensive explanation of RAG architecture and endpoints

## Files

- **`test_rag.py`** - Main test script (supports both direct and HTTP modes)
- **`app.py`** - FastAPI application with RAG endpoints
- **`rag/`** - RAG implementation modules

## Endpoints Tested

When using `--http` mode, the following endpoints are tested:

- `GET /health` - Health check
- `POST /rag/index` - Index documents
- `POST /rag/query` - Query RAG index
- `GET /rag/stats` - Get RAG statistics

## Dependencies

For direct testing:
```bash
pip install sentence-transformers faiss-cpu rank_bm25 nltk numpy
```

For HTTP testing, also install:
```bash
pip install fastapi uvicorn[standard] pydantic redis httpx prometheus-client requests
```

See `requirements.txt` for full dependency list.
