# GCP Kubernetes Deployment

## File Purpose (5 lines)

* **deployment.yaml** – Deploys CounselGPT API on GPU node.
* **service.yaml** – Exposes API using LoadBalancer.
* **redis-deployment.yaml** – Runs Redis on CPU node.
* **redis-service.yaml** – Internal ClusterIP for Redis.
* **hpa.yaml / ingress.yaml** – Optional autoscaling + ingress.

## Connect kubectl and to our cluster

```bash
#login first
gcloud auth login 

#then do the rest
gcloud config set project counselgpt-cse239
gcloud container clusters get-credentials counselgpt-cluster --region us-west1
kubectl get pods
```

## Apply in Correct Order (5 lines)

```bash
kubectl apply -f k8s/gcp/redis-deployment.yaml
kubectl apply -f k8s/gcp/redis-service.yaml
kubectl apply -f k8s/gcp/deployment.yaml
kubectl apply -f k8s/gcp/service.yaml
kubectl get svc counselgpt-api   # Get external IP (Load Balanced one)
```

Alternatively you can just push and cloud build will take care, hopefully without errors :).
