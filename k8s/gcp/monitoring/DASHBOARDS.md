# Grafana Dashboards Overview

## 📊 Available Dashboards

### 1. CounselGPT Overview
**Main monitoring dashboard**

**Panels:**
- 📈 Request Rate (by backend)
- 🎮 GPU Queue Size
- 🔌 Circuit Breaker State
- 💾 Cache Hit Rate
- ❤️ Backend Health Status
- 🔄 Fallback Rate by Reason
- ⏱️ P99 Latency
- 💭 Redis Memory Usage

**Use this to**: Get a quick overview of system health at a glance

---

### 2. Router Metrics
**Deep dive into routing logic**

**Panels:**
- 📊 Requests by Backend & Status
- 🎯 GPU Capacity vs Queue Size
- 🚦 Circuit Breaker States (GPU + CPU)
- 📉 Fallback Reasons Breakdown
- 📈 Latency Percentiles (P50, P90, P99)
- ❌ Error Rate by Backend

**Use this to**: 
- Understand traffic distribution
- Diagnose routing issues
- Monitor GPU saturation
- Identify failure patterns

---

### 3. Semantic Cache Metrics
**Cache performance and efficiency**

**Panels:**
- 🎯 Cache Hit Rate (gauge)
- 📊 Hits vs Misses Over Time
- 🔢 Total Keys Stored
- 💾 Memory Usage (current vs max)
- ⚡ Commands Per Second
- 👥 Connected Clients
- 🗑️ Evicted Keys Rate
- ⭐ Cache Efficiency Score

**Use this to**:
- Monitor cache effectiveness
- Plan capacity increases
- Detect memory issues
- Optimize TTL settings

---

### 4. Backend Metrics
**Backend pod health and performance**

**Panels:**
- ⏱️ Inference Time
- 📝 Tokens Generated
- 📋 Pods Status Table
- 💻 CPU Usage by Pod
- 🧠 Memory Usage by Pod
- 🎮 GPU Utilization (if available)

**Use this to**:
- Monitor inference performance
- Detect resource bottlenecks
- Track pod health
- Plan scaling decisions

---

## 🎨 Custom Panels You Can Add

### Request Success Rate
```promql
sum(rate(router_requests_total{status!~"5.."}[5m])) / 
sum(rate(router_requests_total[5m])) * 100
```

### Average GPU Wait Time
```promql
avg(router_gpu_queue_wait_seconds)
```

### Cache Size Growth
```promql
rate(redis_db_keys[1h])
```

### Cost Per Request (Estimated)
```promql
# GPU: $360/mo ÷ 30 days ÷ 86400s = $0.00014/s
# If handling N req/s, cost/req = $0.00014/N
sum(rate(router_requests_total{backend="gpu"}[5m]))
```

### Backend Availability
```promql
router_backend_health / 1 * 100
```

---

## 📈 Recommended Panel Layouts

### **Operations Dashboard** (4K/Wide Screen)
```
+------------------+------------------+------------------+
|  Request Rate    |  GPU Queue       | Circuit Breaker  |
|  (line graph)    |  (line graph)    | (stat panels)    |
+------------------+------------------+------------------+
|  Cache Hit Rate  |  P99 Latency     | Fallback Reasons |
|  (gauge)         |  (line graph)    | (pie chart)      |
+------------------+------------------+------------------+
|  Backend Health  |  Error Rate      | Redis Memory     |
|  (stat panels)   |  (line graph)    | (gauge)          |
+------------------+------------------+------------------+
```

### **Developer Dashboard** (Laptop)
```
+----------------------------------+
|  Request Rate (GPU vs CPU)       |
+----------------------------------+
|  P50/P90/P99 Latency             |
+----------------------------------+
|  Cache Hit Rate                  |
+----------------------------------+
|  Error Logs (table)              |
+----------------------------------+
```

### **Executive Dashboard** (TV/Monitor)
```
+----------------------------------+
|  System Health: ✅ ALL SYSTEMS GO |
+----------------------------------+
|  Today's Requests: 12,345        |
|  Cache Hit Rate: 62%             |
|  Avg Latency: 3.2s               |
|  Cost Today: $23.15              |
+----------------------------------+
```

---

## 🚨 Alert Rules (Future Setup)

Add these to AlertManager:

```yaml
groups:
- name: counselgpt-critical
  rules:
  - alert: HighErrorRate
    expr: rate(router_requests_total{status=~"5.."}[5m]) / rate(router_requests_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Error rate > 10%"
  
  - alert: GPUCircuitBreakerOpen
    expr: router_circuit_breaker_state{backend="gpu"} == 1
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "GPU circuit breaker open - traffic routing to CPU"
  
  - alert: LowCacheHitRate
    expr: rate(redis_keyspace_hits_total[10m]) / (rate(redis_keyspace_hits_total[10m]) + rate(redis_keyspace_misses_total[10m])) < 0.3
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "Cache hit rate < 30%"
  
  - alert: RedisMemoryHigh
    expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Redis memory > 90%"
```

---

## 📱 Access Methods

### Local Development
```bash
kubectl port-forward svc/grafana 3000:3000
# http://localhost:3000
```

### Production (with Ingress)
```yaml
# Add to ingress/ingress.yaml
- path: /grafana
  pathType: Prefix
  backend:
    service:
      name: grafana
      port:
        number: 3000
```

### Mobile Access (Ngrok)
```bash
# Requires ngrok installed
kubectl port-forward svc/grafana 3000:3000 &
ngrok http 3000
# Use ngrok URL
```

---

**Default Credentials**: admin / admin (change in production!)

**Dashboard Folder**: CounselGPT (auto-created)

**Data Source**: Prometheus (auto-configured)

