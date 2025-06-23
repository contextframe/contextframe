"""Performance monitoring for MCP operations."""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Dict, List, Optional

from .collector import MetricsCollector


@dataclass
class OperationMetrics:
    """Metrics for a single operation."""
    
    operation_type: str
    count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    error_count: int = 0
    timeout_count: int = 0
    
    @property
    def avg_duration_ms(self) -> float:
        """Average duration in milliseconds."""
        return self.total_duration_ms / self.count if self.count > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """Error rate as a percentage."""
        return (self.error_count / self.count * 100) if self.count > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        return 100.0 - self.error_rate


@dataclass
class PerformanceSnapshot:
    """Point-in-time performance snapshot."""
    
    timestamp: datetime
    operations_per_second: float = 0.0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    active_operations: int = 0
    queue_depth: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


@dataclass  
class OperationContext:
    """Context for tracking a single operation."""
    
    operation_id: str
    operation_type: str
    start_time: float
    agent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def duration_ms(self) -> float:
        """Get current duration in milliseconds."""
        return (time.time() - self.start_time) * 1000


class PerformanceMonitor:
    """Track MCP server and agent performance metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        
        # Active operations tracking
        self._active_operations: dict[str, OperationContext] = {}
        
        # Operation metrics by type
        self._operation_metrics: dict[str, OperationMetrics] = {}
        
        # Performance snapshots
        self._snapshots: list[PerformanceSnapshot] = []
        self._max_snapshots = 1440  # 24 hours at 1 per minute
        
        # Response time percentiles tracking
        self._response_times: dict[str, list[float]] = {}
        self._max_response_samples = 1000
        
        # Background monitoring
        self._monitor_task: asyncio.Task | None = None
    
    async def start(self) -> None:
        """Start performance monitoring."""
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self) -> None:
        """Stop performance monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def start_operation(
        self,
        operation_id: str,
        operation_type: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> OperationContext:
        """Start tracking an operation.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation (tool_call, resource_read, etc.)
            agent_id: Optional agent identifier
            metadata: Additional operation context
            
        Returns:
            Operation context for tracking
        """
        context = OperationContext(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=time.time(),
            agent_id=agent_id,
            metadata=metadata or {}
        )
        
        self._active_operations[operation_id] = context
        
        # Initialize metrics for this operation type
        if operation_type not in self._operation_metrics:
            self._operation_metrics[operation_type] = OperationMetrics(
                operation_type=operation_type
            )
        
        return context
    
    async def end_operation(
        self,
        operation_id: str,
        status: str,
        result_size: int | None = None,
        error: str | None = None
    ) -> None:
        """Complete operation tracking.
        
        Args:
            operation_id: Operation identifier
            status: Final status (success, error, timeout)
            result_size: Optional size of the result
            error: Error message if failed
        """
        context = self._active_operations.pop(operation_id, None)
        if not context:
            return
        
        duration_ms = context.duration_ms()
        
        # Update operation metrics
        metrics = self._operation_metrics[context.operation_type]
        metrics.count += 1
        metrics.total_duration_ms += duration_ms
        metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
        metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)
        
        if status == "error":
            metrics.error_count += 1
        elif status == "timeout":
            metrics.timeout_count += 1
        
        # Track response times for percentile calculation
        if context.operation_type not in self._response_times:
            self._response_times[context.operation_type] = []
        
        response_times = self._response_times[context.operation_type]
        response_times.append(duration_ms)
        
        # Keep only recent samples
        if len(response_times) > self._max_response_samples:
            response_times.pop(0)
        
        # Record metric
        await self.metrics.record_performance(
            operation_id=operation_id,
            operation_type=context.operation_type,
            duration_ms=duration_ms,
            status=status,
            agent_id=context.agent_id,
            error=error,
            result_size=result_size
        )
    
    @asynccontextmanager
    async def track_operation(
        self,
        operation_type: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[OperationContext]:
        """Context manager for operation tracking.
        
        Usage:
            async with monitor.track_operation("tool_call") as ctx:
                # Perform operation
                result = await some_operation()
        """
        import uuid
        
        operation_id = str(uuid.uuid4())
        context = await self.start_operation(
            operation_id=operation_id,
            operation_type=operation_type,
            agent_id=agent_id,
            metadata=metadata
        )
        
        try:
            yield context
            await self.end_operation(operation_id, "success")
        except asyncio.TimeoutError:
            await self.end_operation(operation_id, "timeout")
            raise
        except Exception as e:
            await self.end_operation(operation_id, "error", error=str(e))
            raise
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: dict[str, str] | None = None
    ) -> None:
        """Record a custom metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        await self.metrics.record_usage(
            metric_type="custom",
            resource_id=metric_name,
            operation="record",
            value=value,
            metadata=tags
        )
    
    def get_operation_metrics(
        self,
        operation_type: str | None = None
    ) -> dict[str, OperationMetrics]:
        """Get operation metrics.
        
        Args:
            operation_type: Optional filter by operation type
            
        Returns:
            Dictionary of operation metrics
        """
        if operation_type:
            return {
                operation_type: self._operation_metrics.get(
                    operation_type,
                    OperationMetrics(operation_type=operation_type)
                )
            }
        return self._operation_metrics.copy()
    
    def get_response_percentiles(
        self,
        operation_type: str,
        percentiles: list[float] = [0.5, 0.95, 0.99]
    ) -> dict[float, float]:
        """Get response time percentiles.
        
        Args:
            operation_type: Operation type to analyze
            percentiles: List of percentiles to calculate (0-1)
            
        Returns:
            Dictionary mapping percentile to response time in ms
        """
        response_times = self._response_times.get(operation_type, [])
        if not response_times:
            return {p: 0.0 for p in percentiles}
        
        sorted_times = sorted(response_times)
        result = {}
        
        for p in percentiles:
            index = int(len(sorted_times) * p)
            index = min(index, len(sorted_times) - 1)
            result[p] = sorted_times[index]
        
        return result
    
    def get_current_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot."""
        if self._snapshots:
            return self._snapshots[-1]
        
        return PerformanceSnapshot(timestamp=datetime.now(timezone.utc))
    
    def get_performance_history(
        self,
        minutes: int = 60
    ) -> list[PerformanceSnapshot]:
        """Get performance history.
        
        Args:
            minutes: How many minutes of history to return
            
        Returns:
            List of performance snapshots
        """
        if not self._snapshots:
            return []
        
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return [s for s in self._snapshots if s.timestamp >= cutoff]
    
    async def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Snapshot every minute
                await self._take_snapshot()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                # Log error but continue
                print(f"Error in performance monitor: {e}")
    
    async def _take_snapshot(self) -> None:
        """Take a performance snapshot."""
        snapshot = PerformanceSnapshot(timestamp=datetime.now(timezone.utc))
        
        # Calculate operations per second
        total_ops = sum(m.count for m in self._operation_metrics.values())
        if self._snapshots:
            prev_snapshot = self._snapshots[-1]
            time_diff = (snapshot.timestamp - prev_snapshot.timestamp).total_seconds()
            if time_diff > 0:
                prev_total = sum(
                    m.count for m in self._operation_metrics.values()
                )
                snapshot.operations_per_second = (total_ops - prev_total) / time_diff
        
        # Calculate average response time
        total_duration = sum(m.total_duration_ms for m in self._operation_metrics.values())
        if total_ops > 0:
            snapshot.avg_response_time_ms = total_duration / total_ops
        
        # Calculate error rate
        total_errors = sum(m.error_count for m in self._operation_metrics.values())
        if total_ops > 0:
            snapshot.error_rate = (total_errors / total_ops) * 100
        
        # Active operations
        snapshot.active_operations = len(self._active_operations)
        
        # Add snapshot
        self._snapshots.append(snapshot)
        
        # Trim old snapshots
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)