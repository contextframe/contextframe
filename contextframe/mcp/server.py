"""Main MCP server implementation for ContextFrame."""

import asyncio
import logging
import signal
from typing import Optional
from dataclasses import dataclass

from contextframe.frame import FrameDataset
from contextframe.mcp.transport import StdioTransport
from contextframe.mcp.handlers import MessageHandler
from contextframe.mcp.tools import ToolRegistry
from contextframe.mcp.resources import ResourceRegistry
from contextframe.mcp.errors import DatasetNotFound


logger = logging.getLogger(__name__)


@dataclass
class MCPConfig:
    """Configuration for MCP server."""
    
    server_name: str = "contextframe"
    server_version: str = "0.1.0"
    protocol_version: str = "0.1.0"
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    shutdown_timeout: float = 5.0


class ContextFrameMCPServer:
    """MCP server for ContextFrame datasets.
    
    Provides standardized access to ContextFrame datasets through
    the Model Context Protocol, enabling LLMs and AI agents to
    interact with document collections.
    """

    def __init__(
        self,
        dataset_path: str,
        config: Optional[MCPConfig] = None
    ):
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
        self.dataset: Optional[FrameDataset] = None
        self.transport: Optional[StdioTransport] = None
        self.handler: Optional[MessageHandler] = None
        self.tools: Optional[ToolRegistry] = None
        self.resources: Optional[ResourceRegistry] = None

    async def setup(self):
        """Set up server components."""
        try:
            # Open dataset
            self.dataset = FrameDataset.open(self.dataset_path)
        except Exception as e:
            raise DatasetNotFound(self.dataset_path) from e
        
        # Initialize components
        self.transport = StdioTransport()
        self.handler = MessageHandler(self)
        self.tools = ToolRegistry(self.dataset)
        self.resources = ResourceRegistry(self.dataset)
        
        # Connect transport
        await self.transport.connect()
        
        logger.info(f"MCP server initialized for dataset: {self.dataset_path}")

    async def run(self):
        """Main server loop."""
        if not self.transport:
            await self.setup()
        
        # Set up signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )
        
        logger.info("MCP server running, waiting for messages...")
        
        try:
            # Process messages
            async for message in self.transport:
                if self._shutdown_requested:
                    break
                
                try:
                    response = await self.handler.handle(message)
                    if response:  # Don't send response for notifications
                        await self.transport.send_message(response)
                except Exception as e:
                    logger.exception("Error handling message")
                    # Error response already sent by handler
                    
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.exception("Server error")
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
            await self.transport.close()
        
        # Dataset cleanup if needed
        if self.dataset:
            # FrameDataset doesn't require explicit cleanup
            pass
        
        logger.info("Server cleanup complete")

    @classmethod
    async def start(cls, dataset_path: str, config: Optional[MCPConfig] = None):
        """Convenience method to start server."""
        server = cls(dataset_path, config)
        await server.run()


# Entry point for running as module
async def main():
    """Main entry point when running as module."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ContextFrame MCP Server"
    )
    parser.add_argument(
        "dataset",
        help="Path to Lance dataset"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Reduce noise from other loggers
    logging.getLogger("contextframe.frame").setLevel(logging.WARNING)
    
    try:
        await ContextFrameMCPServer.start(args.dataset)
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())