"""Message handlers for MCP server."""

import logging
from typing import Any, Dict, Optional
from pydantic import ValidationError

from contextframe.mcp.errors import (
    InvalidRequest,
    MethodNotFound,
    MCPError,
    InvalidParams
)
from contextframe.mcp.schemas import (
    InitializeParams,
    InitializeResult,
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    MCPCapabilities,
    ToolCallParams,
    ResourceReadParams
)


logger = logging.getLogger(__name__)


class MessageHandler:
    """Routes JSON-RPC messages to appropriate handlers."""

    def __init__(self, server: "ContextFrameMCPServer"):
        self.server = server
        self._method_handlers = {
            "initialize": self.handle_initialize,
            "initialized": self.handle_initialized,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tool_call,
            "resources/list": self.handle_resources_list,
            "resources/read": self.handle_resource_read,
            "shutdown": self.handle_shutdown,
        }

    async def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC message and return response."""
        try:
            # Parse request
            try:
                request = JSONRPCRequest(**message)
            except Exception as e:
                raise InvalidRequest(f"Invalid request format: {str(e)}")

            # Check method exists
            if request.method not in self._method_handlers:
                raise MethodNotFound(request.method)

            # Route to handler
            handler = self._method_handlers[request.method]
            result = await handler(request.params or {})

            # Build response (notifications don't get responses)
            if request.id is None:
                return None
                
            response = JSONRPCResponse(
                jsonrpc="2.0",
                result=result,
                id=request.id
            )

        except MCPError as e:
            # MCP-specific errors
            response = JSONRPCResponse(
                jsonrpc="2.0",
                error=JSONRPCError(**e.to_json_rpc()),
                id=message.get("id")
            )
        except Exception as e:
            # Unexpected errors
            logger.exception("Unexpected error handling message")
            error = MCPError(
                code=-32603,
                message=f"Internal error: {str(e)}"
            )
            response = JSONRPCResponse(
                jsonrpc="2.0",
                error=JSONRPCError(**error.to_json_rpc()),
                id=message.get("id")
            )

        return response.model_dump(exclude_none=True)

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization handshake."""
        try:
            init_params = InitializeParams(**params)
        except ValidationError as e:
            raise InvalidParams(f"Invalid initialize parameters: {str(e)}")
        
        # Initialize server state
        self.server._initialized = True
        
        # Build response
        result = InitializeResult(
            protocolVersion="0.1.0",  # MCP protocol version
            capabilities=MCPCapabilities(
                tools=True,
                resources=True,
                prompts=False,  # Not implemented yet
                logging=False   # Not implemented yet
            ),
            serverInfo={
                "name": "contextframe",
                "version": "0.1.0",
                "description": "MCP server for ContextFrame datasets"
            }
        )
        
        return result.model_dump()

    async def handle_initialized(self, params: Dict[str, Any]) -> None:
        """Handle initialized notification."""
        # Client has confirmed initialization
        logger.info("MCP client initialized")
        return None  # Notifications don't return results

    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools."""
        tools = self.server.tools.list_tools()
        return {"tools": [tool.model_dump() for tool in tools]}

    async def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        tool_params = ToolCallParams(**params)
        result = await self.server.tools.call_tool(
            tool_params.name,
            tool_params.arguments
        )
        return result

    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available resources."""
        resources = self.server.resources.list_resources()
        return {"resources": [resource.model_dump() for resource in resources]}

    async def handle_resource_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource."""
        resource_params = ResourceReadParams(**params)
        content = await self.server.resources.read_resource(resource_params.uri)
        return {"contents": [content]}

    async def handle_shutdown(self, params: Dict[str, Any]) -> None:
        """Handle shutdown request."""
        logger.info("Shutdown requested")
        self.server._shutdown_requested = True
        return None  # Shutdown is a notification