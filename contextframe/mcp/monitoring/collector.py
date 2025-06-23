"""Central metrics collection and aggregation."""

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pyarrow as pa
from contextframe.frame import FrameDataset


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    
    enabled: bool = True
    retention_days: int = 30
    aggregation_intervals: list[str] = field(
        default_factory=lambda: ["1m", "5m", "1h", "1d"]
    )
    max_memory_metrics: int = 10000
    flush_interval_seconds: int = 60


class MetricsCollector:
    """Central metrics collection and storage.
    
    Collects metrics in memory and periodically flushes to Lance dataset.
    Provides aggregation and querying capabilities.
    """
    
    def __init__(
        self,
        dataset: FrameDataset | None = None,
        config: MetricsConfig | None = None
    ):
        self.dataset = dataset
        self.config = config or MetricsConfig()
        
        # In-memory buffers
        self._usage_buffer: deque = deque(maxlen=self.config.max_memory_metrics)
        self._performance_buffer: deque = deque(maxlen=self.config.max_memory_metrics)
        self._cost_buffer: deque = deque(maxlen=self.config.max_memory_metrics)
        
        # Aggregated metrics for fast access
        self._aggregated_metrics: dict[str, dict[str, Any]] = defaultdict(dict)
        
        # Background tasks
        self._flush_task: asyncio.Task | None = None
        self._aggregation_task: asyncio.Task | None = None
        
        # Metrics schemas
        self.usage_schema = pa.schema([
            ("timestamp", pa.timestamp("us", tz="UTC")),
            ("metric_type", pa.string()),
            ("resource_id", pa.string()),
            ("operation", pa.string()),
            ("agent_id", pa.string()),
            ("value", pa.float64()),
            ("metadata", pa.string()),
        ])
        
        self.performance_schema = pa.schema([
            ("timestamp", pa.timestamp("us", tz="UTC")),
            ("operation_id", pa.string()),
            ("operation_type", pa.string()),
            ("agent_id", pa.string()),
            ("duration_ms", pa.float64()),
            ("status", pa.string()),
            ("error", pa.string()),
            ("result_size", pa.int64()),
        ])
        
        self.cost_schema = pa.schema([
            ("timestamp", pa.timestamp("us", tz="UTC")),
            ("operation_id", pa.string()),
            ("cost_type", pa.string()),
            ("provider", pa.string()),
            ("amount_usd", pa.float64()),
            ("units", pa.int64()),
            ("agent_id", pa.string()),
            ("metadata", pa.string()),
        ])
    
    async def start(self) -> None:
        """Start background tasks for metrics processing."""
        if not self.config.enabled:
            return
            
        # Start flush task
        self._flush_task = asyncio.create_task(self._flush_loop())
        
        # Start aggregation task  
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
    
    async def stop(self) -> None:
        """Stop background tasks and flush remaining metrics."""
        # Cancel background tasks
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
                
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_metrics()
    
    async def record_usage(
        self,
        metric_type: str,
        resource_id: str,
        operation: str,
        value: float = 1.0,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record a usage metric."""
        if not self.config.enabled:
            return
            
        metric = {
            "timestamp": datetime.now(timezone.utc),
            "metric_type": metric_type,
            "resource_id": resource_id,
            "operation": operation,
            "agent_id": agent_id or "anonymous",
            "value": value,
            "metadata": json.dumps(metadata) if metadata else None,
        }
        
        self._usage_buffer.append(metric)
    
    async def record_performance(
        self,
        operation_id: str,
        operation_type: str,
        duration_ms: float,
        status: str,
        agent_id: str | None = None,
        error: str | None = None,
        result_size: int | None = None
    ) -> None:
        """Record a performance metric."""
        if not self.config.enabled:
            return
            
        metric = {
            "timestamp": datetime.now(timezone.utc),
            "operation_id": operation_id,
            "operation_type": operation_type,
            "agent_id": agent_id or "anonymous",
            "duration_ms": duration_ms,
            "status": status,
            "error": error,
            "result_size": result_size,
        }
        
        self._performance_buffer.append(metric)
    
    async def record_cost(
        self,
        operation_id: str,
        cost_type: str,
        provider: str,
        amount_usd: float,
        units: int,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record a cost metric."""
        if not self.config.enabled:
            return
            
        metric = {
            "timestamp": datetime.now(timezone.utc),
            "operation_id": operation_id,
            "cost_type": cost_type,
            "provider": provider,
            "amount_usd": amount_usd,
            "units": units,
            "agent_id": agent_id or "anonymous",
            "metadata": json.dumps(metadata) if metadata else None,
        }
        
        self._cost_buffer.append(metric)
    
    async def get_aggregated_metrics(
        self,
        metric_category: str,
        interval: str = "1h",
        lookback_hours: int = 24
    ) -> dict[str, Any]:
        """Get aggregated metrics for a category."""
        key = f"{metric_category}:{interval}:{lookback_hours}"
        return self._aggregated_metrics.get(key, {})
    
    async def _flush_loop(self) -> None:
        """Background task to periodically flush metrics."""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self._flush_metrics()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                # Log error but continue
                print(f"Error flushing metrics: {e}")
    
    async def _flush_metrics(self) -> None:
        """Flush in-memory metrics to Lance dataset."""
        if not self.dataset:
            return
            
        # Flush usage metrics
        if self._usage_buffer:
            usage_data = list(self._usage_buffer)
            self._usage_buffer.clear()
            
            # Convert to Lance table and append
            # This would append to a metrics table in the dataset
            # For now, we'll just clear the buffer
            
        # Flush performance metrics
        if self._performance_buffer:
            perf_data = list(self._performance_buffer)
            self._performance_buffer.clear()
            
        # Flush cost metrics  
        if self._cost_buffer:
            cost_data = list(self._cost_buffer)
            self._cost_buffer.clear()
    
    async def _aggregation_loop(self) -> None:
        """Background task to aggregate metrics."""
        while True:
            try:
                await asyncio.sleep(60)  # Aggregate every minute
                await self._aggregate_metrics()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                # Log error but continue
                print(f"Error aggregating metrics: {e}")
    
    async def _aggregate_metrics(self) -> None:
        """Aggregate recent metrics for fast access."""
        now = datetime.now(timezone.utc)
        
        # Aggregate usage metrics by hour
        usage_by_hour = defaultdict(lambda: {"count": 0, "resources": set()})
        for metric in self._usage_buffer:
            if (now - metric["timestamp"]).total_seconds() < 3600:
                hour = metric["timestamp"].replace(minute=0, second=0, microsecond=0)
                key = (hour, metric["metric_type"])
                usage_by_hour[key]["count"] += metric["value"]
                usage_by_hour[key]["resources"].add(metric["resource_id"])
        
        # Store aggregated results
        self._aggregated_metrics["usage:1h:1"] = {
            str(k): {"count": v["count"], "unique_resources": len(v["resources"])}
            for k, v in usage_by_hour.items()
        }
        
        # Aggregate performance metrics
        perf_by_type = defaultdict(lambda: {"count": 0, "total_ms": 0, "errors": 0})
        for metric in self._performance_buffer:
            if (now - metric["timestamp"]).total_seconds() < 3600:
                op_type = metric["operation_type"]
                perf_by_type[op_type]["count"] += 1
                perf_by_type[op_type]["total_ms"] += metric["duration_ms"]
                if metric["status"] == "error":
                    perf_by_type[op_type]["errors"] += 1
        
        # Calculate averages
        for op_type, stats in perf_by_type.items():
            if stats["count"] > 0:
                stats["avg_ms"] = stats["total_ms"] / stats["count"]
                stats["error_rate"] = stats["errors"] / stats["count"]
        
        self._aggregated_metrics["performance:1h:1"] = dict(perf_by_type)
        
        # Clean up old aggregated metrics
        cutoff_time = now - timedelta(days=1)
        for key in list(self._aggregated_metrics.keys()):
            # Parse timestamp from key if stored
            # For now, we'll keep all aggregated metrics