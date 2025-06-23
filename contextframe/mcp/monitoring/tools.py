"""MCP tools for accessing monitoring data."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from contextframe.mcp.errors import InvalidParams
from contextframe.mcp.tools import tool_registry

from .collector import MetricsCollector
from .cost import CostCalculator
from .performance import PerformanceMonitor
from .usage import UsageTracker


# Global instances (initialized by server)
metrics_collector: MetricsCollector | None = None
usage_tracker: UsageTracker | None = None
performance_monitor: PerformanceMonitor | None = None
cost_calculator: CostCalculator | None = None


def init_monitoring_tools(
    collector: MetricsCollector,
    usage: UsageTracker,
    performance: PerformanceMonitor,
    cost: CostCalculator
) -> None:
    """Initialize monitoring tools with required components."""
    global metrics_collector, usage_tracker, performance_monitor, cost_calculator
    metrics_collector = collector
    usage_tracker = usage
    performance_monitor = performance
    cost_calculator = cost


def _ensure_initialized() -> None:
    """Ensure monitoring components are initialized."""
    if not all([metrics_collector, usage_tracker, performance_monitor, cost_calculator]):
        raise RuntimeError("Monitoring tools not initialized")


@tool_registry.register(
    name="get_usage_metrics",
    description="Get usage metrics for documents and queries",
    input_schema={
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "Start time (ISO format). Defaults to 1 hour ago"
            },
            "end_time": {
                "type": "string",
                "format": "date-time",
                "description": "End time (ISO format). Defaults to now"
            },
            "group_by": {
                "type": "string",
                "enum": ["hour", "day", "week"],
                "description": "Aggregation interval",
                "default": "hour"
            },
            "include_details": {
                "type": "boolean",
                "description": "Include detailed breakdowns",
                "default": False
            }
        }
    }
)
async def get_usage_metrics(params: dict[str, Any]) -> dict[str, Any]:
    """Get usage metrics for documents and queries.
    
    Returns metrics including:
    - Total queries and document accesses
    - Unique documents and agents
    - Query distribution by type
    - Top accessed documents
    - Access patterns over time
    """
    _ensure_initialized()
    
    # Parse parameters
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)
    
    if "start_time" in params:
        start_time = datetime.fromisoformat(params["start_time"].replace("Z", "+00:00"))
    if "end_time" in params:
        end_time = datetime.fromisoformat(params["end_time"].replace("Z", "+00:00"))
    
    group_by = params.get("group_by", "hour")
    include_details = params.get("include_details", False)
    
    # Get usage stats
    stats = await usage_tracker.get_usage_stats(start_time, end_time, group_by)
    
    result = {
        "period": {
            "start": stats.period_start.isoformat(),
            "end": stats.period_end.isoformat()
        },
        "summary": {
            "total_queries": stats.total_queries,
            "total_document_accesses": stats.total_document_accesses,
            "unique_documents": stats.unique_documents_accessed,
            "unique_agents": stats.unique_agents
        },
        "queries_by_type": stats.queries_by_type,
        "access_patterns": stats.access_patterns
    }
    
    if include_details:
        result["top_documents"] = [
            {
                "document_id": doc.document_id,
                "access_count": doc.access_count,
                "search_appearances": doc.search_appearances,
                "last_accessed": doc.last_accessed.isoformat() if doc.last_accessed else None,
                "access_by_operation": doc.access_by_operation
            }
            for doc in stats.top_documents[:10]
        ]
        
        result["top_queries"] = [
            {
                "query": q.query,
                "type": q.query_type,
                "count": q.count,
                "avg_results": q.total_results / q.count if q.count > 0 else 0,
                "avg_execution_time_ms": q.avg_execution_time_ms,
                "success_rate": q.success_rate
            }
            for q in stats.top_queries[:10]
        ]
    
    return result


@tool_registry.register(
    name="get_performance_metrics",
    description="Get performance metrics for MCP operations",
    input_schema={
        "type": "object",
        "properties": {
            "operation_type": {
                "type": "string",
                "description": "Filter by operation type (e.g., tool_call, resource_read)"
            },
            "minutes": {
                "type": "integer",
                "description": "How many minutes of history to include",
                "default": 60
            },
            "include_percentiles": {
                "type": "boolean",
                "description": "Include response time percentiles",
                "default": True
            }
        }
    }
)
async def get_performance_metrics(params: dict[str, Any]) -> dict[str, Any]:
    """Get performance metrics for operations.
    
    Returns metrics including:
    - Operation counts and durations
    - Error rates and success rates
    - Response time percentiles
    - Current performance snapshot
    - Historical trends
    """
    _ensure_initialized()
    
    operation_type = params.get("operation_type")
    minutes = params.get("minutes", 60)
    include_percentiles = params.get("include_percentiles", True)
    
    # Get operation metrics
    metrics = performance_monitor.get_operation_metrics(operation_type)
    
    # Get current snapshot
    current = performance_monitor.get_current_snapshot()
    
    # Get performance history
    history = performance_monitor.get_performance_history(minutes)
    
    result = {
        "current_snapshot": {
            "timestamp": current.timestamp.isoformat(),
            "operations_per_second": current.operations_per_second,
            "avg_response_time_ms": current.avg_response_time_ms,
            "error_rate": current.error_rate,
            "active_operations": current.active_operations
        },
        "operations": {}
    }
    
    # Add operation-specific metrics
    for op_type, op_metrics in metrics.items():
        op_data = {
            "count": op_metrics.count,
            "avg_duration_ms": op_metrics.avg_duration_ms,
            "min_duration_ms": op_metrics.min_duration_ms,
            "max_duration_ms": op_metrics.max_duration_ms,
            "error_rate": op_metrics.error_rate,
            "success_rate": op_metrics.success_rate
        }
        
        if include_percentiles and op_metrics.count > 0:
            percentiles = performance_monitor.get_response_percentiles(
                op_type,
                [0.5, 0.75, 0.90, 0.95, 0.99]
            )
            op_data["percentiles"] = {
                f"p{int(p*100)}": value
                for p, value in percentiles.items()
            }
        
        result["operations"][op_type] = op_data
    
    # Add historical trend
    if history:
        result["history"] = [
            {
                "timestamp": snap.timestamp.isoformat(),
                "ops_per_second": snap.operations_per_second,
                "avg_response_ms": snap.avg_response_time_ms,
                "error_rate": snap.error_rate
            }
            for snap in history[-20:]  # Last 20 snapshots
        ]
    
    return result


@tool_registry.register(
    name="get_cost_report",
    description="Get cost attribution report for MCP operations",
    input_schema={
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "Start time (ISO format). Defaults to 24 hours ago"
            },
            "end_time": {
                "type": "string",
                "format": "date-time",
                "description": "End time (ISO format). Defaults to now"
            },
            "group_by": {
                "type": "string",
                "enum": ["agent", "operation", "provider"],
                "description": "How to group costs",
                "default": "agent"
            },
            "include_projections": {
                "type": "boolean",
                "description": "Include monthly cost projections",
                "default": True
            }
        }
    }
)
async def get_cost_report(params: dict[str, Any]) -> dict[str, Any]:
    """Get cost attribution report.
    
    Returns:
    - Total costs broken down by type
    - Costs grouped by agent/operation/provider
    - Daily cost breakdown
    - Optimization recommendations
    - Monthly projections
    """
    _ensure_initialized()
    
    # Parse parameters
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=1)
    
    if "start_time" in params:
        start_time = datetime.fromisoformat(params["start_time"].replace("Z", "+00:00"))
    if "end_time" in params:
        end_time = datetime.fromisoformat(params["end_time"].replace("Z", "+00:00"))
    
    group_by = params.get("group_by", "agent")
    include_projections = params.get("include_projections", True)
    
    # Get cost report
    report = await cost_calculator.get_cost_report(start_time, end_time, group_by)
    
    result = {
        "period": {
            "start": report.summary.period_start.isoformat(),
            "end": report.summary.period_end.isoformat()
        },
        "total_cost": round(report.summary.total_cost, 4),
        "breakdown": {
            "llm": round(report.summary.llm_cost, 4),
            "storage": round(report.summary.storage_cost, 4),
            "bandwidth": round(report.summary.bandwidth_cost, 4)
        },
        "costs_by_" + group_by: {
            k: round(v, 4)
            for k, v in getattr(report.summary, f"costs_by_{group_by}").items()
        }
    }
    
    # Add daily breakdown
    if report.daily_breakdown:
        result["daily_breakdown"] = [
            {
                "date": day.period_start.date().isoformat(),
                "total": round(day.total_cost, 4),
                "llm": round(day.llm_cost, 4),
                "storage": round(day.storage_cost, 4),
                "bandwidth": round(day.bandwidth_cost, 4)
            }
            for day in report.daily_breakdown[:7]  # Last 7 days
        ]
    
    # Add recommendations
    if report.recommendations:
        result["recommendations"] = report.recommendations
    
    # Add projections
    if include_projections:
        result["projections"] = {
            "monthly_cost": round(report.projected_monthly_cost, 2),
            "annual_cost": round(report.projected_monthly_cost * 12, 2)
        }
    
    return result


@tool_registry.register(
    name="get_monitoring_status",
    description="Get overall monitoring system status",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def get_monitoring_status(params: dict[str, Any]) -> dict[str, Any]:
    """Get overall monitoring system status.
    
    Returns:
    - Monitoring system health
    - Configuration status
    - Buffer sizes and memory usage
    - Collection statistics
    """
    _ensure_initialized()
    
    # Get buffer sizes
    usage_buffer_size = len(metrics_collector._usage_buffer)
    performance_buffer_size = len(metrics_collector._performance_buffer)
    cost_buffer_size = len(metrics_collector._cost_buffer)
    
    # Get collection stats
    total_metrics = usage_buffer_size + performance_buffer_size + cost_buffer_size
    
    # Get active operations
    active_operations = len(performance_monitor._active_operations)
    
    return {
        "status": "healthy" if metrics_collector.config.enabled else "disabled",
        "configuration": {
            "enabled": metrics_collector.config.enabled,
            "retention_days": metrics_collector.config.retention_days,
            "flush_interval_seconds": metrics_collector.config.flush_interval_seconds,
            "max_memory_metrics": metrics_collector.config.max_memory_metrics
        },
        "buffers": {
            "usage": usage_buffer_size,
            "performance": performance_buffer_size,
            "cost": cost_buffer_size,
            "total": total_metrics
        },
        "activity": {
            "active_operations": active_operations,
            "tracked_queries": len(usage_tracker._query_cache),
            "tracked_documents": len(usage_tracker._document_cache),
            "tracked_agents": len(usage_tracker._agent_activity)
        }
    }


@tool_registry.register(
    name="export_metrics",
    description="Export metrics to various formats",
    input_schema={
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["prometheus", "json", "csv"],
                "description": "Export format",
                "default": "json"
            },
            "metric_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["usage", "performance", "cost", "all"]
                },
                "description": "Which metrics to export",
                "default": ["all"]
            },
            "include_raw": {
                "type": "boolean",
                "description": "Include raw metric data",
                "default": False
            }
        }
    }
)
async def export_metrics(params: dict[str, Any]) -> dict[str, Any]:
    """Export metrics to external monitoring systems.
    
    Supports formats:
    - Prometheus text format
    - JSON for custom processing
    - CSV for analysis
    """
    _ensure_initialized()
    
    format_type = params.get("format", "json")
    metric_types = params.get("metric_types", ["all"])
    include_raw = params.get("include_raw", False)
    
    # Determine which metrics to include
    include_all = "all" in metric_types
    include_usage = include_all or "usage" in metric_types
    include_performance = include_all or "performance" in metric_types
    include_cost = include_all or "cost" in metric_types
    
    if format_type == "prometheus":
        # Generate Prometheus text format
        lines = []
        
        if include_usage:
            # Usage metrics
            usage_stats = await usage_tracker.get_usage_stats(
                datetime.now(timezone.utc) - timedelta(hours=1),
                datetime.now(timezone.utc)
            )
            
            lines.extend([
                "# HELP contextframe_queries_total Total number of queries",
                "# TYPE contextframe_queries_total counter",
                f"contextframe_queries_total {usage_stats.total_queries}",
                "",
                "# HELP contextframe_document_accesses_total Total document accesses",
                "# TYPE contextframe_document_accesses_total counter",
                f"contextframe_document_accesses_total {usage_stats.total_document_accesses}",
                ""
            ])
        
        if include_performance:
            # Performance metrics
            metrics = performance_monitor.get_operation_metrics()
            
            for op_type, op_metrics in metrics.items():
                safe_op_type = op_type.replace("/", "_").replace("-", "_")
                lines.extend([
                    f"# HELP contextframe_operation_{safe_op_type}_total Total {op_type} operations",
                    f"# TYPE contextframe_operation_{safe_op_type}_total counter",
                    f"contextframe_operation_{safe_op_type}_total {op_metrics.count}",
                    "",
                    f"# HELP contextframe_operation_{safe_op_type}_duration_ms {op_type} duration",
                    f"# TYPE contextframe_operation_{safe_op_type}_duration_ms histogram",
                    f"contextframe_operation_{safe_op_type}_duration_ms_sum {op_metrics.total_duration_ms}",
                    f"contextframe_operation_{safe_op_type}_duration_ms_count {op_metrics.count}",
                    ""
                ])
        
        return {
            "format": "prometheus",
            "content": "\n".join(lines),
            "content_type": "text/plain"
        }
    
    elif format_type == "json":
        # Generate JSON format
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {}
        }
        
        if include_usage:
            result["metrics"]["usage"] = await get_usage_metrics({})
        
        if include_performance:
            result["metrics"]["performance"] = await get_performance_metrics({})
        
        if include_cost:
            result["metrics"]["cost"] = await get_cost_report({})
        
        return {
            "format": "json",
            "content": result,
            "content_type": "application/json"
        }
    
    else:
        raise InvalidParams(f"Unsupported export format: {format_type}")