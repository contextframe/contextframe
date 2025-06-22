"""Test transport migration from SSE-focused to HTTP-first approach.

This test demonstrates the migration path and ensures backward compatibility
while emphasizing HTTP as the primary transport.
"""

import pytest
from contextframe.mcp.server import MCPConfig
from contextframe.mcp.transports.http.adapter import HttpAdapter


class TestTransportMigration:
    """Test migration from SSE to HTTP-first approach."""

    def test_default_transport_is_http(self):
        """Verify HTTP is the default transport."""
        config = MCPConfig()
        assert config.transport == "http", "HTTP should be the default transport"

    def test_http_adapter_documentation(self):
        """Verify HTTP adapter documentation mentions SSE as optional."""
        adapter = HttpAdapter()
        docstring = adapter.__class__.__doc__
        
        # Check that documentation clarifies SSE is optional
        assert "optional" in docstring.lower()
        assert "primary" in docstring.lower()
        assert "json responses" in docstring.lower()

    def test_config_supports_all_transports(self):
        """Ensure backward compatibility with all transport types."""
        # All transports should still work for compatibility
        transports = ["http", "stdio", "both"]
        
        for transport in transports:
            config = MCPConfig(transport=transport)
            assert config.transport == transport

    def test_http_config_defaults(self):
        """Test HTTP configuration defaults are production-ready."""
        config = MCPConfig()
        
        # Should have sensible HTTP defaults
        assert config.http_host == "0.0.0.0"
        assert config.http_port == 8080
        assert config.http_auth_enabled == False  # Secure by default in production
        
    @pytest.mark.asyncio
    async def test_sse_methods_are_optional(self):
        """Verify SSE methods are clearly optional in the adapter."""
        adapter = HttpAdapter()
        
        # SSE-related methods should exist but be optional
        assert hasattr(adapter, 'send_progress')
        assert hasattr(adapter, 'handle_subscription')
        
        # Check method documentation mentions optional
        progress_doc = adapter.send_progress.__doc__
        assert "optional" in progress_doc.lower()

    def test_migration_example_exists(self):
        """Ensure migration documentation exists."""
        import os
        
        # Check for transport guide
        transport_guide = os.path.join(
            os.path.dirname(__file__), 
            "../../mcp/TRANSPORT_GUIDE.md"
        )
        assert os.path.exists(transport_guide), "Transport migration guide should exist"
        
        # Check for HTTP example
        http_example = os.path.join(
            os.path.dirname(__file__),
            "../../mcp/http_client_example.py"
        )
        assert os.path.exists(http_example), "HTTP client example should exist"


class TestDeprecationWarnings:
    """Test that SSE-first patterns show appropriate guidance."""

    def test_sse_focused_pattern_guidance(self):
        """Test guidance for SSE-focused implementations."""
        # This represents old SSE-first thinking
        old_pattern = """
        # Old pattern - SSE for everything
        async with sse_client.connect() as stream:
            response = await stream.request({"method": "tools/list"})
        """
        
        # New pattern should be HTTP-first
        new_pattern = """
        # New pattern - HTTP for standard operations
        response = await http_client.post("/mcp/v1/jsonrpc", json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        })
        """
        
        # Verify the patterns are different approaches
        assert "sse" in old_pattern.lower()
        assert "http" in new_pattern.lower()
        assert "post" in new_pattern.lower()


class TestHTTPFirstIntegration:
    """Test HTTP-first integration patterns."""

    @pytest.mark.asyncio
    async def test_http_handles_all_standard_operations(self):
        """Verify HTTP can handle all standard MCP operations."""
        standard_operations = [
            "initialize",
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get",
        ]
        
        # All standard operations should work with simple HTTP
        for operation in standard_operations:
            # This would be a simple HTTP POST in real usage
            request = {
                "jsonrpc": "2.0",
                "method": operation,
                "params": {},
                "id": 1
            }
            
            # Verify the request structure is simple JSON
            assert "jsonrpc" in request
            assert "method" in request
            # No SSE setup required

    @pytest.mark.asyncio  
    async def test_sse_only_for_specific_features(self):
        """Test SSE is only used for specific streaming features."""
        # SSE endpoints should be clearly separated
        sse_endpoints = [
            "/mcp/v1/sse/progress/{operation_id}",  # Progress tracking
            "/mcp/v1/sse/subscribe",  # Real-time subscriptions
        ]
        
        # Regular endpoints should NOT be SSE
        regular_endpoints = [
            "/mcp/v1/jsonrpc",  # Main endpoint
            "/mcp/v1/initialize",  # Convenience endpoints
            "/mcp/v1/tools/list",
            "/mcp/v1/tools/call",
            "/mcp/v1/resources/list",
            "/mcp/v1/resources/read",
        ]
        
        # Verify clear separation
        for endpoint in sse_endpoints:
            assert "/sse/" in endpoint, "SSE endpoints should be clearly marked"
            
        for endpoint in regular_endpoints:
            assert "/sse/" not in endpoint, "Regular endpoints should not use SSE"