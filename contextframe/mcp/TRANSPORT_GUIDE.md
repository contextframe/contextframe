# MCP Transport Guide

## Transport Protocol Priority

As of the current MCP specification, the recommended transport protocols are:

1. **HTTP (Primary)** - Simple request/response for all standard operations
2. **stdio** - For local/embedded integrations
3. **SSE** - Optional enhancement for specific streaming scenarios only

## HTTP Transport (Recommended)

The HTTP transport is the primary and recommended way to interact with the MCP server. It provides:

- Simple request/response pattern
- Better compatibility with existing infrastructure
- Easier authentication and authorization
- Standard HTTP caching and proxying support
- Lower overhead for single operations

### Starting the Server

```python
from contextframe.mcp import ContextFrameMCPServer, MCPConfig

# HTTP is now the default transport
config = MCPConfig(
    server_name="my-contextframe-server",
    http_host="localhost",
    http_port=8080
)

server = ContextFrameMCPServer("path/to/dataset", config)
await server.run()
```

### Client Usage

See `http_client_example.py` for a complete example. Basic pattern:

```python
# Standard HTTP POST to /mcp/v1/jsonrpc
response = requests.post(
    "http://localhost:8080/mcp/v1/jsonrpc",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "search", "arguments": {"query": "test"}},
        "id": 1
    }
)
result = response.json()
```

## SSE (Server-Sent Events) - Optional

SSE is available as an optional enhancement for specific use cases:

### When to Use SSE

Only use SSE for:
- Progress tracking of long-running operations (`/mcp/v1/sse/progress/{id}`)
- Real-time dataset change subscriptions (`/mcp/v1/sse/subscribe`)

### When NOT to Use SSE

Do not use SSE for:
- Standard tool calls
- Resource operations
- Any operation expecting a single response

## stdio Transport

The stdio transport is still supported for:
- Local command-line tools
- Embedded integrations
- Development and testing

### Usage

```python
config = MCPConfig(transport="stdio")
```

## Migration from SSE-Focused Implementation

If you have existing code that uses SSE for all operations:

### Old Pattern (Deprecated)
```python
# Opening SSE connection for everything
async with sse_client.stream() as conn:
    response = await conn.send_and_receive(request)
```

### New Pattern (Recommended)
```python
# Simple HTTP request
response = requests.post(url, json=request)
```

## Transport Selection Guide

| Use Case | Recommended Transport | Why |
|----------|----------------------|-----|
| Web API | HTTP | Standard REST-like interface |
| Tool calls | HTTP | Single request/response |
| Resource reads | HTTP | Cacheable, simple |
| Progress tracking | HTTP + SSE (optional) | SSE only for the progress stream |
| Real-time updates | HTTP + SSE (optional) | SSE only for subscriptions |
| CLI tools | stdio | Direct process communication |
| Embedded usage | stdio | No network overhead |

## Configuration Examples

### HTTP Only (Recommended)
```python
config = MCPConfig(
    transport="http",
    http_host="0.0.0.0",
    http_port=8080
)
```

### HTTP with Optional SSE
The HTTP transport automatically includes SSE endpoints.
Clients can choose to use them only when needed.

### Local Development
```python
config = MCPConfig(
    transport="stdio"  # For local CLI usage
)
```

## Best Practices

1. **Default to HTTP**: Always use HTTP unless you have a specific reason not to
2. **Use SSE Sparingly**: Only for actual streaming needs
3. **Design for HTTP**: Structure your operations to work well with request/response
4. **Cache When Possible**: HTTP allows standard caching mechanisms
5. **Monitor Performance**: HTTP has better observability tooling

## Summary

The MCP server prioritizes HTTP as the primary transport protocol. SSE remains available as an optional feature for specific streaming scenarios, but should not be the default choice for general operations.