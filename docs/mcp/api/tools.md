# MCP Tools API Reference

Complete reference documentation for all 43 tools available in the ContextFrame MCP server.

## Tool Categories

### [Document Operations](#document-operations)
Core CRUD operations for managing documents
- [`document_create`](#document_create) - Create new document
- [`document_get`](#document_get) - Retrieve document by ID
- [`document_update`](#document_update) - Update existing document
- [`document_delete`](#document_delete) - Delete document
- [`document_exists`](#document_exists) - Check if document exists
- [`document_list`](#document_list) - List all documents
- [`document_create_batch`](#document_create_batch) - Create multiple documents
- [`document_update_batch`](#document_update_batch) - Update multiple documents
- [`document_delete_batch`](#document_delete_batch) - Delete multiple documents

### [Search Operations](#search-operations)
Advanced search capabilities
- [`search_documents`](#search_documents) - Text, vector, or hybrid search
- [`search_similar`](#search_similar) - Find similar documents
- [`search_by_metadata`](#search_by_metadata) - Filter by metadata
- [`search_within_collection`](#search_within_collection) - Collection-scoped search
- [`search_with_filters`](#search_with_filters) - Advanced filtering
- [`search_stream`](#search_stream) - Streaming search results

### [Collection Management](#collection-management)
Organize documents into collections
- [`collection_create`](#collection_create) - Create new collection
- [`collection_get`](#collection_get) - Get collection details
- [`collection_update`](#collection_update) - Update collection
- [`collection_delete`](#collection_delete) - Delete collection
- [`collection_list`](#collection_list) - List all collections
- [`collection_add_documents`](#collection_add_documents) - Add documents to collection
- [`collection_remove_documents`](#collection_remove_documents) - Remove documents from collection
- [`collection_list_documents`](#collection_list_documents) - List documents in collection
- [`collection_stats`](#collection_stats) - Get collection statistics

### [Analytics Tools](#analytics-tools)
Usage statistics and insights
- [`dataset_stats`](#dataset_stats) - Overall dataset statistics
- [`search_analytics`](#search_analytics) - Search usage patterns
- [`usage_metrics`](#usage_metrics) - API usage metrics
- [`cost_estimate`](#cost_estimate) - Estimate operation costs
- [`performance_metrics`](#performance_metrics) - Performance statistics

### [Import/Export Tools](#importexport-tools)
Bulk data operations
- [`import_documents`](#import_documents) - Bulk import from file
- [`export_documents`](#export_documents) - Bulk export to file
- [`import_from_url`](#import_from_url) - Import from remote source
- [`export_to_cloud`](#export_to_cloud) - Export to cloud storage
- [`import_status`](#import_status) - Check import progress
- [`export_status`](#export_status) - Check export progress

### [System Tools](#system-tools)
Health and management
- [`health_check`](#health_check) - Server health status
- [`list_tools`](#list_tools) - List available tools
- [`get_tool_info`](#get_tool_info) - Get tool details
- [`validate_dataset`](#validate_dataset) - Validate dataset integrity
- [`optimize_dataset`](#optimize_dataset) - Optimize performance
- [`clear_cache`](#clear_cache) - Clear server cache
- [`server_info`](#server_info) - Server configuration info

### [Advanced Tools](#advanced-tools)
Specialized operations
- [`create_embedding`](#create_embedding) - Generate embeddings
- [`reindex_documents`](#reindex_documents) - Rebuild search indexes
- [`backup_dataset`](#backup_dataset) - Create dataset backup
- [`restore_dataset`](#restore_dataset) - Restore from backup

---

## Document Operations

### document_create

Create a new document in the dataset.

**Parameters:**
```json
{
  "id": "string (optional)",          // Custom document ID
  "content": "string (required)",      // Document content
  "metadata": "object (optional)",     // Custom metadata
  "embeddings": "array (optional)",    // Pre-computed embeddings
  "collection_id": "string (optional)", // Add to collection
  "upsert": "boolean (optional)"       // Update if exists (default: false)
}
```

**Returns:**
```json
{
  "id": "doc_abc123",
  "created": true,
  "message": "Document created successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/v1/tools/document_create \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "content": "# Introduction to Machine Learning\n\nMachine learning is...",
      "metadata": {
        "title": "ML Introduction",
        "author": "John Doe",
        "tags": ["ml", "tutorial"]
      }
    }
  }'
```

### document_get

Retrieve a document by its ID.

**Parameters:**
```json
{
  "id": "string (required)",           // Document ID
  "include_embeddings": "boolean",     // Include embeddings (default: false)
  "include_content": "boolean"         // Include content (default: true)
}
```

**Returns:**
```json
{
  "id": "doc_abc123",
  "content": "# Introduction to Machine Learning...",
  "metadata": {
    "title": "ML Introduction",
    "author": "John Doe",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

### document_update

Update an existing document.

**Parameters:**
```json
{
  "id": "string (required)",           // Document ID
  "content": "string (optional)",      // New content
  "metadata": "object (optional)",     // New/updated metadata
  "merge_metadata": "boolean",         // Merge vs replace metadata (default: true)
  "update_embeddings": "boolean"       // Regenerate embeddings (default: true)
}
```

**Returns:**
```json
{
  "id": "doc_abc123",
  "updated": true,
  "message": "Document updated successfully"
}
```

### document_delete

Delete a document from the dataset.

**Parameters:**
```json
{
  "id": "string (required)",           // Document ID
  "permanent": "boolean"               // Hard delete (default: false)
}
```

**Returns:**
```json
{
  "id": "doc_abc123",
  "deleted": true,
  "message": "Document deleted successfully"
}
```

### document_exists

Check if a document exists.

**Parameters:**
```json
{
  "id": "string (required)"            // Document ID
}
```

**Returns:**
```json
{
  "exists": true,
  "id": "doc_abc123"
}
```

### document_list

List documents with optional filtering.

**Parameters:**
```json
{
  "limit": "integer",                  // Max results (default: 100)
  "offset": "integer",                 // Skip results (default: 0)
  "collection_id": "string",           // Filter by collection
  "metadata_filter": "object",         // Filter by metadata
  "sort_by": "string",                 // Sort field (default: "created_at")
  "sort_order": "string"               // "asc" or "desc" (default: "desc")
}
```

**Returns:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "metadata": {...}
    }
  ],
  "total_count": 1523,
  "offset": 0,
  "limit": 100
}
```

### document_create_batch

Create multiple documents in a single operation.

**Parameters:**
```json
{
  "documents": [                       // Array of documents
    {
      "content": "string",
      "metadata": "object",
      "id": "string (optional)"
    }
  ],
  "collection_id": "string",           // Add all to collection
  "upsert": "boolean",                 // Update if exists
  "batch_size": "integer"              // Process in batches (default: 100)
}
```

**Returns:**
```json
{
  "created": 95,
  "updated": 5,
  "failed": 0,
  "total": 100,
  "document_ids": ["doc_1", "doc_2", ...]
}
```

---

## Search Operations

### search_documents

Search documents using text, vector, or hybrid search.

**Parameters:**
```json
{
  "query": "string (required)",        // Search query
  "search_type": "string",             // "text", "vector", "hybrid" (default: "hybrid")
  "limit": "integer",                  // Max results (default: 10)
  "offset": "integer",                 // Skip results (default: 0)
  "collection_id": "string",           // Search within collection
  "metadata_filter": "object",         // Filter by metadata
  "min_score": "number",               // Minimum relevance score
  "rerank": "boolean"                  // Rerank results (default: false)
}
```

**Returns:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "content": "...",
      "metadata": {...},
      "score": 0.95,
      "highlights": ["matching text"]
    }
  ],
  "total_count": 42,
  "query": "machine learning",
  "execution_time_ms": 23
}
```

**Example:**
```python
# Text search
results = client.search_documents(
    query="neural networks",
    search_type="text",
    limit=20
)

# Vector (semantic) search
results = client.search_documents(
    query="How do transformers work?",
    search_type="vector",
    limit=10
)

# Hybrid search (combines text and vector)
results = client.search_documents(
    query="BERT architecture",
    search_type="hybrid",
    metadata_filter={"type": "paper"}
)
```

### search_similar

Find documents similar to a given document.

**Parameters:**
```json
{
  "document_id": "string",             // Reference document ID
  "limit": "integer",                  // Max results (default: 10)
  "min_similarity": "number",          // Min similarity score (0-1)
  "collection_id": "string",           // Search within collection
  "exclude_source": "boolean"          // Exclude reference doc (default: true)
}
```

**Returns:**
```json
{
  "similar_documents": [
    {
      "id": "doc_456",
      "similarity": 0.92,
      "metadata": {...}
    }
  ],
  "source_document_id": "doc_123",
  "total_found": 15
}
```

### search_by_metadata

Search using metadata filters with SQL-like syntax.

**Parameters:**
```json
{
  "filters": "object (required)",      // Filter conditions
  "limit": "integer",                  // Max results
  "offset": "integer",                 // Skip results
  "sort_by": "string",                 // Sort field
  "sort_order": "string"               // "asc" or "desc"
}
```

**Filter Examples:**
```json
// Exact match
{"type": "paper"}

// Multiple conditions (AND)
{"type": "paper", "year": 2024}

// Operators
{"year": {"$gte": 2020}}
{"tags": {"$contains": "ml"}}
{"author": {"$in": ["Smith", "Jones"]}}
{"title": {"$regex": ".*learning.*"}}
```

---

## Collection Management

### collection_create

Create a new collection.

**Parameters:**
```json
{
  "name": "string (required)",         // Collection name
  "description": "string",             // Collection description
  "metadata": "object",                // Custom metadata
  "id": "string"                       // Custom ID (optional)
}
```

**Returns:**
```json
{
  "id": "coll_abc123",
  "name": "Research Papers",
  "created": true
}
```

### collection_add_documents

Add documents to a collection.

**Parameters:**
```json
{
  "collection_id": "string (required)", // Collection ID
  "document_ids": "array (required)",   // Document IDs to add
  "position": "string"                  // Position in collection
}
```

**Returns:**
```json
{
  "collection_id": "coll_abc123",
  "added": 25,
  "already_present": 5,
  "not_found": 0
}
```

### collection_stats

Get detailed statistics for a collection.

**Parameters:**
```json
{
  "collection_id": "string (required)"  // Collection ID
}
```

**Returns:**
```json
{
  "id": "coll_abc123",
  "name": "Research Papers",
  "document_count": 1523,
  "total_size_bytes": 15728640,
  "created_at": "2024-01-01T00:00:00Z",
  "last_updated": "2024-01-15T12:00:00Z",
  "metadata": {...}
}
```

---

## Analytics Tools

### dataset_stats

Get comprehensive dataset statistics.

**Parameters:**
```json
{
  "include_collections": "boolean",     // Include collection stats
  "include_storage": "boolean"          // Include storage details
}
```

**Returns:**
```json
{
  "total_documents": 10523,
  "total_collections": 42,
  "storage_size_bytes": 1073741824,
  "index_size_bytes": 268435456,
  "unique_metadata_keys": ["type", "author", "year"],
  "document_size_stats": {
    "min": 100,
    "max": 50000,
    "avg": 2500,
    "median": 2000
  }
}
```

### usage_metrics

Get API usage metrics.

**Parameters:**
```json
{
  "time_range": "string",              // "hour", "day", "week", "month"
  "group_by": "string"                 // "tool", "user", "hour"
}
```

**Returns:**
```json
{
  "time_range": "day",
  "metrics": {
    "total_requests": 15234,
    "unique_users": 42,
    "by_tool": {
      "search_documents": 8523,
      "document_create": 2341
    },
    "avg_response_time_ms": 45,
    "error_rate": 0.001
  }
}
```

---

## Import/Export Tools

### import_documents

Import documents from various formats.

**Parameters:**
```json
{
  "source": "string (required)",       // File path or URL
  "format": "string",                  // "json", "csv", "parquet"
  "collection_id": "string",           // Target collection
  "mapping": "object",                 // Field mapping
  "batch_size": "integer",             // Import batch size
  "on_error": "string"                 // "skip", "abort" (default: "skip")
}
```

**Returns:**
```json
{
  "import_id": "imp_123",
  "status": "in_progress",
  "processed": 500,
  "total": 1000,
  "errors": []
}
```

### export_documents

Export documents to various formats.

**Parameters:**
```json
{
  "format": "string (required)",       // "json", "csv", "parquet"
  "destination": "string",             // File path or URL
  "document_ids": "array",             // Specific documents
  "collection_id": "string",           // Export collection
  "filters": "object",                 // Metadata filters
  "include_embeddings": "boolean"      // Include embeddings
}
```

**Returns:**
```json
{
  "export_id": "exp_123",
  "status": "completed",
  "documents_exported": 1523,
  "file_size_bytes": 10485760,
  "destination": "/exports/data.json"
}
```

---

## System Tools

### health_check

Check server health and status.

**Parameters:** None

**Returns:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "transport": "http",
  "dataset": {
    "connected": true,
    "document_count": 10523
  }
}
```

### list_tools

List all available tools.

**Parameters:**
```json
{
  "category": "string",                // Filter by category
  "include_schema": "boolean"          // Include input schemas
}
```

**Returns:**
```json
{
  "tools": [
    {
      "name": "search_documents",
      "category": "search",
      "description": "Search documents using text, vector, or hybrid search",
      "input_schema": {...}
    }
  ],
  "total_count": 43
}
```

---

## Error Handling

All tools return structured errors:

```json
{
  "error": {
    "type": "ValidationError",
    "code": "INVALID_PARAMETER",
    "message": "Parameter 'query' is required",
    "details": {
      "parameter": "query",
      "provided": null,
      "expected": "string"
    }
  }
}
```

Common error codes:
- `INVALID_PARAMETER` - Invalid input parameters
- `NOT_FOUND` - Resource not found
- `DUPLICATE_ID` - ID already exists
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `UNAUTHORIZED` - Authentication failed
- `FORBIDDEN` - Insufficient permissions
- `INTERNAL_ERROR` - Server error

## Rate Limits

Default rate limits per tool category:

| Category | Requests/Min | Burst |
|----------|-------------|-------|
| Search | 100 | 200 |
| Document | 50 | 100 |
| Collection | 30 | 60 |
| Import/Export | 10 | 20 |
| Analytics | 20 | 40 |
| System | 100 | 200 |

## Next Steps

- [Integration Examples](../cookbook/index.md) - Real-world usage
- [Error Reference](../reference/errors.md) - Complete error codes
- [Performance Guide](../guides/performance.md) - Optimization tips