"""Tests for MCP analytics tools."""

import asyncio
import pytest
from contextframe.frame import FrameDataset
from contextframe.mcp.analytics.analyzer import (
    QueryAnalyzer,
    QueryMetrics,
    RelationshipAnalyzer,
    UsageAnalyzer,
)
from contextframe.mcp.analytics.optimizer import (
    IndexAdvisor,
    PerformanceBenchmark,
    StorageOptimizer,
)
from contextframe.mcp.analytics.stats import DatasetStats, StatsCollector
from contextframe.mcp.analytics.tools import (
    AnalyzeUsageHandler,
    BenchmarkOperationsHandler,
    ExportMetricsHandler,
    GetDatasetStatsHandler,
    IndexRecommendationsHandler,
    OptimizeStorageHandler,
    QueryPerformanceHandler,
    RelationshipAnalysisHandler,
)
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch


class TestStatsCollector:
    """Test StatsCollector functionality."""

    @pytest.fixture
    def mock_dataset(self):
        """Create a mock dataset."""
        dataset = Mock(spec=FrameDataset)

        # Mock dataset methods
        dataset.get_dataset_stats.return_value = {
            "dataset_stats": {
                "num_fragments": 5,
                "num_deleted_rows": 10,
                "num_small_files": 2,
            },
            "version_info": {
                "current_version": 10,
                "latest_version": 10,
            },
            "storage": {
                "num_rows": 1000,
            },
            "indices": [
                {"name": "embedding_idx", "type": "vector", "fields": ["embedding"]},
                {"name": "id_idx", "type": "scalar", "fields": ["id"]},
            ],
        }

        dataset.get_fragment_stats.return_value = [
            {
                "fragment_id": 0,
                "num_rows": 200,
                "physical_rows": 220,
                "num_deletions": 20,
            },
            {
                "fragment_id": 1,
                "num_rows": 800,
                "physical_rows": 800,
                "num_deletions": 0,
            },
        ]

        dataset.count_by_filter.return_value = 25  # Collection count

        # Mock scanner for content stats
        mock_batch = Mock()
        mock_batch.column_names = ["record_type", "created_at"]
        mock_batch.column.return_value.to_pylist.return_value = [
            "document",
            "document",
            "collection_header",
        ]

        mock_scanner = Mock()
        mock_scanner.to_batches.return_value = [mock_batch]
        dataset.scanner.return_value = mock_scanner

        return dataset

    @pytest.mark.asyncio
    async def test_collect_stats(self, mock_dataset):
        """Test collecting comprehensive stats."""
        collector = StatsCollector(mock_dataset)

        stats = await collector.collect_stats(
            include_content=True,
            include_fragments=True,
            include_relationships=False,
        )

        assert isinstance(stats, DatasetStats)
        assert stats.total_documents == 1000
        assert stats.num_fragments == 5
        assert stats.total_collections == 25
        assert len(stats.indices) == 2

    @pytest.mark.asyncio
    async def test_stats_to_dict(self, mock_dataset):
        """Test converting stats to dictionary."""
        collector = StatsCollector(mock_dataset)
        stats = await collector.collect_stats()

        stats_dict = stats.to_dict()

        assert "summary" in stats_dict
        assert "storage" in stats_dict
        assert "versions" in stats_dict
        assert "indices" in stats_dict


class TestQueryAnalyzer:
    """Test QueryAnalyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create a query analyzer with mock data."""
        dataset = Mock(spec=FrameDataset)
        analyzer = QueryAnalyzer(dataset)

        # Add some test queries
        for i in range(20):
            metrics = QueryMetrics(
                query_type="vector" if i % 2 == 0 else "text",
                query_text=f"test query {i}",
                duration_ms=50 + i * 10,
                rows_scanned=100 + i * 50,
                rows_returned=10 + i,
                index_used=i % 3 == 0,
                timestamp=datetime.now() - timedelta(hours=i),
            )
            analyzer.record_query(metrics)

        return analyzer

    @pytest.mark.asyncio
    async def test_analyze_performance(self, analyzer):
        """Test query performance analysis."""
        analysis = await analyzer.analyze_performance(
            time_range=timedelta(days=1),
            min_duration_ms=100,
        )

        assert "summary" in analysis
        assert "by_type" in analysis
        assert "slow_queries" in analysis

        # Check summary stats
        summary = analysis["summary"]
        assert summary["total_queries"] > 0
        assert "avg_duration_ms" in summary
        assert "p90_duration_ms" in summary


