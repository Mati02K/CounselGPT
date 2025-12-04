FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install system dependencies
# We need python3 and git/curl (for uv/pip operations if needed, though uv is copied)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

WORKDIR /app

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Create venv
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# --------------------------------------
# Install Python dependencies
# --------------------------------------
COPY requirements.txt .

# Install llama-cpp-python from pre-built CUDA wheel
# Using CUDA 12.4 pre-built wheels from abetlen's repository
RUN uv pip install --no-cache \
    llama-cpp-python \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

RUN uv pip install --no-cache -r requirements.txt

# --------------------------------------
# Copy application source
# --------------------------------------
COPY app.py cache.py metrics.py modelclass.py prompt.py ./

# Copy the llm module (your model loaders)
COPY llm ./llm/

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
# --------------------------------------
CMD ["gunicorn", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "1", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "600", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
