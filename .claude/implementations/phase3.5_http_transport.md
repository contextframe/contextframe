# Phase 3.5: HTTP Transport with SSE Implementation Plan

## Overview

Phase 3.5 adds HTTP transport alongside the existing stdio transport, enabling the MCP server to handle web-based clients with real-time streaming via Server-Sent Events (SSE). This provides a production-ready HTTP API while maintaining full compatibility with all existing tools.

## Timeline: 3-4 days

## Implementation Structure

```
contextframe/mcp/transports/
├── __init__.py
├── stdio.py          # Existing stdio adapter
└── http/
    ├── __init__.py
    ├── adapter.py    # HttpAdapter implementation
    ├── server.py     # FastAPI/Starlette server
    ├── sse.py        # Server-Sent Events
    ├── auth.py       # OAuth 2.1 authentication
    ├── session.py    # Session management
    └── security.py   # CORS, rate limiting
```

## Core Components

### 1. HttpAdapter Class

The `HttpAdapter` extends `TransportAdapter` to provide HTTP-specific functionality:

```python
class HttpAdapter(TransportAdapter):
    """HTTP transport adapter with SSE streaming support."""
    
    def __init__(self, app: FastAPI):
        super().__init__()
        self.app = app
        self._active_streams: Dict[str, SSEStream] = {}
    
    async def send_progress(self, progress: Progress) -> None:
        """Send progress via SSE to all active streams."""
        # Stream progress updates in real-time
    
    async def handle_subscription(self, subscription: Subscription) -> AsyncIterator[Dict[str, Any]]:
        """Stream changes via SSE."""
        # Real-time change streaming
```

### 2. FastAPI/Starlette Server

Main HTTP server implementation:

```python
# server.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="ContextFrame MCP Server")

# MCP endpoints
@app.post("/mcp/v1/initialize")
@app.post("/mcp/v1/tools/list")
@app.post("/mcp/v1/tools/call")
@app.post("/mcp/v1/resources/list")
@app.post("/mcp/v1/resources/read")

# SSE endpoints
@app.get("/mcp/v1/sse/subscribe")
@app.get("/mcp/v1/sse/progress/{operation_id}")
```

### 3. SSE Implementation

Real-time streaming for progress and subscriptions:

```python
# sse.py
class SSEStream:
    """Manages an SSE connection for streaming updates."""
    
    async def send_event(self, event_type: str, data: Any):
        """Send an SSE event."""
        
    async def stream_progress(self, operation_id: str):
        """Stream progress updates for an operation."""
        
    async def stream_changes(self, subscription_id: str):
        """Stream dataset changes for a subscription."""
```

### 4. Authentication & Security

OAuth 2.1 with PKCE for secure API access:

```python
# auth.py
class OAuth2Handler:
    """OAuth 2.1 authentication with PKCE."""
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
    
    async def check_permissions(self, user: Dict, resource: str, action: str) -> bool:
        """Check user permissions for resource access."""
```

## Key Features

### 1. Transport Selection

Server can run with either or both transports:

```python
# Run with stdio only (default)
python -m contextframe.mcp dataset.lance

# Run with HTTP only
python -m contextframe.mcp dataset.lance --transport http --port 8080

# Run with both transports
python -m contextframe.mcp dataset.lance --transport both --port 8080
```

### 2. Streaming Capabilities

- **Progress Updates**: Real-time operation progress via SSE
- **Subscriptions**: Live dataset changes streamed to clients
- **Batch Operations**: Stream results as they complete
- **Long-Running Operations**: Keep clients updated

### 3. HTTP-Specific Features

- **RESTful Endpoints**: Standard HTTP API design
- **Request/Response**: JSON for all non-streaming operations
- **File Uploads**: Support for document upload via multipart
- **Health Checks**: `/health` and `/ready` endpoints
- **API Documentation**: Auto-generated OpenAPI/Swagger

### 4. Security Features

- **Authentication**: OAuth 2.1 with JWT tokens
- **Authorization**: Resource-level permissions
- **CORS**: Configurable cross-origin policies
- **Rate Limiting**: Per-user and global limits
- **Request Validation**: Input sanitization

## Integration Points

### 1. Unified Tool Handling

All existing tools work identically:

```python
# server.py updates
async def create_server(dataset_path: str, transport: str = "stdio"):
    if transport == "http" or transport == "both":
        http_adapter = HttpAdapter(app)
        handler = MessageHandler(dataset, http_adapter)
        
        @app.post("/mcp/v1/tools/call")
        async def call_tool(request: ToolCallRequest):
            return await handler.handle_tool_call(request.dict())
```

### 2. Configuration

Extended configuration for HTTP:

