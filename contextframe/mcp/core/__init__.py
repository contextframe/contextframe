"""Core abstractions for transport-agnostic MCP implementation."""

from contextframe.mcp.core.streaming import StreamingAdapter
from contextframe.mcp.core.transport import Progress, TransportAdapter

__all__ = ["TransportAdapter", "Progress", "StreamingAdapter"]
