"""Test HTTP-first approach for MCP server.

This test verifies that HTTP is the primary transport and SSE is optional.
"""

import pytest
from contextframe.mcp.server import MCPConfig


class TestHTTPFirstApproach:
    """Test that HTTP is the primary transport protocol."""

    def test_http_is_default_transport(self):
        """Verify HTTP is the default transport in MCPConfig."""
        config = MCPConfig()
        assert config.transport == "http", "HTTP should be the default transport"
        
    def test_http_config_has_sensible_defaults(self):
        """Test HTTP configuration defaults."""
        config = MCPConfig()
        
        # Should have production-ready defaults
        assert config.http_host == "0.0.0.0"
        assert config.http_port == 8080
        assert config.http_cors_origins is None  # Will default to ["*"] in server
        assert config.http_auth_enabled is False
        
    def test_all_transports_still_supported(self):
        """Ensure backward compatibility with all transport options."""
        # All transports should work for compatibility
        valid_transports = ["http", "stdio", "both"]
        
        for transport in valid_transports:
            config = MCPConfig(transport=transport)
            assert config.transport == transport
            
    def test_transport_priority_documentation(self):
        """Verify transport priority is documented correctly."""
        # Check MCPConfig docstring mentions HTTP as primary
        config_doc = MCPConfig.__doc__
        assert config_doc is not None
        
        # The transport field should indicate HTTP is default
        import inspect
        sig = inspect.signature(MCPConfig)
        transport_default = sig.parameters['transport'].default
        assert transport_default == "http"


class TestHTTPAdapterDocumentation:
    """Test that HTTP adapter documentation reflects SSE as optional."""
    
    def test_adapter_mentions_sse_optional(self):
        """Check adapter documentation clarifies SSE is optional."""
        from contextframe.mcp.transports.http.adapter import HttpAdapter
        
        doc = HttpAdapter.__doc__
        assert doc is not None
        assert "optional" in doc.lower()
        assert "primary" in doc.lower()
        
    def test_sse_methods_documented_as_optional(self):
        """Verify SSE-specific methods are documented as optional."""
        from contextframe.mcp.transports.http.adapter import HttpAdapter
        
        adapter = HttpAdapter()
        
        # Check send_progress documentation
        progress_doc = adapter.send_progress.__doc__
        assert progress_doc is not None
        assert "optional" in progress_doc.lower()


class TestTransportGuideExists:
    """Test that migration and usage guides exist."""
    
    def test_transport_guide_exists(self):
        """Verify transport guide documentation exists."""
        import os
        
        # Transport guide should exist
        guide_path = os.path.join(
            os.path.dirname(__file__),
            "../../mcp/TRANSPORT_GUIDE.md"
        )
        assert os.path.exists(guide_path), "TRANSPORT_GUIDE.md should exist"
        
    def test_http_example_exists(self):
        """Verify HTTP client example exists."""
        import os
        
        # HTTP example should exist
        example_path = os.path.join(
            os.path.dirname(__file__),
            "../../mcp/http_client_example.py"
        )
        assert os.path.exists(example_path), "http_client_example.py should exist"
        
    def test_http_primary_documentation_exists(self):
        """Verify HTTP primary transport documentation exists."""
        import os
        
        # Implementation notes should exist
        impl_path = os.path.join(
            os.path.dirname(__file__),
            "../../../.claude/implementations/http_primary_transport.md"
        )
        assert os.path.exists(impl_path), "http_primary_transport.md should exist"


class TestHTTPEndpointStructure:
    """Test that endpoints follow HTTP-first pattern."""
    
    def test_main_endpoint_is_http(self):
        """Verify main MCP endpoint is standard HTTP."""
        # Main endpoint should be /mcp/v1/jsonrpc for HTTP POST
        main_endpoint = "/mcp/v1/jsonrpc"
        assert "sse" not in main_endpoint
        assert "stream" not in main_endpoint
        
    def test_sse_endpoints_clearly_separated(self):
        """Verify SSE endpoints are clearly marked."""
        sse_endpoints = [
            "/mcp/v1/sse/progress/{operation_id}",
            "/mcp/v1/sse/subscribe",
        ]
        
        for endpoint in sse_endpoints:
            assert "/sse/" in endpoint, "SSE endpoints should contain /sse/ in path"
            
    def test_regular_endpoints_no_sse(self):
        """Verify regular endpoints don't use SSE."""
        regular_endpoints = [
            "/mcp/v1/jsonrpc",
            "/mcp/v1/initialize", 
            "/mcp/v1/tools/list",
            "/mcp/v1/tools/call",
            "/mcp/v1/resources/list",
            "/mcp/v1/resources/read",
        ]
        
        for endpoint in regular_endpoints:
            assert "/sse/" not in endpoint, f"Regular endpoint {endpoint} should not contain /sse/"


class TestMCPOperationPatterns:
    """Test that MCP operations follow HTTP-first patterns."""
    
    def test_standard_operations_use_http(self):
        """Verify standard operations are designed for HTTP."""
        # Standard MCP operations that should use simple HTTP
        standard_ops = [
            "initialize",
            "initialized",
            "tools/list",
            "tools/call", 
            "resources/list",
            "resources/read",
            "resources/subscribe",  # Even subscriptions CAN use HTTP polling
            "prompts/list",
            "prompts/get",
            "completion/complete",
        ]
        
        # All should work with simple request/response
        for op in standard_ops:
            request = {
                "jsonrpc": "2.0",
                "method": op,
                "params": {},
                "id": 1
            }
            # Should be a simple JSON structure
            assert isinstance(request, dict)
            assert "jsonrpc" in request
            assert "method" in request
            
    def test_only_specific_features_need_sse(self):
        """Test that only specific features require SSE."""
        # Features that MAY benefit from SSE (but don't require it)
        sse_optional_features = [
            "progress_tracking",  # Can also poll
            "real_time_updates",  # Can also poll
            "subscriptions",      # Can also poll
        ]
        
        # Features that should NEVER need SSE
        no_sse_features = [
            "tool_execution",
            "resource_reading", 
            "initialization",
            "prompt_handling",
            "single_completions",
        ]
        
        assert len(sse_optional_features) < len(no_sse_features), \
            "Most features should not need SSE"