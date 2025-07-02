"""Unit tests for TEI embedding provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Mock httpx at module level to allow import
httpx_mock = MagicMock()
with patch.dict("sys.modules", {"httpx": httpx_mock}):
    from contextframe.embed.tei_provider import TEIProvider
    from contextframe.embed.base import EmbeddingResult


class TestTEIProvider:
    """Test suite for TEI embedding provider."""
    
    def test_init_defaults(self):
        """Test initialization with default values."""
        provider = TEIProvider(model="BAAI/bge-base-en-v1.5")
        
        assert provider.model == "BAAI/bge-base-en-v1.5"
        assert provider.api_base == "http://localhost:8080"
        assert provider.timeout == 30.0
        assert provider.max_retries == 3
        assert provider.truncate is True
        assert provider.normalize is True
        
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        provider = TEIProvider(
            model="custom-model",
            api_key="test-key",
            api_base="https://my-tei.com",
            timeout=60.0,
            max_retries=5,
            truncate=False,
            normalize=False,
        )
        
        assert provider.model == "custom-model"
        assert provider.api_key == "test-key"
        assert provider.api_base == "https://my-tei.com"
        assert provider.timeout == 60.0
        assert provider.max_retries == 5
        assert provider.truncate is False
        assert provider.normalize is False
        
    def test_init_env_variable(self):
        """Test initialization with environment variable."""
        with patch.dict("os.environ", {"TEI_API_BASE": "http://env-tei:8080"}):
            provider = TEIProvider(model="test-model")
            assert provider.api_base == "http://env-tei:8080"
            
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_client_property(self, mock_client_class):
        """Test client property creates client with correct settings."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test", api_key="bearer-token")
        client = provider.client
        
        # Verify client is created with correct parameters
        mock_client_class.assert_called_once_with(
            base_url="http://localhost:8080",
            headers={"Authorization": "Bearer bearer-token"},
            timeout=30.0,
        )
        
        # Verify same client is returned on subsequent calls
        client2 = provider.client
        assert client is client2
        assert mock_client_class.call_count == 1
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_single_text(self, mock_client_class):
        """Test embedding single text."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = [[0.1, 0.2, 0.3]]
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test-model")
        result = provider.embed("Hello world")
        
        # Verify request
        mock_client.post.assert_called_once_with(
            "/embed",
            json={
                "inputs": ["Hello world"],
                "truncate": True,
                "normalize": True,
            }
        )
        
        # Verify result
        assert isinstance(result, EmbeddingResult)
        assert result.embeddings == [[0.1, 0.2, 0.3]]
        assert result.model == "test-model"
        assert result.dimension == 3
        assert result.usage is None
        assert result.metadata["provider"] == "tei"
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_batch_texts(self, mock_client_class):
        """Test embedding multiple texts."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test-model")
        result = provider.embed(["Text 1", "Text 2", "Text 3"])
        
        # Verify request
        mock_client.post.assert_called_once_with(
            "/embed",
            json={
                "inputs": ["Text 1", "Text 2", "Text 3"],
                "truncate": True,
                "normalize": True,
            }
        )
        
        # Verify result
        assert len(result.embeddings) == 3
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.dimension == 3
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_with_kwargs(self, mock_client_class):
        """Test embedding with custom kwargs."""
        mock_response = Mock()
        mock_response.json.return_value = [[0.1, 0.2]]
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test", truncate=True, normalize=True)
        result = provider.embed("Test", truncate=False, normalize=False)
        
        # Verify kwargs override defaults
        mock_client.post.assert_called_once_with(
            "/embed",
            json={
                "inputs": ["Test"],
                "truncate": False,
                "normalize": False,
            }
        )
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_retry_on_failure(self, mock_client_class):
        """Test retry logic on failures."""
        import httpx
        
        # Create real httpx exceptions
        connect_error = httpx.ConnectError("Connection failed")
        timeout_error = httpx.TimeoutException("Request timed out")
        
        mock_client = Mock()
        # Fail twice, then succeed
        mock_client.post.side_effect = [
            connect_error,
            timeout_error,
            Mock(json=Mock(return_value=[[0.1, 0.2]]), raise_for_status=Mock())
        ]
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test", max_retries=3)
        result = provider.embed("Test")
        
        # Should have tried 3 times
        assert mock_client.post.call_count == 3
        assert result.embeddings == [[0.1, 0.2]]
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_max_retries_exceeded(self, mock_client_class):
        """Test failure when max retries exceeded."""
        import httpx
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test", max_retries=2)
        
        with pytest.raises(RuntimeError) as exc_info:
            provider.embed("Test")
            
        assert "Failed to generate embeddings with TEI after 2 attempts" in str(exc_info.value)
        assert mock_client.post.call_count == 2
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_embed_http_errors(self, mock_client_class):
        """Test handling of various HTTP errors."""
        import httpx
        
        # Test 413 - Input too large
        mock_response_413 = Mock()
        mock_response_413.status_code = 413
        mock_response_413.text = "Input exceeds maximum length"
        error_413 = httpx.HTTPStatusError(
            "413 error", 
            request=Mock(), 
            response=mock_response_413
        )
        
        mock_client = Mock()
        mock_client.post.side_effect = error_413
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test", max_retries=1)
        
        with pytest.raises(RuntimeError) as exc_info:
            provider.embed("Very long text...")
            
        assert "Input too large for TEI server" in str(exc_info.value)
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_get_model_info_success(self, mock_client_class):
        """Test successful model info retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "model_id": "BAAI/bge-base-en-v1.5",
            "max_input_length": 512,
            "version": "1.7.0",
            "backend": "onnx",
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test")
        info = provider.get_model_info()
        
        mock_client.get.assert_called_once_with("/info")
        
        assert info["model"] == "BAAI/bge-base-en-v1.5"
        assert info["provider"] == "tei"
        assert info["dimension"] == 512
        assert info["max_tokens"] == 512
        assert info["supports_batch"] is True
        assert info["tei_version"] == "1.7.0"
        assert info["backend"] == "onnx"
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_get_model_info_fallback(self, mock_client_class):
        """Test model info fallback when endpoint fails."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Info endpoint not available")
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test-model")
        info = provider.get_model_info()
        
        # Should return fallback info
        assert info["model"] == "test-model"
        assert info["provider"] == "tei"
        assert info["dimension"] is None
        assert info["supports_batch"] is True
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_health_check_success(self, mock_client_class):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test")
        health = provider.health_check()
        
        mock_client.get.assert_called_once_with("/health")
        
        assert health["status"] == "healthy"
        assert health["api_base"] == "http://localhost:8080"
        assert health["response"] == {"status": "ok"}
        
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_health_check_failure(self, mock_client_class):
        """Test failed health check."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Connection refused")
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test")
        health = provider.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["api_base"] == "http://localhost:8080"
        assert "Connection refused" in health["error"]
        
    def test_supports_batch(self):
        """Test batch support property."""
        provider = TEIProvider(model="test")
        assert provider.supports_batch is True
        
    def test_max_batch_size(self):
        """Test max batch size property."""
        provider = TEIProvider(model="test")
        assert provider.max_batch_size == 256
        
    def test_validate_texts(self):
        """Test text validation (inherited from base class)."""
        provider = TEIProvider(model="test")
        
        # Single text becomes list
        assert provider.validate_texts("Hello") == ["Hello"]
        
        # List stays list
        assert provider.validate_texts(["Hello", "World"]) == ["Hello", "World"]
        
        # Empty list raises error
        with pytest.raises(ValueError):
            provider.validate_texts([])
            
    @patch("contextframe.embed.tei_provider.httpx.Client")
    def test_client_cleanup(self, mock_client_class):
        """Test client cleanup on deletion."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        provider = TEIProvider(model="test")
        _ = provider.client  # Create client
        
        # Manually call __del__
        provider.__del__()
        
        mock_client.close.assert_called_once()