class TestStorageOptimizer:
    """Test StorageOptimizer functionality."""

    @pytest.fixture
    def optimizer(self):
        """Create storage optimizer."""
        dataset = Mock(spec=FrameDataset)

        # Mock optimization methods
        dataset.compact_files.return_value = {
            "fragments_compacted": 3,
            "files_removed": 5,
            "files_added": 2,
        }

        dataset.cleanup_old_versions.return_value = {
            "bytes_removed": 1024 * 1024 * 100,  # 100MB
            "old_versions_removed": 5,
        }

        dataset.optimize_indices.return_value = {
            "status": "completed",
            "indices_optimized": 2,
        }
        
        # Add fragment stats for dry run
        dataset.get_fragment_stats.return_value = [
            {"num_rows": 5000, "size_bytes": 1024 * 1024},
            {"num_rows": 15000, "size_bytes": 3 * 1024 * 1024},
            {"num_rows": 3000, "size_bytes": 512 * 1024},
        ]
        
        # Add version history for vacuum dry run
        dataset.get_version_history.return_value = [
            {"version": 1, "timestamp": datetime.now() - timedelta(days=10)},
            {"version": 2, "timestamp": datetime.now() - timedelta(days=5)},
            {"version": 3, "timestamp": datetime.now()},
        ]

        return StorageOptimizer(dataset)

    @pytest.mark.asyncio
    async def test_optimize_storage(self, optimizer):
        """Test storage optimization."""
        result = await optimizer.optimize_storage(
            operations=["compact"],
            dry_run=False,
        )

        assert result["operations"]
        assert len(result["operations"]) == 1

        op_result = result["operations"][0]
        assert op_result["operation"] == "compact"
        assert op_result["success"]

    @pytest.mark.asyncio
    async def test_dry_run(self, optimizer):
        """Test dry run mode."""
        result = await optimizer.optimize_storage(
            operations=["compact", "vacuum"],
            dry_run=True,
        )

        assert len(result["operations"]) == 2
        for op in result["operations"]:
            assert op["metrics"].get("preview", False)


