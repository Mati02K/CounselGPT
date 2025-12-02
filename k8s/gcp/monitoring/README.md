# Monitoring Stack (Prometheus + Grafana)

## Components

- **Prometheus**: Metrics collection from all services
- **Grafana**: Visualization dashboards
- **Redis Exporter**: Included in semantic-cache deployment

## Deploy

```bash
# Deploy monitoring stack
kubectl apply -f .

# Wait for pods
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=120s
kubectl wait --for=condition=ready pod -l app=grafana --timeout=120s
```

## Access Grafana

```bash
# Port-forward
kubectl port-forward svc/grafana 3000:3000

# Open browser
# URL: http://localhost:3000
# Username: admin
# Password: admin
```

## Dashboards

1. **CounselGPT Overview**
   - Request rates by backend
   - GPU queue size
   - Circuit breaker states
   - Cache hit rate
   - System health

2. **Router Metrics**
   - Request distribution (GPU vs CPU)
   - GPU capacity and queue
   - Circuit breaker states
   - Fallback reasons
   - Latency percentiles
   - Error rates

3. **Semantic Cache Metrics**
   - Cache hit/miss rates
   - Total keys
   - Memory usage
   - Commands per second
   - Eviction rate
   - Cache efficiency score

4. **Backend Metrics**
   - Inference times
   - Tokens generated
   - Pod status
   - CPU/Memory usage
   - GPU utilization

## Metrics Available

### Router
```promql
router_requests_total{backend, status}
router_request_duration_seconds_bucket{backend}
router_gpu_capacity
router_gpu_queue_size
router_backend_health{backend}
router_circuit_breaker_state{backend}
router_fallback_total{reason}
```

### Cache (Redis)
```promql
redis_keyspace_hits_total
redis_keyspace_misses_total
redis_db_keys
redis_memory_used_bytes
redis_memory_max_bytes
redis_connected_clients
redis_evicted_keys_total
redis_commands_processed_total
```

### Backend
```promql
INFERENCE_TIME
TOKENS_GENERATED
CACHE_HITS
CACHE_MISSES
```

## Useful Queries

### Cache Hit Rate
```promql
rate(redis_keyspace_hits_total[5m]) / 
(rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100
```

### GPU Utilization
```promql
(4 - router_gpu_capacity) / 4 * 100
```

### Request Distribution
```promql
sum(rate(router_requests_total[5m])) by (backend)
```

### P99 Latency
```promql
histogram_quantile(0.99, rate(router_request_duration_seconds_bucket[5m]))
```

### Fallback Rate
```promql
sum(rate(router_fallback_total[5m])) by (reason)
```

## Alerts (Future)

Create AlertManager rules:

```yaml
groups:
- name: counselgpt
  rules:
  - alert: HighErrorRate
    expr: rate(router_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
  
  - alert: GPUCircuitBreakerOpen
    expr: router_circuit_breaker_state{backend="gpu"} == 1
    for: 2m
  
  - alert: LowCacheHitRate
    expr: rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) < 0.3
    for: 10m
  
  - alert: HighMemoryUsage
    expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
    for: 5m
```

## Cost

- Prometheus: ~$5/month (200m CPU, 512Mi RAM)
- Grafana: ~$3/month (100m CPU, 256Mi RAM)
- **Total**: ~$8/month

## Production Setup

For production, add:

1. **Persistent storage** for Prometheus and Grafana
2. **AlertManager** for notifications
3. **Authentication** (change Grafana password!)
4. **Ingress** for external Grafana access
5. **Backup** Grafana dashboards

---

Access Grafana: `kubectl port-forward svc/grafana 3000:3000`

