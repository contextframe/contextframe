# Quick Start Guide

Get the ContextFrame MCP server running in 5 minutes! This guide will walk you through installation, basic configuration, and your first MCP operations.

## Prerequisites

- Python 3.10+ or Docker
- Basic understanding of REST APIs
- A ContextFrame dataset (we'll create one if you don't have one)

## Installation

Choose your preferred installation method:

### Option 1: Using pip

```bash
# Install the ContextFrame package with MCP server
pip install contextframe[mcp]

# Verify installation
contextframe-mcp --version
```

### Option 2: Using Docker

```bash
# Pull the MCP server image
docker pull contextframe/mcp-server:latest

# Run the server
docker run -p 8000:8000 contextframe/mcp-server
```

### Option 3: From source

```bash
# Clone the repository
git clone https://github.com/greyhaven-ai/contextframe.git
cd contextframe

# Install in development mode
pip install -e ".[mcp,dev]"
```

## Starting the Server

### Basic HTTP Server

Start the MCP server with default settings:

```bash
# Start on default port 8000
contextframe-mcp serve

# Or specify a custom port
contextframe-mcp serve --port 3000

# Enable development mode with auto-reload
contextframe-mcp serve --dev
```

You should see:
```
INFO:     Started ContextFrame MCP server on http://0.0.0.0:8000
INFO:     API documentation at http://0.0.0.0:8000/docs
INFO:     MCP endpoint at http://0.0.0.0:8000/mcp/v1
```

### Stdio Mode (for local integrations)

For direct integration with AI agents that support stdio:

```bash
# Start in stdio mode
contextframe-mcp stdio

# Or with a specific dataset
contextframe-mcp stdio --dataset-path /path/to/dataset.lance
```

## Your First MCP Operation

### 1. Check Server Health

Verify the server is running:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "transport": "http",
  "tools_available": 43
}
```

### 2. List Available Tools

See what operations are available:

```bash
curl http://localhost:8000/mcp/v1/tools
```

This returns all 43 available tools with their descriptions and parameters.

### 3. Create Your First Document

Let's create a document using the MCP protocol:

```bash
curl -X POST http://localhost:8000/mcp/v1/tools/document_create \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "content": "# My First Document\n\nThis is my first document in ContextFrame!",
      "metadata": {
        "title": "My First Document",
        "type": "markdown",
        "tags": ["quickstart", "demo"]
      }
    }
  }'
```

Response:
```json
{
  "result": {
    "id": "doc_abc123",
    "dataset_id": "default",
    "message": "Document created successfully"
  }
}
```

### 4. Search for Documents

Now let's search for our document:

```bash
curl -X POST http://localhost:8000/mcp/v1/tools/search_documents \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "first document",
      "limit": 5
    }
  }'
```

## Using with AI Agents

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "contextframe": {
      "command": "contextframe-mcp",
      "args": ["stdio"],
      "env": {
        "DATASET_PATH": "/path/to/your/dataset.lance"
      }
    }
  }
}
```

### Python Client

```python
from contextframe.mcp import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Create a document
doc_id = client.document_create(
    content="# Project Notes\n\nImportant project information...",
    metadata={"project": "alpha", "type": "notes"}
)

# Search documents
results = client.search_documents(
    query="project information",
    limit=10
)

# Get collection stats
stats = client.collection_stats(collection_id="default")
print(f"Documents: {stats['document_count']}")
print(f"Total size: {stats['total_size_bytes']:,} bytes")
```

### Using with curl

For quick testing and scripting:

```bash
# Create a collection
curl -X POST http://localhost:8000/mcp/v1/tools/collection_create \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "name": "research-papers",
      "description": "Academic research papers"
    }
  }'

# List collections
curl -X POST http://localhost:8000/mcp/v1/tools/collection_list \
  -H "Content-Type: application/json" \
  -d '{"params": {}}'
```

## Configuration Basics

### Environment Variables

```bash
# Set the default dataset path
export CONTEXTFRAME_DATASET_PATH=/data/my-dataset.lance

# Enable development mode
export CONTEXTFRAME_DEV_MODE=true

# Set custom host and port
export CONTEXTFRAME_HOST=0.0.0.0
export CONTEXTFRAME_PORT=3000

# Enable API key authentication
export CONTEXTFRAME_API_KEY=your-secret-key
```

### Configuration File

Create a `contextframe-mcp.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8000
  
dataset:
  path: /data/my-dataset.lance
  
security:
  enabled: true
  api_key: ${CONTEXTFRAME_API_KEY}
  
monitoring:
  enabled: true
  level: INFO
```

## What's Next?

Now that you have the MCP server running:

1. **[Explore Core Concepts](../concepts/overview.md)** - Understand how MCP works
2. **[Review API Reference](../api/tools.md)** - See all available tools
3. **[Configure Security](../configuration/security.md)** - Set up authentication
4. **[Try Examples](../cookbook/index.md)** - Real-world usage patterns
5. **[Integrate with AI](../guides/agent-integration.md)** - Connect your agents

## Troubleshooting

### Server won't start

```bash
# Check if port is already in use
lsof -i :8000

# Try a different port
contextframe-mcp serve --port 3001
```

### Can't connect to server

```bash
# Verify server is running
curl http://localhost:8000/health

# Check firewall settings
# Ensure the port is open
```

### Dataset not found

```bash
# Create a new dataset
contextframe-mcp init-dataset /path/to/new/dataset.lance

# Or specify existing dataset
contextframe-mcp serve --dataset-path /path/to/existing.lance
```

## Getting Help

- Check the [FAQ](../reference/faq.md)
- Review [error codes](../reference/errors.md)
- Ask in [GitHub Discussions](https://github.com/greyhaven-ai/contextframe/discussions)
- Report issues on [GitHub](https://github.com/greyhaven-ai/contextframe/issues)