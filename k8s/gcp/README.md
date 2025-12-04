# CounselGPT Kubernetes Manifests (GCP)

## 📁 Folder Structure

```
k8s/gcp/
├── infrastructure/          # Model storage
│   ├── model-pvc.yaml
│   └── model-pvc-filestore.yaml
│
├── redis/                   # Redis cache (separate pod)
│   ├── pvc.yaml                # 10GB storage for Redis data
│   ├── configmap.yaml          # Redis configuration
│   ├── deployment.yaml         # Redis + Redis Exporter
│   └── service.yaml            # Port 6379 (Redis), 9121 (metrics)
│
├── embeddings/              # Semantic embeddings service (separate pod)
│   ├── deployment.yaml         # SentenceTransformer
│   └── service.yaml            # Port 8000 (HTTP API)
│
├── api-gpu/                 # GPU backend (1 pod, CUDA)
│   ├── deployment-gpu.yaml
│   └── service-gpu.yaml
│
├── api-cpu/                 # CPU backend (2-5 pods, HPA)
│   ├── deployment-cpu.yaml
│   ├── service-cpu.yaml
│   └── hpa-cpu.yaml
│
├── router/                  # Smart router (2-5 pods, HPA)
│   └── deployment.yaml
│   └── hpa-router.yaml
│
├── monitoring/              # Prometheus + Grafana
│   ├── prometheus-deployment.yaml
│   ├── grafana-deployment.yaml
│   └── grafana-dashboards.yaml
│
├── ingress/                 # External access + SSL
│   ├── ingress.yaml
│   └── managed-certificate.yaml
│
└── README.md
```

## 🎯 Components

### Infrastructure
- **PVC**: Persistent storage for models (ReadWriteOnce or ReadWriteMany)

### Components

| Component | Purpose | Cost/mo |
|-----------|---------|---------|
| **Infrastructure** | Model storage (Filestore) | ~$200 |
| **Redis** | Cache storage + Redis Exporter | ~$3 |
| **Embeddings** | Semantic embedding generation | ~$3 |
| **Backend GPU** | 1 pod, NVIDIA L4 | ~$360 |
| **Backend CPU** | 2-5 pods, auto-scale | ~$100 |
| **Router** | 2-5 pods, GPU-first routing | ~$20 |
| **Monitoring** | Prometheus + Grafana | ~$8 |
| **Ingress** | Load balancer + SSL | Included |
| **Total** | - | **~$694/mo** |

## Deploy

```bash
# Using Cloud Build (recommended)
git push

# Or manually (in order)
kubectl apply -f infrastructure/      # PVCs for models
kubectl apply -f embeddings/          # Embeddings service
kubectl apply -f redis/               # Redis cache
kubectl apply -f api-gpu/             # GPU backend
kubectl apply -f api-cpu/             # CPU backend
kubectl apply -f router/              # Router (main API)
kubectl apply -f monitoring/          # Prometheus + Grafana
kubectl apply -f ingress/             # External access
```

## Access Grafana

**External URL** (via Ingress):
```
https://34.111.194.27.nip.io/grafana
Username: admin
Password: admin
```

**Or via port-forward** (local development):
```bash
kubectl port-forward svc/grafana 3000:3000
# Open: http://localhost:3000
```

⚠️ **Security**: Change the default password after first login!

## Common Commands

```bash
# Check status
kubectl get pods
kubectl get svc

# View logs
kubectl logs -l tier=gpu -f
kubectl logs -l app=counselgpt-router -f

# Scale CPU
kubectl scale deployment counselgpt-api-cpu --replicas=5

# Restart services
kubectl rollout restart deployment/counselgpt-api-gpu
kubectl rollout restart deployment/counselgpt-api-cpu
kubectl rollout restart deployment/counselgpt-router
```