class TestAnalyticsTools:
    """Test analytics tool handlers."""

    @pytest.fixture
    def mock_dataset(self):
        """Create a comprehensive mock dataset."""
        dataset = Mock(spec=FrameDataset)

        # Set up all necessary mocks
        dataset.get_dataset_stats.return_value = {
            "dataset_stats": {"num_fragments": 5},
            "version_info": {"current_version": 10},
            "storage": {"num_rows": 1000},
            "indices": [],
        }

        dataset.get_fragment_stats.return_value = []
        dataset.count_by_filter.return_value = 0
        dataset.list_indices.return_value = []
        dataset.scanner.return_value = Mock(to_batches=Mock(return_value=[]))

        return dataset

    @pytest.mark.asyncio
    async def test_get_dataset_stats_handler(self, mock_dataset):
        """Test get_dataset_stats tool handler."""
        handler = GetDatasetStatsHandler(mock_dataset)

        # Test schema
        schema = handler.get_input_schema()
        assert schema["type"] == "object"
        assert "include_details" in schema["properties"]

        # Test execution
        result = await handler.execute(include_details=False)

        assert result["success"]
        assert "stats" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_analyze_usage_handler(self, mock_dataset):
        """Test analyze_usage tool handler."""
        handler = AnalyzeUsageHandler(mock_dataset)

        # Test schema
        schema = handler.get_input_schema()
        assert "time_range" in schema["properties"]
        assert "group_by" in schema["properties"]

        # Test execution
        result = await handler.execute(time_range="7d", group_by="day")

        assert result["success"]
        assert "analysis" in result
        assert result["period"] == "7d"

    @pytest.mark.asyncio
    async def test_optimize_storage_handler(self, mock_dataset):
        """Test optimize_storage tool handler."""
        # Mock the optimization methods
        mock_dataset.compact_files = Mock(return_value={"files_removed": 5})
        mock_dataset.cleanup_old_versions = Mock(return_value={"bytes_removed": 1000})

        handler = OptimizeStorageHandler(mock_dataset)

        # Test schema
        schema = handler.get_input_schema()
        assert "operations" in schema["properties"]
        assert "dry_run" in schema["properties"]

        # Test execution
        result = await handler.execute(operations=["compact"], dry_run=True)

        assert result["success"]
        assert result["dry_run"]
        assert "results" in result

    @pytest.mark.asyncio
    async def test_export_metrics_handler(self, mock_dataset):
        """Test export_metrics tool handler."""
        handler = ExportMetricsHandler(mock_dataset)

        # Test different formats
        json_result = await handler.execute(format="json")
        assert json_result["success"]
        assert json_result["format"] == "json"
        assert isinstance(json_result["data"], dict)

        prom_result = await handler.execute(format="prometheus")
        assert prom_result["success"]
        assert prom_result["format"] == "prometheus"
        assert isinstance(prom_result["data"], str)
        assert "# TYPE" in prom_result["data"]

        csv_result = await handler.execute(format="csv")
        assert csv_result["success"]
        assert csv_result["format"] == "csv"
        assert isinstance(csv_result["data"], str)

    @pytest.mark.asyncio
    async def test_benchmark_operations_handler(self, mock_dataset):
        """Test benchmark_operations tool handler."""
        # Mock knn_search
        mock_dataset.knn_search = Mock(return_value=[])

        # Mock scanner for sample data
        mock_batch = Mock()
        mock_batch.column.return_value.to_pylist.return_value = ["id1", "id2"]
        mock_scanner = Mock()
        mock_scanner.to_batches.return_value = [mock_batch]
        mock_dataset.scanner.return_value = mock_scanner

        handler = BenchmarkOperationsHandler(mock_dataset)

        # Test schema validation
        schema = handler.get_input_schema()
        assert schema["properties"]["operations"]["items"]["enum"] == [
            "search",
            "insert",
            "update",
            "scan",
        ]

        # Test execution
        result = await handler.execute(
            operations=["scan"],
            sample_size=10,
            concurrency=1,
        )

        assert result["success"]
        assert "benchmarks" in result
        assert "operations" in result["benchmarks"]


class TestIndexAdvisor:
    """Test IndexAdvisor functionality."""

    @pytest.fixture
    def advisor(self):
        """Create index advisor."""
        dataset = Mock(spec=FrameDataset)
        dataset._dataset = Mock()
        dataset._dataset.schema = Mock()

        # Mock schema fields
        mock_field = Mock()
        mock_field.name = "test_field"
        mock_field.type = "string"
        mock_field.nullable = True
        mock_field.metadata = None

        dataset._dataset.schema.__iter__ = Mock(return_value=iter([mock_field]))
        dataset.list_indices.return_value = []

        return IndexAdvisor(dataset)

    @pytest.mark.asyncio
    async def test_get_recommendations(self, advisor):
        """Test index recommendations."""
        # Record some query patterns
        advisor.record_query_pattern("id = '123'", ["id"])
        advisor.record_query_pattern("created_at > '2024-01-01'", ["created_at"])

        recommendations = await advisor.get_recommendations(
            analyze_queries=True,
            workload_type="mixed",
        )

        assert "current_indices" in recommendations
        assert "recommendations" in recommendations
        assert "index_coverage" in recommendations

        # Should recommend indices for frequently queried fields
        assert len(recommendations["recommendations"]) > 0
