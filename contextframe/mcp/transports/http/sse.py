"""Server-Sent Events (SSE) implementation for HTTP transport."""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SSEStream:
    """Manages an SSE connection for streaming updates.

    This class handles the low-level SSE protocol details including
    event formatting, keepalives, and connection management.
    """

    def __init__(self, client_id: str | None = None):
        self.client_id = client_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self._closed = False
        self._event_id = 0

    async def send_event(
        self,
        data: Any,
        event_type: str | None = None,
        event_id: str | None = None,
        retry: int | None = None,
    ) -> str:
        """Send an SSE event.

        Args:
            data: The data to send (will be JSON encoded if not string)
            event_type: Optional event type
            event_id: Optional event ID for reconnection
            retry: Optional retry timeout in milliseconds

        Returns:
            The formatted SSE event string
        """
        if self._closed:
            raise RuntimeError("SSE stream is closed")

        # Format data
        if not isinstance(data, str):
            data = json.dumps(data)

        # Build SSE event
        lines = []

        if event_id is None:
            self._event_id += 1
            event_id = str(self._event_id)

        if event_type:
            lines.append(f"event: {event_type}")

        lines.append(f"id: {event_id}")

        if retry is not None:
            lines.append(f"retry: {retry}")

        # Split data by newlines and format
        for line in data.split('\n'):
            lines.append(f"data: {line}")

        # SSE events end with double newline
        return '\n'.join(lines) + '\n\n'

    async def send_json(
        self, data: dict[str, Any], event_type: str | None = None
    ) -> str:
        """Send JSON data as an SSE event."""
        return await self.send_event(data, event_type=event_type)

    async def send_keepalive(self) -> str:
        """Send a keepalive comment to maintain connection."""
        return f": keepalive {datetime.now().isoformat()}\n\n"

    async def stream_progress(
        self, operation_id: str, progress_queue: asyncio.Queue
    ) -> AsyncIterator[str]:
        """Stream progress updates for an operation.

        Yields SSE-formatted events for each progress update.
        """
        logger.info(f"Starting progress stream for operation {operation_id}")

        try:
            # Send initial event
            yield await self.send_json(
                {
                    "operation_id": operation_id,
                    "status": "started",
                    "timestamp": datetime.now().isoformat(),
                },
                event_type="progress_start",
            )

            # Stream progress updates
            while not self._closed:
                try:
                    # Wait for progress with timeout for keepalive
                    event = await asyncio.wait_for(
                        progress_queue.get(),
                        timeout=25.0,  # Send keepalive before 30s timeout
                    )

                    # Send progress event
                    yield await self.send_json(
                        event.get("data", event),
                        event_type=event.get("type", "progress"),
                    )

                    # Check if operation is complete
                    if event.get("type") == "complete":
                        logger.info(f"Operation {operation_id} completed")
                        break

                except TimeoutError:
                    # Send keepalive to maintain connection
                    yield await self.send_keepalive()

        except Exception as e:
            logger.error(f"Error in progress stream: {e}")
            yield await self.send_json(
                {"error": str(e), "operation_id": operation_id}, event_type="error"
            )

        finally:
            # Send final event
            yield await self.send_json(
                {
                    "operation_id": operation_id,
                    "status": "closed",
                    "timestamp": datetime.now().isoformat(),
                },
                event_type="progress_end",
            )

    async def stream_changes(
        self, subscription_id: str, change_iterator: AsyncIterator[dict[str, Any]]
    ) -> AsyncIterator[str]:
        """Stream dataset changes for a subscription.

        Yields SSE-formatted events for each change.
        """
        logger.info(f"Starting change stream for subscription {subscription_id}")

        try:
            # Send initial event
            yield await self.send_json(
                {
                    "subscription_id": subscription_id,
                    "status": "connected",
                    "timestamp": datetime.now().isoformat(),
                },
                event_type="subscription_start",
            )

            # Stream changes
            async for change in change_iterator:
                if self._closed:
                    break

                # Send change event
                yield await self.send_json(
                    change, event_type=change.get("type", "change")
                )

        except Exception as e:
            logger.error(f"Error in change stream: {e}")
            yield await self.send_json(
                {"error": str(e), "subscription_id": subscription_id},
                event_type="error",
            )

        finally:
            # Send final event
            yield await self.send_json(
                {
                    "subscription_id": subscription_id,
                    "status": "closed",
                    "timestamp": datetime.now().isoformat(),
                },
                event_type="subscription_end",
            )

    async def close(self) -> None:
        """Close the SSE stream."""
        self._closed = True
        logger.info(f"SSE stream {self.client_id} closed")

    @property
    def is_closed(self) -> bool:
        """Check if stream is closed."""
        return self._closed

    @property
    def age_seconds(self) -> float:
        """Get age of stream in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class SSEManager:
    """Manages multiple SSE streams and their lifecycle."""

    def __init__(self, max_connections: int = 1000, max_age_seconds: int = 3600):
        self.streams: dict[str, SSEStream] = {}
        self.max_connections = max_connections
        self.max_age_seconds = max_age_seconds
        self._cleanup_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the SSE manager and cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("SSE manager started")

    async def stop(self) -> None:
        """Stop the SSE manager and close all streams."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all streams
        for stream in list(self.streams.values()):
            await stream.close()

        self.streams.clear()
        logger.info("SSE manager stopped")

    async def create_stream(self, client_id: str | None = None) -> SSEStream:
        """Create a new SSE stream."""
        # Check connection limit
        if len(self.streams) >= self.max_connections:
            raise RuntimeError(f"Maximum connections ({self.max_connections}) reached")

        stream = SSEStream(client_id)
        self.streams[stream.client_id] = stream
        logger.info(f"Created SSE stream {stream.client_id}")
        return stream

    async def get_stream(self, client_id: str) -> SSEStream | None:
        """Get an existing SSE stream."""
        return self.streams.get(client_id)

    async def close_stream(self, client_id: str) -> None:
        """Close and remove an SSE stream."""
        if client_id in self.streams:
            stream = self.streams[client_id]
            await stream.close()
            del self.streams[client_id]
            logger.info(f"Closed SSE stream {client_id}")

    async def _cleanup_loop(self) -> None:
        """Periodically clean up old or closed streams."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Find streams to close
                to_close = []
                for client_id, stream in self.streams.items():
                    if stream.is_closed or stream.age_seconds > self.max_age_seconds:
                        to_close.append(client_id)

                # Close old streams
                for client_id in to_close:
                    await self.close_stream(client_id)

                if to_close:
                    logger.info(f"Cleaned up {len(to_close)} SSE streams")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SSE cleanup loop: {e}")

    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return len(self.streams)

    @property
    def stats(self) -> dict[str, Any]:
        """Get SSE manager statistics."""
        return {
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "oldest_stream_age": max(
                (s.age_seconds for s in self.streams.values()), default=0
            ),
        }
