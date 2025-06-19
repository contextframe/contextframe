# Phase 3 MCP Implementation Plan

## Overview

Phase 3 enhances the MCP server with advanced features while maintaining full support for BOTH stdio and HTTP transports. Every new tool and feature will work seamlessly with both transport mechanisms.

## Core Principles

- **Transport Agnostic Design**: All features implemented at the handler/tool level, automatically available to both stdio and HTTP clients
- **Backward Compatibility**: No breaking changes to existing stdio implementation
- **Performance Parity**: Consistent performance across transports where applicable

## Key Components

### 1. Transport-Agnostic Architecture

- **Shared Tool Registry**: All tools work with any transport
- **Unified Message Handler**: Single handler serves both transports
- **Abstract Streaming**: Streaming that adapts to transport type
- **Transport Factory**: Easy switching between stdio/HTTPwhwh

### 2. Batch Operations

Execute multiple operations in a single request with atomic transaction support:

- Progress updates via result structure (not just SSE)
- Atomic operations with rollback support
- Works identically in both transports

### 3. Collection Management

Comprehensive tools for organizing and managing document collections:

- Collection CRUD operations
- Document movement between collections
- Collection templates and hierarchies
- Collection statistics and analytics

### 4. Subscription System (Transport-Aware)

Watch for dataset changes with transport-appropriate mechanisms:

- **HTTP**: Real-time SSE streaming
- **Stdio**: Polling-based with change tokens
- Unified subscription management interface

### 5. Advanced Search & Analytics

Enhanced search capabilities with aggregation and analysis:

- Faceted search with counts
- Similarity-based searching
- Search result aggregation
- Performance analytics

### 6. Performance Optimization

Tools for optimizing dataset performance:

- Dataset optimization
- Custom index creation
- Query performance analysis
- Cache management

## New Tools (26 Total)

### Batch Tools (8)
- `batch_search` - Execute multiple searches in one call
- `batch_add` - Add multiple documents with shared settings
- `batch_update` - Update many documents by filter
- `batch_delete` - Delete documents matching criteria
- `batch_enhance` - Enhance multiple documents together
- `batch_extract` - Extract from multiple sources
- `batch_export` - Export multiple documents
- `batch_import` - Import multiple documents

### Collection Tools (6)
- `create_collection` - Initialize with metadata and header
- `update_collection` - Modify collection properties
- `delete_collection` - Remove collection and optionally members
- `list_collections` - Get all collections with stats
- `move_documents` - Move docs between collections
- `get_collection_stats` - Detailed collection analytics

### Subscription Tools (4)
- `subscribe_changes` - Watch for document changes
- `unsubscribe` - Stop watching changes
- `poll_changes` - Get changes since last poll (stdio-friendly)
- `get_subscriptions` - List active subscriptions

### Analytics Tools (4)
- `aggregate_search` - Search with grouping/counting
- `similarity_search` - Find similar documents
- `faceted_search` - Search with facet counts
- `analyze_usage` - Usage analytics

### Performance Tools (4)
- `optimize_dataset` - Run dataset optimization
- `create_index` - Create custom indexes
- `analyze_performance` - Get query performance stats
- `cache_control` - Manage caching settings

## Implementation Timeline

### Phase 3.1: Core Infrastructure (Week 1)
1. Refactor current architecture for transport abstraction
2. Create base classes for transport-agnostic features
3. Implement streaming abstraction layer
4. Add progress reporting framework
5. Ensure all existing tools remain compatible

### Phase 3.2: Batch Operations (Week 2)
1. Implement batch tool schemas and handlers
2. Add transaction support at dataset level
3. Create batch validation framework
4. Implement progress reporting for batches
5. Test with both stdio and HTTP transports

### Phase 3.3: Collection Management (Week 3)
1. Design collection tool schemas
2. Implement collection CRUD operations
3. Add collection statistics and analytics
4. Create collection template system
5. Ensure backward compatibility

### Phase 3.4: Subscriptions (Week 4)
1. Design transport-aware subscription system
2. Implement change detection at dataset level
3. Create polling mechanism for stdio
4. Add SSE streaming for HTTP
5. Build subscription management tools

### Phase 3.5: HTTP Transport (Week 5)
1. Add HTTP transport alongside stdio
2. Implement SSE for streaming
3. Add authentication (OAuth 2.1)
4. Create session management
5. Add security features (CORS, rate limiting)

