# Phase 2: Basic MCP Server Implementation

## Overview
Create a Python-based MCP (Model Context Protocol) server with stdio transport that exposes ContextFrame's core functionality through a standardized protocol for LLM integration.

## Timeline
**Week 2 of MCP Implementation (7 days)**

## Architecture

### Core Components

```
contextframe/
├── mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server class
│   ├── transport.py       # Stdio transport implementation
│   ├── handlers.py        # Request handlers
│   ├── tools.py          # Tool definitions
│   ├── resources.py      # Resource definitions
│   ├── schemas.py        # Pydantic schemas
│   └── errors.py         # Error handling
```

### Server Architecture

```python
# High-level design
class ContextFrameMCPServer:
    """MCP server for ContextFrame datasets."""
    
    def __init__(self, dataset_path: str, config: MCPConfig = None):
        self.dataset = FrameDataset.open(dataset_path)
        self.config = config or MCPConfig()
        self.transport = StdioTransport()
        self.tools = ToolRegistry()
        self.resources = ResourceRegistry()
        self._register_capabilities()
    
    async def run(self):
        """Main server loop."""
        await self.transport.connect()
        async for message in self.transport:
            response = await self.handle_message(message)
            await self.transport.send(response)
```

## Implementation Plan

### Day 1-2: Core Infrastructure

#### 1. Transport Layer (`transport.py`)
```python
class StdioTransport:
    """Handles stdio communication for MCP."""
    
    async def connect(self):
        """Initialize stdio streams."""
        
    async def read_message(self) -> dict:
        """Read and parse JSON-RPC message."""
        
    async def send_message(self, message: dict):
        """Send JSON-RPC response."""
        
    async def close(self):
        """Clean shutdown."""
```

#### 2. Message Handler (`handlers.py`)
```python
class MessageHandler:
    """Routes JSON-RPC messages to appropriate handlers."""
    
    async def handle(self, message: dict) -> dict:
        method = message.get("method")
        
        if method == "initialize":
            return await self.handle_initialize(message)
        elif method == "tools/list":
            return await self.handle_tools_list(message)
        elif method == "tools/call":
            return await self.handle_tool_call(message)
        elif method == "resources/list":
            return await self.handle_resources_list(message)
        # ... etc
```

#### 3. Error Handling (`errors.py`)
```python
class MCPError(Exception):
    """Base MCP error with JSON-RPC error codes."""
    
    def to_json_rpc(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

# Standard JSON-RPC errors
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
```

### Day 3-4: Tool Implementation

#### Tool Registry (`tools.py`)
```python
@dataclass
class Tool:
    name: str
    description: str
    inputSchema: dict
    handler: Callable

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        self.register("search_documents", {
            "description": "Search documents using vector, text, or hybrid search",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "search_type": {"enum": ["vector", "text", "hybrid"]},
                    "limit": {"type": "integer", "default": 10},
                    "filter": {"type": "string"}
                },
                "required": ["query"]
            }
        }, self.search_documents)
```

#### Core Tools to Implement

1. **search_documents**
   - Vector search with embedding generation
   - Text search with BM25
   - Hybrid search with fallback
   - SQL filtering support

2. **add_document**
   - Single document addition
   - Optional embedding generation
   - Metadata validation
   - Collection assignment

3. **get_document**
   - Retrieve by UUID
   - Multiple format support
   - Include relationships

4. **list_documents**
   - Pagination support
   - Filtering by metadata
   - Sorting options

5. **delete_document**
   - Safe deletion by UUID
   - Cascade relationship cleanup

6. **update_document**
   - Update content and metadata
   - Regenerate embeddings if needed

### Day 5: Resource System

#### Resource Registry (`resources.py`)
```python
class ResourceRegistry:
    """Manages MCP resources for dataset exploration."""
    
    def list_resources(self) -> list[dict]:
        return [
            {
                "uri": f"contextframe://dataset/info",
                "name": "Dataset Information",
                "description": "Dataset metadata and statistics",
                "mimeType": "application/json"
            },
            {
                "uri": f"contextframe://dataset/schema",
                "name": "Dataset Schema",
                "description": "Arrow schema information",
                "mimeType": "application/json"
            },
            {
                "uri": f"contextframe://collections",
                "name": "Collections",
                "description": "List of document collections",
                "mimeType": "application/json"
            }
        ]
    
    async def read_resource(self, uri: str) -> dict:
        """Read resource content by URI."""
        if uri == "contextframe://dataset/info":
            return await self._get_dataset_info()
        # ... etc
```

