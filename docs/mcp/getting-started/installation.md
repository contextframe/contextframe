# Installation Guide

This guide covers all installation options for the ContextFrame MCP server, from quick setup to production deployment.

## System Requirements

### Minimum Requirements

- **Python**: 3.10, 3.11, or 3.12
- **Memory**: 2GB RAM
- **Storage**: 1GB free space (plus dataset storage)
- **OS**: Linux, macOS, or Windows (WSL2 recommended)

### Recommended for Production

- **Python**: 3.11+ (better performance)
- **Memory**: 8GB+ RAM
- **Storage**: SSD with sufficient space for datasets
- **OS**: Linux (Ubuntu 22.04 LTS or similar)

## Installation Methods

### 1. PyPI Installation (Recommended)

The simplest way to install ContextFrame with MCP server:

```bash
# Basic installation
pip install contextframe[mcp]

# With all optional dependencies
pip install contextframe[mcp,monitoring,auth]

# For development
pip install contextframe[mcp,dev]
```

Verify installation:
```bash
contextframe-mcp --version
# contextframe-mcp 0.1.0
```

### 2. Docker Installation

For containerized deployments:

```bash
# Pull the latest image
docker pull contextframe/mcp-server:latest

# Run with default settings
docker run -p 8000:8000 contextframe/mcp-server

# Run with custom configuration
docker run -p 8000:8000 \
  -v /path/to/config:/config \
  -v /path/to/data:/data \
  -e CONTEXTFRAME_CONFIG=/config/mcp.yaml \
  contextframe/mcp-server
```

Docker Compose example:
```yaml
version: '3.8'

services:
  mcp-server:
    image: contextframe/mcp-server:latest
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
      - ./config:/config
    environment:
      - CONTEXTFRAME_DATASET_PATH=/data/dataset.lance
      - CONTEXTFRAME_API_KEY=${API_KEY}
    restart: unless-stopped
```

### 3. From Source

For development or customization:

```bash
# Clone the repository
git clone https://github.com/greyhaven-ai/contextframe.git
cd contextframe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[mcp,dev]"

# Run tests to verify
pytest tests/mcp/
```

### 4. Using UV (Fast Python Package Manager)

For faster installation with UV:

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install ContextFrame with UV
uv pip install contextframe[mcp]

# Or in development mode
uv pip install -e ".[mcp,dev]"
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Install ContextFrame
pip install contextframe[mcp]
```

### macOS

```bash
# Using Homebrew
brew install python@3.11

# Install ContextFrame
pip3 install contextframe[mcp]
```

### Windows

#### Option 1: WSL2 (Recommended)

```bash
# In WSL2 Ubuntu
sudo apt-get update
sudo apt-get install -y python3-pip

pip install contextframe[mcp]
```

#### Option 2: Native Windows

```powershell
# Install Python from python.org
# Then in PowerShell:
pip install contextframe[mcp]
```

## Post-Installation Setup

### 1. Initialize a Dataset

Create your first dataset:

```bash
# Create a new dataset
contextframe-mcp init-dataset ~/contextframe-data/my-dataset.lance

# Verify dataset
contextframe-mcp validate-dataset ~/contextframe-data/my-dataset.lance
```

### 2. Create Configuration

Generate a default configuration:

```bash
# Generate config file
contextframe-mcp generate-config > contextframe-mcp.yaml

# Edit as needed
nano contextframe-mcp.yaml
```

### 3. Test the Installation

Start the server and run health check:

```bash
# Start server
contextframe-mcp serve --config contextframe-mcp.yaml

# In another terminal, check health
curl http://localhost:8000/health
```

## Dependency Management

### Core Dependencies

- `lance`: Columnar storage format
- `fastapi`: HTTP server framework
- `pydantic`: Data validation
- `numpy`: Numerical operations
- `typer`: CLI framework

### Optional Dependencies

Install based on your needs:

```bash
# For monitoring
pip install contextframe[monitoring]  # Adds: prometheus-client, opentelemetry

# For advanced auth
pip install contextframe[auth]  # Adds: python-jose, passlib

# For cloud storage
pip install contextframe[cloud]  # Adds: boto3, google-cloud-storage, azure-storage

# All extras
pip install contextframe[all]
```

## Upgrading

### From PyPI

```bash
# Upgrade to latest version
pip install --upgrade contextframe[mcp]

# Upgrade to specific version
pip install contextframe[mcp]==0.2.0
```

### Docker

```bash
# Pull latest image
docker pull contextframe/mcp-server:latest

# Or specific version
docker pull contextframe/mcp-server:0.2.0
```

## Uninstallation

### Remove PyPI Installation

```bash
# Uninstall package
pip uninstall contextframe

# Remove configuration files (optional)
rm -rf ~/.contextframe/
```

### Remove Docker

```bash
# Stop and remove container
docker stop contextframe-mcp
docker rm contextframe-mcp

# Remove image
docker rmi contextframe/mcp-server:latest
```

## Troubleshooting Installation

### Common Issues

#### Python Version Mismatch

```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m pip install contextframe[mcp]
```

#### Permission Errors

```bash
# Install for current user only
pip install --user contextframe[mcp]

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install contextframe[mcp]
```

#### Missing System Dependencies

```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# On macOS
xcode-select --install
```

### Verification Steps

1. Check installation:
```bash
pip show contextframe
contextframe-mcp --help
```

2. Test import:
```python
python -c "import contextframe.mcp; print('Success!')"
```

3. Run built-in tests:
```bash
contextframe-mcp test-installation
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get running in 5 minutes
- [Configuration Guide](../configuration/index.md) - Configure for your needs
- [Security Setup](../configuration/security.md) - Enable authentication
- [Production Deployment](../guides/production-deployment.md) - Scale for production