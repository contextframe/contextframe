"""Tests for batch operation handler."""

import pytest
import asyncio
from typing import Any, Dict, List

from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.batch.handler import BatchOperationHandler, execute_parallel
from contextframe.mcp.core.transport import TransportAdapter, Progress


class MockTransportAdapter(TransportAdapter):
    """Mock transport adapter for testing."""
    
    def __init__(self):
        super().__init__()
        self.progress_updates: List[Progress] = []
        self.messages_sent: List[Dict[str, Any]] = []
        
        # Add progress handler to capture updates
        self.add_progress_handler(self._capture_progress)
    
    async def _capture_progress(self, progress: Progress):
        self.progress_updates.append(progress)
    
    async def initialize(self) -> None:
        pass
    
    async def shutdown(self) -> None:
        pass
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        self.messages_sent.append(message)
    
    async def receive_message(self) -> None:
        return None


@pytest.fixture
async def test_dataset(tmp_path):
    """Create test dataset."""
    dataset_path = tmp_path / "test_batch_handler.lance"
    dataset = FrameDataset.create(str(dataset_path))
    yield dataset


@pytest.fixture
def mock_transport():
    """Create mock transport."""
    return MockTransportAdapter()


@pytest.fixture
def batch_handler(test_dataset, mock_transport):
    """Create batch handler with mocks."""
    return BatchOperationHandler(test_dataset, mock_transport)


class TestBatchOperationHandler:
    """Test batch operation handler functionality."""
    
    @pytest.mark.asyncio
    async def test_execute_batch_success(self, batch_handler, mock_transport):
        """Test successful batch execution."""
        items = [1, 2, 3, 4, 5]
        
        async def processor(item: int) -> int:
            return item * 2
        
        result = await batch_handler.execute_batch(
            operation="test_multiply",
            items=items,
            processor=processor
        )
        
        # Check results
        assert result.total_processed == 5
        assert result.total_errors == 0
        assert result.results == [2, 4, 6, 8, 10]
        assert result.operation == "test_multiply"
        
        # Check progress updates
        assert len(mock_transport.progress_updates) == 5
        for i, progress in enumerate(mock_transport.progress_updates):
            assert progress.operation == "test_multiply"
            assert progress.current == i + 1
            assert progress.total == 5
    
    @pytest.mark.asyncio
    async def test_execute_batch_with_errors(self, batch_handler):
        """Test batch execution with some errors."""
        items = [1, 2, 0, 4, 5]  # 0 will cause division error
        
        def processor(item: int) -> float:
            return 10 / item  # Division by zero for item=0
        
        result = await batch_handler.execute_batch(
            operation="test_divide",
            items=items,
            processor=processor,
            max_errors=2
        )
        
        # Check results
        assert result.total_processed == 4
        assert result.total_errors == 1
        assert result.results == [10.0, 5.0, 2.5, 2.0]
        assert len(result.errors) == 1
        assert result.errors[0]["item_index"] == 2
        assert "division by zero" in result.errors[0]["error"]
    
    @pytest.mark.asyncio
    async def test_execute_batch_atomic_failure(self, batch_handler):
        """Test atomic batch execution that fails."""
        items = [1, 2, 0, 4, 5]
        
        def processor(item: int) -> float:
            return 10 / item
        
        with pytest.raises(Exception) as excinfo:
            await batch_handler.execute_batch(
                operation="test_atomic",
                items=items,
                processor=processor,
                atomic=True
            )
        
        assert "Atomic operation failed at item 2" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_execute_batch_max_errors(self, batch_handler):
        """Test stopping after max errors."""
        items = list(range(10))  # [0, 1, 2, ..., 9]
        
        def processor(item: int) -> float:
            if item < 5:
                raise ValueError(f"Item {item} too small")
            return item
        
        result = await batch_handler.execute_batch(
            operation="test_max_errors",
            items=items,
            processor=processor,
            max_errors=3
        )
        
        # Should stop after 3 errors
        assert result.total_errors == 3
        # Only items 0, 1, 2 should have been processed (all failed)
        assert result.total_processed == 0


class TestExecuteParallel:
    """Test parallel execution utility."""
    
    @pytest.mark.asyncio
    async def test_execute_parallel_basic(self):
        """Test basic parallel execution."""
        async def task(i: int) -> int:
            await asyncio.sleep(0.01)  # Simulate work
            return i * 2
        
        tasks = [lambda i=i: task(i) for i in range(10)]
        
        results = await execute_parallel(tasks, max_parallel=3)
        
        assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    
    @pytest.mark.asyncio
    async def test_execute_parallel_with_errors(self):
        """Test parallel execution with some errors."""
        async def task(i: int) -> int:
            if i == 5:
                raise ValueError("Test error")
            return i * 2
        
        tasks = [lambda i=i: task(i) for i in range(10)]
        
        # execute_parallel doesn't handle errors - they propagate
        with pytest.raises(ValueError):
            await execute_parallel(tasks, max_parallel=3)