### Day 6-7: Testing & Integration

#### 1. Protocol Compliance Tests
```python
# tests/test_mcp_protocol.py
async def test_initialization_handshake():
    """Test MCP initialization sequence."""
    server = ContextFrameMCPServer(test_dataset)
    
    # Send initialize
    response = await server.handle_message({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {}
        },
        "id": 1
    })
    
    assert response["result"]["protocolVersion"] == "0.1.0"
    assert "tools" in response["result"]["capabilities"]
```

#### 2. Integration Tests
- Test with sample MCP client
- Verify tool execution
- Resource reading
- Error handling

#### 3. Performance Benchmarks
- Measure request/response latency
- Test concurrent requests
- Memory usage under load

## Key Design Decisions

### 1. Async Architecture
- All I/O operations are async
- Use `asyncio` for concurrency
- Non-blocking dataset operations

### 2. Schema Validation
- Pydantic for request/response validation
- JSON Schema for tool inputs
- Clear error messages

### 3. Embedding Integration
- Reuse LiteLLMProvider from Phase 1
- Environment-based configuration
- Graceful fallback for missing credentials

### 4. Error Handling
- Map ContextFrame exceptions to MCP errors
- Detailed error messages
- Proper JSON-RPC error codes

## Configuration

### Server Configuration (`mcp_config.json`)
```json
{
  "server": {
    "name": "contextframe",
    "version": "0.1.0"
  },
  "embedding": {
    "provider": "openai",
    "model": "text-embedding-ada-002"
  },
  "limits": {
    "max_results": 1000,
    "max_chunk_size": 10000
  }
}
```

### Client Configuration (for Claude Desktop, etc.)
```json
{
  "mcpServers": {
    "contextframe": {
      "command": "python",
      "args": ["-m", "contextframe.mcp", "/path/to/dataset.lance"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## Usage Examples

### Starting the Server
```bash
# Basic usage
python -m contextframe.mcp /path/to/dataset.lance

# With configuration
python -m contextframe.mcp /path/to/dataset.lance --config mcp_config.json

# With environment variables
CONTEXTFRAME_EMBED_MODEL=text-embedding-3-small \
python -m contextframe.mcp /path/to/dataset.lance
```

### Example Tool Calls

#### Search Documents
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_documents",
    "arguments": {
      "query": "machine learning applications",
      "search_type": "hybrid",
      "limit": 5,
      "filter": "collection = 'research-papers'"
    }
  },
  "id": 1
}
```

#### Add Document
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "add_document",
    "arguments": {
      "content": "# Introduction to MCP\n\nThe Model Context Protocol...",
      "metadata": {
        "title": "MCP Overview",
        "identifier": "mcp-001",
        "collection": "documentation"
      },
      "generate_embedding": true
    }
  },
  "id": 2
}
```

## Success Criteria

### Functional Requirements
- [ ] Server starts and accepts stdio connections
- [ ] Initialization handshake completes successfully
- [ ] All 6 core tools are implemented and functional
- [ ] Resources can be listed and read
- [ ] Proper error handling with JSON-RPC error codes

### Performance Requirements
- [ ] < 100ms response time for simple queries
- [ ] Handle 10+ concurrent requests
- [ ] Memory usage < 500MB for typical datasets

### Integration Requirements
- [ ] Works with Claude Desktop
- [ ] Compatible with other MCP clients
- [ ] Proper shutdown handling

## Next Steps (Phase 3)

After Phase 2 is complete, Phase 3 will add:
- Advanced MCP features (streaming, subscriptions)
- Batch operations
- Collection management tools
- HTTP transport option
- Performance optimizations

## References

- [MCP Specification](https://modelcontextprotocol.io/docs)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [ContextFrame Documentation](../../docs/README.md)
- [Phase 1 Implementation](../../contextframe/scripts/README.md)