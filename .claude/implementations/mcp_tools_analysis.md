# MCP Tools Analysis - ContextFrame

This comprehensive guide documents all available MCP tools in the ContextFrame system, organized by category with detailed information about their purpose, usage, and integration.

## Table of Contents

1. [Core Document Tools](#1-core-document-tools)
2. [Batch Operation Tools](#2-batch-operation-tools)
3. [Collection Management Tools](#3-collection-management-tools)
4. [Enhancement Tools](#4-enhancement-tools)
5. [Analytics Tools](#5-analytics-tools)
6. [Monitoring Tools](#6-monitoring-tools)
7. [Subscription Tools](#7-subscription-tools)

---

## 1. Core Document Tools

Located in `contextframe/mcp/tools.py`, these tools provide fundamental CRUD operations for documents.

### 1.1 search_documents

**Purpose**: Search documents using vector, text, or hybrid search methods.

**Input Parameters**:
```json
{
  "query": "string (required)",
  "search_type": "vector | text | hybrid (default: hybrid)",
  "limit": "integer 1-1000 (default: 10)",
  "filter": "SQL filter expression (optional)"
}
```

**Output Format**:
```json
{
  "documents": [
    {
      "uuid": "string",
      "content": "string",
      "metadata": {},
      "score": "float (optional)"
    }
  ],
  "total_count": "integer",
  "search_type_used": "string"
}
```

**Performance Considerations**:
- Vector search requires embedding generation (API call)
- Text search uses Lance's full-text search capabilities
- Hybrid search falls back to text if vector fails
- Filters are applied at the storage layer for efficiency

**Error Handling**:
- `EmbeddingError`: When vector embedding generation fails
- `FilterError`: When SQL filter expression is invalid
- `InvalidSearchType`: When search type is not recognized

### 1.2 add_document

**Purpose**: Add a new document to the dataset with optional chunking and embedding generation.

**Input Parameters**:
```json
{
  "content": "string (required)",
  "metadata": "object (optional)",
  "generate_embedding": "boolean (default: true)",
  "collection": "string (optional)",
  "chunk_size": "integer 100-10000 (optional)",
  "chunk_overlap": "integer 0-1000 (optional)"
}
```

**Output Format**:
```json
{
  "document": {
    "uuid": "string",
    "content": "string",
    "metadata": {}
  }
}
```
Or for chunked documents:
```json
{
  "documents": [...],
  "total_chunks": "integer"
}
```

**Performance Considerations**:
- Chunking is performed synchronously
- Embedding generation requires API call per chunk
- Large documents should use chunking for better retrieval

### 1.3 get_document

**Purpose**: Retrieve a document by its UUID.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "include_content": "boolean (default: true)",
  "include_metadata": "boolean (default: true)",
  "include_embeddings": "boolean (default: false)"
}
```

**Output Format**:
```json
{
  "document": {
    "uuid": "string",
    "content": "string (optional)",
    "metadata": "object (optional)",
    "embedding": "array (optional)"
  }
}
```

**Error Handling**:
- `DocumentNotFound`: When UUID doesn't exist

### 1.4 list_documents

**Purpose**: List documents with pagination and filtering.

**Input Parameters**:
```json
{
  "limit": "integer 1-1000 (default: 100)",
  "offset": "integer >= 0 (default: 0)",
  "filter": "SQL filter expression (optional)",
  "order_by": "SQL order expression (optional)",
  "include_content": "boolean (default: false)"
}
```

**Output Format**:
```json
{
  "documents": [...],
  "total_count": "integer",
  "offset": "integer",
  "limit": "integer"
}
```

### 1.5 update_document

**Purpose**: Update an existing document's content or metadata.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "content": "string (optional)",
  "metadata": "object (optional)",
  "regenerate_embedding": "boolean (default: false)"
}
```

**Implementation Details**:
- Uses atomic delete + add pattern
- Preserves UUID and relationships
- Metadata updates are merged, not replaced

### 1.6 delete_document

**Purpose**: Delete a document from the dataset.

**Input Parameters**:
```json
{
  "document_id": "string (required)"
}
```

**Output Format**:
```json
{
  "deleted": true,
  "document_id": "string"
}
```

---

## 2. Batch Operation Tools

Located in `contextframe/mcp/batch/tools.py`, these tools enable efficient bulk operations.

### 2.1 batch_search

**Purpose**: Execute multiple searches in parallel with progress tracking.

**Input Parameters**:
```json
{
  "queries": [
    {
      "query": "string",
      "search_type": "vector | text | hybrid",
      "limit": "integer",
      "filter": "string"
    }
  ],
  "max_parallel": "integer (default: 10)"
}
```

**Output Format**:
```json
{
  "searches_completed": "integer",
  "searches_failed": "integer",
  "results": [
    {
      "query": "string",
      "success": "boolean",
      "results": [...],
      "count": "integer",
      "error": "string (optional)"
    }
  ],
  "errors": [...]
}
```

**Performance Considerations**:
- Controlled parallelism prevents resource exhaustion
- Each search maintains independent error handling
- Progress reported via transport adapter

### 2.2 batch_add

**Purpose**: Add multiple documents efficiently with atomic transaction support.

**Input Parameters**:
```json
{
  "documents": [
    {
      "content": "string",
      "metadata": "object"
    }
  ],
  "shared_settings": {
    "metadata": "object",
    "generate_embeddings": "boolean"
  },
  "atomic": "boolean (default: false)"
}
```

**Transaction Support**:
- Atomic mode: All succeed or all fail
- Non-atomic: Individual failures don't stop batch
- Shared settings applied to all documents

### 2.3 batch_update

**Purpose**: Update multiple documents by filter or IDs.

**Input Parameters**:
```json
{
  "document_ids": ["string"] | null,
  "filter": "string | null",
  "updates": {
    "metadata_updates": "object",
    "content_template": "string",
    "regenerate_embeddings": "boolean"
  },
  "max_documents": "integer (default: 1000)"
}
```

**Features**:
- Template-based content updates
- Bulk metadata merging
- Batch embedding regeneration

### 2.4 batch_delete

**Purpose**: Delete multiple documents with safety checks.

**Input Parameters**:
```json
{
  "document_ids": ["string"] | null,
  "filter": "string | null",
  "confirm_count": "integer | null",
  "dry_run": "boolean (default: false)"
}
```

**Safety Features**:
- Dry run preview
- Count confirmation
- Detailed deletion report

### 2.5 batch_enhance

**Purpose**: Enhance multiple documents with LLM operations.

**Input Parameters**:
```json
{
  "document_ids": ["string"] | null,
  "filter": "string | null",
  "enhancements": ["context", "tags", "title", "metadata"],
  "purpose": "string",
  "batch_size": "integer (optional)"
}
```

**Enhancement Types**:
- Context: Add explanatory context
- Tags: Generate relevant tags
- Title: Improve document titles
- Metadata: Extract structured data

### 2.6 batch_extract

**Purpose**: Extract content from multiple files/sources.

**Input Parameters**:
```json
{
  "sources": [
    {
      "type": "file | url",
      "path": "string",
      "url": "string"
    }
  ],
  "add_to_dataset": "boolean (default: true)",
  "shared_metadata": "object",
  "collection": "string",
  "continue_on_error": "boolean (default: false)"
}
```

**Supported Formats**:
- Markdown (.md)
- JSON (.json)
- YAML (.yaml, .yml)
- CSV (.csv)
- Plain text (fallback)

### 2.7 batch_export

**Purpose**: Export documents in bulk to various formats.

**Input Parameters**:
```json
{
  "document_ids": ["string"] | null,
  "filter": "string | null",
  "format": "json | jsonl | csv | parquet",
  "output_path": "string",
  "include_embeddings": "boolean (default: false)",
  "chunk_size": "integer (optional)"
}
```

**Export Features**:
- Chunked exports for large datasets
- Format-specific optimizations
- Embedding inclusion option

### 2.8 batch_import

**Purpose**: Import documents from files.

**Input Parameters**:
```json
{
  "source_path": "string",
  "format": "json | jsonl | csv | parquet",
  "mapping": "object (field mappings)",
  "validation": {
    "max_errors": "integer",
    "require_schema_match": "boolean"
  },
  "generate_embeddings": "boolean"
}
```

---

## 3. Collection Management Tools

Located in `contextframe/mcp/collections/tools.py`, these tools manage document collections and hierarchies.

### 3.1 create_collection

**Purpose**: Create a new collection with header and initial configuration.

**Input Parameters**:
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "parent_collection": "string (optional)",
  "template": "string (optional)",
  "metadata": "object (optional)",
  "initial_members": ["string"] (optional)
}
```

**Features**:
- Hierarchical collections via parent_collection
- Template application for standardization
- Automatic relationship management
- Collection header document creation

### 3.2 update_collection

**Purpose**: Update collection properties and membership.

**Input Parameters**:
```json
{
  "collection_id": "string (required)",
  "name": "string (optional)",
  "description": "string (optional)",
  "metadata_updates": "object (optional)",
  "add_members": ["string"] (optional),
  "remove_members": ["string"] (optional)
}
```

**Membership Management**:
- Batch add/remove operations
- Automatic relationship updates
- Member count tracking

### 3.3 delete_collection

**Purpose**: Delete a collection and optionally its members.

**Input Parameters**:
```json
{
  "collection_id": "string (required)",
  "delete_members": "boolean (default: false)",
  "recursive": "boolean (default: false)"
}
```

**Deletion Options**:
- Keep members (remove relationships only)
- Delete members
- Recursive deletion of subcollections

### 3.4 list_collections

**Purpose**: List collections with filtering and statistics.

**Input Parameters**:
```json
{
  "parent_id": "string (optional)",
  "include_empty": "boolean (default: true)",
  "include_stats": "boolean (default: false)",
  "sort_by": "name | created_at | member_count",
  "limit": "integer (default: 100)",
  "offset": "integer (default: 0)"
}
```

**Output Features**:
- Hierarchical structure
- Member statistics
- Size calculations
- Metadata aggregation

### 3.5 move_documents

**Purpose**: Move documents between collections.

**Input Parameters**:
```json
{
  "document_ids": ["string"] (required),
  "source_collection": "string (optional)",
  "target_collection": "string (optional)",
  "update_metadata": "boolean (default: false)"
}
```

**Movement Features**:
- Batch operations
- Metadata inheritance
- Relationship updates

### 3.6 get_collection_stats

**Purpose**: Get detailed statistics for a collection.

**Input Parameters**:
```json
{
  "collection_id": "string (required)",
  "include_subcollections": "boolean (default: false)",
  "include_member_details": "boolean (default: false)"
}
```

**Statistics Provided**:
- Member counts (direct and total)
- Size calculations
- Tag aggregation
- Date ranges
- Member type distribution

---

## 4. Enhancement Tools

Located in `contextframe/mcp/enhancement_tools.py`, these tools use LLM to enhance documents.

### 4.1 enhance_context

**Purpose**: Add context to explain document relevance for a specific purpose.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "purpose": "string (required)",
  "current_context": "string (optional)"
}
```

**Use Cases**:
- Adding domain-specific context
- Explaining document significance
- Improving searchability

### 4.2 extract_metadata

**Purpose**: Extract custom metadata from document using LLM.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "schema": "string (prompt describing what to extract)",
  "format": "json | text (default: json)"
}
```

**Examples**:
- Extract key facts and dates
- Identify entities and relationships
- Generate structured summaries

### 4.3 generate_tags

**Purpose**: Generate relevant tags for a document.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "tag_types": "string (default: 'topics, technologies, concepts')",
  "max_tags": "integer 1-20 (default: 5)"
}
```

### 4.4 improve_title

**Purpose**: Generate or improve document title.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "style": "descriptive | technical | concise (default: descriptive)"
}
```

### 4.5 enhance_for_purpose

**Purpose**: Enhance document with purpose-specific metadata.

**Input Parameters**:
```json
{
  "document_id": "string (required)",
  "purpose": "string (required)",
  "fields": ["context", "tags", "custom_metadata"] (default: all)
}
```

### 4.6 extract_from_file

**Purpose**: Extract content and metadata from various file formats.

**Input Parameters**:
```json
{
  "file_path": "string (required)",
  "add_to_dataset": "boolean (default: true)",
  "generate_embedding": "boolean (default: true)",
  "collection": "string (optional)"
}
```

### 4.7 batch_extract (Directory Processing)

**Purpose**: Extract content from multiple files in a directory.

**Input Parameters**:
```json
{
  "directory": "string (required)",
  "patterns": ["*.md", "*.txt", "*.json"] (default patterns),
  "recursive": "boolean (default: true)",
  "add_to_dataset": "boolean (default: true)",
  "collection": "string (optional)"
}
```

---

## 5. Analytics Tools

Located in `contextframe/mcp/analytics/tools.py`, these tools provide dataset analysis and optimization.

### 5.1 get_dataset_stats

**Purpose**: Get comprehensive dataset statistics including storage, content, and index metrics.

**Input Parameters**:
```json
{
  "include_details": "boolean (default: true)",
  "include_fragments": "boolean (default: true)",
  "sample_size": "integer 100-100000 (optional)"
}
```

**Statistics Provided**:
- Storage metrics (size, fragments, versions)
- Content analysis (types, sizes, dates)
- Index information
- Relationship graph metrics

### 5.2 analyze_usage

**Purpose**: Analyze dataset usage patterns and access frequencies.

**Input Parameters**:
```json
{
  "time_range": "string (e.g., '7d', '24h', '30d')",
  "group_by": "hour | day | week (default: hour)",
  "include_patterns": "boolean (default: true)"
}
```

**Analysis Features**:
- Access frequency heatmaps
- Popular documents
- Query patterns
- User behavior analysis

### 5.3 query_performance

**Purpose**: Analyze query performance and identify optimization opportunities.

**Input Parameters**:
```json
{
  "time_range": "string (default: '7d')",
  "query_type": "vector | text | hybrid | filter (optional)",
  "min_duration_ms": "number (default: 0)"
}
```

**Performance Metrics**:
- Query execution times
- Index utilization
- Scan statistics
- Slow query identification

### 5.4 relationship_analysis

**Purpose**: Analyze document relationships and graph structure.

**Input Parameters**:
```json
{
  "max_depth": "integer 1-10 (default: 3)",
  "relationship_types": ["string"] (optional),
  "include_orphans": "boolean (default: true)"
}
```

**Graph Analysis**:
- Connectivity metrics
- Cluster identification
- Orphaned documents
- Relationship type distribution

### 5.5 optimize_storage

**Purpose**: Optimize dataset storage through compaction and cleanup.

**Input Parameters**:
```json
{
  "operations": ["compact", "vacuum", "reindex"],
  "dry_run": "boolean (default: true)",
  "target_version": "integer (optional)"
}
```

**Optimization Operations**:
- Compact: Merge small fragments
- Vacuum: Remove old versions
- Reindex: Rebuild indexes

### 5.6 index_recommendations

**Purpose**: Get recommendations for index improvements.

**Input Parameters**:
```json
{
  "analyze_queries": "boolean (default: true)",
  "workload_type": "search | analytics | mixed (default: mixed)"
}
```

**Recommendations**:
- Missing index suggestions
- Unused index identification
- Index type optimization
- Configuration tuning

### 5.7 benchmark_operations

**Purpose**: Benchmark dataset operations to measure performance.

**Input Parameters**:
```json
{
  "operations": ["search", "insert", "update", "scan"],
  "sample_size": "integer 1-10000 (default: 100)",
  "concurrency": "integer 1-100 (default: 1)"
}
```

**Benchmark Metrics**:
- Operation throughput
- Latency percentiles
- Resource utilization
- Scalability analysis

### 5.8 export_metrics

**Purpose**: Export dataset metrics for monitoring systems.

**Input Parameters**:
```json
{
  "format": "prometheus | json | csv (default: json)",
  "metrics": ["string"] (optional, default: all)",
  "labels": "object (optional)"
}
```

**Export Formats**:
- Prometheus: For Grafana/Prometheus
- JSON: For custom processing
- CSV: For spreadsheet analysis

---

## 6. Monitoring Tools

Located in `contextframe/mcp/monitoring/tools.py`, these tools track system performance and usage.

### 6.1 get_usage_metrics

**Purpose**: Get usage metrics for documents and queries.

**Input Parameters**:
```json
{
  "start_time": "ISO datetime (default: 1 hour ago)",
  "end_time": "ISO datetime (default: now)",
  "group_by": "hour | day | week (default: hour)",
  "include_details": "boolean (default: false)"
}
```

**Metrics Provided**:
- Query counts and types
- Document access patterns
- Agent activity
- Top documents and queries

### 6.2 get_performance_metrics

**Purpose**: Get performance metrics for MCP operations.

**Input Parameters**:
```json
{
  "operation_type": "string (optional)",
  "minutes": "integer (default: 60)",
  "include_percentiles": "boolean (default: true)"
}
```

**Performance Data**:
- Operation latencies
- Error rates
- Throughput metrics
- Response time percentiles

### 6.3 get_cost_report

**Purpose**: Get cost attribution report for MCP operations.

**Input Parameters**:
```json
{
  "start_time": "ISO datetime (default: 24 hours ago)",
  "end_time": "ISO datetime (default: now)",
  "group_by": "agent | operation | provider (default: agent)",
  "include_projections": "boolean (default: true)"
}
```

**Cost Analysis**:
- LLM API costs
- Storage costs
- Bandwidth costs
- Monthly projections
- Optimization recommendations

### 6.4 get_monitoring_status

**Purpose**: Get overall monitoring system status.

**Output Includes**:
- System health status
- Configuration details
- Buffer statistics
- Active operation counts

### 6.5 export_metrics (Monitoring)

**Purpose**: Export metrics to various formats for external systems.

**Input Parameters**:
```json
{
  "format": "prometheus | json | csv (default: json)",
  "metric_types": ["usage", "performance", "cost", "all"],
  "include_raw": "boolean (default: false)"
}
```

---

## 7. Subscription Tools

Located in `contextframe/mcp/subscriptions/tools.py`, these tools enable real-time change monitoring.

### 7.1 subscribe_changes

**Purpose**: Create a subscription to monitor dataset changes.

**Input Parameters**:
```json
{
  "resource_type": "documents | collections | all (default: all)",
  "filters": "object (optional)",
  "options": {
    "polling_interval": "integer (default: 5)",
    "include_data": "boolean (default: false)",
    "batch_size": "integer (default: 100)"
  }
}
```

**Output Format**:
```json
{
  "subscription_id": "string",
  "poll_token": "string",
  "polling_interval": "integer"
}
```

**Implementation**:
- Polling-based change detection
- Efficient version comparison
- Configurable batch sizes

### 7.2 poll_changes

**Purpose**: Poll for changes since the last poll.

**Input Parameters**:
```json
{
  "subscription_id": "string (required)",
  "poll_token": "string (optional for first poll)",
  "timeout": "integer 0-300 (default: 30)"
}
```

**Long Polling**:
- Waits up to timeout for changes
- Returns immediately if changes available
- Efficient for real-time updates

### 7.3 unsubscribe

**Purpose**: Cancel an active subscription.

**Input Parameters**:
```json
{
  "subscription_id": "string (required)"
}
```

**Cleanup**:
- Stops change monitoring
- Returns final poll token
- Cleans up resources

### 7.4 get_subscriptions

**Purpose**: Get list of active subscriptions.

**Input Parameters**:
```json
{
  "resource_type": "documents | collections | all (optional)"
}
```

**Subscription Info**:
- Active subscription IDs
- Resource types monitored
- Configuration details
- Creation timestamps

---

## Integration Patterns

### Tool Composition

Many operations benefit from combining multiple tools:

1. **Document Enrichment Pipeline**:
   ```
   extract_from_file → add_document → enhance_context → generate_tags
   ```

2. **Collection Migration**:
   ```
   create_collection → batch_search → move_documents → get_collection_stats
   ```

3. **Performance Analysis**:
   ```
   get_dataset_stats → query_performance → index_recommendations → optimize_storage
   ```

### Error Recovery

All tools implement consistent error handling:

1. **Validation Errors**: Return `InvalidParams` with details
2. **Resource Errors**: Return specific errors (e.g., `DocumentNotFound`)
3. **System Errors**: Return `InternalError` with safe error messages

### Performance Best Practices

1. **Batch Operations**: Use batch tools for bulk operations
2. **Filtering**: Apply filters at the storage layer
3. **Projections**: Request only needed fields
4. **Pagination**: Use offset/limit for large result sets
5. **Dry Runs**: Test destructive operations first

### Monitoring Integration

1. **Usage Tracking**: All operations automatically tracked
2. **Performance Metrics**: Latencies recorded for analysis
3. **Cost Attribution**: API calls attributed to agents
4. **Export Options**: Multiple formats for external systems

---

## Conclusion

The ContextFrame MCP tool system provides comprehensive functionality for document management, from basic CRUD operations to advanced analytics and monitoring. The modular design allows for flexible composition of operations while maintaining consistent error handling and performance characteristics.

Key strengths:
- **Scalability**: Batch operations and efficient storage layer
- **Flexibility**: Composable tools for complex workflows
- **Observability**: Built-in monitoring and analytics
- **Safety**: Transactions, dry runs, and validation
- **Integration**: Standard formats and protocols

The tool system continues to evolve with new capabilities being added to support emerging use cases and performance requirements.