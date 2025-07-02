# Text Embeddings Inference (TEI) Setup Guide

This guide provides detailed instructions for setting up Text Embeddings Inference (TEI) to use with ContextFrame.

## Overview

TEI is a high-performance inference server for text embeddings that requires separate deployment from your Python application. Unlike pip-installable embedding libraries, TEI runs as a standalone service that your application communicates with via HTTP.

## Prerequisites

### Hardware Requirements

#### GPU Setup (Recommended)
- **NVIDIA GPU** with CUDA compute capability ≥ 7.5
- **CUDA** version 12.2 or higher
- **Docker** with NVIDIA Container Toolkit
- **Supported GPUs**:
  - RTX 4000 series (Ada Lovelace)
  - RTX 3000 series (Ampere) 
  - A100, A30, A40, A10
  - H100 (Hopper)
  - T4, RTX 2000 series (Turing) - Flash Attention disabled

**Note**: V100, Titan V, and GTX 1000 series are NOT supported.

#### CPU Setup (Alternative)
- Any modern x86_64 or ARM processor
- Docker installed
- At least 8GB RAM (varies by model)

### Software Requirements
- Docker or Docker Desktop
- Python 3.10+ with ContextFrame installed
- Network access to download models (first run only)

## Installation Methods

### Method 1: Docker (Recommended)

#### GPU Deployment

1. **Install NVIDIA Container Toolkit**:
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify installation
docker run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

2. **Run TEI with GPU**:
```bash
# Basic setup
docker run --gpus all -p 8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5

# With specific GPU
docker run --gpus '"device=0"' -p 8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5

# Production setup with restart
docker run -d --name tei-server \
  --gpus all \
  --restart unless-stopped \
  -p 8080:80 \
  -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-large-en-v1.5 \
  --max-concurrent-requests 512
```

#### CPU Deployment

```bash
# Basic CPU setup
docker run -p 8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7 \
  --model-id BAAI/bge-base-en-v1.5

# With performance tuning
docker run -d --name tei-server-cpu \
  --restart unless-stopped \
  -p 8080:80 \
  -v $PWD/tei-data:/data \
  --cpus="4.0" \
  --memory="8g" \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7 \
  --model-id BAAI/bge-base-en-v1.5 \
  --max-concurrent-requests 100
```

### Method 2: Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  tei:
    image: ghcr.io/huggingface/text-embeddings-inference:1.7
    container_name: tei-server
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./tei-data:/data
    environment:
      # Optional: Set Hugging Face token for gated models
      # - HUGGING_FACE_HUB_TOKEN=your_token_here
    command: >
      --model-id BAAI/bge-base-en-v1.5
      --max-concurrent-requests 512
      --max-client-batch-size 32
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 90s

  # Optional: CPU-only variant
  tei-cpu:
    image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.7
    container_name: tei-server-cpu
    profiles: ["cpu"]  # Only starts with --profile cpu
    restart: unless-stopped
    ports:
      - "8081:80"
    volumes:
      - ./tei-data-cpu:/data
    command: >
      --model-id BAAI/bge-small-en-v1.5
      --max-concurrent-requests 100
```

Run with:
```bash
# GPU version (default)
docker-compose up -d

# CPU version
docker-compose --profile cpu up -d

# View logs
docker-compose logs -f tei
```

### Method 3: Kubernetes

For production deployments:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tei-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tei
  template:
    metadata:
      labels:
        app: tei
    spec:
      containers:
      - name: tei
        image: ghcr.io/huggingface/text-embeddings-inference:1.7
        args:
          - "--model-id"
          - "BAAI/bge-base-en-v1.5"
          - "--max-concurrent-requests"
          - "512"
        ports:
        - containerPort: 80
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
        volumeMounts:
        - name: model-cache
          mountPath: /data
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: tei-model-cache
---
apiVersion: v1
kind: Service
metadata:
  name: tei-service
spec:
  selector:
    app: tei
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

## Model Selection

### Recommended Models by Use Case

| Use Case | Model | Dimensions | Notes |
|----------|-------|------------|-------|
| General English | `BAAI/bge-base-en-v1.5` | 768 | Best balance |
| High Quality | `BAAI/bge-large-en-v1.5` | 1024 | Better accuracy |
| Fast/Lightweight | `BAAI/bge-small-en-v1.5` | 384 | 3x faster |
| Multilingual | `BAAI/bge-m3` | 1024 | 100+ languages |
| Code | `jinaai/jina-embeddings-v2-base-code` | 768 | Programming languages |
| Long Context | `jinaai/jina-embeddings-v2-base-en` | 768 | 8K token context |

### Memory Requirements

Approximate memory usage per model:

- Small models (384 dims): ~500MB
- Base models (768 dims): ~1.5GB  
- Large models (1024 dims): ~3GB
- XL models (1536 dims): ~5GB

Add 2-4GB for TEI runtime overhead.

## Verification and Testing

### 1. Check Server Health

```bash
# Health check
curl http://localhost:8080/health

