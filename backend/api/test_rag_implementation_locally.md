# Testing RAG Implementation Locally

This guide explains how to test the RAG (Retrieval Augmented Generation) implementation locally without Docker.

## Prerequisites

- Python 3.9+ (tested with Python 3.11)
- pip or conda for package management
- ~2GB disk space for model downloads
- Internet connection (for initial model downloads)

## Quick Start

### 1. Navigate to the API Directory

```bash
cd backend/api
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install RAG-specific dependencies
pip install sentence-transformers faiss-cpu rank_bm25 nltk numpy

# If you want to run the full server, also install:
pip install fastapi uvicorn pydantic redis httpx prometheus-client
```

### 4. Download NLTK Data

The first time you run the RAG module, it will attempt to download NLTK data automatically. If you encounter SSL errors (common on macOS), run this manually:

```bash
python -c "
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
"
```

---

## Option A: Quick RAG Module Test (Recommended First)

This tests the RAG module directly without needing the full server or LLM:

```bash
cd backend/api
python test_rag.py
```

**Expected Output:**
```
============================================================
CounselGPT RAG Local Test
============================================================

[1] Loading RAG Service...
    ✓ RAG Service loaded

[2] Indexing sample lease document...
    ✓ Indexed: X chunks created

[3] Testing queries...
------------------------------------------------------------

📝 Query: "What is the monthly rent?"
   Found 2 results:
   [1] Score: 0.XXX | BM25: 0.XX | Dense: 0.XX
       "The Tenant agrees to pay a monthly rent of $2,150.00..."

... (more queries)

============================================================
✅ RAG Module Test Complete!
============================================================
```

---