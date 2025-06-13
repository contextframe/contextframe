"""Tests for enhanced LiteLLM provider functionality."""

import os
import pytest
from unittest.mock import Mock, patch

from contextframe.embed.litellm_provider import LiteLLMProvider


class TestLiteLLMProviderEnhanced:
    """Test enhanced LiteLLM provider features."""
    
    def test_provider_detection_comprehensive(self):
        """Test provider detection for all supported patterns."""
        test_cases = [
            # Explicit provider prefixes
            ("openai/text-embedding-ada-002", "openai"),
            ("azure/my-deployment", "azure"),
            ("cohere/embed-english-v3.0", "cohere"),
            ("voyage/voyage-01", "voyage"),
            ("anthropic/claude-embed", "anthropic"),
            ("huggingface/BAAI/bge-large-en", "huggingface"),
            ("together_ai/togethercomputer/m2-bert", "together_ai"),
            ("bedrock/amazon.titan-embed-text-v1", "bedrock"),
            ("vertex_ai/textembedding-gecko", "vertex_ai"),
            ("replicate/model-id", "replicate"),
            ("ollama/all-minilm", "ollama"),
            ("mistral/mistral-embed", "mistral"),
            ("jina/jina-embeddings-v2-base-en", "jina"),
            
            # Implicit detection from model names
            ("voyage-01", "voyage"),
            ("voyage-large-2", "voyage"),
            ("embed-english-v3.0", "cohere"),
            ("embed-multilingual-v3.0", "cohere"),
            ("jina-embeddings-v2-base-en", "jina"),
            ("mistral-embed", "mistral"),
            ("bge-large-en-v1.5", "huggingface"),
            ("gte-large", "huggingface"),
            ("titan-embed-text-v1", "bedrock"),
            ("text-embedding-ada-002", "openai"),
            ("text-embedding-3-large", "openai"),
            
            # Default cases
            ("unknown-model", "openai"),
            ("custom-model", "openai"),
        ]
        
        for model, expected_provider in test_cases:
            provider = LiteLLMProvider(model=model)
            assert provider._detect_provider() == expected_provider, f"Failed for model: {model}"
    
    def test_model_dimensions_lookup(self):
        """Test model dimension lookup for known models."""
        # Test with provider prefix
        provider = LiteLLMProvider("openai/text-embedding-ada-002")
        info = provider.get_model_info(skip_dimension_check=True)
        assert info["dimension"] == 1536
        
        # Test without provider prefix
        provider = LiteLLMProvider("text-embedding-ada-002")
        info = provider.get_model_info(skip_dimension_check=True)
        assert info["dimension"] == 1536
        
        # Test Cohere model
        provider = LiteLLMProvider("cohere/embed-english-v3.0")
        info = provider.get_model_info(skip_dimension_check=True)
        assert info["dimension"] == 1024
        
        # Test unknown model
        provider = LiteLLMProvider("unknown/custom-model")
        info = provider.get_model_info(skip_dimension_check=True)
        assert info["dimension"] is None
    
    def test_api_key_environment_mapping(self):
        """Test API key environment variable mapping."""
        test_cases = [
            ("openai", "test-key", "OPENAI_API_KEY"),
            ("azure", "test-key", "AZURE_API_KEY"),
            ("cohere", "test-key", "COHERE_API_KEY"),
            ("voyage", "test-key", "VOYAGE_API_KEY"),
            ("anthropic", "test-key", "ANTHROPIC_API_KEY"),
            ("huggingface", "test-key", "HUGGINGFACE_API_KEY"),
            ("jina", "test-key", "JINA_API_KEY"),
            ("mistral", "test-key", "MISTRAL_API_KEY"),
            ("together_ai", "test-key", "TOGETHERAI_API_KEY"),
            ("replicate", "test-key", "REPLICATE_API_TOKEN"),
            ("deepinfra", "test-key", "DEEPINFRA_API_KEY"),
            ("ai21", "test-key", "AI21_API_KEY"),
            ("nlp_cloud", "test-key", "NLP_CLOUD_API_KEY"),
        ]
        
        for provider_name, api_key, env_var in test_cases:
            # Clear environment
            if env_var in os.environ:
                del os.environ[env_var]
            
            # Create provider with explicit provider
            provider = LiteLLMProvider(f"{provider_name}/test-model", api_key=api_key)
            provider._set_api_key()
            
            assert os.environ.get(env_var) == api_key
            
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]
    
    def test_bedrock_credentials_parsing(self):
        """Test AWS Bedrock credential parsing."""
        # Clear AWS environment variables
        for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
            if var in os.environ:
                del os.environ[var]
        
        provider = LiteLLMProvider("bedrock/amazon.titan-embed", api_key="access123:secret456")
        provider._set_api_key()
        
        assert os.environ["AWS_ACCESS_KEY_ID"] == "access123"
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == "secret456"
        
        # Clean up
        del os.environ["AWS_ACCESS_KEY_ID"]
        del os.environ["AWS_SECRET_ACCESS_KEY"]
    
    def test_max_batch_size_by_provider(self):
        """Test max batch size limits by provider."""
        test_cases = [
            ("openai/text-embedding-ada-002", 2048),
            ("azure/deployment", 2048),
            ("cohere/embed-english-v3.0", 96),
            ("voyage/voyage-01", 128),
            ("jina/jina-embeddings-v2", 2048),
            ("mistral/mistral-embed", 512),
            ("together_ai/model", 100),
            ("huggingface/model", 512),
            ("bedrock/model", 512),
            ("vertex_ai/model", 250),
            ("replicate/model", 100),
            ("ollama/model", 1),
            ("unknown/model", 100),  # Default
        ]
        
        for model, expected_batch_size in test_cases:
            provider = LiteLLMProvider(model=model)
            assert provider.max_batch_size == expected_batch_size
    
    def test_custom_model_support(self):
        """Test support for custom models not in MODEL_DIMENSIONS."""
        # Test ModernBERT example
        provider = LiteLLMProvider("huggingface/answerdotai/ModernBERT-base")
        assert provider.model == "huggingface/answerdotai/ModernBERT-base"
        assert provider._detect_provider() == "huggingface"
        
        # Test ColBERT example
        provider = LiteLLMProvider(
            "huggingface/colbert-ir/colbertv2.0",
            api_base="http://localhost:8000/v1"
        )
        assert provider.model == "huggingface/colbert-ir/colbertv2.0"
        assert provider.api_base == "http://localhost:8000/v1"
        
        # Test completely custom model
        provider = LiteLLMProvider(
            "custom/my-special-model",
            api_base="http://my-server/v1",
            custom_llm_provider="openai"
        )
        assert provider.model == "custom/my-special-model"
        assert provider.custom_llm_provider == "openai"
    
    @patch('litellm.embedding')
    def test_embed_with_litellm_mock(self, mock_embedding):
        """Test embed method with mocked litellm."""
        # Mock the litellm module
        mock_litellm = Mock()
        mock_litellm.embedding = mock_embedding
        
        # Mock response
        mock_response = Mock()
        mock_response.data = [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]}
        ]
        mock_response.model = "text-embedding-ada-002"
        mock_response.usage = Mock(prompt_tokens=10, total_tokens=10)
        mock_embedding.return_value = mock_response
        
        # Create provider and patch litellm
        provider = LiteLLMProvider("text-embedding-ada-002", api_key="test-key")
        provider._litellm = mock_litellm
        
        # Test embedding
        result = provider.embed(["Hello", "World"])
        
        # Verify call
        mock_embedding.assert_called_once()
        call_args = mock_embedding.call_args[1]
        assert call_args["model"] == "text-embedding-ada-002"
        assert call_args["input"] == ["Hello", "World"]
        
        # Verify result
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.embeddings[1] == [0.4, 0.5, 0.6]
        assert result.model == "text-embedding-ada-002"
        assert result.dimension == 3
        assert result.usage["prompt_tokens"] == 10
    
    @patch('litellm.embedding')
    def test_dynamic_dimension_detection(self, mock_embedding):
        """Test automatic dimension detection for unknown models."""
        # Mock the litellm module
        mock_litellm = Mock()
        mock_litellm.embedding = mock_embedding
        
        # Mock response for test embedding
        mock_response = Mock()
        mock_response.data = [{"embedding": [0.1] * 768}]  # 768 dimensions
        mock_response.model = "custom/unknown-model"
        mock_embedding.return_value = mock_response
        
        # Create provider with unknown model
        provider = LiteLLMProvider("custom/unknown-model")
        provider._litellm = mock_litellm
        
        # Get model info (should trigger test embedding)
        info = provider.get_model_info()
        
        # Should have made a test call
        mock_embedding.assert_called_once()
        assert info["dimension"] == 768
        assert info["model"] == "custom/unknown-model"
    
    def test_initialization_parameters(self):
        """Test all initialization parameters are stored correctly."""
        provider = LiteLLMProvider(
            model="openai/text-embedding-3-large",
            api_key="test-key",
            api_base="https://api.example.com",
            api_version="2023-05-15",
            timeout=30.0,
            max_retries=5,
            organization="test-org",
            custom_llm_provider="custom",
            input_type="search_document",
            encoding_format="base64"
        )
        
        assert provider.model == "openai/text-embedding-3-large"
        assert provider.api_key == "test-key"
        assert provider.api_base == "https://api.example.com"
        assert provider.api_version == "2023-05-15"
        assert provider.timeout == 30.0
        assert provider.max_retries == 5
        assert provider.organization == "test-org"
        assert provider.custom_llm_provider == "custom"
        assert provider.input_type == "search_document"
        assert provider.encoding_format == "base64"
    
    def test_error_handling(self):
        """Test error handling in embed method."""
        provider = LiteLLMProvider("test-model")
        
        # Mock litellm to raise an exception
        mock_litellm = Mock()
        mock_litellm.embedding.side_effect = Exception("API Error")
        provider._litellm = mock_litellm
        
        with pytest.raises(RuntimeError) as exc_info:
            provider.embed("Test text")
        
        assert "Failed to generate embeddings with test-model" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)


class TestLiteLLMProviderIntegration:
    """Integration tests requiring actual LiteLLM library."""
    
    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration test"
    )
    def test_real_openai_embedding(self):
        """Test with real OpenAI API (requires API key)."""
        provider = LiteLLMProvider("text-embedding-ada-002")
        result = provider.embed("Hello, world!")
        
        assert len(result.embeddings) == 1
        assert len(result.embeddings[0]) == 1536
        assert result.model == "text-embedding-ada-002"
        assert result.dimension == 1536
        assert result.usage is not None
    
    def test_import_error_handling(self):
        """Test handling when litellm is not installed."""
        provider = LiteLLMProvider("test-model")
        
        # Force import error
        provider._litellm = None
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ImportError) as exc_info:
                _ = provider.litellm
            
            assert "LiteLLM is required" in str(exc_info.value)
            assert "pip install 'contextframe[extract]'" in str(exc_info.value)