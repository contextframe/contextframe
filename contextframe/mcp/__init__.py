"""MCP (Model Context Protocol) server implementation for ContextFrame.

This module provides a standardized way to expose ContextFrame datasets
to LLMs and AI agents through the Model Context Protocol.
"""

from contextframe.mcp.server import ContextFrameMCPServer

__all__ = ["ContextFrameMCPServer"]
