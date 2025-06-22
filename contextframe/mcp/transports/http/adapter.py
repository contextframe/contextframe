"""HTTP transport adapter implementation."""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncIterator
from contextframe.mcp.core.streaming import SSEStreamingAdapter
from contextframe.mcp.core.transport import Progress, Subscription, TransportAdapter
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)


class HttpAdapter(TransportAdapter):
    """HTTP transport adapter with SSE streaming support.

    This adapter enables the MCP server to handle HTTP requests and
    provide real-time streaming via Server-Sent Events (SSE).
    """

    def __init__(self):
        super().__init__()
        self._streaming = SSEStreamingAdapter()
        self._active_streams: dict[str, SSEStream] = {}
        self._operation_progress: dict[str, asyncio.Queue] = {}
        self._subscription_queues: dict[str, asyncio.Queue] = {}
        self._active_operations: set[str] = set()

    async def initialize(self) -> None:
        """Initialize HTTP transport."""
        logger.info("HTTP transport initialized")

    async def shutdown(self) -> None:
        """Shutdown HTTP transport and close all streams."""
        # Close all active SSE streams
        for stream_id in list(self._active_streams.keys()):
            await self.close_stream(stream_id)

        # Clear all queues
        self._operation_progress.clear()
        self._subscription_queues.clear()
        self._active_operations.clear()

        logger.info("HTTP transport shutdown")

    async def send_message(self, message: dict[str, Any]) -> None:
        """HTTP doesn't use send_message - responses are returned directly."""
        # In HTTP, responses are returned from request handlers
        # This method is here for interface compatibility
        pass

    async def receive_message(self) -> dict[str, Any] | None:
        """HTTP doesn't use receive_message - requests come via HTTP."""
        # In HTTP, messages come through HTTP request handlers
        # This method is here for interface compatibility
        return None

    async def send_progress(self, progress: Progress) -> None:
        """Send progress update via SSE to relevant streams."""
        await super().send_progress(progress)

        # Send to operation-specific progress streams
        operation_id = (
            progress.details.get("operation_id") if progress.details else None
        )
        if operation_id and operation_id in self._operation_progress:
            queue = self._operation_progress[operation_id]
            await queue.put(
                {
                    "type": "progress",
                    "data": {
                        "operation": progress.operation,
                        "current": progress.current,
                        "total": progress.total,
                        "status": progress.status,
                        "details": progress.details,
                    },
                }
            )

    async def handle_subscription(
        self, subscription: Subscription
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream dataset changes via SSE.

        Unlike stdio which uses polling, HTTP streams changes in real-time.
        """
        self._subscriptions[subscription.id] = subscription

        # Create a queue for this subscription
        queue = asyncio.Queue()
        self._subscription_queues[subscription.id] = queue

        try:
            # Yield initial subscription confirmation
            yield {
                "type": "subscription_created",
                "subscription_id": subscription.id,
                "resource_type": subscription.resource_type,
                "filter": subscription.filter,
            }

            # Stream changes as they arrive
            while subscription.id in self._subscriptions:
                try:
                    # Wait for changes with timeout
                    change = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield change
                except TimeoutError:
                    # Send keepalive
                    yield {"type": "keepalive", "subscription_id": subscription.id}

        finally:
            # Cleanup
            if subscription.id in self._subscription_queues:
                del self._subscription_queues[subscription.id]
            self.cancel_subscription(subscription.id)

    def register_stream(self, stream_id: str, stream: "SSEStream") -> None:
        """Register an active SSE stream."""
        self._active_streams[stream_id] = stream

    async def close_stream(self, stream_id: str) -> None:
        """Close and unregister an SSE stream."""
        if stream_id in self._active_streams:
            stream = self._active_streams[stream_id]
            await stream.close()
            del self._active_streams[stream_id]

    async def create_operation(self, operation_type: str) -> str:
        """Create a new operation for progress tracking."""
        operation_id = str(uuid.uuid4())
        self._active_operations.add(operation_id)
        self._operation_progress[operation_id] = asyncio.Queue()
        return operation_id

    async def complete_operation(self, operation_id: str) -> None:
        """Mark an operation as complete."""
        if operation_id in self._active_operations:
            self._active_operations.remove(operation_id)

            # Send completion event
            if operation_id in self._operation_progress:
                queue = self._operation_progress[operation_id]
                await queue.put({"type": "complete", "operation_id": operation_id})

    @asynccontextmanager
    async def operation_context(self, operation_type: str):
        """Context manager for operations with automatic cleanup."""
        operation_id = await self.create_operation(operation_type)
        try:
            yield operation_id
        finally:
            await self.complete_operation(operation_id)
            # Cleanup queue after a delay to ensure clients receive completion
            await asyncio.sleep(5.0)
            if operation_id in self._operation_progress:
                del self._operation_progress[operation_id]

    async def stream_operation_progress(
        self, operation_id: str
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream progress updates for a specific operation."""
        if operation_id not in self._operation_progress:
            yield {"type": "error", "error": f"Operation {operation_id} not found"}
            return

        queue = self._operation_progress[operation_id]

        while operation_id in self._active_operations or not queue.empty():
            try:
                # Wait for progress with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event

                # Stop if operation is complete
                if event.get("type") == "complete":
                    break

            except TimeoutError:
                # Send keepalive
                yield {"type": "keepalive", "operation_id": operation_id}

    async def notify_change(self, change: dict[str, Any]) -> None:
        """Notify all relevant subscriptions about a change."""
        for sub_id, subscription in self._subscriptions.items():
            # Check if change matches subscription filter
            if self._matches_subscription(change, subscription):
                if sub_id in self._subscription_queues:
                    await self._subscription_queues[sub_id].put(
                        {"type": "change", "subscription_id": sub_id, "change": change}
                    )

    def _matches_subscription(
        self, change: dict[str, Any], subscription: Subscription
    ) -> bool:
        """Check if a change matches a subscription's filters."""
        # Check resource type
        if change.get("resource_type") != subscription.resource_type:
            return False

        # Apply additional filters if present
        if subscription.filter:
            # This would be more sophisticated in production
            # For now, simple string matching
            filter_dict = (
                json.loads(subscription.filter)
                if isinstance(subscription.filter, str)
                else subscription.filter
            )
            for key, value in filter_dict.items():
                if change.get(key) != value:
                    return False

        return True

    @property
    def supports_streaming(self) -> bool:
        """HTTP transport supports true streaming via SSE."""
        return True

    @property
    def transport_type(self) -> str:
        """Transport type identifier."""
        return "http"

    def get_streaming_adapter(self) -> SSEStreamingAdapter:
        """Get the streaming adapter for this transport."""
        return self._streaming
