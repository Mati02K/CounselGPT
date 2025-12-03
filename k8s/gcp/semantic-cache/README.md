# Semantic Cache (Redis Stack + Embeddings)

## Overview

Production-ready semantic caching service combining:
- **Redis Stack**: Vector similarity search with RediSearch
- **Embedding Service**: Generates semantic embeddings for prompts

## Architecture

```
Backend → counselgpt-redis:8000 → Embeddings Service (SentenceTransformer)
       ↓                                 ↓
       └─────────→ counselgpt-redis:6379 ─→ Redis Stack (Vector Storage)
```

## Features

✅ **Vector Similarity**: Redis Stack with RediSearch VSS module  
✅ **Semantic Embeddings**: all-MiniLM-L6-v2 model (384-dim)  
✅ **Persistent Storage**: 10GB PVC for cache data  
✅ **Dual Services**: Redis (6379) + Embeddings API (8000)  
✅ **Prometheus Metrics**: Redis Exporter included  
✅ **Fast Similarity Search**: Native Redis vector operations  

## Deploy

```bash
# Deploy cache
kubectl apply -f .

# Without Redis Commander (optional UI)
kubectl apply -f configmap.yaml -f pvc.yaml -f deployment.yaml -f service.yaml
```

## Access

### From Backends

```python
# Embedding Service API
EMBEDDING_URL = "http://counselgpt-redis:8000"

# Generate embeddings
response = requests.post(f"{EMBEDDING_URL}/embed", 
    json={"texts": ["What is contract law?"]})
embeddings = response.json()["embeddings"]

# Redis (direct access)
REDIS_URL = "redis://counselgpt-redis:6379"
```

### Embedding Service Endpoints

- **POST /embed**: Generate embeddings
  ```json
  {
    "texts": ["prompt1", "prompt2"]
  }
  ```
  Returns:
  ```json
  {
    "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
    "model": "all-MiniLM-L6-v2",
    "dimension": 384
  }
  ```

- **GET /health**: Health check
- **GET /**: Service info

### Redis Commander (Web UI)

```bash
# Deploy UI (optional)
kubectl apply -f redis-commander.yaml

# Access
kubectl port-forward svc/redis-commander 8081:8081
# Open: http://localhost:8081
```

### Redis CLI

```bash
# Connect to Redis
kubectl exec -it deployment/semantic-cache -- redis-cli

# Check stats
127.0.0.1:6379> INFO stats
127.0.0.1:6379> DBSIZE
127.0.0.1:6379> MEMORY USAGE <key>
```

## Configuration

### Memory Policy

```
maxmemory 2gb
maxmemory-policy allkeys-lru  # Evict least recently used
```

### Persistence

```
save 900 1      # Save if 1 key changed in 15 min
save 300 10     # Save if 10 keys changed in 5 min
save 60 10000   # Save if 10000 keys changed in 1 min
```

### Performance

- **IO Threads**: 4 (parallel I/O)
- **Lazy Freeing**: Enabled (better performance)
- **TCP Backlog**: 511 connections

## Monitoring

### Prometheus Metrics

```promql
# Cache hit rate
rate(redis_keyspace_hits_total[5m]) / 
(rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))

# Memory usage
redis_memory_used_bytes / redis_memory_max_bytes

# Keys count
redis_db_keys

# Connected clients
redis_connected_clients

# Operations per second
rate(redis_commands_processed_total[1m])
```

### Check Health

```bash
# Check pod
kubectl get pod -l app=semantic-cache

# Check logs
kubectl logs -l app=semantic-cache -c redis

# Check metrics
kubectl logs -l app=semantic-cache -c redis-exporter
```

## Maintenance

### Clear Cache

```bash
# Clear all keys
kubectl exec deployment/semantic-cache -- redis-cli FLUSHALL

# Clear specific pattern
kubectl exec deployment/semantic-cache -- redis-cli --scan --pattern "llama:cache:*" | xargs kubectl exec deployment/semantic-cache -- redis-cli DEL
```

### Backup Data

```bash
# Trigger RDB snapshot
kubectl exec deployment/semantic-cache -- redis-cli BGSAVE

# Copy snapshot
kubectl cp semantic-cache-xxx:/data/dump.rdb ./backup-dump.rdb
```

### Restore Data

```bash
# Copy snapshot to pod
kubectl cp ./backup-dump.rdb semantic-cache-xxx:/data/dump.rdb

# Restart Redis
kubectl rollout restart deployment/semantic-cache
```

## Scaling

### Increase Memory

Edit `deployment.yaml`:
```yaml
resources:
  limits:
    memory: "4Gi"  # Increase from 3Gi
```

Edit `configmap.yaml`:
```
maxmemory 3gb  # Increase from 2gb
```

Apply:
```bash
kubectl apply -f configmap.yaml -f deployment.yaml
kubectl rollout restart deployment/semantic-cache
```

### Increase Storage

```bash
# Edit PVC
kubectl edit pvc redis-cache-data
# Change: storage: 20Gi  # Increase from 10Gi

# Restart pod to use new space
kubectl rollout restart deployment/semantic-cache
```

## Cost

- **Storage**: 10GB × $0.10/GB = ~$1/month
- **Compute**: 200m CPU, 2Gi RAM = ~$5/month
- **Total**: ~$6/month

## Troubleshooting

### Cache Not Working

```bash
# Check Redis is running
kubectl get pod -l app=semantic-cache

# Test connection
kubectl exec deployment/semantic-cache -- redis-cli ping
# Should return: PONG

# Check from backend pod
kubectl exec -it deployment/counselgpt-api-cpu-xxx -- sh
# Inside pod:
python -c "import redis; r=redis.from_url('redis://counselgpt-redis:6379'); print(r.ping())"
```

### High Memory Usage

```bash
# Check memory
kubectl exec deployment/semantic-cache -- redis-cli INFO memory

# Check keys count
kubectl exec deployment/semantic-cache -- redis-cli DBSIZE

# Manually evict (if needed)
kubectl exec deployment/semantic-cache -- redis-cli FLUSHDB
```

### Performance Issues

```bash
# Check slow queries
kubectl exec deployment/semantic-cache -- redis-cli SLOWLOG GET 10

# Check command stats
kubectl exec deployment/semantic-cache -- redis-cli INFO commandstats

# Monitor in real-time
kubectl exec -it deployment/semantic-cache -- redis-cli --stat
```

---

For semantic caching implementation details, see: `deployment/SEMANTIC_CACHING.md`

