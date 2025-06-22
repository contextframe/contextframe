"""FastAPI/Starlette HTTP server implementation for MCP."""

import asyncio
import logging
from contextframe import FrameDataset
from contextframe.mcp.handlers import MessageHandler
from contextframe.mcp.schemas import (
    InitializeParams,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    ResourceReadParams,
    ToolCallParams,
)
from contextframe.mcp.transports.http.adapter import HttpAdapter
from contextframe.mcp.transports.http.auth import get_current_user, oauth2_scheme
from contextframe.mcp.transports.http.config import HTTPTransportConfig
from contextframe.mcp.transports.http.security import RateLimiter
from contextframe.mcp.transports.http.sse import SSEManager
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MCPHTTPServer:
    """HTTP server for MCP protocol using FastAPI."""

    def __init__(
        self,
        dataset: FrameDataset,
        config: HTTPTransportConfig | None = None,
    ):
        self.dataset = dataset
        self.config = config or HTTPTransportConfig()

        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(
                f"Invalid HTTP transport configuration: {'; '.join(errors)}"
            )

        # Create components
        self.adapter = HttpAdapter()
        self.handler = MessageHandler(dataset, self.adapter)
        self.sse_manager = SSEManager(
            max_connections=self.config.sse_max_connections,
            max_age_seconds=self.config.sse_max_age_seconds,
        )
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.rate_limit_requests_per_minute,
            burst=self.config.rate_limit_burst,
        )

        # Create FastAPI app
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.adapter.initialize()
            await self.sse_manager.start()
            logger.info(
                f"MCP HTTP server started on {self.config.host}:{self.config.port}"
            )
            if self.config.ssl_enabled:
                logger.info("SSL/TLS enabled")
            if self.config.auth_enabled:
                logger.info("Authentication enabled")
            yield
            # Shutdown
            await self.sse_manager.stop()
            await self.adapter.shutdown()
            logger.info("MCP HTTP server stopped")

        app = FastAPI(
            title="ContextFrame MCP Server",
            description="Model Context Protocol server for ContextFrame",
            version="1.0.0",
            lifespan=lifespan,
        )

        # Add CORS middleware if enabled
        if self.config.cors_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins,
                allow_credentials=self.config.cors_credentials,
                allow_methods=self.config.cors_methods,
                allow_headers=self.config.cors_headers,
            )

        # Add routes
        self._add_routes(app)

        return app

    def _add_routes(self, app: FastAPI) -> None:
        """Add all MCP routes to the app."""

        # Dependency for optional auth
        auth_dep = Depends(get_current_user) if self.config.auth_enabled else None

        # Health check endpoints
        @app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy"}

        @app.get("/ready")
        async def ready():
            """Readiness check endpoint."""
            # Check if dataset is accessible
            try:
                await asyncio.to_thread(lambda: len(self.dataset))
                return {"status": "ready"}
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Dataset not ready: {e}")

        # MCP JSON-RPC endpoint
        @app.post("/mcp/v1/jsonrpc")
        async def jsonrpc_endpoint(
            request: JSONRPCRequest, user: dict | None = auth_dep
        ):
            """Main JSON-RPC endpoint for MCP protocol."""
            # Apply rate limiting if enabled
            if self.config.rate_limit_enabled:
                if not await self.rate_limiter.check_rate_limit(
                    user["id"] if user else "anonymous"
                ):
                    return JSONRPCResponse(
                        id=request.id,
                        error=JSONRPCError(code=-32000, message="Rate limit exceeded"),
                    )

            # Handle the request
            try:
                response = await self.handler.handle_message(request.model_dump())
                return JSONRPCResponse(**response)
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                return JSONRPCResponse(
                    id=request.id,
                    error=JSONRPCError(
                        code=-32603, message="Internal error", data=str(e)
                    ),
                )

        # Convenience REST endpoints that wrap JSON-RPC
        @app.post("/mcp/v1/initialize")
        async def initialize(params: InitializeParams, user: dict | None = auth_dep):
            """Initialize MCP session."""
            request = JSONRPCRequest(
                method="initialize", params=params.model_dump(), id=1
            )
            return await jsonrpc_endpoint(request, user)

        @app.get("/mcp/v1/tools/list")
        async def list_tools(user: dict | None = auth_dep):
            """List available tools."""
            request = JSONRPCRequest(method="tools/list", id=1)
            return await jsonrpc_endpoint(request, user)

        @app.post("/mcp/v1/tools/call")
        async def call_tool(params: ToolCallParams, user: dict | None = auth_dep):
            """Call a tool."""
            request = JSONRPCRequest(
                method="tools/call", params=params.model_dump(), id=1
            )
            response = await jsonrpc_endpoint(request, user)

            # Check if this is a batch operation that returns an operation_id
            if (
                hasattr(response, "result")
                and isinstance(response.result, dict)
                and "operation_id" in response.result
            ):
                # Add operation_id to response headers for client convenience
                return JSONResponse(
                    content=response.model_dump(),
                    headers={"X-Operation-Id": response.result["operation_id"]},
                )

            return response

        @app.get("/mcp/v1/resources/list")
        async def list_resources(user: dict | None = auth_dep):
            """List available resources."""
            request = JSONRPCRequest(method="resources/list", id=1)
            return await jsonrpc_endpoint(request, user)

        @app.post("/mcp/v1/resources/read")
        async def read_resource(
            params: ResourceReadParams, user: dict | None = auth_dep
        ):
            """Read a resource."""
            request = JSONRPCRequest(
                method="resources/read", params=params.model_dump(), id=1
            )
            return await jsonrpc_endpoint(request, user)

        # SSE endpoints
        @app.get("/mcp/v1/sse/progress/{operation_id}")
        async def stream_progress(operation_id: str, user: dict | None = auth_dep):
            """Stream progress updates for an operation via SSE."""
            # Create SSE stream
            stream = await self.sse_manager.create_stream()

            async def event_generator():
                try:
                    async for event in self.adapter.stream_operation_progress(
                        operation_id
                    ):
                        yield await stream.send_json(
                            event, event_type=event.get("type")
                        )
                finally:
                    await self.sse_manager.close_stream(stream.client_id)

            return EventSourceResponse(event_generator())

        @app.get("/mcp/v1/sse/subscribe")
        async def subscribe_changes(
            resource_type: str = "documents",
            filter: str | None = None,
            user: dict | None = auth_dep,
        ):
            """Subscribe to dataset changes via SSE."""
            # Create subscription
            from contextframe.mcp.core.transport import Subscription

            subscription = Subscription(
                id=str(asyncio.create_task(asyncio.sleep(0)).get_name()),
                resource_type=resource_type,
                filter=filter,
            )

            # Create SSE stream
            stream = await self.sse_manager.create_stream()

            async def event_generator():
                try:
                    async for change in self.adapter.handle_subscription(subscription):
                        yield await stream.send_json(
                            change, event_type=change.get("type")
                        )
                finally:
                    await self.sse_manager.close_stream(stream.client_id)
                    self.adapter.cancel_subscription(subscription.id)

            return EventSourceResponse(event_generator())

        # Metrics endpoint
        @app.get("/metrics")
        async def metrics():
            """Prometheus-compatible metrics endpoint."""
            metrics_data = {
                "sse_active_connections": self.sse_manager.active_connections,
                "rate_limiter_stats": await self.rate_limiter.get_stats(),
                "dataset_size": len(self.dataset),
                "adapter_subscriptions": len(self.adapter._subscriptions),
            }

            # Format as Prometheus text format
            lines = []
            for key, value in metrics_data.items():
                lines.append(f"# TYPE {key} gauge")
                lines.append(f"{key} {value}")

            return Response(content="\n".join(lines), media_type="text/plain")

        # OpenAPI schema
        @app.get("/openapi.json")
        async def openapi():
            """Get OpenAPI schema."""
            return app.openapi()


async def create_http_server(
    dataset_path: str, config: HTTPTransportConfig | None = None, **kwargs
) -> MCPHTTPServer:
    """Create and configure an HTTP MCP server.

    Args:
        dataset_path: Path to the Lance dataset
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional server configuration

    Returns:
        Configured MCPHTTPServer instance
    """
    # Open dataset
    dataset = FrameDataset.open(dataset_path)

    # Create server
    server = MCPHTTPServer(
        dataset=dataset,
        config=config,
    )

    return server
