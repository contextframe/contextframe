"""Transport abstraction for MCP server.

This module provides the base abstraction for different transport mechanisms
(stdio, HTTP, etc.) ensuring all tools and features work consistently across
transport types.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Progress:
    """Progress update for long-running operations."""

    operation: str
    current: int
    total: int
    status: str
    details: dict[str, Any] | None = None


@dataclass
class Subscription:
    """Subscription for change notifications."""

    id: str
    resource_type: str
    filter: str | None = None
    last_poll: str | None = None


class TransportAdapter(ABC):
    """Base class for transport adapters.

    This abstraction ensures that all MCP features (tools, resources,
    subscriptions, etc.) work identically across different transports.
    """

    def __init__(self):
        self._subscriptions: dict[str, Subscription] = {}
        self._progress_handlers = []

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the transport."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the transport cleanly."""
        pass

    @abstractmethod
    async def send_message(self, message: dict[str, Any]) -> None:
        """Send a message through the transport."""
        pass

    @abstractmethod
    async def receive_message(self) -> dict[str, Any] | None:
        """Receive a message from the transport."""
        pass

    async def send_progress(self, progress: Progress) -> None:
        """Send progress update in transport-appropriate way.

        - Stdio: Include in structured response
        - HTTP: Send via SSE
        """
        # Default implementation stores progress for inclusion in response
        for handler in self._progress_handlers:
            await handler(progress)

    def add_progress_handler(self, handler):
        """Add a progress handler callback."""
        self._progress_handlers.append(handler)

    async def handle_subscription(
        self, subscription: Subscription
    ) -> AsyncIterator[dict[str, Any]]:
        """Handle subscription in transport-appropriate way.

        - Stdio: Polling-based with change tokens
        - HTTP: SSE streaming
        """
        self._subscriptions[subscription.id] = subscription

        # Base implementation - subclasses override
        while subscription.id in self._subscriptions:
            # This would be overridden by transport-specific logic
            await asyncio.sleep(1)
            yield {"subscription_id": subscription.id, "changes": []}

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel an active subscription."""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            return True
        return False

    @property
    def supports_streaming(self) -> bool:
        """Whether this transport supports streaming responses."""
        return False

    @property
    def transport_type(self) -> str:
        """Identifier for the transport type."""
        return "base"