### Phase 3.6: Performance & Testing (Week 6)
1. Add caching layer (works with both transports)
2. Implement connection pooling
3. Create comprehensive test suite
4. Performance benchmarking
5. Documentation and examples

## Technical Architecture

### Directory Structure
```
contextframe/mcp/
├── core/
│   ├── transport.py      # Transport abstraction
│   ├── handlers.py       # Unified handlers
│   └── streaming.py      # Streaming abstraction
├── transports/
│   ├── stdio.py          # Stdio transport
│   └── http/
│       ├── server.py     # FastAPI/Starlette app
│       ├── auth.py       # OAuth 2.1
│       └── sse.py        # Server-sent events
├── tools/
│   ├── batch.py          # Batch operations
│   ├── collections.py    # Collection management
│   ├── subscriptions.py  # Change subscriptions
│   ├── analytics.py      # Search analytics
│   └── performance.py    # Performance tools
└── utils/
    ├── cache.py          # Caching layer
    └── pool.py           # Connection pooling
```

### Transport Abstraction Design

```python
class TransportAdapter(ABC):
    """Base class for transport adapters"""
    
    @abstractmethod
    async def send_progress(self, progress: Progress) -> None:
        """Send progress update (SSE for HTTP, structured response for stdio)"""
    
    @abstractmethod
    async def handle_subscription(self, subscription: Subscription) -> None:
        """Handle subscription (streaming for HTTP, polling for stdio)"""

class StdioAdapter(TransportAdapter):
    """Stdio implementation - returns structured data"""
    
class HttpAdapter(TransportAdapter):
    """HTTP implementation - uses SSE for streaming"""
```

### Example: Transport-Agnostic Batch Handler

```python
async def batch_search_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute multiple searches in one call - works with both transports"""
    queries = args["queries"]
    results = []
    
    for i, query in enumerate(queries):
        # Report progress (transport handles how to send it)
        await transport.send_progress({
            "operation": "batch_search",
            "current": i + 1,
            "total": len(queries),
            "status": f"Searching: {query['query']}"
        })
        
        result = await search_documents(query)
        results.append(result)
    
    return {
        "batch_results": results,
        "total_processed": len(queries)
    }
```

### Subscription Design

```python
# Stdio-friendly polling approach
{
    "name": "poll_changes",
    "arguments": {
        "since_token": "2024-01-15T10:30:00Z",
        "limit": 100
    }
}

# Returns changes and new token
{
    "changes": [...],
    "next_token": "2024-01-15T10:35:00Z",
    "has_more": false
}
```

## Success Criteria

- ✅ All 26 new tools work with stdio transport
- ✅ All 26 new tools work with HTTP transport  
- ✅ No breaking changes to existing stdio implementation
- ✅ Consistent behavior across transports
- ✅ Clear documentation for transport differences
- ✅ Performance metrics:
  - Batch operations with <2s overhead
  - <100ms query latency with caching
  - Support for 1000+ concurrent HTTP connections
- ✅ Production security for HTTP (OAuth 2.1, CORS, rate limiting)
- ✅ Comprehensive test coverage for both transports

## Configuration

```json
{
    "transport": "stdio",  // or "http"
    "http": {
        "host": "0.0.0.0",
        "port": 8080,
        "auth": {
            "enabled": true,
            "provider": "oauth2"
        }
    },
    "batch": {
        "max_size": 100,
        "timeout": 30,
        "transaction_mode": "atomic"
    },
    "subscriptions": {
        "poll_interval": 5,     // for stdio
        "max_subscribers": 100,
        "change_retention": 3600
    },
    "cache": {
        "enabled": true,
        "ttl": 300,
        "backend": "memory"  // or "redis"
    },
    "performance": {
        "connection_pool_size": 10,
        "max_concurrent_operations": 50
    }
}
```

## Dependencies

- **Core**: FastAPI/Starlette (HTTP only), pydantic
- **Auth**: python-jose, httpx-oauth
- **Caching**: redis (optional)
- **Monitoring**: prometheus-client
- **Testing**: pytest-asyncio, httpx

This plan ensures complete feature parity between transports while enabling advanced capabilities for production deployments.