# CounselGPT Architecture on GKE

## System Architecture

```
                    Internet
                       ↓
              ┌────────────────┐
              │  Load Balancer │ (Ingress)
              │  + SSL Cert    │
              └────────┬───────┘
                       ↓
              ┌────────────────┐
              │  Router Pods   │ (2-5 replicas, HPA)
              │  GPU-first     │───────┐
              │  Circuit Break │       │ /metrics
              └────────┬───────┘       │
                       ↓               │
            ┌──────────┴──────────┐    │
            ↓                     ↓    │
    ┌───────────────┐     ┌───────────────┐
    │   GPU Pods    │     │   CPU Pods    │
    │   (1 replica) │─┐   │  (2-5, HPA)   │─┐ /metrics
    │   Fast (2-5s) │ │   │  Slow (15-30s)│ │
    └───────┬───────┘ │   └───────┬───────┘ │
            │         │           │         │
            └─────────┼───────────┘         │
                      ↓                     │
         ┌────────────┴────────────┐        │
         ↓                         ↓        │
  ┌─────────────┐          ┌──────────────┐ │
  │   Redis     │          │  Embeddings  │ │ /metrics (Redis only)
  │   (Cache)   │          │  (Semantic)  │ │
  │  Port 6379  │          │  Port 8000   │ │
  └──────┬──────┘          └──────┬───────┘ │
         │                        │         │
         └────────────────────────┘         │
                      ↓                     │
              ┌────────────────┐            │
              │   Model PVC    │            ↓
              │  Qwen + Llama  │   ┌──────────────┐
              └────────────────┘   │  Prometheus  │
                                   │  (scrapes)   │
                                   └──────┬───────┘
                                          ↓
                                   ┌──────────────┐
                                   │   Grafana    │ ← Port-forward 3000
                                   │  Dashboards  │
                                   └──────────────┘
```

## Components

| Component | Pods | Purpose | Cost/mo |
|-----------|------|---------|---------|
| **Ingress** | - | External access + SSL | Included |
| **Router** | 2-5 | Smart GPU-first routing | ~$20 |
| **GPU Backend** | 1 | Fast inference (CUDA) | ~$360 |
| **CPU Backend** | 2-5 | Slow inference (fallback) | ~$100 |
| **Redis** | 1 | Cache storage + metrics | ~$3 |
| **Embeddings** | 1 | Semantic embedding service | ~$3 |
| **Monitoring** | 2 | Prometheus + Grafana | ~$8 |
| **Model Storage** | - | Filestore (ReadWriteMany) | ~$200 |
| **Total** | 8-15 | - | **~$694** |

## Request Flow

### Cache Hit (Fast Path)
```
User → Router → GPU Pod → Redis Cache
                           ↓ (HIT!)
                User ← Router ← GPU Pod ← Cache
                
Latency: ~50ms
```

### Cache Miss (Inference Path)
```
User → Router → GPU Pod → Redis Cache
                ↓ (MISS)    ↓ (no match)
                │           ↓
                │     Get Embedding (Embeddings Service)
                │           ↓
                Load Model → Run Inference
                ↓           ↓
                Store in Cache (with embedding)
                ↓
User ← Router ← Response

Latency: ~3-5s (GPU) or ~20s (CPU)
```

### GPU Queue Full (Fallback Path)
```
User → Router → GPU Queue Full?
                ↓ (yes)
                CPU Pod → Run Inference
                ↓
User ← Router ← Response

Latency: ~20s
```

## Scaling Behavior

### Low Traffic (< 10 req/min)
- Router: 2 pods
- GPU: 1 pod (handles all)
- CPU: 2 pods (idle)
- Cache hit rate: ~40%

### Medium Traffic (10-50 req/min)
- Router: 2-3 pods
- GPU: 1 pod (80% utilized)
- CPU: 2-3 pods (handle overflow)
- Cache hit rate: ~50%

### High Traffic (> 50 req/min)
- Router: 3-5 pods
- GPU: 1 pod (maxed out)
- CPU: 4-5 pods (handle majority)
- Cache hit rate: ~60%

## Data Flow

### Semantic Cache Lookup
```
1. User prompt → Call Embeddings Service (5-10ms)
2. Embeddings Service → Generate 384-dim vector
3. API → Search Redis for similar embeddings (cosine similarity)
4. If similarity ≥ 95% → Return cached response
5. Else → Run inference → Store in Redis with embedding
```

### Model Loading
```
1. Init: Download models from GCS to PVC
2. GPU/CPU pods: Mount PVC at /models
3. Load models into RAM
4. Ready for inference
```

## Failure Modes

### GPU Pod Down
- Router circuit breaker opens
- All traffic → CPU pods
- Slower but functional

### CPU Pods Down
- All traffic → GPU pod
- GPU saturates
- Higher latency, queueing

### Redis Down
- Cache disabled
- All requests run inference
- Slower, higher cost
- System still functional

### Embeddings Service Down
- Semantic cache disabled (exact match only)
- Lower cache hit rate
- System still functional

### PVC Unavailable
- Pods fail to start
- Models can't be loaded
- **Complete failure**

## Cost Optimization

### Reduce Costs
1. Scale GPU to 0 during off-hours
2. Use CPU-only (no GPU) = ~$100/mo
3. Reduce Filestore to 100GB = $20/mo
4. Single CPU pod = ~$30/mo

### Increase Performance
1. Add more GPU pods = ~$360/pod
2. Increase GPU concurrency limit
3. Use faster Filestore tier
4. Increase cache memory

---

**Current setup**: Balanced cost/performance at ~$686/month

