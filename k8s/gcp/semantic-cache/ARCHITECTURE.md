# Semantic Cache Architecture

## Overview

The semantic cache runs as a **single pod with two containers**:
1. **Redis Stack** - Vector storage with RediSearch
2. **Embedding Service** - Generates semantic embeddings

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           Semantic Cache Pod                        │
│                                                     │
│  ┌──────────────────┐    ┌──────────────────────┐ │
│  │  Redis Stack     │    │ Embedding Service    │ │
│  │  (port 6379)     │    │  (port 8000)         │ │
│  │                  │    │                      │ │
│  │  - RediSearch    │    │  - FastAPI           │ │
│  │  - Vector VSS    │    │  - SentenceTransf.   │ │
│  │  - RedisJSON     │    │  - all-MiniLM-L6-v2  │ │
│  │  - 2GB Memory    │    │  - 384-dim vectors   │ │
│  └──────────────────┘    └──────────────────────┘ │
│           ↑                        ↑               │
└───────────┼────────────────────────┼───────────────┘
            │                        │
       Port 6379               Port 8000
            │                        │
    ┌───────┴────────────────────────┴───────┐
    │     Service: counselgpt-redis          │
    │  - redis: 6379                         │
    │  - embeddings: 8000                    │
    │  - metrics: 9121                       │
    └────────────────────────────────────────┘
                     ↑
         ┌───────────┴───────────┐
         │                       │
    GPU Backend           CPU Backend
```

## How It Works

### 1. Backend Makes Request

```python
import requests

# Backend wants to cache a prompt
prompt = "What is contract law?"
```

### 2. Generate Embedding

```python
# Call embedding service
response = requests.post(
    "http://counselgpt-redis:8000/embed",
    json={"texts": [prompt]}
)
embedding = response.json()["embeddings"][0]  # 384-dim vector
```

### 3. Search Redis for Similar Prompts

```python
import redis
from redis.commands.search.query import Query

r = redis.Redis(host="counselgpt-redis", port=6379)

# Search for similar vectors (cosine similarity >= 0.95)
query = (
    Query("(*)=>[KNN 10 @embedding $vec AS score]")
    .sort_by("score")
    .return_fields("score", "response")
    .dialect(2)
)

result = r.ft("idx:cache").search(query, {"vec": embedding})
```

### 4. Cache Hit or Miss

```python
if result.docs and float(result.docs[0].score) >= 0.95:
    # HIT: Return cached response
    return result.docs[0].response
else:
    # MISS: Run inference
    response = run_inference(prompt)
    
    # Store in cache with embedding
    r.json().set(f"cache:{hash}", "$", {
        "prompt": prompt,
        "response": response,
        "embedding": embedding
    })
    
    return response
```

## Components

### Redis Stack

**Image**: `redis/redis-stack-server:latest`

**Includes**:
- RediSearch 2.x (vector similarity search)
- RedisJSON (JSON document storage)
- RedisGraph, RedisBloom, RedisTimeSeries

**Configuration**:
```bash
REDIS_ARGS="--maxmemory 2gb --maxmemory-policy allkeys-lru --save 900 1 --save 300 10 --save 60 10000"
```

**Resources**:
- CPU: 200m - 500m
- Memory: 2Gi - 3Gi
- Storage: 10GB PVC

### Embedding Service

**Image**: Custom (`semantic-embeddings:latest`)

**Stack**:
- Python 3.11
- FastAPI
- sentence-transformers
- Model: `all-MiniLM-L6-v2` (pre-downloaded in image)

**Resources**:
- CPU: 200m - 500m
- Memory: 512Mi - 1Gi (model is ~100MB)

**Endpoints**:
- `POST /embed` - Generate embeddings
- `GET /health` - Health check
- `GET /` - Service info

## Vector Index Setup

### Create Index (One-time)

```python
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

schema = (
    TextField("prompt"),
    TextField("response"),
    VectorField("embedding",
        "FLAT",  # or "HNSW" for larger datasets
        {
            "TYPE": "FLOAT32",
            "DIM": 384,
            "DISTANCE_METRIC": "COSINE"
        }
    )
)

r.ft("idx:cache").create_index(
    schema,
    definition=IndexDefinition(
        prefix=["cache:"],
        index_type=IndexType.JSON
    )
)
```

## Performance

### Embedding Generation
- **Latency**: 5-10ms per prompt
- **Throughput**: ~100 req/s (single container)
- **Batching**: Supports batch embedding (faster)

### Vector Search
- **Latency**: 1-5ms (depends on dataset size)
- **Algorithm**: FLAT (brute force, accurate) or HNSW (approximate, faster)
- **Scalability**: Up to millions of vectors

## Cost Breakdown

| Component | CPU | Memory | Storage | Cost/mo |
|-----------|-----|--------|---------|---------|
| Redis Stack | 200-500m | 2-3Gi | 10GB | ~$5 |
| Embeddings | 200-500m | 512Mi-1Gi | - | ~$3 |
| **Total** | - | - | - | **~$8** |

## Scaling

### Increase Memory (More Cache)

```yaml
# deployment.yaml
resources:
  limits:
    memory: "4Gi"

# env
- name: REDIS_ARGS
  value: "--maxmemory 3gb ..."
```

### Increase Embedding Throughput

```yaml
# Add more replicas (read-only embedding service)
replicas: 3  # 3x embedding pods

# Load balancer will distribute
```

### Use HNSW Index (Faster Search)

```python
# For >100k vectors, use HNSW
VectorField("embedding", "HNSW", {
    "TYPE": "FLOAT32",
    "DIM": 384,
    "DISTANCE_METRIC": "COSINE",
    "M": 16,
    "EF_CONSTRUCTION": 200
})
```

## Monitoring

### Embedding Service Metrics

```bash
# Check embedding service
kubectl exec -it deployment/semantic-cache -c embeddings -- curl localhost:8000/health
```

### Redis Stack Metrics

```bash
# Check Redis
kubectl exec -it deployment/semantic-cache -c redis -- redis-cli INFO

# Check vector index
kubectl exec -it deployment/semantic-cache -c redis -- redis-cli FT.INFO idx:cache
```

## Advantages

✅ **Co-located**: Redis + Embeddings in same pod (low latency)  
✅ **Official Images**: Redis Stack is maintained by Redis Labs  
✅ **Native Vector Search**: No external vector DB needed  
✅ **Simple Architecture**: Single pod, one service  
✅ **Pre-built Model**: Model cached in Docker image (fast startup)  
✅ **Horizontal Scaling**: Can add read replicas if needed  

## Comparison to Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **This Solution** | Simple, co-located, official Redis | Limited to Redis capabilities |
| **Separate Vector DB** | More features, better scaling | Extra service, complexity |
| **Embeddings in Backend** | No extra service | Duplicate models, more memory |
| **RedisAI** | Run models in Redis | Complex setup, limited models |

---

**Current Setup**: Redis Stack + Sidecar Embedding Service ✅

