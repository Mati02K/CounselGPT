# Running RAG Tests with HTTP Server

This guide explains how to set up and test the RAG system via HTTP endpoints from scratch.

## Prerequisites

Before starting, ensure you have:

1. **Git** - To clone the repository
2. **Python 3.9+** - Tested with Python 3.11+
3. **pip** - Python package manager (usually comes with Python)
4. **Internet connection** - For downloading dependencies and models

### Check Prerequisites

```bash
# Check Git version
git --version

# Check Python version (should be 3.9 or higher)
python3 --version

# Check pip version
pip3 --version
```

If any of these commands fail, install the missing software first.

---

## Complete Setup from Scratch

### Step 1: Clone the Repository

If you haven't cloned the repository yet:

```bash
# Navigate to where you want to clone the project
cd ~/projects  # or your preferred directory

# Clone the repository (replace with your actual repository URL)
git clone <repository-url> CounselGPT

# Navigate into the project
cd CounselGPT
```

**Note:** If you already have the repository, skip to Step 2.

### Step 2: Navigate to API Directory

```bash
cd backend/api
```

You should now be in: `CounselGPT/backend/api/`

### Step 3: Create Virtual Environment

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

After activation, your terminal prompt should show `(venv)` at the beginning.

**Note:** Always activate the virtual environment before working with the project.

### Step 4: Upgrade pip (Recommended)

```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies

Install all required dependencies from `requirements.txt`:

```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Install additional dependency for HTTP testing
pip install requests
```

**Expected output:**
```
Collecting fastapi...
Collecting uvicorn...
Collecting sentence-transformers...
...
Successfully installed ...
```

**Installation may take 5-10 minutes** depending on your internet speed, as it downloads:
- FastAPI and server dependencies (~50MB)
- Sentence transformers and ML models (~500MB)
- FAISS, numpy, and other scientific libraries

### Step 6: Download NLTK Data

The RAG system requires NLTK data for text processing:

```bash
python -c "
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
"
```

**Expected output:**
```
[nltk_data] Downloading package punkt to ...
[nltk_data] Downloading package punkt_tab to ...
```

If you encounter SSL errors (common on macOS), this script handles them automatically.

### Step 7: Verify Installation

Test that everything is installed correctly:

```bash
# Test Python imports
python3 -c "import fastapi; import uvicorn; import sentence_transformers; print('✓ All dependencies installed successfully!')"
```

If this command runs without errors, you're ready to proceed!

---

## Running RAG Tests with HTTP Server

### Step 8: Start the Server

**Terminal 1** - Start the FastAPI server:

```bash
# Make sure you're in the correct directory
cd ~/projects/CounselGPT/backend/api  # Adjust path to your project location

# Activate virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
uvicorn app:app --port 8000 --host 0.0.0.0
```

**Expected output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Server is now running!** Keep this terminal open.

**Note:** The first time you start the server, it may take a minute to download embedding models automatically.

### Step 9: Run RAG Tests via HTTP

**Terminal 2** (new terminal window/tab) - Run the HTTP test:

```bash
# Navigate to the project directory
cd ~/projects/CounselGPT/backend/api  # Adjust path to your project location

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the HTTP test
python test_rag.py --http
```

**Expected output:**
```
============================================================
CounselGPT RAG Local Test
============================================================

[Testing via HTTP API]
Make sure server is running: uvicorn app:app --port 8000
------------------------------------------------------------
✓ Server is healthy

[2] Indexing sample lease document...
    ✓ Indexed: X chunks created

[3] Testing queries...
------------------------------------------------------------

📝 Query: "What is the monthly rent?"
   Found 2 results:
   [1] Score: X.XXX | BM25: X.XX | Dense: X.XX
       [Text content of retrieved chunk...]

... (more queries and results)

[4] RAG Service Stats:
{
  "models": {...},
  "indices": {...},
  ...
}

============================================================
✅ RAG HTTP API Test Complete!
============================================================
```

## Troubleshooting

### Server won't start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
pip install fastapi uvicorn[standard] pydantic
```

**Error: `ModuleNotFoundError: No module named 'llama_cpp'`**
- This is expected if you haven't installed llama-cpp-python
- The server will still work for RAG endpoints (`/rag/index`, `/rag/query`)
- Only the `/infer` endpoint requires llama-cpp-python

### Cannot connect to server

**Error: `✗ Cannot connect to server. Is it running?`**
- Make sure the server is running in Terminal 1
- Check that it's listening on port 8000: `lsof -i :8000`
- Try: `curl http://localhost:8000/health`

**Error: `Connection refused`**
- Server might not be running
- Check for port conflicts: Another process might be using port 8000
- Change port: `uvicorn app:app --port 8001` (and update BASE_URL in test_rag.py)

### Test fails with import errors

**Error: `ModuleNotFoundError: No module named 'requests'`**
```bash
pip install requests
```

## Testing Endpoints Manually

You can also test endpoints directly using `curl`:

### Health Check
```bash
curl http://localhost:8000/health
```

### Index Document
```bash
curl -X POST http://localhost:8000/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "document_id": "my_doc",
    "use_semantic_chunking": true
  }'
```

### Query RAG
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the monthly rent?",
    "top_k": 3,
    "use_reranking": true
  }'
```

### Get Stats
```bash
curl http://localhost:8000/rag/stats
```

## Alternative: Direct Module Testing (No Server)

If you don't need to test HTTP endpoints, you can test the RAG module directly without starting a server:

```bash
python test_rag.py
```

This mode:
- ✅ Doesn't require server
- ✅ Faster startup
- ✅ Tests RAG logic directly
- ❌ Doesn't test HTTP endpoints

## Stopping the Server

To stop the server, go to Terminal 1 and press `Ctrl+C`.

## Next Steps

After testing:
- Review the retrieved chunks to verify relevance
- Check scores (BM25, Dense, Hybrid) to understand retrieval quality
- Adjust `top_k`, `use_reranking`, and chunking parameters as needed
