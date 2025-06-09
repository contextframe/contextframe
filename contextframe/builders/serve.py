"""
Serving module for ContextFrame.

Provides MCP (Model Context Protocol) server capabilities for ContextFrame datasets,
allowing LLMs and agents to interact with context data.
"""

from pathlib import Path
from typing import Any


def create_mcp_server(
    dataset_path: str | Path, server_name: str = "contextframe"
) -> Any:
    """
    Create an MCP server for a ContextFrame dataset.

    Args:
        dataset_path: Path to the Lance dataset
        server_name: Name for the MCP server

    Returns:
        MCP server instance
    """
    import mcp

    # Implementation placeholder
    raise NotImplementedError("MCP server creation coming soon")


def create_mcp_tools(dataset) -> list[dict[str, Any]]:
    """
    Create MCP tool definitions for ContextFrame operations.

    Args:
        dataset: ContextFrame dataset instance

    Returns:
        List of MCP tool definitions
    """
    import mcp

    # Implementation placeholder
    raise NotImplementedError("MCP tools creation coming soon")


def create_rest_api(dataset_path: str | Path, include_mcp_bridge: bool = True) -> Any:
    """
    Create a REST API for ContextFrame dataset with optional MCP bridge.

    Args:
        dataset_path: Path to the Lance dataset
        include_mcp_bridge: Include MCP-compatible endpoints

    Returns:
        FastAPI application instance
    """
    from fastapi import FastAPI
    import uvicorn

    # Implementation placeholder
    raise NotImplementedError("REST API creation coming soon")


def serve_dataset(
    dataset_path: str | Path,
    host: str = "0.0.0.0",
    port: int = 8000,
    server_type: str = "mcp",
) -> None:
    """
    Serve a ContextFrame dataset via MCP or REST API.

    Args:
        dataset_path: Path to the Lance dataset
        host: Host to bind to
        port: Port to bind to
        server_type: Type of server ("mcp" or "rest")
    """
    import uvicorn

    # Implementation placeholder
    raise NotImplementedError("Dataset serving coming soon")


__all__ = ["create_mcp_server", "create_mcp_tools", "create_rest_api", "serve_dataset"]

