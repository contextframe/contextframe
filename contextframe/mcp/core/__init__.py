"""Core abstractions for transport-agnostic MCP implementation."""

from contextframe.mcp.core.transport import TransportAdapter, Progress
from contextframe.mcp.core.streaming import StreamingAdapter

__all__ = [
    "TransportAdapter",
    "Progress", 
    "StreamingAdapter"
]