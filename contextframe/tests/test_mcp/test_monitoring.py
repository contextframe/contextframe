"""Test monitoring system for MCP server."""

import asyncio
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from contextframe.mcp.monitoring.collector import MetricsCollector, MetricsConfig
from contextframe.mcp.monitoring.cost import CostCalculator, LLMPricing, PricingConfig
from contextframe.mcp.monitoring.integration import (
    MonitoredMessageHandler,
    MonitoringSystem,
)
from contextframe.mcp.monitoring.performance import PerformanceMonitor
from contextframe.mcp.monitoring.usage import UsageTracker


@pytest.fixture
def metrics_config():
    """Create test metrics configuration."""
    return MetricsConfig(
        enabled=True,
        retention_days=7,
        flush_interval_seconds=10,
        max_memory_metrics=1000
    )


@pytest.fixture
def pricing_config():
    """Create test pricing configuration."""
    return PricingConfig(
        llm_pricing={
            "openai:gpt-4": LLMPricing("openai", "gpt-4", 0.03, 0.06),
            "openai:gpt-3.5-turbo": LLMPricing("openai", "gpt-3.5-turbo", 0.0005, 0.0015),
        },
        bandwidth_cost_per_gb=0.09
    )


@pytest.fixture
def mock_dataset():
    """Create mock dataset."""
    return MagicMock()


@pytest.fixture
async def monitoring_system(mock_dataset, metrics_config, pricing_config):
    """Create monitoring system for testing."""
    system = MonitoringSystem(mock_dataset, metrics_config, pricing_config)
    await system.start()
    yield system
    await system.stop()


