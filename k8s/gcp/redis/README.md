# Redis Cache Service

This folder contains Kubernetes manifests for the Redis cache service.

## Overview

Redis serves as the caching layer for CounselGPT, storing both:
- **Exact match cache**: Direct prompt → response mapping
- **Semantic cache data**: Cached responses with embeddings for similarity search

## Components

### Redis Stack Server
- **Image**: `redis/redis-stack-server:latest`
- **Port**: 6379 (Redis protocol)
- **Features**:
  - RediSearch module for vector similarity
  - Persistence enabled (RDB snapshots)
  - LRU eviction when memory limit reached
  - 2GB max memory configured

### Redis Exporter (Sidecar)
- **Image**: `oliver006/redis_exporter:latest`
- **Port**: 9121 (Prometheus metrics)
- **Purpose**: Expose Redis metrics for monitoring

## Files

```
redis/
├── configmap.yaml    # Redis configuration (if needed)
├── pvc.yaml          # 10GB persistent storage for Redis data
├── deployment.yaml   # Redis + Redis Exporter containers
└── service.yaml      # Exposes ports 6379 and 9121
```

## Service Details

**Service Name**: `counselgpt-redis`

**Ports**:
- `6379` → Redis (TCP)
- `9121` → Metrics (HTTP)

**Access from other pods**:
```bash
# Redis connection string
redis://counselgpt-redis:6379

# Metrics endpoint
http://counselgpt-redis:9121/metrics
```

## Configuration

### Memory Settings
- **Max Memory**: 2GB
- **Eviction Policy**: `allkeys-lru` (Least Recently Used)
- **Persistence**: RDB snapshots (900s with 1 change, 300s with 10 changes, 60s with 10000 changes)

### Resource Limits
```yaml
requests:
  cpu: 100m
  memory: 1Gi
limits:
  cpu: 500m
  memory: 3Gi
```

## Usage

### Deploy
```bash
# Create PVC first
kubectl apply -f pvc.yaml

# Deploy Redis
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Verify
```bash
# Check pod status
kubectl get pods -l app=redis

# Test connection
kubectl exec -it <redis-pod-name> -c redis -- redis-cli ping
# Expected: PONG

# Check metrics
kubectl exec -it <redis-pod-name> -c redis-exporter -- wget -O- localhost:9121/metrics | head -20
```

### Monitor
```bash
# View logs
kubectl logs -l app=redis -c redis -f

# View exporter logs
kubectl logs -l app=redis -c redis-exporter -f

# Port-forward for local access
kubectl port-forward svc/counselgpt-redis 6379:6379
redis-cli -h localhost
```

## Health Checks

### Liveness Probe
- TCP socket check on port 6379
- Ensures Redis process is running

### Readiness Probe
- Redis `PING` command
- Ensures Redis is accepting connections

## Metrics Exposed

Key metrics available at `counselgpt-redis:9121/metrics`:

- `redis_keyspace_hits_total` - Cache hits
- `redis_keyspace_misses_total` - Cache misses
- `redis_db_keys` - Number of keys stored
- `redis_memory_used_bytes` - Current memory usage
- `redis_memory_max_bytes` - Max memory limit
- `redis_connected_clients` - Active connections
- `redis_evicted_keys_total` - Keys evicted due to memory pressure
- `redis_commands_processed_total` - Total commands processed

## Troubleshooting

### High Memory Usage
```bash
# Check memory usage
kubectl exec -it <redis-pod-name> -c redis -- redis-cli INFO memory

# Check eviction stats
kubectl exec -it <redis-pod-name> -c redis -- redis-cli INFO stats | grep evicted

# Clear cache if needed
kubectl exec -it <redis-pod-name> -c redis -- redis-cli FLUSHALL
```

### Connection Issues
```bash
# Check service endpoints
kubectl get endpoints counselgpt-redis

# Test from API pod
kubectl exec -it <api-pod-name> -- nc -zv counselgpt-redis 6379
```

### Low Cache Hit Rate
- Check if embeddings service is running (needed for semantic cache)
- Verify TTL settings (default 1800s = 30min)
- Monitor cache size - might be evicting too aggressively

## Related Services

- **Embeddings Service** (`counselgpt-embeddings:8000`) - Generates semantic embeddings
- **API Services** - Connect to Redis for caching
- **Prometheus** - Scrapes metrics from Redis Exporter

## Security Notes

- Redis is exposed as ClusterIP (internal only)
- No authentication configured (should be added for production)
- Network policies can restrict access to specific pods

## Cost

Estimated cost: **~$3/month**
- CPU: 100m-500m
- Memory: 1Gi-3Gi
- Storage: 10GB PD-Standard

---

For more information, see [k8s/gcp/README.md](../README.md)

