FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (no build tools needed - using pre-built wheels!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

WORKDIR /app

# --------------------------------------
# Install Python dependencies
# --------------------------------------
COPY requirements.txt .

# Install llama-cpp-python from pre-built CUDA wheel (MUCH faster!)
# Using CUDA 12.4 pre-built wheels from abetlen's repository
RUN pip install --upgrade pip && \
    pip install llama-cpp-python \
        --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 && \
    pip install --no-cache-dir -r requirements.txt

# --------------------------------------
# Copy application source
# --------------------------------------
COPY app.py cache.py metrics.py modelclass.py prometheus.yml ./

# Copy the llm module (your model loaders)
COPY llm ./llm/

# Copy your prompt file
COPY prompt.py .

# --------------------------------------
# Model directory will be mounted externally
# --------------------------------------
VOLUME ["/models"]

# --------------------------------------
# Gunicorn API port
# --------------------------------------
EXPOSE 8000

# --------------------------------------
# Start API with 1 worker (GPU doesn't support multiple workers safely)
# CUDA contexts don't fork well, causing memory conflicts
# For better throughput, scale horizontally with more pods instead
# --------------------------------------
CMD ["gunicorn", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "1", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "600", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
