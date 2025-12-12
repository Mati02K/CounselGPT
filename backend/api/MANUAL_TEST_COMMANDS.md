# Manual Test Commands for /infer Endpoint with RAG

Copy and paste these commands one by one. Each command has a comment explaining what it does.

---

## Step 1: Check Server Health

```bash
curl -X GET http://localhost:8000/health | jq  # Check if server is running and show RAG status
```

---

## Step 2: Index Document for RAG

```bash
python3 -c "import requests, json; text = open('documents/sample_lease.txt').read(); print(json.dumps(requests.post('http://localhost:8000/rag/index', json={'text': text, 'document_id': 'test_lease', 'use_semantic_chunking': True, 'max_chunk_size': 512, 'similarity_threshold': 0.5, 'set_as_default': True}).json(), indent=2))"  # Index the lease document so RAG can retrieve context from it
```

---

## Step 3: Verify Document is Indexed

```bash
curl -X GET http://localhost:8000/rag/documents | jq  # List all indexed documents to confirm indexing worked
```

---

## Step 4: Test /infer WITHOUT RAG (Baseline)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": false}' | jq  # Test inference without RAG - use_gpu:false for local testing without GPU
```

---

## Step 5: Test /infer WITH RAG (Enhanced)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq  # Test inference with RAG enabled - retrieves document context for accurate answer
```

---

## Step 6: Compare Response Fields Only

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq '{response, rag_used, rag_context_length, estimated_tokens}'  # Show only key fields: response, RAG status, context length, token count
```

---

## Step 7: Test Different Query with RAG

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What happens if I pay rent late?", "model_name": "qwen", "use_gpu": false, "max_tokens": 250, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq -r '.response'  # Test different question - RAG retrieves relevant sections about late payments
```

---

## Step 8: Test with Conversation History

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "What is the monthly rent?"}, {"role": "assistant", "content": "The monthly rent is $2,150."}, {"role": "user", "content": "What happens if I pay it late?"}], "model_name": "qwen", "use_gpu": false, "max_tokens": 300, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq -r '.response'  # Test messages format with conversation history and RAG context
```

---

## Step 9: Test Security Deposit Question

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "How much is the security deposit?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq -r '.response'  # Test RAG retrieval for security deposit information
```

---

## Step 10: Test Pets Question

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "Are pets allowed in the property?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq -r '.response'  # Test RAG retrieval for pet policy information
```

---

## Step 11: Check What RAG Retrieves (Before Inference)

```bash
curl -X POST http://localhost:8000/rag/query -H "Content-Type: application/json" -d '{"query": "What is the monthly rent?", "top_k": 3, "use_reranking": true}' | jq '.results[] | {rank, score, text: (.text | .[0:150])}'  # Show document chunks RAG retrieves before sending to model
```

---

## Step 12: Test with Minimal Context (rag_top_k=1)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 1}' | jq '{response: .response[0:100], rag_context_length}'  # Test with only 1 chunk - shows shorter context length
```

---

## Step 13: Test with More Context (rag_top_k=5)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 5}' | jq '{response: .response[0:100], rag_context_length}'  # Test with 5 chunks - shows longer context length
```

---

## Step 14: Test Caching (First Request)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": true, "use_rag": true, "rag_top_k": 3}' | jq '{cached, rag_used}'  # First request - computes and caches result (cached: false)
```

---

## Step 15: Test Cache Hit (Second Request)

```bash
curl -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": true, "use_rag": true, "rag_top_k": 3}' | jq '{cached, rag_used}'  # Second identical request - returns cached result (cached: true, faster)
```

---

## Step 16: View RAG Statistics

```bash
curl -X GET http://localhost:8000/rag/stats | jq  # Show RAG service statistics: models loaded, documents indexed
```

---

## Side-by-Side Comparison

**Without RAG:**
```bash
echo "=== WITHOUT RAG ===" && curl -s -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": false}' | jq -r '.response'  # Generic response without document context
```

**With RAG:**
```bash
echo "=== WITH RAG ===" && curl -s -X POST http://localhost:8000/infer -H "Content-Type: application/json" -d '{"prompt": "What is the monthly rent?", "model_name": "qwen", "use_gpu": false, "max_tokens": 200, "use_cache": false, "use_rag": true, "rag_top_k": 3}' | jq -r '.response'  # Accurate response with document context
```

---

## Notes

- **use_gpu**: Set to `false` for local testing without GPU, `true` if you have GPU available
- **use_rag**: Set to `true` to enable RAG context retrieval, `false` for baseline
- **rag_top_k**: Number of document chunks to retrieve (1-10, default: 3)
- **use_cache**: Set to `true` to enable Redis caching for faster repeated queries

## Expected Results

- **Without RAG**: Generic response, may not have specific document details
- **With RAG**: 
  - `rag_used: true`
  - `rag_context_length: > 0` (shows context was retrieved)
  - More accurate, document-specific answers
  - References to actual values from the lease document