class TestMetricsCollector:
    """Test metrics collection functionality."""
    
    @pytest.mark.asyncio
    async def test_record_usage_metric(self, mock_dataset, metrics_config):
        """Test recording usage metrics."""
        collector = MetricsCollector(mock_dataset, metrics_config)
        
        await collector.record_usage(
            metric_type="document_access",
            resource_id="doc-123",
            operation="read",
            value=1.0,
            agent_id="agent-1",
            metadata={"source": "test"}
        )
        
        # Check metric was buffered
        assert len(collector._usage_buffer) == 1
        metric = collector._usage_buffer[0]
        assert metric["metric_type"] == "document_access"
        assert metric["resource_id"] == "doc-123"
        assert metric["operation"] == "read"
        assert metric["agent_id"] == "agent-1"
    
    @pytest.mark.asyncio
    async def test_record_performance_metric(self, mock_dataset, metrics_config):
        """Test recording performance metrics."""
        collector = MetricsCollector(mock_dataset, metrics_config)
        
        await collector.record_performance(
            operation_id="op-123",
            operation_type="tool_call",
            duration_ms=150.5,
            status="success",
            agent_id="agent-1",
            result_size=1024
        )
        
        # Check metric was buffered
        assert len(collector._performance_buffer) == 1
        metric = collector._performance_buffer[0]
        assert metric["operation_id"] == "op-123"
        assert metric["operation_type"] == "tool_call"
        assert metric["duration_ms"] == 150.5
        assert metric["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_record_cost_metric(self, mock_dataset, metrics_config):
        """Test recording cost metrics."""
        collector = MetricsCollector(mock_dataset, metrics_config)
        
        await collector.record_cost(
            operation_id="op-123",
            cost_type="llm",
            provider="openai",
            amount_usd=0.015,
            units=500,
            agent_id="agent-1"
        )
        
        # Check metric was buffered
        assert len(collector._cost_buffer) == 1
        metric = collector._cost_buffer[0]
        assert metric["cost_type"] == "llm"
        assert metric["provider"] == "openai"
        assert metric["amount_usd"] == 0.015
        assert metric["units"] == 500
    
    @pytest.mark.asyncio
    async def test_metrics_disabled(self, mock_dataset):
        """Test that metrics are not recorded when disabled."""
        config = MetricsConfig(enabled=False)
        collector = MetricsCollector(mock_dataset, config)
        
        await collector.record_usage(
            metric_type="test",
            resource_id="test",
            operation="test"
        )
        
        # No metrics should be recorded
        assert len(collector._usage_buffer) == 0


class TestUsageTracker:
    """Test usage tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_track_document_access(self, monitoring_system):
        """Test tracking document access."""
        usage = monitoring_system.usage_tracker
        
        # Track multiple accesses
        await usage.track_document_access("doc-1", "read", "agent-1")
        await usage.track_document_access("doc-1", "search_hit", "agent-2")
        await usage.track_document_access("doc-2", "update", "agent-1")
        
        # Check document cache
        assert len(usage._document_cache) == 2
        
        doc1_stats = usage._document_cache["doc-1"]
        assert doc1_stats.access_count == 2
        assert doc1_stats.search_appearances == 1
        assert doc1_stats.access_by_operation["read"] == 1
        assert doc1_stats.access_by_operation["search_hit"] == 1
    
    @pytest.mark.asyncio
    async def test_track_query(self, monitoring_system):
        """Test tracking query execution."""
        usage = monitoring_system.usage_tracker
        
        # Track queries
        await usage.track_query(
            query="test query",
            query_type="vector",
            result_count=10,
            execution_time_ms=50.0,
            agent_id="agent-1",
            success=True
        )
        
        await usage.track_query(
            query="test query",
            query_type="vector",
            result_count=5,
            execution_time_ms=40.0,
            agent_id="agent-2",
            success=True
        )
        
        # Check query cache
        query_key = "vector:test query"
        assert query_key in usage._query_cache
        
        stats = usage._query_cache[query_key]
        assert stats.count == 2
        assert stats.total_results == 15
        assert stats.avg_execution_time_ms == 45.0  # (50 + 40) / 2
        assert stats.success_rate == 1.0
    
    @pytest.mark.asyncio
    async def test_get_usage_stats(self, monitoring_system):
        """Test getting aggregated usage statistics."""
        usage = monitoring_system.usage_tracker
        
        # Track some activity
        await usage.track_document_access("doc-1", "read", "agent-1")
        await usage.track_document_access("doc-2", "read", "agent-2")
        await usage.track_query("test", "vector", 5, 10.0, "agent-1")
        
        # Get stats
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        stats = await usage.get_usage_stats(start_time, end_time)
        
        assert stats.total_document_accesses >= 2
        assert stats.unique_documents_accessed == 2
        assert stats.total_queries >= 1
        assert stats.unique_agents >= 2


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_operation_tracking(self, monitoring_system):
        """Test tracking operation performance."""
        perf = monitoring_system.performance_monitor
        
        # Start operation
        context = await perf.start_operation(
            operation_id="op-1",
            operation_type="tool_call",
            agent_id="agent-1"
        )
        
        assert "op-1" in perf._active_operations
        assert context.operation_type == "tool_call"
        
        # Simulate some work
        await asyncio.sleep(0.01)
        
        # End operation
        await perf.end_operation(
            operation_id="op-1",
            status="success",
            result_size=100
        )
        
        assert "op-1" not in perf._active_operations
        
        # Check metrics
        metrics = perf.get_operation_metrics("tool_call")
        assert "tool_call" in metrics
        op_metrics = metrics["tool_call"]
        assert op_metrics.count == 1
        assert op_metrics.error_count == 0
        assert op_metrics.avg_duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_operation_context_manager(self, monitoring_system):
        """Test operation tracking with context manager."""
        perf = monitoring_system.performance_monitor
        
        # Track successful operation
        async with perf.track_operation("test_op", "agent-1") as ctx:
            assert ctx.operation_type == "test_op"
            await asyncio.sleep(0.01)
        
        # Track failed operation
        with pytest.raises(ValueError):
            async with perf.track_operation("test_op", "agent-1"):
                raise ValueError("Test error")
        
        # Check metrics
        metrics = perf.get_operation_metrics("test_op")
        op_metrics = metrics["test_op"]
        assert op_metrics.count == 2
        assert op_metrics.error_count == 1
        assert op_metrics.success_rate == 50.0
    
    @pytest.mark.asyncio
    async def test_response_percentiles(self, monitoring_system):
        """Test response time percentile calculation."""
        perf = monitoring_system.performance_monitor
        
        # Track multiple operations with different durations
        for i in range(10):
            ctx = await perf.start_operation(f"op-{i}", "test_op")
            await asyncio.sleep(0.001 * i)  # Variable delays
            await perf.end_operation(f"op-{i}", "success")
        
        # Get percentiles
        percentiles = perf.get_response_percentiles(
            "test_op",
            [0.5, 0.9, 0.99]
        )
        
        assert 0.5 in percentiles
        assert 0.9 in percentiles
        assert percentiles[0.5] < percentiles[0.9]


class TestCostCalculator:
    """Test cost calculation functionality."""
    
    @pytest.mark.asyncio
    async def test_llm_cost_tracking(self, monitoring_system):
        """Test LLM usage cost tracking."""
        cost_calc = monitoring_system.cost_calculator
        
        # Track GPT-4 usage
        cost = await cost_calc.track_llm_usage(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            operation_id="op-1",
            agent_id="agent-1"
        )
        
        # GPT-4: $0.03/1k input, $0.06/1k output
        expected_cost = (1000/1000 * 0.03) + (500/1000 * 0.06)
        assert cost == expected_cost
        assert cost == 0.06  # $0.03 + $0.03
        
        # Track GPT-3.5 usage
        cost = await cost_calc.track_llm_usage(
            provider="openai",
            model="gpt-3.5-turbo",
            input_tokens=2000,
            output_tokens=1000,
            operation_id="op-2",
            agent_id="agent-1"
        )
        
        # GPT-3.5: $0.0005/1k input, $0.0015/1k output
        expected_cost = (2000/1000 * 0.0005) + (1000/1000 * 0.0015)
        assert cost == expected_cost
        assert cost == 0.0025  # $0.001 + $0.0015
    
    @pytest.mark.asyncio
    async def test_storage_cost_tracking(self, monitoring_system):
        """Test storage operation cost tracking."""
        cost_calc = monitoring_system.cost_calculator
        
        # Track read operation (1GB)
        cost = await cost_calc.track_storage_usage(
            operation="read",
            size_bytes=1024 * 1024 * 1024,  # 1GB
            agent_id="agent-1"
        )
        
        assert cost == 0.01  # $0.01 per GB read
        
        # Track write operation (2GB)
        cost = await cost_calc.track_storage_usage(
            operation="write",
            size_bytes=2 * 1024 * 1024 * 1024,  # 2GB
            agent_id="agent-1"
        )
        
        assert cost == 0.04  # $0.02 per GB write * 2GB
    
    @pytest.mark.asyncio
    async def test_bandwidth_cost_tracking(self, monitoring_system):
        """Test bandwidth cost tracking."""
        cost_calc = monitoring_system.cost_calculator
        
        # Track egress bandwidth
        cost = await cost_calc.track_bandwidth_usage(
            size_bytes=10 * 1024 * 1024 * 1024,  # 10GB
            direction="egress",
            agent_id="agent-1"
        )
        
        assert cost == 0.9  # $0.09 per GB * 10GB
        
        # Track ingress (should be free)
        cost = await cost_calc.track_bandwidth_usage(
            size_bytes=10 * 1024 * 1024 * 1024,
            direction="ingress",
            agent_id="agent-1"
        )
        
        assert cost == 0.0
    
    @pytest.mark.asyncio
    async def test_cost_report(self, monitoring_system):
        """Test cost report generation."""
        cost_calc = monitoring_system.cost_calculator
        
        # Track some costs
        await cost_calc.track_llm_usage(
            "openai", "gpt-4", 1000, 500, "op-1", "agent-1"
        )
        await cost_calc.track_storage_usage(
            "read", 1024 * 1024 * 1024, "agent-1"
        )
        
        # Get report
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)
        report = await cost_calc.get_cost_report(start_time, end_time, "agent")
        
        assert report.summary.total_cost > 0
        assert report.summary.llm_cost > 0
        assert report.summary.storage_cost > 0
        assert report.projected_monthly_cost > 0


class TestMonitoredMessageHandler:
    """Test monitored message handler."""
    
    @pytest.mark.asyncio
    async def test_message_handling_with_monitoring(self, monitoring_system):
        """Test that messages are tracked by monitoring."""
        # Create mock server and handler
        mock_server = MagicMock()
        mock_server.tools = MagicMock()
        mock_server.resources = MagicMock()
        
        # Create base handler mock
        with patch('contextframe.mcp.handlers.MessageHandler') as MockHandler:
            mock_base_handler = AsyncMock()
            mock_base_handler.handle.return_value = {
                "jsonrpc": "2.0",
                "result": {"success": True},
                "id": 1
            }
            MockHandler.return_value = mock_base_handler
            
            # Create monitored handler
            handler = MonitoredMessageHandler(mock_server, monitoring_system)
            
            # Handle a message
            message = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "test_tool"},
                "id": 1,
                "agent_id": "test-agent"
            }
            
            result = await handler.handle(message)
            
            # Check that base handler was called
            mock_base_handler.handle.assert_called_once()
            
            # Check monitoring was updated
            perf_metrics = monitoring_system.performance_monitor.get_operation_metrics()
            assert "tools/call" in perf_metrics
            assert perf_metrics["tools/call"].count == 1
            assert perf_metrics["tools/call"].error_count == 0


class TestMonitoringTools:
    """Test monitoring MCP tools."""
    
    @pytest.mark.asyncio
    async def test_get_usage_metrics_tool(self, monitoring_system):
        """Test get_usage_metrics tool."""
        from contextframe.mcp.monitoring.tools import get_usage_metrics
        
        # Track some usage
        await monitoring_system.usage_tracker.track_document_access(
            "doc-1", "read", "agent-1"
        )
        
        # Get metrics
        result = await get_usage_metrics({})
        
        assert "summary" in result
        assert "queries_by_type" in result
        assert result["summary"]["total_document_accesses"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_tool(self, monitoring_system):
        """Test get_performance_metrics tool."""
        from contextframe.mcp.monitoring.tools import get_performance_metrics
        
        # Track some operations
        await monitoring_system.performance_monitor.start_operation(
            "op-1", "test_op", "agent-1"
        )
        await monitoring_system.performance_monitor.end_operation(
            "op-1", "success"
        )
        
        # Get metrics
        result = await get_performance_metrics({})
        
        assert "operations" in result
        assert "current_snapshot" in result
        assert "test_op" in result["operations"]
    
    @pytest.mark.asyncio
    async def test_get_cost_report_tool(self, monitoring_system):
        """Test get_cost_report tool."""
        from contextframe.mcp.monitoring.tools import get_cost_report
        
        # Track some costs
        await monitoring_system.cost_calculator.track_llm_usage(
            "openai", "gpt-3.5-turbo", 1000, 500, "op-1", "agent-1"
        )
        
        # Get report
        result = await get_cost_report({})
        
        assert "total_cost" in result
        assert "breakdown" in result
        assert result["total_cost"] > 0