"""Embedding generation module for ContextFrame."""

from .base import EmbeddingProvider, EmbeddingResult
from .batch import BatchEmbedder, create_embedder
from .integration import create_frame_records_with_embeddings, embed_extraction_results
from .litellm_provider import LiteLLMProvider

# Import TEI provider if httpx is available
try:
    from .tei_provider import TEIProvider
    _TEI_AVAILABLE = True
except ImportError:
    _TEI_AVAILABLE = False
    TEIProvider = None

__all__ = [
    "EmbeddingProvider",
    "EmbeddingResult",
    "LiteLLMProvider",
    "BatchEmbedder",
    "create_embedder",
    "embed_extraction_results",
    "create_frame_records_with_embeddings",
]

# Only export TEIProvider if available
if _TEI_AVAILABLE:
    __all__.append("TEIProvider")
