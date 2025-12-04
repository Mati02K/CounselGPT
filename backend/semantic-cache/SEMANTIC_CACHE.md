# Semantic Cache Integration

## How GPU/CPU Services Call Redis Embeddings

### Network Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌─────────────────┐                ┌────────────────────┐  │
│  │  GPU Backend    │                │ Semantic Cache Pod │  │
│  │                 │                │                    │  │
│  │  cache.py       │───────┐        │  ┌──────────────┐ │  │
│  │   ↓             │       │        │  │ Embeddings   │ │  │
│  │  counselgpt-api │       │        │  │ Service      │ │  │
│  └─────────────────┘       │        │  │ :8000        │ │  │
│                            │        │  └──────────────┘ │  │
│  ┌─────────────────┐       │        │  ┌──────────────┐ │  │
│  │  CPU Backend    │       │        │  │ Redis Stack  │ │  │
│  │                 │       │        │  │ :6379        │ │  │
│  │  cache.py       │───────┼────────┼─→│ Vector Store │ │  │
│  │   ↓             │       │        │  └──────────────┘ │  │
│  │  counselgpt-api │       │        └────────────────────┘  │
│  └─────────────────┘       │                 ↑              │
│                            │                 │              │
│  Service: counselgpt-redis │                 │              │
│    - redis: 6379 ──────────┴─────────────────┘              │
│    - embeddings: 8000 ─────┘                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Connection Details

### Service Discovery

Both GPU and CPU backends can reach the semantic cache via Kubernetes DNS:

```python
# In cache.py (GPU/CPU backends)
embedding_url = "http://counselgpt-redis:8000"  # Embeddings service
redis_url = "redis://counselgpt-redis:6379"      # Redis Stack
```

**Why this works:**
- All services in the same Kubernetes namespace (default)
- Kubernetes DNS resolves `counselgpt-redis` to the service ClusterIP
- Service routes traffic to the semantic-cache pod
- Port 8000 → Embeddings container
- Port 6379 → Redis container

### Request Flow

#### 1. **Cache GET (with Semantic Search)**

```python
# Backend (GPU/CPU pod)
cached = cache.get("What is contract law?", max_tokens=400)
```

**What happens:**

```
1. Backend → Embedding Service
   POST http://counselgpt-redis:8000/embed
   Body: {"texts": ["What is contract law?"]}
   ← Returns: {"embeddings": [[0.1, 0.2, ...]], "dimension": 384}

2. Backend → Redis Stack
   Scan cache keys: "llama:cache:*"
   For each: Compute cosine similarity with cached embedding
   Find best match with similarity ≥ 0.95

3. If found → Cache HIT (return cached response)
   If not found → Cache MISS (run inference)
```

#### 2. **Cache SET (with Embedding Storage)**

```python
# Backend (GPU/CPU pod)
response = run_inference(prompt)
cache.set(prompt, max_tokens, response)
```

**What happens:**

```
1. Backend → Embedding Service
   POST http://counselgpt-redis:8000/embed
   Body: {"texts": [prompt]}
   ← Returns: embedding vector

2. Backend → Redis Stack
   Store: {
     "prompt": prompt,
     "max_tokens": max_tokens,
     "response": response,
     "embedding": [0.1, 0.2, ...]  ← Vector for semantic search
   }
   TTL: 1800 seconds (30 minutes)
```

## Code Integration

### Updated cache.py

```python
class ResponseCache:
    def __init__(
        self,
        redis_url: str = "redis://counselgpt-redis:6379",
        embedding_url: str = "http://counselgpt-redis:8000",  ← Connects to sidecar
        use_semantic: bool = True,
        similarity_threshold: float = 0.95
    ):
        # Connect to Redis
        self.redis_client = redis.from_url(redis_url)
        
        # Connect to Embedding Service
        self.embedding_client = httpx.Client()
        
        # Test connection
        response = self.embedding_client.get(f"{embedding_url}/health")
        # ✓ Connection successful!
```

### Initialization in app.py

```python
# GPU/CPU backends (app.py)
cache = ResponseCache(
    redis_url=os.getenv("REDIS_URL", "redis://counselgpt-redis:6379"),
    embedding_url=os.getenv("EMBEDDING_URL", "http://counselgpt-redis:8000"),
    use_semantic=True,
    similarity_threshold=0.95
)
```

