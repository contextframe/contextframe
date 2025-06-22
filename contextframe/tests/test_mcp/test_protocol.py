"""Test MCP protocol compliance."""

import asyncio
import json
import pytest
import tempfile
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.handlers import MessageHandler
from contextframe.mcp.resources import ResourceRegistry
from contextframe.mcp.server import ContextFrameMCPServer, MCPConfig
from contextframe.mcp.tools import ToolRegistry
from contextframe.mcp.transport import StdioTransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
async def test_dataset(tmp_path):
    """Create a test dataset."""
    dataset_path = tmp_path / "test.lance"
    dataset = FrameDataset.create(str(dataset_path))

    # Add some test documents
    records = [
        FrameRecord(
            text_content="Test document 1",
            metadata={"title": "Doc 1", "collection": "test"},
        ),
        FrameRecord(
            text_content="Test document 2",
            metadata={"title": "Doc 2", "collection": "test"},
        ),
    ]
    dataset.add_many(records)

    return str(dataset_path)


@pytest.fixture
async def mcp_server(test_dataset):
    """Create MCP server instance with HTTP as default transport."""
    # HTTP is the default transport as per current MCP specification
    config = MCPConfig(transport="http")
    server = ContextFrameMCPServer(test_dataset, config=config)
    # Manual setup without connecting transport
    server.dataset = FrameDataset.open(test_dataset)
    server.handler = MessageHandler(server)
    server.tools = ToolRegistry(server.dataset)
    server.resources = ResourceRegistry(server.dataset)
    # Skip transport setup for tests
    return server


class TestProtocolCompliance:
    """Test MCP protocol compliance."""

    @pytest.mark.asyncio
    async def test_initialization_handshake(self, mcp_server):
        """Test MCP initialization sequence."""
        # Create initialize request
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "0.1.0", "capabilities": {}},
            "id": 1,
        }

        # Handle request
        response = await mcp_server.handler.handle(request)

        # Verify response
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "0.1.0"
        assert response["result"]["capabilities"]["tools"] is True
        assert response["result"]["capabilities"]["resources"] is True
        assert response["result"]["serverInfo"]["name"] == "contextframe"

    @pytest.mark.asyncio
    async def test_method_not_found(self, mcp_server):
        """Test handling of unknown methods."""
        request = {"jsonrpc": "2.0", "method": "unknown_method", "params": {}, "id": 2}

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found
        assert "unknown_method" in response["error"]["message"]

    @pytest.mark.asyncio
    async def test_invalid_request(self, mcp_server):
        """Test handling of invalid requests."""
        # Missing jsonrpc field
        request = {"method": "initialize", "params": {}, "id": 3}

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request

    @pytest.mark.asyncio
    async def test_tools_list(self, mcp_server):
        """Test listing available tools."""
        # Initialize first
        await mcp_server.handler.handle(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "0.1.0", "capabilities": {}},
                "id": 1,
            }
        )

        # List tools
        request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 4}

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "result" in response
        assert "tools" in response["result"]

        # Verify expected tools
        tool_names = {tool["name"] for tool in response["result"]["tools"]}
        expected_tools = {
            "search_documents",
            "add_document",
            "get_document",
            "list_documents",
            "update_document",
            "delete_document",
        }
        assert expected_tools.issubset(tool_names)

    @pytest.mark.asyncio
    async def test_resources_list(self, mcp_server):
        """Test listing available resources."""
        request = {"jsonrpc": "2.0", "method": "resources/list", "params": {}, "id": 5}

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        assert "result" in response
        assert "resources" in response["result"]

        # Verify expected resources
        resource_uris = {res["uri"] for res in response["result"]["resources"]}
        expected_resources = {
            "contextframe://dataset/info",
            "contextframe://dataset/schema",
            "contextframe://dataset/stats",
            "contextframe://collections",
            "contextframe://relationships",
        }
        assert expected_resources.issubset(resource_uris)

    @pytest.mark.asyncio
    async def test_notification_no_response(self, mcp_server):
        """Test that notifications don't return responses."""
        # Notifications have no ID
        request = {"jsonrpc": "2.0", "method": "initialized", "params": {}}

        response = await mcp_server.handler.handle(request)

        # Notifications should return None (no response sent)
        assert response is None


class TestToolExecution:
    """Test tool execution through MCP."""

    @pytest.mark.asyncio
    async def test_search_documents_tool(self, mcp_server):
        """Test search_documents tool execution."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_documents",
                "arguments": {"query": "test", "search_type": "hybrid", "limit": 5},
            },
            "id": 10,
        }

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 10
        assert "result" in response
        assert "documents" in response["result"]
        assert "search_type_used" in response["result"]

    @pytest.mark.asyncio
    async def test_add_document_tool(self, mcp_server):
        """Test add_document tool execution."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add_document",
                "arguments": {
                    "content": "New test document",
                    "metadata": {"title": "New Doc"},
                    "generate_embedding": False,
                },
            },
            "id": 11,
        }

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 11
        assert "result" in response
        assert "document" in response["result"]
        assert response["result"]["document"]["content"] == "New test document"

    @pytest.mark.asyncio
    async def test_invalid_tool_params(self, mcp_server):
        """Test tool execution with invalid parameters."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_documents",
                "arguments": {
                    # Missing required 'query' parameter
                    "search_type": "text"
                },
            },
            "id": 12,
        }

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 12
        assert "error" in response
        assert response["error"]["code"] == -32602  # Invalid params


class TestResourceReading:
    """Test resource reading through MCP."""

    @pytest.mark.asyncio
    async def test_read_dataset_info(self, mcp_server):
        """Test reading dataset info resource."""
        request = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {"uri": "contextframe://dataset/info"},
            "id": 20,
        }

        response = await mcp_server.handler.handle(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 20
        assert "result" in response
        assert "contents" in response["result"]
        assert len(response["result"]["contents"]) > 0

        # Verify content structure
        content = response["result"]["contents"][0]
        assert content["uri"] == "contextframe://dataset/info"
        assert content["mimeType"] == "application/json"
        assert "text" in content

        # Parse JSON content
        info = json.loads(content["text"])
        assert "dataset_path" in info
        assert "storage_format" in info
        assert info["storage_format"] == "lance"
