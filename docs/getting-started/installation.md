# Installation

ContextFrame provides flexible installation options to suit different use cases, from simple Python library usage to full-featured deployments with external connectors and MCP server support.

## Requirements

- **Python**: 3.10, 3.11, or 3.12
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Storage**: Depends on dataset size (Lance uses efficient columnar storage)

## Quick Install

For basic ContextFrame functionality:

```bash
pip install contextframe
```

Or using uv (recommended for faster installation):

```bash
uv pip install contextframe
```

## Installation Options

### Core Package

The base package includes:
- FrameDataset and FrameRecord classes
- Lance storage backend
- Basic search and query capabilities
- Schema validation

```bash
pip install contextframe
```

### With Embeddings Support

To use vector embeddings and semantic search:

```bash
pip install "contextframe[embeddings]"
```

This includes:
- OpenAI embeddings support
- Vector index creation
- KNN search capabilities

### With External Connectors

To import data from external sources:

```bash
# All connectors
pip install "contextframe[connectors]"

# Or install specific connectors
pip install "contextframe[github]"      # GitHub integration
pip install "contextframe[notion]"      # Notion integration
pip install "contextframe[slack]"       # Slack integration
pip install "contextframe[gdrive]"      # Google Drive
pip install "contextframe[discord]"     # Discord
```

### With MCP Server

For AI agent integration via Model Context Protocol:

```bash
pip install "contextframe[mcp]"
```

### Development Installation

For contributing or development work:

```bash
# Clone the repository
git clone https://github.com/contextframe/contextframe
cd contextframe

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Or using uv
uv pip install -e ".[dev]"
```

### Full Installation

For all features:

```bash
pip install "contextframe[all]"
```

## Environment Setup

### API Keys

ContextFrame uses environment variables for API keys:

```bash
# For embeddings (if using OpenAI)
export OPENAI_API_KEY="your-api-key"

# For external connectors
export GITHUB_TOKEN="your-github-token"
export NOTION_TOKEN="your-notion-integration-token"
export SLACK_BOT_TOKEN="your-slack-bot-token"
# ... etc
```

### Using Doppler (Recommended)

ContextFrame recommends Doppler for environment management:

```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login and setup project
doppler login
doppler setup

# Run commands with Doppler
doppler run -- python your_script.py
```

### Using .env Files

Alternatively, create a `.env` file:

```bash
# .env
OPENAI_API_KEY=your-api-key
GITHUB_TOKEN=your-github-token
NOTION_TOKEN=your-notion-token
```

Then load in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Verifying Installation

Test your installation:

```python
# test_install.py
import contextframe
from contextframe import FrameDataset, FrameRecord

# Check version
print(f"ContextFrame version: {contextframe.__version__}")

# Create a test dataset
dataset = FrameDataset.create("test.lance")

# Create and add a test record
record = FrameRecord.create(
    title="Test Document",
    content="This is a test document to verify installation."
)
dataset.add(record)

# Verify the record was added
print(f"Dataset contains {len(dataset)} records")
```

Run the test:

```bash
python test_install.py
```

Expected output:
```
ContextFrame version: X.Y.Z
Dataset contains 1 records
```

## Platform-Specific Notes

### macOS

If you encounter issues with PyArrow on Apple Silicon:

```bash
# Install with conda for better compatibility
conda install -c conda-forge pyarrow
```

### Windows

Ensure you have Visual C++ 14.0 or greater installed:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Linux

On Ubuntu/Debian, you may need to install additional dependencies:

```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
```

## Docker Installation

For containerized deployments:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install ContextFrame
RUN pip install contextframe[all]

# Copy your application
COPY . .

CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t contextframe-app .
docker run -v $(pwd)/data:/app/data contextframe-app
```

## Cloud Storage Configuration

ContextFrame supports cloud storage backends:

### AWS S3

```python
dataset = FrameDataset(
    "s3://my-bucket/datasets/my-dataset.lance",
    storage_options={
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY",
        "region": "us-east-1"
    }
)
```

### Google Cloud Storage

```python
dataset = FrameDataset(
    "gs://my-bucket/datasets/my-dataset.lance",
    storage_options={
        "service_account": "path/to/service-account.json"
    }
)
```

### Azure Blob Storage

```python
dataset = FrameDataset(
    "az://my-container/datasets/my-dataset.lance",
    storage_options={
        "account_name": "YOUR_ACCOUNT_NAME",
        "account_key": "YOUR_ACCOUNT_KEY"
    }
)
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'contextframe'**
   - Ensure you're in the correct Python environment
   - Try: `pip show contextframe` to verify installation

2. **PyArrow compatibility issues**
   - Ensure PyArrow version matches ContextFrame requirements
   - Try: `pip install --upgrade pyarrow`

3. **Permission errors with datasets**
   - Ensure write permissions for dataset location
   - Check file ownership: `ls -la *.lance`

4. **Memory errors with large datasets**
   - Use batch operations: `dataset.add_many(docs, batch_size=1000)`
   - Enable memory mapping in Lance

### Getting Help

- Check the [FAQ](../faq.md)
- See [Troubleshooting Guide](../troubleshooting.md)
- Visit [GitHub Issues](https://github.com/contextframe/contextframe/issues)
- Join our [Discord Community](https://discord.gg/contextframe)

## Next Steps

Now that you have ContextFrame installed:

1. Follow the [First Steps](first-steps.md) guide
2. Explore [Basic Examples](basic-examples.md)
3. Learn about [Core Concepts](../core-concepts/architecture.md)
4. Try the [Quick Start Tutorial](../quickstart.md)