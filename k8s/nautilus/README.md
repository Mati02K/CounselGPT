# Nautilus Deployment

## 1. Connect to Nautilus and add it your kubectl namespace

Follow the official guide:
[https://nrp.ai/documentation/userdocs/start/getting-started/](https://nrp.ai/documentation/userdocs/start/getting-started/)

## 2. Required Files

All manifests are in `k8s/nautilus/`:

* `namespace.yaml` — Creates your namespace
* `ceph-s3-secret.yaml` — S3 credentials (Ask me :- **[mthiruma@ucsc.edu](mailto:mthiruma@ucsc.edu)**)
* `cephfs-pvc.yaml` — CephFS volume for model storage
* `s3-sync-job.yaml` — Downloads GGUF model from S3 → PVC
* `deployment.yaml` — API running llama.cpp + GPU
* `service.yaml` — Exposes service NodePort / LoadBalancer
* `redis-deployment.yaml` + `redis-service.yaml` — Redis cache
* `ingress.yaml` — Exposes API at `https://<yourname>.nrp-nautilus.io`

---

# BEFORE K8s: Upload Model to Ceph S3

```
s3cmd --configure
```

Use this `~/.s3cfg`:

```
access_key = <ACCESS>
secret_key = <SECRET>
host_base = https://s3-west.nrp-nautilus.io
host_bucket = https://s3-west.nrp-nautilus.io
use_https = True
signature_v2 = False
```

Upload:

```
s3cmd put \
 deployment/models/llama-2-7b-chat.Q4_K_M.gguf \
 s3://counselgpt-models/llama-2-7b-chat.Q4_K_M.gguf \
 --force
```

---

# K8s Setup 
We copied model from S3 bucket to our PVC for serving models inside the cluster.

Namespace

```
kubectl apply -f k8s/nautilus/namespace.yaml
```

S3 Secret

```
kubectl apply -f k8s/nautilus/ceph-s3-secret.yaml
```

CephFS PVC (Model Storage)

```
kubectl apply -f k8s/nautilus/cephfs-pvc.yaml
```

Sync Model (S3 → PVC)

```
kubectl apply -f k8s/nautilus/s3-sync-job.yaml
kubectl logs -f job/s3-sync-mthiruma -n cse239fall2025
```

Verify model is downloaded:

```
kubectl exec -it <api-pod> -- ls -lh /models
```

---

# Deploy the Application


```
kubectl apply -f k8s/nautilus/redis-deployment.yaml
kubectl apply -f k8s/nautilus/redis-service.yaml
kubectl apply -f k8s/nautilus/deployment.yaml
kubectl apply -f k8s/nautilus/service.yaml
kubectl apply -f k8s/nautilus/ingress.yaml
```

