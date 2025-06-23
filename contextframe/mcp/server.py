"""Main MCP server implementation for ContextFrame."""

import asyncio
import logging
import signal
from contextframe.frame import FrameDataset
from contextframe.mcp.core.transport import TransportAdapter
from contextframe.mcp.errors import DatasetNotFound
from contextframe.mcp.handlers import MessageHandler
from contextframe.mcp.resources import ResourceRegistry
from contextframe.mcp.tools import ToolRegistry
from contextframe.mcp.transports.stdio import StdioAdapter
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from contextframe.mcp.monitoring.integration import MonitoringSystem
    from contextframe.mcp.security.integration import SecurityMiddleware

logger = logging.getLogger(__name__)


@dataclass
class MCPConfig:
    """Configuration for MCP server."""

    server_name: str = "contextframe"
    server_version: str = "0.1.0"
    protocol_version: str = "0.1.0"
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    shutdown_timeout: float = 5.0

    # Transport configuration
    # HTTP is the primary transport for MCP as per current specification
    transport: Literal["stdio", "http", "both"] = "http"

    # HTTP-specific configuration
    http_host: str = "0.0.0.0"
    http_port: int = 8080
    http_cors_origins: list[str] = None
    http_auth_enabled: bool = False
    http_rate_limit: dict[str, int] = None
    http_ssl_cert: str | None = None
    http_ssl_key: str | None = None
    
    # Monitoring configuration
    monitoring_enabled: bool = True
    monitoring_retention_days: int = 30
    monitoring_flush_interval: int = 60
    pricing_config_path: str | None = None
    
    # Security configuration
    security_enabled: bool = True
    auth_providers: list[str] = None  # ["api_key", "oauth", "jwt"]
    anonymous_allowed: bool = False
    anonymous_permissions: list[str] = None
    api_keys_file: str | None = None
    oauth_config_file: str | None = None
    jwt_config_file: str | None = None
    audit_log_file: str | None = None
    audit_retention_days: int = 90