```json
{
    "transport": {
        "type": "http",
        "http": {
            "host": "0.0.0.0",
            "port": 8080,
            "cors": {
                "origins": ["*"],
                "credentials": true
            },
            "auth": {
                "enabled": true,
                "issuer": "https://auth.example.com",
                "audience": "contextframe-mcp"
            },
            "rate_limit": {
                "requests_per_minute": 60,
                "burst": 10
            },
            "ssl": {
                "enabled": false,
                "cert": "/path/to/cert.pem",
                "key": "/path/to/key.pem"
            }
        }
    }
}
```

## API Endpoints

### Core MCP Endpoints

```
POST /mcp/v1/initialize        # Initialize session
POST /mcp/v1/tools/list        # List available tools
POST /mcp/v1/tools/call        # Call a tool
POST /mcp/v1/resources/list    # List resources
POST /mcp/v1/resources/read    # Read a resource
```

### Streaming Endpoints

```
GET  /mcp/v1/sse/subscribe     # Subscribe to changes (SSE)
GET  /mcp/v1/sse/progress/:id  # Stream operation progress (SSE)
POST /mcp/v1/subscriptions     # Manage subscriptions
```

### Utility Endpoints

```
GET  /health                   # Health check
GET  /ready                    # Readiness check
GET  /metrics                  # Prometheus metrics
GET  /openapi.json            # OpenAPI specification
```

## Example Usage

### HTTP Client Example

```python
import httpx
import asyncio
from httpx_sse import aconnect_sse

# Initialize client
async with httpx.AsyncClient() as client:
    # Authenticate
    token = await authenticate(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Call a tool
    response = await client.post(
        "http://localhost:8080/mcp/v1/tools/call",
        json={
            "name": "search_documents",
            "arguments": {"query": "machine learning"}
        },
        headers=headers
    )
    
    # Stream progress for batch operation
    batch_response = await client.post(
        "http://localhost:8080/mcp/v1/tools/call",
        json={
            "name": "batch_enhance",
            "arguments": {"documents": [...]}
        },
        headers=headers
    )
    
    operation_id = batch_response.json()["operation_id"]
    
    # Stream progress via SSE
    async with aconnect_sse(
        client, 
        "GET", 
        f"http://localhost:8080/mcp/v1/sse/progress/{operation_id}",
        headers=headers
    ) as event_source:
        async for sse in event_source.aiter_sse():
            print(f"Progress: {sse.data}")
```

### JavaScript/Browser Example

```javascript
// Subscribe to changes
const eventSource = new EventSource(
    'http://localhost:8080/mcp/v1/sse/subscribe?resource_type=documents',
    { headers: { 'Authorization': `Bearer ${token}` } }
);

eventSource.onmessage = (event) => {
    const change = JSON.parse(event.data);
    console.log('Document changed:', change);
};

// Call a tool
const response = await fetch('http://localhost:8080/mcp/v1/tools/call', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        name: 'add_document',
        arguments: {
            content: 'Document content',
            metadata: { title: 'New Document' }
        }
    })
});
```

## Testing Strategy

### 1. Unit Tests

- HttpAdapter methods
- SSE streaming functionality
- Authentication/authorization
- Rate limiting logic

### 2. Integration Tests

- Full HTTP request/response cycle
- SSE connection management
- Tool execution via HTTP
- Concurrent request handling

### 3. Performance Tests

- Throughput benchmarking
- SSE connection scaling
- Memory usage under load
- Latency measurements

## Migration Guide

For users transitioning from stdio to HTTP:

1. **Configuration**: Update transport settings
2. **Authentication**: Obtain OAuth tokens
3. **Client Updates**: Use HTTP client libraries
4. **Streaming**: Switch from polling to SSE
5. **Error Handling**: Handle HTTP status codes

## Success Criteria

1. **Feature Parity**
   - All 43 tools work via HTTP
   - Identical results to stdio transport
   - No breaking changes

2. **Performance**
   - <50ms latency for simple operations
   - Support 1000+ concurrent SSE connections
   - Efficient streaming for large responses

3. **Security**
   - OAuth 2.1 compliance
   - Secure by default configuration
   - Comprehensive audit logging

4. **Developer Experience**
   - Clear API documentation
   - SDK examples in multiple languages
   - Migration guides and tutorials

## Dependencies

```toml
# pyproject.toml additions
[tool.poetry.dependencies]
fastapi = "^0.104.0"
uvicorn = { version = "^0.24.0", extras = ["standard"] }
sse-starlette = "^1.6.0"
python-jose = { version = "^3.3.0", extras = ["cryptography"] }
httpx = "^0.25.0"
slowapi = "^0.1.9"  # Rate limiting
python-multipart = "^0.0.6"  # File uploads
```

## Next Steps After Phase 3.5

With HTTP transport complete:
1. Finalize Phase 3.6 (Analytics & Performance tools)
2. Production deployment guides
3. Kubernetes manifests and Helm charts
4. Monitoring and observability setup
5. Performance optimization and caching