"""Embedding generation module for ContextFrame."""

from .base import EmbeddingProvider, EmbeddingResult
from .batch import BatchEmbedder, create_embedder
from .integration import create_frame_records_with_embeddings, embed_extraction_results
from .litellm_provider import LiteLLMProvider

__all__ = [
    "EmbeddingProvider",
    "EmbeddingResult",
    "LiteLLMProvider",
    "BatchEmbedder",
    "create_embedder",
    "embed_extraction_results",
    "create_frame_records_with_embeddings",
]
