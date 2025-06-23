"""Usage tracking for documents and queries."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .collector import MetricsCollector


@dataclass
class QueryStats:
    """Statistics for a single query."""
    
    query: str
    query_type: str
    count: int = 0
    total_results: int = 0
    avg_execution_time_ms: float = 0.0
    success_rate: float = 1.0


@dataclass
class DocumentStats:
    """Statistics for document usage."""
    
    document_id: str
    access_count: int = 0
    search_appearances: int = 0
    last_accessed: datetime | None = None
    access_by_operation: dict[str, int] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Aggregated usage statistics."""
    
    period_start: datetime
    period_end: datetime
    total_queries: int = 0
    total_document_accesses: int = 0
    unique_documents_accessed: int = 0
    unique_agents: int = 0
    queries_by_type: dict[str, int] = field(default_factory=dict)
    top_documents: list[DocumentStats] = field(default_factory=list)
    top_queries: list[QueryStats] = field(default_factory=list)
    access_patterns: dict[str, Any] = field(default_factory=dict)


class UsageTracker:
    """Track document access patterns and query statistics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        
        # Local caches for fast lookups
        self._query_cache: dict[str, QueryStats] = {}
        self._document_cache: dict[str, DocumentStats] = {}
        self._agent_activity: dict[str, datetime] = {}
    
    async def track_document_access(
        self,
        document_id: str,
        operation: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record document access event.
        
        Args:
            document_id: ID of the accessed document
            operation: Type of operation (read, search_hit, update, delete)
            agent_id: Optional agent identifier
            metadata: Additional context about the access
        """
        # Update local cache
        if document_id not in self._document_cache:
            self._document_cache[document_id] = DocumentStats(document_id=document_id)
        
        doc_stats = self._document_cache[document_id]
        doc_stats.access_count += 1
        doc_stats.last_accessed = datetime.now(timezone.utc)
        
        if operation not in doc_stats.access_by_operation:
            doc_stats.access_by_operation[operation] = 0
        doc_stats.access_by_operation[operation] += 1
        
        if operation == "search_hit":
            doc_stats.search_appearances += 1
        
        # Track agent activity
        if agent_id:
            self._agent_activity[agent_id] = datetime.now(timezone.utc)
        
        # Record metric
        await self.metrics.record_usage(
            metric_type="document_access",
            resource_id=document_id,
            operation=operation,
            value=1.0,
            agent_id=agent_id,
            metadata=metadata
        )
    
    async def track_query(
        self,
        query: str,
        query_type: str,
        result_count: int,
        execution_time_ms: float,
        agent_id: str | None = None,
        success: bool = True,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record query execution.
        
        Args:
            query: The query string
            query_type: Type of query (vector, text, hybrid, sql)
            result_count: Number of results returned
            execution_time_ms: Query execution time in milliseconds
            agent_id: Optional agent identifier
            success: Whether the query succeeded
            metadata: Additional query context
        """
        # Update query cache
        query_key = f"{query_type}:{query[:100]}"  # Truncate long queries
        
        if query_key not in self._query_cache:
            self._query_cache[query_key] = QueryStats(
                query=query[:100],
                query_type=query_type
            )
        
        q_stats = self._query_cache[query_key]
        q_stats.count += 1
        q_stats.total_results += result_count
        
        # Update average execution time
        prev_total_time = q_stats.avg_execution_time_ms * (q_stats.count - 1)
        q_stats.avg_execution_time_ms = (prev_total_time + execution_time_ms) / q_stats.count
        
        # Update success rate
        if not success:
            prev_successes = q_stats.success_rate * (q_stats.count - 1)
            q_stats.success_rate = prev_successes / q_stats.count
        
        # Track agent activity
        if agent_id:
            self._agent_activity[agent_id] = datetime.now(timezone.utc)
        
        # Record metric
        await self.metrics.record_usage(
            metric_type="query",
            resource_id=query_type,
            operation="execute",
            value=float(result_count),
            agent_id=agent_id,
            metadata={
                "query": query[:100],
                "execution_time_ms": execution_time_ms,
                "success": success,
                **(metadata or {})
            }
        )
    
    async def get_usage_stats(
        self,
        start_time: datetime,
        end_time: datetime,
        group_by: str = "hour"
    ) -> UsageStats:
        """Get aggregated usage statistics.
        
        Args:
            start_time: Start of the period
            end_time: End of the period  
            group_by: Aggregation interval (hour, day, week)
            
        Returns:
            Aggregated usage statistics
        """
        stats = UsageStats(
            period_start=start_time,
            period_end=end_time
        )
        
        # Get metrics from collector
        usage_metrics = await self.metrics.get_aggregated_metrics(
            "usage",
            interval="1h",
            lookback_hours=int((end_time - start_time).total_seconds() / 3600)
        )
        
        # Aggregate from local caches
        # Count unique documents accessed
        accessed_docs = set()
        for doc_id, doc_stats in self._document_cache.items():
            if doc_stats.last_accessed and start_time <= doc_stats.last_accessed <= end_time:
                accessed_docs.add(doc_id)
                stats.total_document_accesses += doc_stats.access_count
        
        stats.unique_documents_accessed = len(accessed_docs)
        
        # Get top documents
        sorted_docs = sorted(
            self._document_cache.values(),
            key=lambda d: d.access_count,
            reverse=True
        )
        stats.top_documents = sorted_docs[:10]
        
        # Count queries by type
        for query_key, q_stats in self._query_cache.items():
            stats.total_queries += q_stats.count
            if q_stats.query_type not in stats.queries_by_type:
                stats.queries_by_type[q_stats.query_type] = 0
            stats.queries_by_type[q_stats.query_type] += q_stats.count
        
        # Get top queries
        sorted_queries = sorted(
            self._query_cache.values(),
            key=lambda q: q.count,
            reverse=True
        )
        stats.top_queries = sorted_queries[:10]
        
        # Count unique agents
        active_agents = set()
        for agent_id, last_active in self._agent_activity.items():
            if start_time <= last_active <= end_time:
                active_agents.add(agent_id)
        stats.unique_agents = len(active_agents)
        
        # Access patterns by time
        if group_by == "hour":
            stats.access_patterns = self._calculate_hourly_patterns(start_time, end_time)
        elif group_by == "day":
            stats.access_patterns = self._calculate_daily_patterns(start_time, end_time)
        
        return stats
    
    def _calculate_hourly_patterns(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> dict[str, Any]:
        """Calculate hourly access patterns."""
        patterns = {}
        
        # This would analyze the metrics to find patterns
        # For now, return a simple structure
        current = start_time.replace(minute=0, second=0, microsecond=0)
        while current < end_time:
            hour_key = current.strftime("%Y-%m-%d %H:00")
            patterns[hour_key] = {
                "queries": 0,
                "document_accesses": 0
            }
            current += timedelta(hours=1)
        
        return patterns
    
    def _calculate_daily_patterns(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> dict[str, Any]:
        """Calculate daily access patterns."""
        patterns = {}
        
        current = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        while current < end_time:
            day_key = current.strftime("%Y-%m-%d")
            patterns[day_key] = {
                "queries": 0,
                "document_accesses": 0,
                "peak_hour": None
            }
            current += timedelta(days=1)
        
        return patterns
    
    async def get_document_usage(
        self,
        document_id: str,
        lookback_days: int = 30
    ) -> DocumentStats | None:
        """Get usage statistics for a specific document.
        
        Args:
            document_id: Document to get stats for
            lookback_days: How far back to look
            
        Returns:
            Document usage statistics or None if not found
        """
        return self._document_cache.get(document_id)
    
    async def get_query_performance(
        self,
        query_type: str | None = None,
        limit: int = 20
    ) -> list[QueryStats]:
        """Get query performance statistics.
        
        Args:
            query_type: Optional filter by query type
            limit: Maximum number of results
            
        Returns:
            List of query statistics
        """
        queries = list(self._query_cache.values())
        
        if query_type:
            queries = [q for q in queries if q.query_type == query_type]
        
        # Sort by execution count
        queries.sort(key=lambda q: q.count, reverse=True)
        
        return queries[:limit]