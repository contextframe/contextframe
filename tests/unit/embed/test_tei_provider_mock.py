"""Unit tests for TEI provider using mocks."""

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_tei_provider_initialization():
    """Test that TEI provider can be imported and initialized with mocks."""
    # Mock httpx module
    httpx_mock = MagicMock()
    httpx_mock.Client = Mock
    
    with patch.dict("sys.modules", {"httpx": httpx_mock}):
        # Import after patching
        from contextframe.embed.tei_provider import TEIProvider
        
        # Test basic initialization
        provider = TEIProvider(model="test-model")
        assert provider.model == "test-model"
        assert provider.api_base == "http://localhost:8080"
        assert provider.timeout == 30.0
        assert provider.max_retries == 3
        assert provider.truncate is True
        assert provider.normalize is True


def test_tei_provider_custom_config():
    """Test TEI provider with custom configuration."""
    httpx_mock = MagicMock()
    httpx_mock.Client = Mock
    
    with patch.dict("sys.modules", {"httpx": httpx_mock}):
        from contextframe.embed.tei_provider import TEIProvider
        
        provider = TEIProvider(
            model="custom-model",
            api_key="test-key",
            api_base="https://custom-tei.com",
            timeout=60.0,
            max_retries=5,
            truncate=False,
            normalize=False
        )
        
        assert provider.model == "custom-model"
        assert provider.api_key == "test-key"
        assert provider.api_base == "https://custom-tei.com"
        assert provider.timeout == 60.0
        assert provider.max_retries == 5
        assert provider.truncate is False
        assert provider.normalize is False


def test_tei_import_without_httpx():
    """Test that TEI provider raises ImportError without httpx."""
    # Ensure httpx is not available
    with patch.dict("sys.modules", {"httpx": None}):
        # Clear any cached imports
        import sys
        if "contextframe.embed.tei_provider" in sys.modules:
            del sys.modules["contextframe.embed.tei_provider"]
        
        # Should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            from contextframe.embed.tei_provider import TEIProvider
            TEIProvider(model="test")
        
        assert "httpx is required for TEI provider" in str(exc_info.value)