# CounselGPT — Ask Legal Questions, Get Answers in Seconds

**CounselGPT** is a **full-stack, production-deployed legal AI system** that answers U.S. legal questions in seconds using **LLMs optimized for legal reasoning**.

It combines:

* **LLM inference optimized with GGUF + CUDA**
* **Semantic caching with Redis**
* **GPU-aware Kubernetes deployments**
* **Real-time observability (Prometheus + Grafana)**
* **Rigorous evaluation using LegalBench**

👉 **Live Demo:**
🔗 [CounselGPT*](https://mati02k.github.io/CounselGPT/)

> Ask questions related to U.S. law, statutes, contracts, definitions, and legal reasoning — and receive concise, structured responses.

[* - Site is down right now due to cost constraints of hosting in cloud. But you can clone and use minikube to deploy and see.]

---

## 🎥 Demo

![CounselGPT Demo](assets/demo.gif)

---

## 📄 Project Report & Presentation

* 📘 **Technical Report:** [Report](assets/Technical_report.pdf)
* 📊 **Final Presentation Slides:** [Report](assets/CounselGPT.pdf)

> These documents describe system design, benchmarking methodology, LegalBench evaluation, and performance analysis.

---

## 🧠 How CounselGPT Works (High Level)

1. **User query** is sent from React frontend
2. **FastAPI backend** constructs a structured prompt
3. **LLM inference** runs via `llama.cpp` (GGUF, GPU-accelerated)
4. **Redis semantic cache** checks for similar past queries
5. **Metrics are recorded** (latency, tokens, cache hits, GPU usage)
6. **Response returned** to user in real time

---

## 🧪 Evaluation & Benchmarking

CounselGPT is evaluated using **LegalBench**, a Stanford-led benchmark suite for legal reasoning tasks. You can find more details about our LegalBench Evalaution here :- [`LegalBench Overview`](https://github.com/VasaviSD/lora-legal-training/tree/main/benchmark)

For LLM-Serving Benchmarking details:

* **k6 load testing**
* **GPU vs CPU comparison**
* **Quantization (4-bit vs 8-bit) analysis**

📁 See details here:
➡️ [`benchmark/README.md`](benchmark/README.md)

---

## 🧬 LoRA Fine-Tuning (Separate Repository)

This repository focuses on **inference, deployment, and evaluation**.

If you’re interested in **how the LLM was fine-tuned using LoRA on U.S. law data**, see:

🔗 **LoRA Training Repo:**
[https://github.com/VasaviSD/lora-legal-training](https://github.com/VasaviSD/lora-legal-training)

That repo includes:

* USLawQA dataset usage
* LoRA adapter training pipeline
* LegalBench before/after comparisons
* Detailed analysis of where LoRA helps vs doesn’t

---

## 🏗️ Tech Stack (Detailed)

### 🔹 Backend & LLM Inference

* **Python 3.11**
* **FastAPI** — high-performance inference API
* **llama.cpp** — GGUF-based LLM inference
* **Qwen / LLaMA-family models**
* **CUDA 12.4** — GPU acceleration
* **Thread-safe inference locking**
* **Context-aware prompt construction**

### 🔹 Caching & Data

* **Redis Stack**

  * Semantic response caching
  * TTL-based eviction
* **Custom similarity thresholds**

### 🔹 Frontend

* **React**
* **Vite**
* **Modern SPA architecture**
* **Deployed via GitHub Pages**

### 🔹 Infrastructure & Deployment

* **Docker (CUDA and CPU specific images)**
* **Kubernetes**

  * GKE (Google Kubernetes Engine)
  * Nautilus HPC (GPU workloads)
* **Node-level GPU scheduling**

### 🔹 Observability & Monitoring

* **Prometheus**

  * Inference latency
  * Token throughput
  * Cache hit/miss ratios
* **Grafana Dashboards**

  * GPU vs CPU performance
  * Load testing results
  * Sustainability metrics (tokens/Watt)

---

## 🚀 Deployment Guides

* **GCP Kubernetes Deployment**
  📁 [`k8s/gcp/README.md`](k8s/gcp/README.md)

* **Nautilus HPC Deployment**
  📁 [`k8s/nautilus/README.md`](k8s/nautilus/README.md)

---

## 🎯 Project Goals

* Build a **production-grade legal LLM system and offer best LLM-Serving with limited constraints**
* Demonstrate **end-to-end AI infra skills**
* Optimize **cost, latency, and sustainability**
* Rigorously **evaluate legal reasoning quality**

---
