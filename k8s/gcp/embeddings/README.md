# Embeddings Service

This folder contains Kubernetes manifests for the semantic embeddings service.

## Overview

The embeddings service generates vector embeddings from text prompts, enabling semantic caching. It runs as a separate microservice that can be called by the API backends.

## Purpose

- **Generate Embeddings**: Convert text prompts to 384-dimensional vectors
- **Enable Semantic Cache**: Allow similar queries to match cached responses
- **Decoupled Architecture**: Runs independently from Redis for better scalability

## Components

### Embeddings Container
- **Image**: Custom-built (see `backend/embeddings/`)
- **Port**: 8000 (HTTP API)
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformer)
  - Dimension: 384
  - Size: ~380MB
  - Speed: ~50-100 embeddings/second on CPU

## Files

```
embeddings/
├── deployment.yaml   # Embeddings service with model loading
└── service.yaml      # Exposes port 8000 (HTTP API)
```

## Service Details

**Service Name**: `counselgpt-embeddings`

**Port**: `8000` (HTTP)

**Endpoints**:
- `GET /health` - Health check
- `POST /embed` - Generate embeddings
- `GET /` - Service info

**Access from other pods**:
```bash
# HTTP endpoint
http://counselgpt-embeddings:8000
```

## API Usage

### Health Check
```bash
curl http://counselgpt-embeddings:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "model": "/models/semantic/all-MiniLM-L6-v2",
  "dimension": 384
}
```

### Generate Embeddings
```bash
curl -X POST http://counselgpt-embeddings:8000/embed \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["What is contract law?", "Tell me about contracts"]
  }'
```

**Response**:
```json
{
  "embeddings": [
    [0.123, -0.456, 0.789, ...],  // 384 dimensions
    [0.134, -0.445, 0.801, ...]
  ],
  "model": "/models/semantic/all-MiniLM-L6-v2",
  "dimension": 384
}
```

## Resource Configuration

```yaml
requests:
  cpu: 100m
  memory: 512Mi
limits:
  cpu: 1000m
  memory: 2Gi
```

## Model Loading

The deployment uses an **initContainer** to download the embedding model from GCS:

```bash
gs://counselgpt-models/all-MiniLM-L6-v2.zip
```

The model is stored on the shared PVC (`counselgpt`) and mounted at `/models`.

## Deployment

### Deploy
```bash
# Deploy embeddings service
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=embeddings --timeout=300s
```

### Verify
```bash
# Check pod status
kubectl get pods -l app=embeddings

# View logs (watch model loading)
kubectl logs -l app=embeddings -f

# Test health endpoint
kubectl port-forward svc/counselgpt-embeddings 8000:8000 &
curl http://localhost:8000/health
```

### Test Embedding Generation
```bash
# Generate test embedding
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test prompt"]}'
```

## Health Checks

### Startup Probe
- HTTP GET `/health`
- Initial delay: 30s
- Allows 2 minutes for model loading (12 failures × 10s)

### Liveness Probe
- HTTP GET `/health`
- Checks every 30s
- Ensures service is responsive

### Readiness Probe
- HTTP GET `/health`
- Checks every 10s
- Marks pod ready for traffic

## Performance

### Throughput
- **Single Request**: ~10-20ms per embedding
- **Batch (10 texts)**: ~50-100ms total
- **Capacity**: ~50-100 requests/second

### Latency
- Model loading: ~30-60 seconds (startup)
- Embedding generation: ~10-20ms per text
- Cold start (pod restart): ~60s

## Integration

The embeddings service is called by:

1. **GPU API** (`counselgpt-api-gpu`)
2. **CPU API** (`counselgpt-api-cpu`)

When caching responses:
```python
# In backend/api/cache.py
embedding_url = "http://counselgpt-embeddings:8000"
embedding = requests.post(f"{embedding_url}/embed", json={"texts": [prompt]})
redis.set(key, {"response": response, "embedding": embedding})
```

## Scaling

### Horizontal Scaling
```bash
# Scale to multiple replicas if needed
kubectl scale deployment embeddings --replicas=3
```

### When to Scale
- If embedding latency > 100ms consistently
- If CPU utilization > 80%
- If handling > 100 requests/second

## Troubleshooting

### Pod Won't Start
```bash
# Check events
kubectl describe pod -l app=embeddings

# Common issues:
# 1. Model download failed (GCS permissions)
# 2. PVC not mounted
# 3. Out of memory
```

### Model Loading Slow
```bash
# Check initContainer logs
kubectl logs <pod-name> -c download-models

# Check if model already exists on PVC
kubectl exec <pod-name> -- ls -lh /models/semantic/
```

### Service Not Responding
```bash
# Check if service has endpoints
kubectl get endpoints counselgpt-embeddings

# Check pod health
kubectl get pods -l app=embeddings

# View logs for errors
kubectl logs -l app=embeddings --tail=100
```

### High Memory Usage
- The model uses ~400MB in memory
- Each request adds ~10-20MB temporarily
- Scale up memory limits if OOMKilled

## Monitoring

Currently, the embeddings service does **not** expose Prometheus metrics.

**To add metrics** (optional):
1. Add `prometheus-client` to `backend/embeddings/Dockerfile.embeddings`
2. Expose `/metrics` endpoint in `embeddings.py`
3. Add Prometheus annotations to service

## Cost

Estimated cost: **~$3/month**
- CPU: 100m-1000m
- Memory: 512Mi-2Gi
- Shared PVC usage: ~400MB

## Comparison: Before vs After

### Before (Embedded in Redis Pod)
```
Redis Pod:
├─ redis (Port 6379)
├─ redis-exporter (Port 9121)
└─ embeddings (Port 8000)  ❌ Tightly coupled
```

### After (Separate Service) ✅
```
Redis Pod:                    Embeddings Pod:
├─ redis (Port 6379)         └─ embeddings (Port 8000)
└─ redis-exporter (9121)     
```

**Benefits**:
- ✅ Better isolation
- ✅ Independent scaling
- ✅ Easier debugging
- ✅ More resilient (Redis failure doesn't affect embeddings)

## Related Services

- **Redis** (`counselgpt-redis:6379`) - Stores cached data
- **API Services** - Call embeddings service for semantic cache
- **PVC** (`counselgpt`) - Stores embedding model

---

For more information, see:
- [Backend Code](../../../backend/embeddings/)
- [Main Architecture](../ARCHITECTURE.md)
- [GCP Deployment Guide](../README.md)

