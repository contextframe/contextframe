"""Base handler for batch operations with transport-agnostic progress tracking."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass

from contextframe.frame import FrameDataset
from contextframe.mcp.core.transport import TransportAdapter, Progress
from contextframe.mcp.core.streaming import StreamingAdapter


logger = logging.getLogger(__name__)


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult:
    """Result of a batch operation."""
    
    total_processed: int
    total_errors: int
    results: List[Any]
    errors: List[Dict[str, Any]]
    operation: str


class BatchOperationHandler:
    """Base class for batch operations with progress tracking.
    
    Provides a consistent interface for batch operations across
    different transports (stdio, HTTP) with proper progress tracking
    and error handling.
    """
    
    def __init__(self, dataset: FrameDataset, transport: TransportAdapter):
        """Initialize batch handler.
        
        Args:
            dataset: The FrameDataset to operate on
            transport: Transport adapter for progress/streaming
        """
        self.dataset = dataset
        self.transport = transport
        self.streaming: Optional[StreamingAdapter] = None
        
        # Get streaming adapter if transport is StdioAdapter
        if hasattr(transport, 'get_streaming_adapter'):
            self.streaming = transport.get_streaming_adapter()
    
    async def execute_batch(
        self,
        operation: str,
        items: List[T],
        processor: Callable[[T], R],
        atomic: bool = False,
        max_errors: Optional[int] = None
    ) -> BatchResult:
        """Execute batch operation with progress tracking.
        
        Args:
            operation: Name of the operation for progress tracking
            items: List of items to process
            processor: Async function to process each item
            atomic: If True, rollback all on any failure
            max_errors: Stop after this many errors (None = no limit)
            
        Returns:
            BatchResult with processed items and errors
        """
        total = len(items)
        results = []
        errors = []
        
        # Start streaming if available
        if self.streaming:
            await self.streaming.start_stream(operation, total)
        
        try:
            for i, item in enumerate(items):
                # Send progress
                await self.transport.send_progress(Progress(
                    operation=operation,
                    current=i + 1,
                    total=total,
                    status=f"Processing item {i + 1} of {total}"
                ))
                
                try:
                    # Process item
                    if asyncio.iscoroutinefunction(processor):
                        result = await processor(item)
                    else:
                        result = processor(item)
                    
                    results.append(result)
                    
                    # Stream result if available
                    if self.streaming:
                        await self.streaming.send_item(result)
                        
                except Exception as e:
                    error = {
                        "item_index": i,
                        "item": item,
                        "error": str(e),
                        "type": type(e).__name__
                    }
                    errors.append(error)
                    
                    # Stream error if available
                    if self.streaming:
                        await self.streaming.send_error(error)
                    
                    # Check if we should stop
                    if atomic:
                        raise BatchOperationError(
                            f"Atomic operation failed at item {i}: {e}"
                        )
                    
                    if max_errors and len(errors) >= max_errors:
                        logger.warning(
                            f"Stopping batch after {max_errors} errors"
                        )
                        break
            
            # Complete streaming
            if self.streaming:
                batch_result = BatchResult(
                    total_processed=len(results),
                    total_errors=len(errors),
                    results=results,
                    errors=errors,
                    operation=operation
                )
                
                summary = {
                    "total_processed": batch_result.total_processed,
                    "total_errors": batch_result.total_errors,
                    "errors": batch_result.errors
                }
                
                return await self.streaming.complete_stream(summary)
            
            return BatchResult(
                total_processed=len(results),
                total_errors=len(errors),
                results=results,
                errors=errors,
                operation=operation
            )
            
        except Exception as e:
            # Ensure stream is properly closed on error
            if self.streaming:
                await self.streaming.complete_stream({
                    "error": str(e),
                    "total_processed": len(results),
                    "total_errors": len(errors) + 1
                })
            raise


class BatchOperationError(Exception):
    """Error in batch operation."""
    pass


async def execute_parallel(
    tasks: List[Callable[[], Any]],
    max_parallel: int = 5
) -> List[Any]:
    """Execute tasks with controlled parallelism.
    
    Args:
        tasks: List of async callables to execute
        max_parallel: Maximum concurrent tasks
        
    Returns:
        List of results in same order as tasks
    """
    semaphore = asyncio.Semaphore(max_parallel)
    
    async def run_with_semaphore(task: Callable[[], Any]) -> Any:
        async with semaphore:
            result = task()
            if asyncio.iscoroutine(result):
                return await result
            return result
    
    return await asyncio.gather(*[
        run_with_semaphore(task) for task in tasks
    ])