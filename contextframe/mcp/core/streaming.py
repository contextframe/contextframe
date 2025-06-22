"""Streaming abstraction for transport-agnostic responses."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StreamingResponse:
    """Container for streaming response data."""

    operation: str
    total_items: int | None = None
    items: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    completed: bool = False


class StreamingAdapter(ABC):
    """Adapter for handling streaming responses across transports."""

    @abstractmethod
    async def start_stream(
        self, operation: str, total_items: int | None = None
    ) -> None:
        """Start a streaming operation."""
        pass

    @abstractmethod
    async def send_item(self, item: dict[str, Any]) -> None:
        """Send a single item in the stream."""
        pass

    @abstractmethod
    async def send_error(self, error: str) -> None:
        """Send an error in the stream."""
        pass

    @abstractmethod
    async def complete_stream(self, metadata: dict[str, Any] | None = None) -> Any:
        """Complete the streaming operation and return final result."""
        pass


class BufferedStreamingAdapter(StreamingAdapter):
    """Streaming adapter that buffers all items for non-streaming transports."""

    def __init__(self):
        self._response: StreamingResponse | None = None

    async def start_stream(
        self, operation: str, total_items: int | None = None
    ) -> None:
        """Start buffering items."""
        self._response = StreamingResponse(operation=operation, total_items=total_items)

    async def send_item(self, item: dict[str, Any]) -> None:
        """Add item to buffer."""
        if self._response:
            self._response.items.append(item)

    async def send_error(self, error: str) -> None:
        """Record error."""
        if self._response:
            self._response.error = error

    async def complete_stream(
        self, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Return buffered response."""
        if not self._response:
            raise RuntimeError("No streaming operation in progress")

        self._response.completed = True
        if metadata:
            self._response.metadata.update(metadata)

        # Convert to dict for JSON serialization
        return {
            "operation": self._response.operation,
            "total_items": len(self._response.items),
            "items": self._response.items,
            "metadata": self._response.metadata,
            "error": self._response.error,
            "completed": self._response.completed,
        }


class SSEStreamingAdapter(StreamingAdapter):
    """Streaming adapter for Server-Sent Events (HTTP transport)."""

    def __init__(self, send_sse_func):
        self.send_sse = send_sse_func
        self._operation: str | None = None
        self._item_count = 0

    async def start_stream(
        self, operation: str, total_items: int | None = None
    ) -> None:
        """Send stream start event."""
        self._operation = operation
        self._item_count = 0
        await self.send_sse(
            {
                "event": "stream_start",
                "operation": operation,
                "total_items": total_items,
            }
        )

    async def send_item(self, item: dict[str, Any]) -> None:
        """Send item via SSE."""
        self._item_count += 1
        await self.send_sse(
            {"event": "stream_item", "item": item, "index": self._item_count}
        )

    async def send_error(self, error: str) -> None:
        """Send error via SSE."""
        await self.send_sse({"event": "stream_error", "error": error})

    async def complete_stream(
        self, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send completion event and return summary."""
        result = {
            "event": "stream_complete",
            "operation": self._operation,
            "total_items": self._item_count,
            "metadata": metadata or {},
        }
        await self.send_sse(result)
        return result
