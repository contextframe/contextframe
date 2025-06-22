"""Tests for HTTP transport implementation."""

import asyncio
import pytest
from contextframe.mcp.core.transport import Progress, Subscription
from contextframe.mcp.transports.http.adapter import HttpAdapter
from contextframe.mcp.transports.http.config import HTTPTransportConfig
from contextframe.mcp.transports.http.sse import SSEManager, SSEStream
from unittest.mock import AsyncMock, MagicMock


class TestHttpAdapter:
    """Test HttpAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create an HttpAdapter instance."""
        return HttpAdapter()

    @pytest.mark.asyncio
    async def test_initialize_shutdown(self, adapter):
        """Test adapter initialization and shutdown."""
        await adapter.initialize()
        assert adapter._active_streams == {}
        assert adapter._operation_progress == {}

        await adapter.shutdown()
        assert len(adapter._active_streams) == 0

    @pytest.mark.asyncio
    async def test_send_progress(self, adapter):
        """Test sending progress updates."""
        # Create a mock progress handler
        progress_received = []

        async def handler(progress):
            progress_received.append(progress)

        adapter.add_progress_handler(handler)

        # Send progress
        progress = Progress(
            operation="test_op",
            current=1,
            total=10,
            status="Testing",
            details={"operation_id": "test-123"},
        )
        await adapter.send_progress(progress)

        # Check handler was called
        assert len(progress_received) == 1
        assert progress_received[0] == progress

    @pytest.mark.asyncio
    async def test_create_operation(self, adapter):
        """Test creating and completing operations."""
        # Create operation
        op_id = await adapter.create_operation("test_operation")
        assert op_id in adapter._active_operations
        assert op_id in adapter._operation_progress

        # Complete operation
        await adapter.complete_operation(op_id)
        assert op_id not in adapter._active_operations

    @pytest.mark.asyncio
    async def test_stream_operation_progress(self, adapter):
        """Test streaming operation progress."""
        # Create operation
        op_id = await adapter.create_operation("test_operation")

        # Stream progress in background
        async def stream_progress():
            events = []
            async for event in adapter.stream_operation_progress(op_id):
                events.append(event)
                if event.get("type") == "complete":
                    break
            return events

        # Start streaming
        stream_task = asyncio.create_task(stream_progress())

        # Send some progress
        await adapter.send_progress(
            Progress(
                operation="test_op",
                current=5,
                total=10,
                status="Halfway",
                details={"operation_id": op_id},
            )
        )

        # Complete operation
        await adapter.complete_operation(op_id)

        # Get results
        events = await stream_task
        assert len(events) >= 2  # At least progress and complete events
        assert events[-1]["type"] == "complete"

    @pytest.mark.asyncio
    async def test_subscription_handling(self, adapter):
        """Test subscription creation and notification."""
        # Create subscription
        sub = Subscription(
            id="test-sub", resource_type="documents", filter='{"type": "test"}'
        )

        # Handle subscription
        events = []

        async def collect_events():
            async for event in adapter.handle_subscription(sub):
                events.append(event)
                if len(events) >= 2:  # Initial + one change
                    break

        # Start collecting
        collect_task = asyncio.create_task(collect_events())

        # Wait for subscription to be registered
        await asyncio.sleep(0.1)

        # Send a change notification
        await adapter.notify_change(
            {"resource_type": "documents", "type": "test", "change": "created"}
        )

        # Cancel subscription
        adapter.cancel_subscription(sub.id)

        # Wait for task to complete
        try:
            await asyncio.wait_for(collect_task, timeout=1.0)
        except TimeoutError:
            collect_task.cancel()

        # Check events
        assert len(events) >= 1
        assert events[0]["type"] == "subscription_created"


class TestSSEStream:
    """Test SSEStream class."""

    @pytest.fixture
    def stream(self):
        """Create an SSEStream instance."""
        return SSEStream()

    @pytest.mark.asyncio
    async def test_send_event(self, stream):
        """Test sending SSE events."""
        # Send simple event
        result = await stream.send_event("Hello World")
        assert "data: Hello World" in result
        assert result.endswith("\n\n")

        # Send JSON event
        result = await stream.send_json({"key": "value"}, event_type="test")
        assert "event: test" in result
        assert 'data: {"key": "value"}' in result

    @pytest.mark.asyncio
    async def test_send_keepalive(self, stream):
        """Test sending keepalive messages."""
        result = await stream.send_keepalive()
        assert result.startswith(": keepalive")
        assert result.endswith("\n\n")

    @pytest.mark.asyncio
    async def test_stream_closed(self, stream):
        """Test stream closure."""
        await stream.close()
        assert stream.is_closed

        # Should raise error when trying to send after close
        with pytest.raises(RuntimeError):
            await stream.send_event("test")


class TestSSEManager:
    """Test SSEManager class."""

    @pytest.fixture
    async def manager(self):
        """Create and start an SSEManager instance."""
        manager = SSEManager(max_connections=10)
        await manager.start()
        yield manager
        await manager.stop()

    @pytest.mark.asyncio
    async def test_create_stream(self, manager):
        """Test creating streams."""
        stream1 = await manager.create_stream()
        assert stream1.client_id in manager.streams

        stream2 = await manager.create_stream("custom-id")
        assert stream2.client_id == "custom-id"
        assert len(manager.streams) == 2

    @pytest.mark.asyncio
    async def test_max_connections(self, manager):
        """Test connection limit enforcement."""
        # Create max connections
        for i in range(10):
            await manager.create_stream(f"stream-{i}")

        # Should raise error on next connection
        with pytest.raises(RuntimeError, match="Maximum connections"):
            await manager.create_stream()

    @pytest.mark.asyncio
    async def test_close_stream(self, manager):
        """Test closing streams."""
        stream = await manager.create_stream("test-stream")
        assert "test-stream" in manager.streams

        await manager.close_stream("test-stream")
        assert "test-stream" not in manager.streams
        assert stream.is_closed


class TestHTTPTransportConfig:
    """Test HTTPTransportConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HTTPTransportConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.cors_enabled is True
        assert config.auth_enabled is False
        assert config.rate_limit_enabled is True

    def test_validation(self):
        """Test configuration validation."""
        # Valid config
        config = HTTPTransportConfig()
        errors = config.validate()
        assert len(errors) == 0

        # Invalid port
        config = HTTPTransportConfig(port=70000)
        errors = config.validate()
        assert any("port" in e for e in errors)

        # Auth without secret
        config = HTTPTransportConfig(auth_enabled=True)
        errors = config.validate()
        assert any("secret key" in e for e in errors)

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = HTTPTransportConfig(
            host="localhost", port=8000, auth_enabled=True, auth_secret_key="secret"
        )

        data = config.to_dict()
        assert data["server"]["host"] == "localhost"
        assert data["server"]["port"] == 8000
        assert data["auth"]["enabled"] is True

    def test_from_env(self, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("MCP_HTTP_HOST", "127.0.0.1")
        monkeypatch.setenv("MCP_HTTP_PORT", "9000")
        monkeypatch.setenv("MCP_HTTP_AUTH_ENABLED", "true")
        monkeypatch.setenv("MCP_HTTP_AUTH_SECRET_KEY", "env-secret")

        config = HTTPTransportConfig.from_env()
        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.auth_enabled is True
        assert config.auth_secret_key == "env-secret"
