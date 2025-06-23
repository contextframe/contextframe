# Phase 4.1: Production Monitoring Implementation Plan

## Overview

This phase implements comprehensive monitoring capabilities for the MCP server, enabling production-grade observability and cost tracking.

## Architecture

### Core Components

1. **MetricsCollector** - Central metrics aggregation
2. **UsageTracker** - Document and query usage tracking
3. **PerformanceMonitor** - Response time and throughput monitoring
4. **CostCalculator** - LLM API and storage cost attribution
5. **MetricsExporter** - Export to various monitoring systems

### Data Storage

Metrics will be stored in:
- **In-memory**: Recent metrics (last hour) for fast access
- **Lance dataset**: Historical metrics in dedicated tables
- **Export targets**: Prometheus, CloudWatch, etc.

## Implementation Details

### 1. Context Usage Metrics

Track how documents are accessed and used:

```python
class UsageTracker:
    """Track document access patterns and query statistics."""
    
    async def track_document_access(
        self,
        document_id: str,
        operation: str,  # read, search_hit, update, delete
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record document access event."""
        
    async def track_query(
        self,
        query: str,
        query_type: str,  # vector, text, hybrid, sql
        result_count: int,
        execution_time_ms: float,
        agent_id: str | None = None
    ) -> None:
        """Record query execution."""
        
    async def get_usage_stats(
        self,
        start_time: datetime,
        end_time: datetime,
        group_by: str = "hour"  # hour, day, week
    ) -> UsageStats:
        """Get aggregated usage statistics."""
```

Metrics collected:
- Document access frequency
- Query patterns and types
- Search result relevance (click-through)
- Collection usage distribution
- Time-based access patterns

### 2. Agent Performance Tracking

Monitor MCP operation performance:

```python
class PerformanceMonitor:
    """Track MCP server and agent performance metrics."""
    
    async def start_operation(
        self,
        operation_id: str,
        operation_type: str,  # tool_call, resource_read, subscription
        agent_id: str | None = None
    ) -> OperationContext:
        """Start tracking an operation."""
        
    async def end_operation(
        self,
        operation_id: str,
        status: str,  # success, error, timeout
        result_size: int | None = None,
        error: str | None = None
    ) -> None:
        """Complete operation tracking."""
        
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: dict[str, str] | None = None
    ) -> None:
        """Record a custom metric."""
```

Metrics collected:
- Response times (p50, p95, p99)
- Request throughput
- Error rates by operation
- Resource utilization
- Queue depths (for batch operations)
- Active connections

### 3. Cost Attribution

Track costs associated with operations:

```python
class CostCalculator:
    """Calculate and track costs for operations."""
    
    def __init__(self, pricing_config: PricingConfig):
        self.llm_pricing = pricing_config.llm_pricing
        self.storage_pricing = pricing_config.storage_pricing
        
    async def track_llm_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation_id: str,
        agent_id: str | None = None
    ) -> float:
        """Track LLM API usage and calculate cost."""
        
    async def track_storage_usage(
        self,
        operation: str,  # read, write, delete
        size_bytes: int,
        agent_id: str | None = None
    ) -> float:
        """Track storage operations and costs."""
        
    async def get_cost_report(
        self,
        start_time: datetime,
        end_time: datetime,
        group_by: str = "agent"  # agent, operation, model
    ) -> CostReport:
        """Generate cost attribution report."""
```

Cost tracking includes:
- LLM API calls (by provider/model)
- Storage operations (reads/writes)
- Bandwidth usage
- Compute time for operations
- Cost allocation by agent/purpose

### 4. Metrics Storage Schema

```python
# Lance table schemas for metrics storage

USAGE_METRICS_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("us", tz="UTC")),
    ("metric_type", pa.string()),  # document_access, query, etc.
    ("resource_id", pa.string()),  # document_id, collection_id
    ("operation", pa.string()),
    ("agent_id", pa.string()),
    ("value", pa.float64()),
    ("metadata", pa.string()),  # JSON string
])

PERFORMANCE_METRICS_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("us", tz="UTC")),
    ("operation_id", pa.string()),
    ("operation_type", pa.string()),
    ("agent_id", pa.string()),
    ("duration_ms", pa.float64()),
    ("status", pa.string()),
    ("error", pa.string()),
    ("result_size", pa.int64()),
])

COST_METRICS_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("us", tz="UTC")),
    ("operation_id", pa.string()),
    ("cost_type", pa.string()),  # llm, storage, bandwidth
    ("provider", pa.string()),
    ("amount_usd", pa.float64()),
    ("units", pa.int64()),  # tokens, bytes, requests
    ("agent_id", pa.string()),
    ("metadata", pa.string()),
])
```

