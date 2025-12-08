# **Nautilus Deployment**

This folder contains all Kubernetes manifests required to deploy **CounselGPT API**, **semantic embeddings**, **Redis caching**, **Prometheus monitoring**, and **Grafana dashboard** on Nautilus.

---

# **1. Connect to Nautilus & Configure kubectl**

Follow:
[https://nrp.ai/documentation/userdocs/start/getting-started/](https://nrp.ai/documentation/userdocs/start/getting-started/)

Set kubeconfig:

```bash
mkdir -p ~/.kube
mv ~/Downloads/config ~/.kube/config
```

---

# **2. File Overview (Current Architecture)**

### **Core App**

| File              | Purpose                                                       |
| ----------------- | ------------------------------------------------------------- |
| `deployment.yaml` | Main CounselGPT API (llama.cpp + Qwen + Redis + GPU affinity) |
| `service.yaml`    | Exposes API to cluster (ClusterIP → Ingress)                  |
| `ingress.yaml`    | Public endpoint (`https://<name>.nrp-nautilus.io/infer`)      |

### **Model Storage**

| File                  | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `ceph-s3-secret.yaml` | S3 credentials for downloading GGUF models    |
| `cephfs-pvc.yaml`     | Persistent model storage mounted at `/models` |
| `s3-sync-job.yaml`    | Copies model from S3 → CephFS PVC             |

### **Semantic Embedding Service**

| File                     | Purpose                                          |
| ------------------------ | ------------------------------------------------ |
| `embedding.yaml`         | Deployment running SentenceTransformer inference |
| `embedding-service.yaml` | ClusterIP for API pods to call embeddings        |
| `embedding-pvc.yaml`     | Storage for embedding models                     |

### **Redis (Caching Layer)**

| File                    | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `redis-deployment.yaml` | Redis pod                                 |
| `redis-service.yaml`    | ClusterIP Redis endpoint                  |
| `redisconfigmap.yaml`   | Redis config (maxmemory, eviction policy) |
| `redis-pvc.yaml`        | Redis local storage                       |

---

### **Monitoring (Prometheus + Grafana)**

| File                     | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `prometheus.yaml`        | Prometheus server deployment                      |
| `prometheus-config.yaml` | Scrape configs + targets (API, embeddings, Redis) |
| `grafana.yaml`           | Grafana deployment with dashboards                |
| `service-monitor.yaml`   | Prometheus Operator service monitor               |
| `hpa.yaml`               | Horizontal Pod Autoscaler for CounselGPT API      |

---

# **3. BEFORE K8s: Upload Model to Ceph S3**

Configure:

```bash
s3cmd --configure
```

Use:

```
access_key = <ACCESS>
secret_key = <SECRET>
host_base = https://s3-west.nrp-nautilus.io
host_bucket = https://s3-west.nrp-nautilus.io
use_https = True
signature_v2 = False
```

Upload GGUF models:

```bash
s3cmd put <LOCAL_MODEL>.gguf s3://counselgpt-models/ --force
```

---

# **4. Apply Namespace**

```bash
kubectl apply -f namespace.yaml
```

---

# **5. Model Storage + Sync Setup**

### Create S3 Secret

```bash
kubectl apply -f ceph-s3-secret.yaml
```

### Create Model Storage (CephFS PVC)

```bash
kubectl apply -f cephfs-pvc.yaml
```

### Sync GGUF from S3 → PVC

```bash
kubectl apply -f s3-sync-job.yaml
kubectl logs -f job/s3-sync-mthiruma -n cse239fall2025
```

---

# **6. Deploy Redis Cache**

```bash
kubectl apply -f redisconfigmap.yaml
kubectl apply -f redis-pvc.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f redis-service.yaml
```

---

# **7. Deploy Semantic Embedding Service**

```bash
kubectl apply -f embedding-pvc.yaml
kubectl apply -f embedding.yaml
kubectl apply -f embedding-service.yaml
```

Check:

```bash
kubectl get pods -n cse239fall2025
kubectl port-forward svc/counselgpt-embeddings-mthiruma 8000:8000
curl localhost:8000/health
```

---

# **8. Deploy the CounselGPT API**

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

Confirm:

```bash
kubectl get ingress -n cse239fall2025
```

---

# **9. Deploy Monitoring Stack**

### Prometheus

```bash
kubectl apply -f prometheus-config.yaml
kubectl apply -f prometheus.yaml
kubectl apply -f service-monitor.yaml
```

### Grafana

```bash
kubectl apply -f grafana.yaml
```

Port-forward to view dashboards if needed:

```bash
kubectl port-forward svc/grafana 3000:3000 -n cse239fall2025
```

---

# **10. Deploy Horizontal Pod Autoscaler**

```bash
kubectl apply -f hpa.yaml
```

---

# **11. Verify Everything**

```bash
kubectl get pods -n cse239fall2025
kubectl get svc -n cse239fall2025
kubectl get ingress -n cse239fall2025
```

---

# **12. Clear Redis Cache (for benchmarking)**

```bash
curl -X POST https://<your-ingress>.nrp-nautilus.io/cache/clear
```

---

