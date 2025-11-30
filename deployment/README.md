
# CounselGPT Deployment

This directory contains all backend code and configuration required to run the CounselGPT inference service locally and in production.

## Directory Overview

| File/Folder        | Purpose                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `app.py`           | Main API server exposing inference, health, and metrics endpoints. |
| `modelclass.py`    | Loads the GGUF model and runs inference using llama.cpp bindings.  |
| `cache.py`         | Redis caching helper used by the API.                              |
| `metrics.py`       | Prometheus metrics definitions and `/metrics` exporter.            |
| `Dockerfile`       | Docker image definition for building the API service.              |
| `requirements.txt` | Python dependencies for the API service.                           |
| `models/`          | Local-only model directory used during development.                |
| `grafana/`         | Customised Grafana dashboard scripts for inferencing               |
| `prometheus.yml`   | Prometheus scrape configuration (local only).                      |

---

# Running Locally (GPU Required)

The following setup replicates the production environment using Docker containers.

## 1. Create network

```
docker network create counselgpt-net
```

## 2. Start Redis

```
docker run -d \
  --name redis-cache \
  --network counselgpt-net \
  -p 6379:6379 \
  redis:7-alpine
```

## 3. Start API container (with GPU required)

```
docker run --rm \
  --name counselgpt-api \
  --gpus all \
  -p 8000:8000 \
  -e MODEL_PATH=/models/llama-2-7b-chat.Q4_K_M.gguf \
  -e REDIS_URL=redis://redis-cache:6379 \
  --network counselgpt-net \
  -v /home/mathesh/Documents/code/CounselGPT/deployment/models:/models \
  mathesh0208/counselgptapi:v6
```

---

# Local Monitoring Stack (Optional)

## Prometheus

```
docker run -d \
  --name prom \
  --network counselgpt-net \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## Grafana

```
docker run -d \
  --name grafana \
  --network counselgpt-net \
  -p 3000:3000 \
  grafana/grafana
```

## Node Exporter

```
docker run -d \
  --name node-exporter \
  --network counselgpt-net \
  -p 9100:9100 \
  prom/node-exporter
```

## DCGM GPU Exporter

```
docker run -d \
  --name dcgm \
  --gpus all \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --network counselgpt-net \
  -p 9400:9400 \
  nvcr.io/nvidia/k8s/dcgm-exporter:latest
```

---

# Testing

## Local test

```
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

## Nautilus test

```
curl -X POST https://counselgpt-mathesh.nrp-nautilus.io/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello"}'
```

---
