"""Base classes for embedding providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Union


@dataclass
class EmbeddingResult:
    """Result of an embedding operation from an encoding model.
    
    Attributes:
        embeddings: The generated embeddings as a list of float lists
        model: The encoding model used (e.g., "text-embedding-ada-002")
        dimension: The dimension of the embeddings
        usage: Token usage information (if available)
        metadata: Additional metadata from the encoding model
    """
    embeddings: List[List[float]]
    model: str
    dimension: int
    usage: Optional[dict[str, int]] = None
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        """Validate embeddings and set dimension."""
        if self.metadata is None:
            self.metadata = {}
            
        # Validate all embeddings have same dimension
        if self.embeddings:
            first_dim = len(self.embeddings[0])
            if not all(len(emb) == first_dim for emb in self.embeddings):
                raise ValueError("All embeddings must have the same dimension")
            
            # Set dimension from embeddings if not provided
            if self.dimension is None:
                self.dimension = first_dim
            elif self.dimension != first_dim:
                raise ValueError(
                    f"Embedding dimension {first_dim} does not match "
                    f"specified dimension {self.dimension}"
                )


class EmbeddingProvider(ABC):
    """Abstract base class for encoding model providers.
    
    This class defines the interface for different embedding providers
    (OpenAI, Cohere, HuggingFace, etc.) that use encoding models to
    transform text into vector representations.
    """
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        """Initialize the embedding provider.
        
        Args:
            model: The encoding model identifier (e.g., "text-embedding-ada-002")
            api_key: Optional API key (uses environment variable if not provided)
        """
        self.model = model
        self.api_key = api_key
    
    @abstractmethod
    def embed(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> EmbeddingResult:
        """Generate embeddings using the encoding model.
        
        Args:
            texts: Single text or list of texts to encode
            **kwargs: Additional provider-specific arguments
            
        Returns:
            EmbeddingResult containing the embeddings from the encoding model
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the encoding model.
        
        Returns:
            Dictionary with model information including:
            - dimension: The embedding dimension
            - max_tokens: Maximum input tokens (if applicable)
            - provider: The provider name
            - capabilities: List of capabilities
        """
        pass
    
    @property
    @abstractmethod
    def supports_batch(self) -> bool:
        """Whether this encoding model supports batch processing."""
        pass
    
    @property
    def max_batch_size(self) -> Optional[int]:
        """Maximum batch size supported by the encoding model."""
        return None
    
    def validate_texts(self, texts: Union[str, List[str]]) -> List[str]:
        """Validate and normalize input texts for the encoding model.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            List of validated texts
            
        Raises:
            ValueError: If texts are invalid for the encoding model
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All texts must be strings")
        
        if not all(t.strip() for t in texts):
            raise ValueError("Empty texts cannot be embedded")
        
        return texts