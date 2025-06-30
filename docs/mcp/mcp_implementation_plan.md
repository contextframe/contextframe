# ContextFrame MCP Implementation Plan

## Overview

Based on comprehensive research, we'll implement a hybrid approach that delivers immediate value through bash scripts while building toward a full MCP server implementation.

## Implementation Phases

### Phase 1: Bash Script Wrappers (Week 1)

Create immediately useful CLI commands that wrap the Python API.

#### Scripts to Create:

1. **contextframe-search**
```bash
#!/bin/bash
# Search documents in a ContextFrame dataset
# Usage: contextframe-search <dataset> <query> [--limit 10] [--type vector|text]
```

2. **contextframe-add**
```bash
#!/bin/bash
# Add documents to a ContextFrame dataset
# Usage: contextframe-add <dataset> <file> [--tags tag1,tag2] [--extract]
```

3. **contextframe-get**
```bash
#!/bin/bash
# Get a document by UUID
# Usage: contextframe-get <dataset> <uuid> [--format json|markdown]
```

4. **contextframe-list**
```bash
#!/bin/bash
# List documents with filters
# Usage: contextframe-list <dataset> [--collection name] [--limit 50]
```

5. **contextframe-enrich**
```bash
#!/bin/bash
# Enrich documents with LLM
# Usage: contextframe-enrich <dataset> <uuid> [--prompt "custom prompt"]
```

6. **contextframe-export**
```bash
#!/bin/bash
# Export dataset or documents
# Usage: contextframe-export <dataset> [--format json|parquet] [--output file]
```

### Phase 2: Basic MCP Server (Week 2-3)

Implement core MCP server with stdio transport.

#### Directory Structure:
```
contextframe/serve/
├── __init__.py
├── mcp_server.py         # Main server class
├── handlers/
│   ├── __init__.py
│   ├── lifecycle.py      # Initialize/shutdown
│   ├── resources.py      # Resource handlers
│   └── tools.py          # Tool handlers
├── transport/
│   ├── __init__.py
│   └── stdio.py          # stdio transport
├── tools/
│   ├── __init__.py
│   ├── search.py         # Search tool
│   ├── crud.py           # CRUD operations
│   └── enrich.py         # Enrichment tool
└── errors.py             # Error handling
```

#### Core Tools:
- `contextframe_search`: Vector/text search
- `contextframe_get`: Retrieve document
- `contextframe_list`: List with filters
- `contextframe_add`: Create document
- `contextframe_update`: Update document
- `contextframe_delete`: Delete document
- `contextframe_enrich`: LLM enrichment

### Phase 3: Advanced MCP Features (Week 4-5)

Add production-ready features.

#### Features to Add:
- HTTP transport with SSE
- Resource subscriptions
- Batch operations
- Collection management
- Performance optimizations
- Comprehensive error handling

### Phase 4: Integration & Polish (Week 6)

#### Tasks:
- NPX-style deployment
- Claude Code integration guide
- Migration guide (scripts → MCP)
- Performance benchmarks
- Security hardening

## Technical Architecture

### MCP Server Design

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

class ContextFrameMCP(Server):
    def __init__(self, dataset_path: str):
        super().__init__("contextframe")
        self.dataset = FrameDataset.open(dataset_path)
        
    async def handle_initialize(self, params):
        return {
            "capabilities": {
                "tools": {},
                "resources": {"subscribe": True},
                "prompts": {}
            }
        }
```

### Tool Schema Example

```python
@server.tool()
async def contextframe_search(
    query: str,
    search_type: Literal["vector", "text", "hybrid"] = "hybrid",
    limit: int = 10,
    collection: Optional[str] = None
) -> str:
    """
    Search documents in the ContextFrame dataset.
    
    Best for: Finding relevant documents based on semantic similarity or text matching
    Not recommended for: Retrieving specific documents by ID (use contextframe_get)
    """
    # Implementation
```

## Success Metrics

### Phase 1 (Bash Scripts):
- All 6 core scripts functional
- < 100ms response time
- Clear help documentation
- Error handling for common cases

### Phase 2 (Basic MCP):
- Stdio transport working
- All 7 core tools implemented
- JSON-RPC compliance
- Basic test coverage

### Phase 3 (Advanced MCP):
- HTTP transport option
- < 100ms query latency
- Subscription support
- 90% test coverage

### Phase 4 (Integration):
- NPX deployment working
- Documentation complete
- Migration guide published
- Security review passed

## Deployment Strategy

### For Bash Scripts:
```bash
# Install scripts
pip install contextframe[cli]

# Use immediately
contextframe-search mydata.lance "relevant documents"
```

### For MCP Server:
```json
{
  "mcpServers": {
    "contextframe": {
      "command": "npx",
      "args": ["-y", "contextframe-mcp"],
      "env": {
        "CONTEXTFRAME_DATASET": "path/to/dataset.lance"
      }
    }
  }
}
```

## Risk Mitigation

1. **Complexity**: Start simple, iterate based on feedback
2. **Performance**: Profile early, optimize based on metrics
3. **Adoption**: Provide clear migration path from scripts
4. **Security**: Follow MCP security best practices
5. **Maintenance**: Comprehensive testing and documentation

## Timeline

- **Week 1**: Bash scripts (immediate value)
- **Week 2-3**: Basic MCP server
- **Week 4-5**: Advanced features
- **Week 6**: Integration and polish

This phased approach ensures we deliver value immediately while building toward a comprehensive MCP implementation.