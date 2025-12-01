FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including build tools for CUDA compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

WORKDIR /app

# --------------------------------------
# Install Python dependencies
# --------------------------------------
COPY requirements.txt .

# Install llama-cpp-python with CUDA support (must be built from source)
ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=all"
ENV FORCE_CMAKE=1

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade --force-reinstall llama-cpp-python --no-cache-dir && \
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
# Start API
# --------------------------------------
CMD ["gunicorn", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "1", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "600", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
