"""Transport layer for MCP server - handles stdio communication."""

import asyncio
import json
import sys
from collections.abc import AsyncIterator
from contextframe.mcp.errors import ParseError
from typing import Any, Dict, Optional


class StdioTransport:
    """Handles stdio communication for MCP using JSON-RPC 2.0 protocol."""

    def __init__(self):
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._running = False

    async def connect(self) -> None:
        """Initialize stdio streams for async communication."""
        loop = asyncio.get_event_loop()

        # Create async streams from stdin/stdout
        self._reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(self._reader)

        await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

        # For stdout, we'll use a transport/protocol pair
        w_transport, w_protocol = await loop.connect_write_pipe(
            lambda: asyncio.Protocol(), sys.stdout
        )
        self._writer = asyncio.StreamWriter(w_transport, w_protocol, self._reader, loop)

        self._running = True

    async def read_message(self) -> dict[str, Any]:
        """Read and parse a JSON-RPC message from stdin.

        Messages are expected to be newline-delimited JSON.
        """
        if not self._reader:
            raise RuntimeError("Transport not connected")

        try:
            # Read until newline
            line = await self._reader.readline()
            if not line:
                raise EOFError("Connection closed")

            # Decode and parse JSON
            message_str = line.decode('utf-8').strip()
            if not message_str:
                # Empty line, try again
                return await self.read_message()

            try:
                message = json.loads(message_str)
            except json.JSONDecodeError as e:
                raise ParseError({"error": str(e), "input": message_str})

            return message

        except Exception as e:
            if isinstance(e, (ParseError, EOFError)):
                raise
            raise ParseError({"error": str(e)})

    async def send_message(self, message: dict[str, Any]) -> None:
        """Send a JSON-RPC message to stdout."""
        if not self._writer:
            raise RuntimeError("Transport not connected")

        try:
            # Serialize to JSON and add newline
            message_str = json.dumps(message, separators=(',', ':')) + '\n'

            # Write to stdout
            self._writer.write(message_str.encode('utf-8'))
            await self._writer.drain()

        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    async def close(self) -> None:
        """Clean shutdown of transport."""
        self._running = False

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

        self._reader = None
        self._writer = None

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        """Async iterator for reading messages."""
        while self._running:
            try:
                message = await self.read_message()
                yield message
            except EOFError:
                # Connection closed, stop iteration
                break
            except Exception:
                # Let other exceptions propagate
                raise

    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self._reader is not None and self._writer is not None and self._running
