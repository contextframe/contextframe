# HTTP as Primary Transport for MCP Server

## Overview

As of the current MCP specification, HTTP is the primary transport protocol for the Model Context Protocol. SSE (Server-Sent Events) is an optional enhancement for specific streaming use cases only.

## Transport Hierarchy

1. **HTTP (Primary)**: Simple request/response pattern for all MCP operations
2. **SSE (Optional)**: Only for real-time streaming scenarios like progress updates and subscriptions
3. **stdio**: For local/embedded usage

## HTTP-First Implementation

### Primary Endpoint

The main MCP endpoint handles all standard operations with simple JSON responses:

```
POST /mcp/v1/jsonrpc
Content-Type: application/json
Accept: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {...},
  "id": 1
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {...},
  "id": 1
}
```

### Optional SSE Endpoints

SSE is ONLY used for specific streaming scenarios:

1. **Operation Progress** - `/mcp/v1/sse/progress/{operation_id}`
   - Used when tracking long-running operations
   - Optional - clients can poll instead

2. **Subscriptions** - `/mcp/v1/sse/subscribe`
   - Used for real-time dataset change notifications
   - Optional - clients can poll for changes

## Migration from SSE-Focused Usage

If you were previously using SSE for all operations:

### Before (SSE-focused):
```python
# Opening SSE connection for all operations
async with sse_client.connect() as stream:
    response = await stream.send_request({"method": "tools/list"})
```

### After (HTTP-first):
```python
# Simple HTTP request
response = requests.post(
    "http://localhost:8000/mcp/v1/jsonrpc",
    json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}
)
```

## When to Use Each Transport

### Use HTTP for:
- Tool calls
- Resource operations
- Initialization
- All synchronous operations
- Any request expecting a single response

### Use SSE only for:
- Tracking progress of long-running operations
- Subscribing to real-time dataset changes
- Scenarios requiring server-to-client push

## Configuration

Default transport should be HTTP:

```python
# Recommended
config = MCPConfig(transport="http")

# Only use SSE when specifically needed
# for streaming scenarios
```

## Client Implementation Guidelines

1. **Start with HTTP**: Always implement HTTP client first
2. **Add SSE selectively**: Only add SSE support for specific features
3. **Graceful degradation**: SSE features should be optional enhancements

## Performance Considerations

- HTTP has lower overhead for single request/response
- SSE only beneficial for multiple server-initiated messages
- HTTP supports better caching and proxying
- HTTP has simpler authentication and rate limiting

## Summary

The MCP server implementation prioritizes HTTP as the primary transport, with SSE available as an optional enhancement for specific streaming use cases. This aligns with the latest MCP specification and provides better compatibility, simpler implementation, and clearer separation of concerns.