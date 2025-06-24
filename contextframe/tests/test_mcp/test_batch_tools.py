"""Tests for MCP batch operation tools."""

import asyncio
import pytest
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.batch import BatchTools
from contextframe.mcp.core.transport import Progress, TransportAdapter
from contextframe.mcp.tools import ToolRegistry
from typing import Any, Dict, List
from uuid import uuid4


class MockTransportAdapter(TransportAdapter):
    """Mock transport adapter for testing."""

    def __init__(self):
        super().__init__()
        self.progress_updates: list[Progress] = []
        self.messages_sent: list[dict[str, Any]] = []

        # Add progress handler to capture updates
        self.add_progress_handler(self._capture_progress)

    async def _capture_progress(self, progress: Progress):
        self.progress_updates.append(progress)

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def send_message(self, message: dict[str, Any]) -> None:
        self.messages_sent.append(message)

    async def receive_message(self) -> None:
        return None


@pytest.fixture
async def test_dataset(tmp_path):
    """Create a test dataset with sample documents."""
    dataset_path = tmp_path / "test_batch.lance"
    dataset = FrameDataset.create(str(dataset_path))

    # Add test documents - simple approach
    for i in range(10):
        record = FrameRecord(
            text_content=f"Test document {i}: This is test content about topic {i % 3}",
            metadata={
                "title": f"Test Document {i}",
                "record_type": "document",
                "custom_metadata": {
                    "x_topic": f"topic_{i % 3}",
                    "x_index": str(i)
                }
            }
        )
        dataset.add(record)

    yield dataset


@pytest.fixture
async def batch_tools(test_dataset):
    """Create batch tools with test dataset and transport."""
    transport = MockTransportAdapter()
    await transport.initialize()

    # Create tool registry with document tools
    tool_registry = ToolRegistry(test_dataset, transport)

    # Create batch tools
    batch_tools = BatchTools(test_dataset, transport, tool_registry)

    yield batch_tools

    await transport.shutdown()


class TestBatchSearch:
    """Test batch search functionality."""

    @pytest.mark.asyncio
    async def test_batch_search_basic(self, batch_tools):
        """Test basic batch search with multiple queries."""
        params = {
            "queries": [
                {"query": "topic 0", "search_type": "text", "limit": 5},
                {"query": "topic 1", "search_type": "text", "limit": 5},
                {"query": "topic 2", "search_type": "text", "limit": 5},
            ],
            "max_parallel": 3,
        }

        result = await batch_tools.batch_search(params)

        assert result["searches_completed"] == 3
        assert result["searches_failed"] == 0
        assert len(result["results"]) == 3

        # Each query should find documents
        for search_result in result["results"]:
            assert search_result["success"]
            assert "query" in search_result
            assert "results" in search_result
            assert "count" in search_result


class TestBatchAdd:
    """Test batch add functionality."""

    @pytest.mark.asyncio
    async def test_batch_add_atomic(self, batch_tools):
        """Test atomic batch add."""
        params = {
            "documents": [
                {"content": "New document 1", "metadata": {"title": "Doc 1", "custom_metadata": {"x_type": "test"}}},
                {"content": "New document 2", "metadata": {"title": "Doc 2", "custom_metadata": {"x_type": "test"}}},
                {"content": "New document 3", "metadata": {"title": "Doc 3", "custom_metadata": {"x_type": "test"}}},
            ],
            "shared_settings": {
                "generate_embeddings": False,
                "collection": "batch_test",
            },
            "atomic": True,
        }

        # Get initial count
        initial_count = batch_tools.dataset._dataset.count_rows()

        result = await batch_tools.batch_add(params)

        assert result["success"]
        assert result["documents_added"] == 3
        assert result["atomic"]

        # Verify documents were added
        final_count = batch_tools.dataset._dataset.count_rows()
        assert final_count == initial_count + 3

    @pytest.mark.asyncio
    async def test_batch_add_non_atomic(self, batch_tools):
        """Test non-atomic batch add."""
        params = {
            "documents": [
                {"content": "Doc A", "metadata": {"title": "Doc A", "custom_metadata": {"x_idx": "1"}}},
                {"content": "Doc B", "metadata": {"title": "Doc B", "custom_metadata": {"x_idx": "2"}}},
            ],
            "shared_settings": {"generate_embeddings": False},
            "atomic": False,
        }

        result = await batch_tools.batch_add(params)

        assert result["documents_added"] == 2
        assert result["documents_failed"] == 0
        assert not result["atomic"]


class TestBatchUpdate:
    """Test batch update functionality."""

    @pytest.mark.asyncio
    async def test_batch_update_by_filter(self, batch_tools):
        """Test updating documents by filter."""
        params = {
            "filter": "text_content LIKE '%topic 0%'",
            "updates": {"metadata_updates": {"custom_metadata": {"x_updated": "true", "x_version": "2"}}},
            "max_documents": 10,
        }

        result = await batch_tools.batch_update(params)

        assert "documents_updated" in result
        assert result["documents_updated"] > 0
        assert result["documents_failed"] == 0


class TestBatchDelete:
    """Test batch delete functionality."""

    @pytest.mark.asyncio
    async def test_batch_delete_dry_run(self, batch_tools):
        """Test batch delete with dry run."""
        params = {"filter": "text_content LIKE '%topic 1%'", "dry_run": True}

        result = await batch_tools.batch_delete(params)

        assert result["success"]
        assert result["dry_run"]
        assert result["documents_to_delete"] > 0
        assert "document_ids" in result

    @pytest.mark.asyncio
    async def test_batch_delete_with_confirm(self, batch_tools):
        """Test batch delete with confirmation count."""
        # First do a dry run to get count
        dry_run_params = {
            "filter": "text_content LIKE '%document 0%' OR text_content LIKE '%document 1%' OR text_content LIKE '%document 2%'",
            "dry_run": True,
        }

        dry_run_result = await batch_tools.batch_delete(dry_run_params)
        count = dry_run_result["documents_to_delete"]

        # Now delete with wrong confirm count
        wrong_params = {
            "filter": "text_content LIKE '%document 0%' OR text_content LIKE '%document 1%' OR text_content LIKE '%document 2%'",
            "dry_run": False,
            "confirm_count": count + 1,
        }

        wrong_result = await batch_tools.batch_delete(wrong_params)
        assert not wrong_result["success"]
        assert "Expected" in wrong_result["error"]

        # Delete with correct confirm count
        correct_params = {
            "filter": "text_content LIKE '%document 0%' OR text_content LIKE '%document 1%' OR text_content LIKE '%document 2%'",
            "dry_run": False,
            "confirm_count": count,
        }

        correct_result = await batch_tools.batch_delete(correct_params)
        assert correct_result["success"]
        assert correct_result["documents_deleted"] == count