# Get model info
curl http://localhost:8080/info
```

### 2. Test Embedding Generation

```bash
# Test single embedding
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["Hello, world!"]}'

# Test batch embedding
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["Text 1", "Text 2", "Text 3"]}'
```

### 3. Python Test Script

```python
import requests
import numpy as np

# Test TEI connection
def test_tei_server(url="http://localhost:8080"):
    try:
        # Health check
        health = requests.get(f"{url}/health")
        print(f"✅ Server health: {health.status_code}")
        
        # Get info
        info = requests.get(f"{url}/info")
        if info.status_code == 200:
            print(f"✅ Model info: {info.json()}")
        
        # Test embedding
        response = requests.post(
            f"{url}/embed",
            json={"inputs": ["Test embedding"]}
        )
        if response.status_code == 200:
            embedding = response.json()[0]
            print(f"✅ Embedding shape: {len(embedding)} dimensions")
            print(f"✅ First 5 values: {embedding[:5]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_tei_server()
```

## Performance Tuning

### GPU Optimization

```bash
# Enable Flash Attention (if supported)
docker run --gpus all -p 8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5 \
  --flash-attention

# Increase batch size for better throughput
docker run --gpus all -p 8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5 \
  --max-client-batch-size 64 \
  --max-batch-tokens 16384
```

### CPU Optimization

```bash
# Use multiple CPU cores
docker run -p 8080:80 -v $PWD/tei-data:/data \
  --cpus="8.0" \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7 \
  --model-id BAAI/bge-base-en-v1.5 \
  --max-concurrent-requests 200
```

## Monitoring

### Prometheus Metrics

TEI exposes metrics at `/metrics`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'tei'
    static_configs:
      - targets: ['localhost:8080']
```

Key metrics:
- `tei_request_duration_seconds` - Request latency
- `tei_request_queue_size` - Pending requests
- `tei_batch_size` - Average batch size

### Logging

```bash
# View logs
docker logs -f tei-server

# Save logs
docker logs tei-server > tei.log 2>&1
```

## Troubleshooting

### Common Issues

1. **CUDA Error**: Ensure NVIDIA drivers and CUDA toolkit are properly installed
2. **Out of Memory**: Use smaller model or reduce batch size
3. **Slow Performance**: Enable Flash Attention, increase batch size
4. **Connection Refused**: Check firewall rules and port binding
5. **Model Download Fails**: Set `HUGGING_FACE_HUB_TOKEN` for gated models

### Debug Mode

```bash
# Run with debug logging
docker run --gpus all -p 8080:80 -v $PWD/tei-data:/data \
  -e RUST_LOG=debug \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5
```

## Security Considerations

### Authentication

For production, add authentication:

```bash
# Using Nginx proxy
server {
    listen 443 ssl;
    server_name tei.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        auth_basic "TEI Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Network Security

```bash
# Bind to localhost only
docker run --gpus all -p 127.0.0.1:8080:80 -v $PWD/tei-data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.7 \
  --model-id BAAI/bge-base-en-v1.5
```

## Additional Resources

- [TEI Official Documentation](https://huggingface.co/docs/text-embeddings-inference)
- [TEI GitHub Repository](https://github.com/huggingface/text-embeddings-inference)
- [Supported Models List](https://huggingface.co/docs/text-embeddings-inference/en/supported_models)
- [TEI Docker Hub](https://github.com/huggingface/text-embeddings-inference/pkgs/container/text-embeddings-inference)

## Next Steps

Once TEI is running, you can use it with ContextFrame:

```python
from contextframe.embed import create_embedder

# Create embedder
embedder = create_embedder(
    model="BAAI/bge-base-en-v1.5",
    provider_type="tei",
    api_base="http://localhost:8080"
)

# Embed documents
results = embedder.embed_batch(["Document 1", "Document 2"])
```

For more ContextFrame integration examples, see the [TEI embeddings demo](../../examples/tei_embeddings_demo.py).