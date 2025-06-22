"""Analytics and performance tools for ContextFrame MCP server.

This module provides tools for:
- Dataset statistics and metrics
- Usage pattern analysis
- Query performance monitoring
- Relationship graph analysis
- Storage optimization
- Index recommendations
- Operation benchmarking
- Metrics export for monitoring
"""

from .analyzer import QueryAnalyzer, RelationshipAnalyzer, UsageAnalyzer
from .optimizer import IndexAdvisor, PerformanceBenchmark, StorageOptimizer
from .stats import DatasetStats, StatsCollector
from .tools import (
    AnalyzeUsageHandler,
    BenchmarkOperationsHandler,
    ExportMetricsHandler,
    GetDatasetStatsHandler,
    IndexRecommendationsHandler,
    OptimizeStorageHandler,
    QueryPerformanceHandler,
    RelationshipAnalysisHandler,
)

__all__ = [
    # Core classes
    "StatsCollector",
    "DatasetStats",
    "QueryAnalyzer",
    "UsageAnalyzer",
    "RelationshipAnalyzer",
    "StorageOptimizer",
    "IndexAdvisor",
    "PerformanceBenchmark",
    # Tool handlers
    "GetDatasetStatsHandler",
    "AnalyzeUsageHandler",
    "QueryPerformanceHandler",
    "RelationshipAnalysisHandler",
    "OptimizeStorageHandler",
    "IndexRecommendationsHandler",
    "BenchmarkOperationsHandler",
    "ExportMetricsHandler",
]
