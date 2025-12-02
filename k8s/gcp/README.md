# CounselGPT Kubernetes Manifests (GCP)

## 📁 Folder Structure

```
k8s/gcp/
├── infrastructure/          # Shared infrastructure
│   ├── redis-deployment.yaml
│   ├── redis-service.yaml
│   ├── model-pvc.yaml      # Standard PVC
│   └── model-pvc-filestore.yaml  # Filestore PVC (ReadWriteMany)
│
├── backend-gpu/             # GPU backend (CUDA-enabled)
│   ├── deployment-gpu.yaml
│   └── service-gpu.yaml
│
├── backend-cpu/             # CPU backend (CPU-only)
│   ├── deployment-cpu.yaml
│   ├── service-cpu.yaml
│   └── hpa-cpu.yaml        # Auto-scaling
│
├── router/                  # Intelligent router
│   └── deployment.yaml     # Router + service + HPA
│
├── ingress/                 # External access
│   ├── ingress.yaml
│   └── managed-certificate.yaml
│
├── apply.sh                 # Deploy everything
├── delete.sh                # Clean up everything
└── README.md               # This file
```

## 🎯 Components

### Infrastructure
- **Redis**: Cache for semantic caching
- **PVC**: Persistent storage for models (ReadWriteOnce or ReadWriteMany)

### Backend GPU
- **Deployment**: 1 replica with NVIDIA L4 GPU
- **Service**: Internal service for GPU pods
- **Image**: `counselgptapi:gpu-*`
- **Cost**: ~$360/month

### Backend CPU
- **Deployment**: 2-5 replicas (auto-scales)
- **Service**: Internal service for CPU pods
- **HPA**: Scales 2-5 pods based on load
- **Image**: `counselgptapi:cpu-*`
- **Cost**: ~$60-150/month

### Router
- **Deployment**: 2-5 replicas (auto-scales)
- **Service**: `counselgpt-api` (main entry point)
- **Features**: GPU-first routing, circuit breaker, health monitoring
- **Image**: `counselgpt-router:*`
- **Cost**: ~$15-30/month

### Ingress
- **Ingress**: GCP HTTP(S) load balancer
- **Certificate**: Managed SSL certificate
- **Domain**: `*.nip.io` or custom domain