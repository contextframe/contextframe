"""LiteLLM embedding provider for unified access to encoding models."""

import os
from typing import Any, List, Optional, Union

from .base import EmbeddingProvider, EmbeddingResult


class LiteLLMProvider(EmbeddingProvider):
    """Embedding provider using LiteLLM's unified interface.
    
    Supports multiple encoding models through a single interface:
    - OpenAI: text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
    - Cohere: embed-english-v3.0, embed-multilingual-v3.0
    - Voyage: voyage-01, voyage-02
    - And many more via LiteLLM's extensive model support
    """
    
    # Known model dimensions (can be extended)
    MODEL_DIMENSIONS = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "embed-english-v3.0": 1024,
        "embed-multilingual-v3.0": 1024,
        "embed-english-v2.0": 4096,
        "embed-multilingual-v2.0": 768,
    }
    
    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """Initialize LiteLLM provider.
        
        Args:
            model: Encoding model identifier (can include provider prefix)
            api_key: API key (optional, uses env var if not provided)
            api_base: API base URL for custom endpoints
            api_version: API version (for Azure OpenAI)
        """
        super().__init__(model, api_key)
        self.api_base = api_base
        self.api_version = api_version
        self._litellm = None
    
    @property
    def litellm(self):
        """Lazy import of litellm."""
        if self._litellm is None:
            try:
                import litellm
                self._litellm = litellm
            except ImportError:
                raise ImportError(
                    "LiteLLM is required for this provider. "
                    "Install with: pip install 'contextframe[extract]'"
                )
        return self._litellm
    
    def embed(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> EmbeddingResult:
        """Generate embeddings using LiteLLM's encoding models.
        
        Args:
            texts: Single text or list of texts to encode
            **kwargs: Additional arguments passed to litellm.embedding()
                     Common options include:
                     - encoding_format: "float" or "base64"
                     - user: User identifier for tracking
            
        Returns:
            EmbeddingResult with embeddings from the encoding model
        """
        texts = self.validate_texts(texts)
        single_input = len(texts) == 1
        
        # Set up API credentials if provided
        if self.api_key:
            self._set_api_key()
        
        # Prepare kwargs
        embed_kwargs = {
            "model": self.model,
            "input": texts,
        }
        
        if self.api_base:
            embed_kwargs["api_base"] = self.api_base
        if self.api_version:
            embed_kwargs["api_version"] = self.api_version
            
        embed_kwargs.update(kwargs)
        
        try:
            # Call LiteLLM's embedding endpoint
            response = self.litellm.embedding(**embed_kwargs)
            
            # Extract embeddings from response
            embeddings = []
            for item in response.data:
                embeddings.append(item['embedding'])
            
            # Get usage information if available
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            # Determine dimension
            dimension = len(embeddings[0]) if embeddings else None
            
            return EmbeddingResult(
                embeddings=embeddings,
                model=response.model if hasattr(response, 'model') else self.model,
                dimension=dimension,
                usage=usage,
                metadata={
                    "provider": self._detect_provider(),
                    "encoding_format": kwargs.get("encoding_format", "float"),
                }
            )
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate embeddings with {self.model}: {str(e)}"
            )
    
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the encoding model."""
        provider = self._detect_provider()
        
        # Get dimension from known models or make a test call
        dimension = self.MODEL_DIMENSIONS.get(self.model.split("/")[-1])
        if dimension is None:
            try:
                # Make a test embedding call to get dimension
                result = self.embed("test")
                dimension = result.dimension
            except:
                dimension = None
        
        return {
            "model": self.model,
            "provider": provider,
            "dimension": dimension,
            "supports_batch": True,
            "capabilities": ["text-embedding"],
            "api_base": self.api_base,
        }
    
    @property
    def supports_batch(self) -> bool:
        """LiteLLM supports batch embedding for all providers."""
        return True
    
    @property
    def max_batch_size(self) -> Optional[int]:
        """Maximum batch size varies by provider."""
        provider = self._detect_provider()
        
        # Known limits by provider
        if provider == "openai":
            return 2048  # OpenAI's batch limit
        elif provider == "cohere":
            return 96  # Cohere's batch limit
        else:
            return 100  # Conservative default
    
    def _detect_provider(self) -> str:
        """Detect the provider from the model string."""
        model = self.model.lower()
        
        if "/" in model:
            return model.split("/")[0]
        elif "voyage" in model:
            return "voyage"
        elif model.startswith("embed-"):
            return "cohere"
        elif "embedding" in model:
            return "openai"
        else:
            return "openai"  # Default to OpenAI
    
    def _set_api_key(self):
        """Set the appropriate environment variable for the API key."""
        provider = self._detect_provider()
        
        # Map provider to environment variable
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "cohere": "COHERE_API_KEY",
            "voyage": "VOYAGE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
        }
        
        env_var = env_vars.get(provider, f"{provider.upper()}_API_KEY")
        os.environ[env_var] = self.api_key