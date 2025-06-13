"""Tests for the embed module."""

import pytest

from contextframe.embed import (
    BatchEmbedder,
    EmbeddingProvider,
    EmbeddingResult,
    LiteLLMProvider,
)


class MockProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""
    
    def __init__(self, dimension: int = 128):
        super().__init__(model="mock-model")
        self.dimension = dimension
        self.call_count = 0
    
    def embed(self, texts, **kwargs):
        """Generate mock embeddings."""
        texts = self.validate_texts(texts)
        self.call_count += 1
        
        # Generate fake embeddings
        embeddings = []
        for text in texts:
            # Simple hash-based fake embedding
            embedding = [float(ord(c) % 10) / 10 for c in text[:self.dimension]]
            # Pad if needed
            if len(embedding) < self.dimension:
                embedding.extend([0.0] * (self.dimension - len(embedding)))
            embeddings.append(embedding)
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=self.model,
            dimension=self.dimension,
            usage={"prompt_tokens": len(texts) * 10, "total_tokens": len(texts) * 10},
        )
    
    def get_model_info(self):
        return {
            "model": self.model,
            "dimension": self.dimension,
            "provider": "mock",
            "supports_batch": True,
        }
    
    @property
    def supports_batch(self):
        return True
    
    @property
    def max_batch_size(self):
        return 10


class TestEmbeddingResult:
    """Test EmbeddingResult dataclass."""
    
    def test_single_embedding_normalization(self):
        """Test that single embeddings are normalized to 2D."""
        result = EmbeddingResult(
            embeddings=[[0.1, 0.2, 0.3]],
            model="test",
            dimension=3
        )
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert len(result.embeddings) == 1
    
    def test_dimension_validation(self):
        """Test dimension validation."""
        with pytest.raises(ValueError, match="does not match"):
            EmbeddingResult(
                embeddings=[[0.1, 0.2]],
                model="test",
                dimension=3  # Mismatch
            )
    
    def test_dimension_inference(self):
        """Test dimension is inferred from embeddings."""
        result = EmbeddingResult(
            embeddings=[[0.1, 0.2, 0.3, 0.4]],
            model="test",
            dimension=None
        )
        assert result.dimension == 4


class TestLiteLLMProvider:
    """Test LiteLLM provider."""
    
    def test_initialization(self):
        """Test provider initialization."""
        provider = LiteLLMProvider(model="text-embedding-ada-002")
        assert provider.model == "text-embedding-ada-002"
        assert provider.supports_batch is True
    
    def test_model_info(self):
        """Test getting model information."""
        provider = LiteLLMProvider(model="text-embedding-ada-002")
        info = provider.get_model_info()
        
        assert info["model"] == "text-embedding-ada-002"
        assert info["dimension"] == 1536  # Known dimension
        assert info["provider"] == "openai"
        assert info["supports_batch"] is True
    
    def test_provider_detection(self):
        """Test provider detection from model names."""
        provider = LiteLLMProvider(model="cohere/embed-english-v3.0")
        assert provider._detect_provider() == "cohere"
        
        provider = LiteLLMProvider(model="embed-english-v3.0")
        assert provider._detect_provider() == "cohere"
        
        provider = LiteLLMProvider(model="voyage-01")
        assert provider._detect_provider() == "voyage"
    
    def test_text_validation(self):
        """Test text validation."""
        provider = LiteLLMProvider()
        
        # Valid texts
        assert provider.validate_texts("hello") == ["hello"]
        assert provider.validate_texts(["hello", "world"]) == ["hello", "world"]
        
        # Invalid texts
        with pytest.raises(ValueError, match="No texts"):
            provider.validate_texts([])
        
        with pytest.raises(ValueError, match="must be strings"):
            provider.validate_texts([123])
        
        with pytest.raises(ValueError, match="Empty texts"):
            provider.validate_texts(["", "hello"])


class TestBatchEmbedder:
    """Test batch embedder functionality."""
    
    def test_basic_batch_embedding(self):
        """Test basic batch embedding."""
        provider = MockProvider(dimension=10)
        embedder = BatchEmbedder(provider, batch_size=2)
        
        texts = ["text1", "text2", "text3", "text4", "text5"]
        result = embedder.embed_batch(texts)
        
        assert len(result.embeddings) == 5
        assert result.dimension == 10
        assert provider.call_count == 3  # 5 texts with batch size 2 = 3 calls
    
    def test_progress_callback(self):
        """Test progress callback."""
        provider = MockProvider()
        progress_calls = []
        
        def progress(completed, total):
            progress_calls.append((completed, total))
        
        embedder = BatchEmbedder(provider, batch_size=2, progress_callback=progress)
        texts = ["text1", "text2", "text3"]
        embedder.embed_batch(texts)
        
        # Should have progress updates after each batch
        assert len(progress_calls) == 2
        assert progress_calls[0] == (2, 3)  # First batch
        assert progress_calls[1] == (3, 3)  # Second batch
    
    def test_embed_documents(self):
        """Test embedding documents."""
        provider = MockProvider(dimension=5)
        embedder = BatchEmbedder(provider)
        
        documents = [
            {"id": 1, "content": "Hello world", "metadata": "test"},
            {"id": 2, "content": "Goodbye world", "other": "data"},
            {"id": 3, "title": "No content"},  # Missing content field
        ]
        
        result_docs = embedder.embed_documents(documents)
        
        assert len(result_docs) == 3
        
        # First two should have embeddings
        assert result_docs[0]["embedding"] is not None
        assert len(result_docs[0]["embedding"]) == 5
        assert result_docs[0]["embedding_model"] == "mock-model"
        assert result_docs[0]["embedding_dimension"] == 5
        
        assert result_docs[1]["embedding"] is not None
        
        # Third should have error
        assert result_docs[2]["embedding"] is None
        assert result_docs[2]["embedding_error"] == "No text content"
    
    def test_empty_batch_error(self):
        """Test error on empty batch."""
        provider = MockProvider()
        embedder = BatchEmbedder(provider)
        
        with pytest.raises(ValueError, match="No texts provided"):
            embedder.embed_batch([])


class TestIntegration:
    """Test integration with extraction results."""
    
    def test_embed_extraction_results(self):
        """Test embedding extraction results."""
        from contextframe.embed.integration import embed_extraction_results
        from contextframe.extract import ExtractionResult
        
        # Create extraction results
        results = [
            ExtractionResult(
                content="Document 1 content",
                metadata={"title": "Doc 1"},
                chunks=["chunk1", "chunk2"]
            ),
            ExtractionResult(
                content="Document 2 content",
                metadata={"title": "Doc 2"}
            ),
        ]
        
        # Embed with mock provider
        provider = MockProvider(dimension=8)
        enhanced = embed_extraction_results(
            results,
            provider,
            embed_content=True,
            embed_chunks=True
        )
        
        # Check content embeddings
        assert "content_embedding" in enhanced[0].metadata
        assert len(enhanced[0].metadata["content_embedding"]) == 8
        assert "embedding_model" in enhanced[0].metadata
        
        # Check chunk embeddings
        assert "chunk_embeddings" in enhanced[0].metadata
        assert len(enhanced[0].metadata["chunk_embeddings"]) == 2
        assert enhanced[0].metadata["chunk_embeddings"][0]["index"] == 0
        
        # Second doc has no chunks
        assert "content_embedding" in enhanced[1].metadata
        assert "chunk_embeddings" not in enhanced[1].metadata