## Network Test

### From GPU/CPU Pod

```bash
# Check if services are reachable
kubectl exec -it deployment/counselgpt-api-gpu -- sh

# Test Redis
$ ping counselgpt-redis
# PING counselgpt-redis.default.svc.cluster.local (10.x.x.x)

# Test Embedding Service
$ curl http://counselgpt-redis:8000/health
# {"status":"healthy","model":"all-MiniLM-L6-v2","dimension":384}

# Test Redis connection
$ apt update && apt install -y redis-tools
$ redis-cli -h counselgpt-redis ping
# PONG
```

## Configuration

### Environment Variables (GPU/CPU Deployments)

```yaml
env:
- name: REDIS_URL
  value: "redis://counselgpt-redis:6379"
- name: EMBEDDING_URL
  value: "http://counselgpt-redis:8000"
- name: USE_SEMANTIC_CACHE
  value: "true"
- name: SIMILARITY_THRESHOLD
  value: "0.95"
```

### Service Definition (counselgpt-redis)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: counselgpt-redis  ← DNS name backends use
spec:
  selector:
    app: semantic-cache    ← Selects the cache pod
  ports:
  - name: redis
    port: 6379             ← Redis Stack
    targetPort: 6379
  - name: embeddings
    port: 8000             ← Embedding Service
    targetPort: 8000
  - name: metrics
    port: 9121             ← Prometheus metrics
    targetPort: 9121
```

## Performance Characteristics

### Latency

| Operation | Latency | Notes |
|-----------|---------|-------|
| **Exact Match** | 1-2ms | Hash lookup in Redis |
| **Embedding Generation** | 5-10ms | POST to embedding service |
| **Semantic Search** | 10-50ms | Depends on cache size |
| **Total (semantic hit)** | 15-60ms | Still faster than inference! |
| **Total (semantic miss)** | 2-5s (GPU) | Falls back to inference |

### Cache Hit Scenarios

```python
# Scenario 1: Exact duplicate prompt
prompt1 = "What is contract law?"
prompt2 = "What is contract law?"
# → Exact match (1-2ms) ✓

# Scenario 2: Similar prompt
prompt1 = "What is contract law?"
prompt2 = "Explain contract law to me"
# → Semantic match if similarity ≥ 0.95 (15-60ms) ✓

# Scenario 3: Different topic
prompt1 = "What is contract law?"
prompt2 = "What is criminal law?"
# → Semantic miss, run inference (2-5s)
```

## Fallback Behavior

### Embedding Service Unavailable

```python
# If embedding service fails:
logger.warning("Embedding service unavailable. Falling back to exact matching.")
self.use_semantic = False

# Cache still works with exact hash matching!
# No errors, just reduced hit rate
```

### Redis Unavailable

```python
# If Redis fails:
logger.warning("Redis connection failed. Caching disabled.")
self.redis_client = None

# All requests go to inference
# System still functional, just slower
```

## Monitoring

### Check Connections

```bash
# Check embedding service health
kubectl exec deployment/counselgpt-api-gpu -- \
  curl http://counselgpt-redis:8000/health

# Check Redis connection
kubectl exec deployment/counselgpt-api-gpu -- \
  python -c "import redis; r=redis.Redis(host='counselgpt-redis', port=6379); print(r.ping())"
```

### Logs

```bash
# GPU backend logs (should show semantic cache hits)
kubectl logs -l tier=gpu -f | grep -i "semantic"
# ✓ Embedding service connected: all-MiniLM-L6-v2 (384 dims)
# Cache HIT (semantic) similarity=0.967

# CPU backend logs
kubectl logs -l tier=cpu -f | grep -i "cache"
# Cache HIT (exact) for key: llama:cache:abc...
# Cache HIT (semantic) similarity=0.952
```

## Summary

✅ **Network Connectivity**: GPU/CPU backends can reach `counselgpt-redis:8000` via Kubernetes service  
✅ **Code Integration**: `cache.py` updated to call embedding service and do semantic search  
✅ **Automatic**: Backends automatically use semantic caching on startup  
✅ **Graceful Fallback**: Falls back to exact matching if embedding service fails  
✅ **No Config Changes**: Works out-of-the-box after deployment  

The GPU and CPU services **will automatically connect** to the Redis embeddings service when deployed! 🎉