class ContextFrameMCPServer:
    """MCP server for ContextFrame datasets.

    Provides standardized access to ContextFrame datasets through
    the Model Context Protocol, enabling LLMs and AI agents to
    interact with document collections.
    """

    def __init__(self, dataset_path: str, config: MCPConfig | None = None):
        """Initialize MCP server.

        Args:
            dataset_path: Path to Lance dataset
            config: Server configuration
        """
        self.dataset_path = dataset_path
        self.config = config or MCPConfig()

        # Server state
        self._initialized = False
        self._shutdown_requested = False

        # Components (initialized in setup)
        self.dataset: FrameDataset | None = None
        self.transport: TransportAdapter | None = None
        self.handler: MessageHandler | None = None
        self.tools: ToolRegistry | None = None
        self.resources: ResourceRegistry | None = None
        self.monitoring: "MonitoringSystem" | None = None
        self.security: "SecurityMiddleware" | None = None

    async def setup(self):
        """Set up server components."""
        try:
            # Open dataset
            self.dataset = FrameDataset.open(self.dataset_path)
        except Exception as e:
            raise DatasetNotFound(self.dataset_path) from e

        # Initialize monitoring if enabled
        if self.config.monitoring_enabled:
            from contextframe.mcp.monitoring.collector import MetricsConfig
            from contextframe.mcp.monitoring.cost import PricingConfig
            from contextframe.mcp.monitoring.integration import (
                MonitoredMessageHandler,
                MonitoredToolRegistry,
                MonitoringSystem,
            )
            
            # Create monitoring config
            metrics_config = MetricsConfig(
                enabled=True,
                retention_days=self.config.monitoring_retention_days,
                flush_interval_seconds=self.config.monitoring_flush_interval
            )
            
            # Load pricing config if provided
            pricing_config = None
            if self.config.pricing_config_path:
                pricing_config = PricingConfig.from_file(self.config.pricing_config_path)
            else:
                pricing_config = PricingConfig()
            
            # Initialize monitoring system
            self.monitoring = MonitoringSystem(
                self.dataset,
                metrics_config,
                pricing_config
            )
            await self.monitoring.start()
        
        # Initialize security if enabled
        if self.config.security_enabled:
            await self._setup_security()

        # Initialize transport based on configuration
        if self.config.transport == "stdio":
            self.transport = StdioAdapter()
            
            # Use secured/monitored versions based on configuration
            if self.security:
                from contextframe.mcp.security.integration import SecuredMessageHandler
                self.handler = SecuredMessageHandler(self, self.security)
            elif self.monitoring:
                from contextframe.mcp.monitoring.integration import MonitoredMessageHandler
                self.handler = MonitoredMessageHandler(self, self.monitoring)
            else:
                self.handler = MessageHandler(self)
            
            if self.monitoring:
                from contextframe.mcp.monitoring.integration import MonitoredToolRegistry
                self.tools = MonitoredToolRegistry(self.dataset, self.transport, self.monitoring)
            else:
                self.tools = ToolRegistry(self.dataset, self.transport)
            
            self.resources = ResourceRegistry(self.dataset)
            await self.transport.initialize()
        elif self.config.transport == "http":
            await self._setup_http_transport()
        elif self.config.transport == "both":
            # For "both", we'll run HTTP server with stdio fallback
            await self._setup_http_transport()

        logger.info(
            f"MCP server initialized for dataset: {self.dataset_path} with {self.config.transport} transport"
            + (f" and monitoring enabled" if self.config.monitoring_enabled else "")
        )

    async def _setup_security(self):
        """Set up security components."""
        import json
        from contextframe.mcp.security import (
            APIKeyAuth,
            OAuth2Provider,
            OAuth2Config,
            JWTHandler,
            JWTConfig,
            MultiAuthProvider,
            AccessControl,
            RateLimiter,
            RateLimitConfig,
            AuditLogger,
            AuditConfig,
        )
        from contextframe.mcp.security.integration import SecurityMiddleware
        
        # Build auth providers
        auth_providers = []
        
        if not self.config.auth_providers:
            # Default to API key auth
            self.config.auth_providers = ["api_key"]
        
        for provider_type in self.config.auth_providers:
            if provider_type == "api_key" and self.config.api_keys_file:
                # Load API keys from file
                try:
                    with open(self.config.api_keys_file, "r") as f:
                        api_keys = json.load(f)
                    auth_providers.append(APIKeyAuth(api_keys))
                except Exception as e:
                    logger.warning(f"Failed to load API keys: {e}")
            
            elif provider_type == "oauth" and self.config.oauth_config_file:
                # Load OAuth config
                try:
                    with open(self.config.oauth_config_file, "r") as f:
                        oauth_data = json.load(f)
                    oauth_config = OAuth2Config(**oauth_data)
                    auth_providers.append(OAuth2Provider(oauth_config))
                except Exception as e:
                    logger.warning(f"Failed to load OAuth config: {e}")
            
            elif provider_type == "jwt" and self.config.jwt_config_file:
                # Load JWT config
                try:
                    with open(self.config.jwt_config_file, "r") as f:
                        jwt_data = json.load(f)
                    jwt_config = JWTConfig(**jwt_data)
                    auth_providers.append(JWTHandler(jwt_config))
                except Exception as e:
                    logger.warning(f"Failed to load JWT config: {e}")
        
        # Create multi-auth provider if multiple providers
        auth_provider = None
        if len(auth_providers) > 1:
            auth_provider = MultiAuthProvider(auth_providers)
        elif len(auth_providers) == 1:
            auth_provider = auth_providers[0]
        
        # Create access control
        access_control = AccessControl()
        
        # Create rate limiter
        rate_limiter = RateLimiter(RateLimitConfig())
        
        # Create audit logger
        audit_config = AuditConfig(
            storage_backend="file" if self.config.audit_log_file else "memory",
            file_path=self.config.audit_log_file,
            retention_days=self.config.audit_retention_days
        )
        audit_logger = AuditLogger(audit_config)
        
        # Create security middleware
        self.security = SecurityMiddleware(
            auth_provider=auth_provider,
            access_control=access_control,
            rate_limiter=rate_limiter,
            audit_logger=audit_logger,
            anonymous_allowed=self.config.anonymous_allowed,
            anonymous_permissions=set(self.config.anonymous_permissions or [])
        )
        
        await self.security.start()
        
        logger.info(
            f"Security initialized with providers: {self.config.auth_providers}"
            + f", anonymous_allowed: {self.config.anonymous_allowed}"
        )

    async def _setup_http_transport(self):
        """Set up HTTP transport and server."""
        from contextframe.mcp.transports.http import create_http_server
        from contextframe.mcp.transports.http.config import HTTPTransportConfig

        # Create HTTP config from MCP config
        http_config = HTTPTransportConfig(
            host=self.config.http_host,
            port=self.config.http_port,
            cors_origins=self.config.http_cors_origins or ["*"],
            auth_enabled=self.config.http_auth_enabled,
            rate_limit_requests_per_minute=self.config.http_rate_limit.get(
                "requests_per_minute", 60
            )
            if self.config.http_rate_limit
            else 60,
            rate_limit_burst=self.config.http_rate_limit.get("burst", 10)
            if self.config.http_rate_limit
            else 10,
            ssl_cert=self.config.http_ssl_cert,
            ssl_key=self.config.http_ssl_key,
            ssl_enabled=bool(self.config.http_ssl_cert and self.config.http_ssl_key),
        )

        self.http_server = await create_http_server(
            self.dataset_path,
            config=http_config,
        )

        # For compatibility, set transport to the HTTP adapter
        self.transport = self.http_server.adapter
        
        # Use secured/monitored versions based on configuration
        if self.security:
            from contextframe.mcp.security.integration import SecuredMessageHandler
            self.handler = SecuredMessageHandler(self, self.security)
        elif self.monitoring:
            from contextframe.mcp.monitoring.integration import MonitoredMessageHandler
            self.handler = MonitoredMessageHandler(self, self.monitoring)
        else:
            self.handler = self.http_server.handler
        
        if self.monitoring:
            from contextframe.mcp.monitoring.integration import MonitoredToolRegistry
            self.tools = MonitoredToolRegistry(self.dataset, self.transport, self.monitoring)
        else:
            self.tools = ToolRegistry(self.dataset, self.transport)
        
        self.resources = ResourceRegistry(self.dataset)

    async def run(self):
        """Main server loop."""
        if not self.transport and not hasattr(self, 'http_server'):
            await self.setup()

        # Set up signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        if self.config.transport == "stdio":
            logger.info(
                "MCP server running with stdio transport, waiting for messages..."
            )
            await self._run_stdio()
        elif self.config.transport == "http" or self.config.transport == "both":
            logger.info(
                f"MCP server running with HTTP transport on {self.config.http_host}:{self.config.http_port}"
            )
            await self._run_http()

    async def _run_stdio(self):
        """Run stdio transport loop."""
        try:
            # Process messages
            while not self._shutdown_requested:
                message = await self.transport.receive_message()
                if message is None:
                    break

                try:
                    response = await self.handler.handle(message)
                    if response:  # Don't send response for notifications
                        await self.transport.send_message(response)
                except Exception:
                    logger.exception("Error handling message")
                    # Error response already sent by handler

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception:
            logger.exception("Server error")
            raise
        finally:
            await self.cleanup()

    async def _run_http(self):
        """Run HTTP server."""
        import uvicorn
        from contextframe.mcp.transports.http.security import SecurityConfig

        try:
            # Get SSL config if enabled
            ssl_config = {}
            if self.config.http_ssl_cert and self.config.http_ssl_key:
                ssl_config = {
                    "ssl_keyfile": self.config.http_ssl_key,
                    "ssl_certfile": self.config.http_ssl_cert,
                }

            # Run uvicorn server
            config = uvicorn.Config(
                app=self.http_server.app,
                host=self.config.http_host,
                port=self.config.http_port,
                log_level="info",
                **ssl_config,
            )
            server = uvicorn.Server(config)

            # Run server with proper shutdown handling
            await server.serve()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception:
            logger.exception("HTTP server error")
            raise
        finally:
            await self.cleanup()

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True

        # Give ongoing operations time to complete
        await asyncio.sleep(0.1)

    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up server resources")

        if self.transport:
            await self.transport.shutdown()

        # Stop monitoring if enabled
        if self.monitoring:
            logger.info("Stopping monitoring system")
            await self.monitoring.stop()
        
        # Stop security if enabled
        if self.security:
            logger.info("Stopping security system")
            await self.security.stop()

        # Dataset cleanup if needed
        if self.dataset:
            # FrameDataset doesn't require explicit cleanup
            pass

        logger.info("Server cleanup complete")

    @classmethod
    async def start(cls, dataset_path: str, config: MCPConfig | None = None):
        """Convenience method to start server."""
        server = cls(dataset_path, config)
        await server.run()


# Entry point for running as module
async def main():
    """Main entry point when running as module."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ContextFrame MCP Server")
    parser.add_argument("dataset", help="Path to Lance dataset")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "http", "both"],
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="HTTP server port (default: 8080)"
    )
    parser.add_argument(
        "--cors-origins", nargs="*", help="CORS allowed origins (default: *)"
    )
    parser.add_argument(
        "--auth", action="store_true", help="Enable OAuth 2.1 authentication"
    )
    parser.add_argument("--ssl-cert", help="Path to SSL certificate file")
    parser.add_argument("--ssl-key", help="Path to SSL key file")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()],
    )

    # Reduce noise from other loggers
    logging.getLogger("contextframe.frame").setLevel(logging.WARNING)

    # Create configuration
    config = MCPConfig(
        transport=args.transport,
        http_host=args.host,
        http_port=args.port,
        http_cors_origins=args.cors_origins,
        http_auth_enabled=args.auth,
        http_ssl_cert=args.ssl_cert,
        http_ssl_key=args.ssl_key,
    )

    try:
        await ContextFrameMCPServer.start(args.dataset, config)
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
