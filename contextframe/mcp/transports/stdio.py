"""Stdio transport adapter implementation."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextframe.mcp.core.streaming import BufferedStreamingAdapter
from contextframe.mcp.core.transport import Progress, Subscription, TransportAdapter
from contextframe.mcp.transport import StdioTransport
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StdioAdapter(TransportAdapter):
    """Stdio transport adapter using existing StdioTransport.

    This adapter wraps the existing stdio implementation to work with
    the new transport abstraction while maintaining backward compatibility.
    """

    def __init__(self):
        super().__init__()
        self._transport = StdioTransport()
        self._streaming = BufferedStreamingAdapter()
        self._current_progress: list[Progress] = []

        # Set up progress handler to collect progress
        self.add_progress_handler(self._collect_progress)

    async def _collect_progress(self, progress: Progress):
        """Collect progress updates for inclusion in response."""
        self._current_progress.append(progress)

    async def initialize(self) -> None:
        """Initialize stdio streams."""
        await self._transport.connect()
        logger.info("Stdio transport initialized")

    async def shutdown(self) -> None:
        """Close stdio streams."""
        await self._transport.close()
        logger.info("Stdio transport shutdown")

    async def send_message(self, message: dict[str, Any]) -> None:
        """Send message via stdout."""
        # Include any collected progress in the response
        if self._current_progress and "result" in message:
            if not isinstance(message["result"], dict):
                message["result"] = {"value": message["result"]}
            message["result"]["progress_updates"] = [
                {
                    "operation": p.operation,
                    "current": p.current,
                    "total": p.total,
                    "status": p.status,
                    "details": p.details,
                }
                for p in self._current_progress
            ]
            self._current_progress.clear()

        await self._transport.send_message(message)

    async def receive_message(self) -> dict[str, Any] | None:
        """Receive message from stdin."""
        return await self._transport.read_message()

    async def send_progress(self, progress: Progress) -> None:
        """For stdio, progress is collected and included in final response."""
        await super().send_progress(progress)

    async def handle_subscription(
        self, subscription: Subscription
    ) -> AsyncIterator[dict[str, Any]]:
        """Stdio uses polling-based subscriptions.

        Returns changes since last poll using change tokens.
        """
        self._subscriptions[subscription.id] = subscription

        # For stdio, we don't actually stream - the client will poll
        # This is a placeholder that would be called by poll_changes tool
        yield {
            "subscription_id": subscription.id,
            "message": "Use poll_changes tool to check for updates",
            "next_poll_token": subscription.last_poll or "initial",
        }

    @property
    def supports_streaming(self) -> bool:
        """Stdio doesn't support true streaming."""
        return False

    @property
    def transport_type(self) -> str:
        """Transport type identifier."""
        return "stdio"

    def get_streaming_adapter(self) -> BufferedStreamingAdapter:
        """Get the streaming adapter for this transport."""
        return self._streaming
