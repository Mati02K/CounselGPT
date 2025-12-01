FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# --------------------------------------
# System packages
# --------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

WORKDIR /app

# --------------------------------------
# Install Python dependencies
# --------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

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
