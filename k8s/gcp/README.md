# CounselGPT Kubernetes Manifests (GCP)

## 📁 Folder Structure

```
k8s/gcp/
├── infrastructure/          # Model storage
│   ├── model-pvc.yaml
│   └── model-pvc-filestore.yaml
│
├── semantic-cache/          # Redis Stack + Embeddings Service
│   ├── pvc.yaml                # 10GB storage
│   ├── deployment.yaml         # Redis Stack + SentenceTransformer
│   ├── service.yaml            # Ports 6379 (Redis), 8000 (Embeddings)
│   └── redis-commander.yaml    # Optional UI
│
├── backend-gpu/             # GPU backend (1 pod, CUDA)
│   ├── deployment-gpu.yaml
│   └── service-gpu.yaml
│
├── backend-cpu/             # CPU backend (2-5 pods, HPA)
│   ├── deployment-cpu.yaml
│   ├── service-cpu.yaml
│   └── hpa-cpu.yaml
│
├── router/                  # Smart router (2-5 pods, HPA)
│   └── deployment.yaml
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
| **Semantic Cache** | Redis with embeddings | ~$6 |
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

# Or manually
kubectl apply -f infrastructure/
kubectl apply -f semantic-cache/
kubectl apply -f backend-gpu/
kubectl apply -f backend-cpu/
kubectl apply -f router/
kubectl apply -f monitoring/
kubectl apply -f ingress/
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