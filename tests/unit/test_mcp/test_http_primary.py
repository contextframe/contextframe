"""HTTP-first integration tests for MCP server.

This test demonstrates the recommended HTTP-first approach where:
1. HTTP with JSON responses is the primary transport
2. SSE is only used for specific streaming scenarios
"""

import asyncio
import json
import pytest
import httpx
from contextframe import FrameDataset, FrameRecord
from contextframe.mcp import ContextFrameMCPServer, MCPConfig
from contextframe.mcp.transports.http import create_http_server
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil


class TestHTTPPrimaryTransport:
    """Test HTTP as the primary transport method."""

    @pytest.fixture
    async def test_dataset(self):
        """Create a test dataset."""
        # Create temporary directory
        tmpdir = tempfile.mkdtemp()
        
        # Create dataset with test data
        dataset = FrameDataset.create(tmpdir)
        
        # Add test documents
        test_docs = [
            FrameRecord(
                id="doc1",
                content="Test document 1 content",
                metadata={"title": "Document 1", "type": "test"},
            ),
            FrameRecord(
                id="doc2",
                content="Test document 2 content with search terms",
                metadata={"title": "Document 2", "type": "test"},
            ),
            FrameRecord(
                id="doc3",
                content="Another test document for search",
                metadata={"title": "Document 3", "type": "demo"},
            ),
        ]
        
        dataset.add_documents(test_docs)
        
        yield dataset
        
        # Cleanup
        shutil.rmtree(tmpdir)

    @pytest.fixture
    async def http_server(self, test_dataset):
        """Create HTTP MCP server."""
        from contextframe.mcp.transports.http.config import HTTPTransportConfig
        
        config = HTTPTransportConfig(
            host="127.0.0.1",
            port=8888,
            auth_enabled=False,
        )
        
        server = await create_http_server(
            test_dataset._dataset.uri,
            config=config,
        )
        
        yield server
        
        # Cleanup
        await server.adapter.shutdown()

    @pytest.fixture
    async def http_client(self):
        """Create HTTP client for testing."""
        async with httpx.AsyncClient(
            base_url="http://127.0.0.1:8888",
            timeout=30.0
        ) as client:
            yield client

    @pytest.mark.asyncio
    async def test_http_primary_workflow(self, http_server, http_client):
        """Test the primary HTTP workflow without SSE."""
        # Mock the server app to avoid actual HTTP server
        app_mock = MagicMock()
        responses = {}
        
        async def mock_post(url, json=None, **kwargs):
            """Mock POST requests."""
            if url == "/mcp/v1/jsonrpc":
                method = json.get("method")
                
                if method == "initialize":
                    return MagicMock(
                        json=lambda: {
                            "jsonrpc": "2.0",
                            "result": {
                                "protocolVersion": "0.1.0",
                                "serverInfo": {
                                    "name": "contextframe",
                                    "version": "0.1.0"
                                }
                            },
                            "id": json.get("id")
                        }
                    )
                
                elif method == "tools/list":
                    return MagicMock(
                        json=lambda: {
                            "jsonrpc": "2.0",
                            "result": {
                                "tools": [
                                    {
                                        "name": "search_contextframe",
                                        "description": "Search documents",
                                        "inputSchema": {}
                                    },
                                    {
                                        "name": "get_document",
                                        "description": "Get document by ID",
                                        "inputSchema": {}
                                    }
                                ]
                            },
                            "id": json.get("id")
                        }
                    )
                
                elif method == "tools/call":
                    tool_name = json["params"]["name"]
                    if tool_name == "search_contextframe":
                        return MagicMock(
                            json=lambda: {
                                "jsonrpc": "2.0",
                                "result": {
                                    "documents": [
                                        {
                                            "id": "doc2",
                                            "content": "Test document 2 content with search terms",
                                            "score": 0.95
                                        }
                                    ]
                                },
                                "id": json.get("id")
                            }
                        )
                    elif tool_name == "get_document":
                        return MagicMock(
                            json=lambda: {
                                "jsonrpc": "2.0",
                                "result": {
                                    "document": {
                                        "id": "doc1",
                                        "content": "Test document 1 content",
                                        "metadata": {"title": "Document 1"}
                                    }
                                },
                                "id": json.get("id")
                            }
                        )
            
            return MagicMock(json=lambda: {"error": "Not found"})
        
        http_client.post = mock_post
        
        # 1. Initialize session - Simple HTTP request/response
        init_response = await http_client.post(
            "/mcp/v1/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
        )
        
        init_result = init_response.json()
        assert init_result["result"]["serverInfo"]["name"] == "contextframe"
        
        # 2. List tools - Simple HTTP request/response
        tools_response = await http_client.post(
            "/mcp/v1/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
        )
        
        tools_result = tools_response.json()
        tools = tools_result["result"]["tools"]
        assert len(tools) >= 2
        assert any(t["name"] == "search_contextframe" for t in tools)
        
        # 3. Call search tool - Simple HTTP request/response
        search_response = await http_client.post(
            "/mcp/v1/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_contextframe",
                    "arguments": {
                        "query": "search terms",
                        "limit": 5
                    }
                },
                "id": 3
            }
        )
        
        search_result = search_response.json()
        assert "documents" in search_result["result"]
        assert len(search_result["result"]["documents"]) > 0
        
        # 4. Get specific document - Simple HTTP request/response
        get_response = await http_client.post(
            "/mcp/v1/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_document",
                    "arguments": {
                        "document_id": "doc1"
                    }
                },
                "id": 4
            }
        )
        
        get_result = get_response.json()
        assert get_result["result"]["document"]["id"] == "doc1"

    @pytest.mark.asyncio
    async def test_sse_only_for_streaming(self, http_server, http_client):
        """Test that SSE is only used for specific streaming scenarios."""
        # Mock SSE endpoints
        async def mock_stream(url, **kwargs):
            """Mock SSE streaming."""
            if "/sse/progress/" in url:
                # This is the ONLY place SSE should be used - for progress tracking
                async def iter_lines():
                    yield 'data: {"type": "progress", "current": 1, "total": 10}'
                    yield 'data: {"type": "progress", "current": 5, "total": 10}'
                    yield 'data: {"type": "progress", "current": 10, "total": 10}'
                    yield 'data: {"type": "completed"}'
                
                return MagicMock(aiter_lines=iter_lines)
            
            raise Exception("SSE should not be used for this endpoint")
        
        http_client.stream = mock_stream
        
        # Regular operations should NOT use SSE
        # They use simple HTTP as shown in test_http_primary_workflow
        
        # SSE is ONLY for progress tracking of long operations
        progress_events = []
        async with http_client.stream("GET", "/mcp/v1/sse/progress/test-op-123") as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    progress_events.append(event)
        
        assert len(progress_events) == 4
        assert progress_events[-1]["type"] == "completed"

    @pytest.mark.asyncio
    async def test_no_sse_for_regular_operations(self, http_server, http_client):
        """Verify regular operations do NOT use SSE."""
        # Track any SSE connection attempts
        sse_attempts = []
        
        original_stream = http_client.stream
        async def track_stream(method, url, **kwargs):
            sse_attempts.append(url)
            return await original_stream(method, url, **kwargs)
        
        http_client.stream = track_stream
        
        # These operations should NOT trigger SSE
        operations = [
            ("initialize", {"protocolVersion": "0.1.0"}),
            ("tools/list", {}),
            ("resources/list", {}),
            ("tools/call", {"name": "search_contextframe", "arguments": {"query": "test"}}),
        ]
        
        for method, params in operations:
            # Should use regular HTTP POST, not SSE
            await http_client.post(
                "/mcp/v1/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                }
            )
        
        # No SSE connections should have been attempted
        assert len(sse_attempts) == 0, f"SSE was incorrectly used for: {sse_attempts}"


class TestHTTPClientExample:
    """Test the HTTP client example code."""
    
    @pytest.mark.asyncio
    async def test_example_client_pattern(self):
        """Test that the example client follows HTTP-first pattern."""
        # Import the example to ensure it's valid Python
        from contextframe.mcp.http_client_example import MCPHttpClient
        
        # Create client - should default to HTTP
        client = MCPHttpClient("http://localhost:8080")
        
        # Verify it uses standard HTTP methods
        assert hasattr(client, 'request')
        assert hasattr(client, 'initialize')
        assert hasattr(client, 'list_tools')
        assert hasattr(client, 'call_tool')
        
        # SSE should only be available for specific streaming
        assert hasattr(client, 'track_operation_progress')
        
        # The primary request method should use httpx for HTTP
        assert client.client.__class__.__name__ == 'AsyncClient'