### 5. MCP Monitoring Tools

New tools for accessing monitoring data:

```python
# Monitoring tools accessible via MCP

@tool_registry.register("get_usage_metrics")
async def get_usage_metrics(params: GetUsageMetricsParams) -> UsageMetricsResult:
    """Get usage metrics for documents and queries."""
    
@tool_registry.register("get_performance_metrics")
async def get_performance_metrics(params: GetPerformanceParams) -> PerformanceResult:
    """Get performance metrics for operations."""
    
@tool_registry.register("get_cost_report")
async def get_cost_report(params: GetCostReportParams) -> CostReportResult:
    """Get cost attribution report."""
    
@tool_registry.register("export_metrics")
async def export_metrics(params: ExportMetricsParams) -> ExportResult:
    """Export metrics to external monitoring system."""
```

### 6. Integration Points

#### With Existing Components

```python
# In MessageHandler
async def handle_message(self, message: dict) -> dict:
    operation_id = str(uuid.uuid4())
    
    # Start performance tracking
    ctx = await self.performance_monitor.start_operation(
        operation_id=operation_id,
        operation_type=message["method"],
        agent_id=self._get_agent_id(message)
    )
    
    try:
        # Execute operation
        result = await self._execute_method(message)
        
        # Track success
        await self.performance_monitor.end_operation(
            operation_id=operation_id,
            status="success",
            result_size=self._calculate_result_size(result)
        )
        
        return result
    except Exception as e:
        # Track error
        await self.performance_monitor.end_operation(
            operation_id=operation_id,
            status="error",
            error=str(e)
        )
        raise
```

#### With Analytics Tools

The monitoring system will integrate with Phase 3.6 analytics:
- Analytics tools provide dataset-level insights
- Monitoring tracks operation-level metrics
- Combined view shows full system health

### 7. Configuration

```python
@dataclass
class MonitoringConfig:
    """Configuration for monitoring system."""
    
    # Metrics collection
    enabled: bool = True
    metrics_retention_days: int = 30
    aggregation_intervals: list[str] = field(
        default_factory=lambda: ["1m", "5m", "1h", "1d"]
    )
    
    # Performance thresholds
    slow_query_threshold_ms: float = 1000
    error_rate_threshold: float = 0.05
    
    # Cost tracking
    track_costs: bool = True
    pricing_config_path: str | None = None
    
    # Export targets
    prometheus_enabled: bool = False
    prometheus_port: int = 9090
    cloudwatch_enabled: bool = False
    cloudwatch_namespace: str = "ContextFrame/MCP"
```

### 8. Monitoring Dashboard

Create a simple web dashboard for monitoring:

```python
# In contextframe/mcp/monitoring/dashboard.py
class MonitoringDashboard:
    """Simple web dashboard for monitoring metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.app = FastAPI(title="ContextFrame Monitoring")
        self.metrics = metrics_collector
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.get("/metrics/usage")
        async def usage_metrics(
            start: datetime = Query(default=datetime.now() - timedelta(hours=1)),
            end: datetime = Query(default=datetime.now())
        ):
            return await self.metrics.get_usage_stats(start, end)
```

## Implementation Order

1. **Week 1**: Core infrastructure
   - MetricsCollector base class
   - In-memory metrics storage
   - Basic performance tracking

2. **Week 2**: Usage tracking
   - Document access tracking
   - Query pattern analysis
   - Integration with existing tools

3. **Week 3**: Cost attribution
   - LLM cost tracking
   - Storage cost calculation
   - Cost reporting tools

4. **Week 4**: Export and dashboards
   - Prometheus exporter
   - Simple web dashboard
   - Alerting rules

## Success Criteria

1. **Performance Impact**: < 5% overhead on operations
2. **Data Completeness**: 100% of operations tracked
3. **Cost Accuracy**: Within 5% of actual costs
4. **Query Performance**: Metrics queries < 100ms
5. **Integration**: Works with all existing tools

## Testing Strategy

1. **Unit Tests**: Each component tested in isolation
2. **Integration Tests**: End-to-end monitoring flows
3. **Performance Tests**: Verify minimal overhead
4. **Accuracy Tests**: Validate cost calculations
5. **Load Tests**: Handle high-volume metrics

## Future Enhancements

- Machine learning for anomaly detection
- Predictive cost modeling
- Auto-scaling recommendations
- Performance optimization suggestions
- Custom alerting rules