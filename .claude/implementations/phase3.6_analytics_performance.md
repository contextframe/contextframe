# Phase 3.6: Analytics & Performance Tools Implementation Plan

## Overview

Phase 3.6 adds 8 analytics and performance tools to provide insights into dataset usage, query patterns, and optimization opportunities. These tools help users understand and optimize their ContextFrame deployments.

## Timeline: 2-3 days

## Implementation Structure

```
contextframe/mcp/analytics/
├── __init__.py
├── stats.py           # Dataset statistics and metrics
├── analyzer.py        # Query and performance analysis
├── optimizer.py       # Storage and index optimization
└── tools.py          # Tool implementations
```

## Tools to Implement

### 1. Analytics Tools (4 tools)

#### `get_dataset_stats`
- **Purpose**: Comprehensive dataset statistics
- **Returns**:
  - Total documents, collections, size
  - Document type distribution
  - Metadata field usage
  - Embedding coverage
  - Version history stats
  - Relationship graph metrics

#### `analyze_usage`
- **Purpose**: Usage patterns and access analytics
- **Parameters**:
  - `time_range`: Period to analyze
  - `group_by`: Hour, day, week
  - `include_queries`: Include query patterns
- **Returns**:
  - Access frequency by document/collection
  - Query patterns and types
  - Popular search terms
  - User access patterns (if tracked)

#### `query_performance`
- **Purpose**: Analyze query performance
- **Parameters**:
  - `time_range`: Analysis period
  - `query_type`: vector, text, hybrid, filter
  - `min_duration`: Minimum query time to include
- **Returns**:
  - Slow queries with explanations
  - Query type distribution
  - Filter efficiency analysis
  - Optimization recommendations

#### `relationship_analysis`
- **Purpose**: Analyze document relationships
- **Parameters**:
  - `max_depth`: How deep to traverse
  - `relationship_types`: Types to analyze
  - `include_orphans`: Include unconnected docs
- **Returns**:
  - Relationship graph statistics
  - Clustering coefficients
  - Connected components
  - Orphaned documents
  - Circular dependencies

### 2. Performance Tools (4 tools)

#### `optimize_storage`
- **Purpose**: Optimize Lance dataset storage
- **Parameters**:
  - `operations`: ["compact", "vacuum", "reindex"]
  - `dry_run`: Preview changes
  - `target_version`: Optimize to specific version
- **Returns**:
  - Space reclaimed
  - Fragments consolidated
  - Performance improvements
  - Optimization log

#### `index_recommendations`
- **Purpose**: Suggest index improvements
- **Parameters**:
  - `analyze_queries`: Recent queries to analyze
  - `workload_type`: "search", "analytics", "mixed"
- **Returns**:
  - Missing index suggestions
  - Redundant index identification
  - Index usage statistics
  - Implementation commands

#### `benchmark_operations`
- **Purpose**: Benchmark key operations
- **Parameters**:
  - `operations`: ["search", "insert", "update", "scan"]
  - `sample_size`: Number of operations
  - `concurrency`: Parallel operations
- **Returns**:
  - Operation latencies (p50, p90, p99)
  - Throughput metrics
  - Resource utilization
  - Comparison with baselines

#### `export_metrics`
- **Purpose**: Export analytics for monitoring
- **Parameters**:
  - `format`: "prometheus", "json", "csv"
  - `metrics`: Specific metrics to export
  - `labels`: Additional labels
- **Returns**:
  - Formatted metrics
  - Timestamp
  - Ready for monitoring systems

## Architecture Patterns

### 1. StatsCollector Base Class
```python
class StatsCollector:
    """Base class for collecting dataset statistics."""
    
    async def collect_stats(self) -> Dict[str, Any]:
        """Collect all statistics."""
        stats = {
            "basic": await self._collect_basic_stats(),
            "content": await self._collect_content_stats(),
            "performance": await self._collect_performance_stats(),
            "relationships": await self._collect_relationship_stats()
        }
        return stats
```

### 2. Query Analyzer
```python
class QueryAnalyzer:
    """Analyze query patterns and performance."""
    
    def __init__(self, dataset: FrameDataset):
        self.dataset = dataset
        self.query_log = []  # In production, use persistent storage
    
    async def analyze_query(self, query: str, duration: float):
        """Analyze a single query."""
        # Extract query features
        # Identify optimization opportunities
        # Track patterns
```

### 3. Storage Optimizer
```python
class StorageOptimizer:
    """Optimize Lance dataset storage."""
    
    async def compact(self, dry_run: bool = True):
        """Compact dataset fragments."""
        # Use Lance's optimize operations
        # Track space savings
        # Report improvements
```

## Integration Points

### 1. With Existing Tools
- Query performance integrates with search tools
- Storage optimization works with batch operations
- Analytics complement subscription monitoring

### 2. Transport Considerations
- All tools work with stdio transport
- Ready for HTTP streaming when added
- Metrics export designed for monitoring integration

## Testing Strategy

### 1. Unit Tests
- Mock dataset statistics
- Test metric calculations
- Verify optimization logic

### 2. Integration Tests
- Real dataset analysis
- Performance benchmarking
- Storage optimization verification

### 3. Performance Tests
- Analytics overhead measurement
- Optimization impact testing

## Example Usage

### Get Dataset Statistics
```python
result = await get_dataset_stats({
    "include_details": True,
    "calculate_sizes": True
})

# Returns:
{
    "total_documents": 10000,
    "total_collections": 25,
    "storage_size_mb": 256.5,
    "avg_document_size": 2650,
    "embedding_coverage": 0.95,
    "version_count": 142,
    "relationships": {
        "total": 3500,
        "types": {
            "child_of": 2000,
            "references": 1500
        }
    }
}
```

### Analyze Query Performance
```python
result = await query_performance({
    "time_range": "7d",
    "min_duration": 100  # ms
})

# Returns:
{
    "slow_queries": [
        {
            "query": "complex filter expression",
            "avg_duration_ms": 250,
            "count": 45,
            "recommendation": "Add index on metadata.category"
        }
    ],
    "query_distribution": {
        "vector": 0.6,
        "text": 0.3,
        "hybrid": 0.1
    }
}
```

### Optimize Storage
```python
result = await optimize_storage({
    "operations": ["compact", "vacuum"],
    "dry_run": False
})

# Returns:
{
    "space_reclaimed_mb": 45.2,
    "fragments_before": 150,
    "fragments_after": 12,
    "duration_seconds": 8.5,
    "version_created": 143
}
```

## Success Criteria

1. **Comprehensive Analytics**
   - Complete dataset insights
   - Actionable recommendations
   - Performance visibility

2. **Effective Optimization**
   - Measurable performance gains
   - Safe storage operations
   - Clear improvement metrics

3. **Tool Integration**
   - Works with all transports
   - Complements existing tools
   - Production-ready metrics

## Next Steps After Phase 3.6

With all 43 tools complete:
1. Phase 3.5: Add HTTP transport with SSE
2. Performance testing at scale
3. Production deployment guides
4. Integration examples