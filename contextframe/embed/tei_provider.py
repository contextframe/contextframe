"""Text Embeddings Inference (TEI) provider for Hugging Face's embedding server."""

import os
from typing import Any, Optional, Union

try:
    import httpx
except ImportError:
    httpx = None
    
from .base import EmbeddingProvider, EmbeddingResult


class TEIProvider(EmbeddingProvider):
    """Embedding provider for Text Embeddings Inference (TEI) server.
    
    TEI is Hugging Face's high-performance embedding server supporting:
    - Any Sentence Transformer model
    - BERT, RoBERTa, XLM-RoBERTa based models
    - Custom models with proper tokenizer configs
    - Optimized inference with ONNX/TensorRT
    - Built-in batching and pooling
    
    Examples:
        # Using default localhost endpoint
        provider = TEIProvider(model="BAAI/bge-large-en-v1.5")
        
        # Using custom endpoint
        provider = TEIProvider(
            model="BAAI/bge-large-en-v1.5",
            api_base="http://your-tei-server:8080"
        )
        
        # With authentication
        provider = TEIProvider(
            model="BAAI/bge-large-en-v1.5",
            api_base="https://your-tei-server.com",
            api_key="your-bearer-token"
        )
    """
    
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        truncate: bool = True,
        normalize: bool = True,
    ):
        """Initialize TEI provider.
        
        Args:
            model: Model name (used for identification, actual model is set on TEI server)
            api_key: Optional bearer token for authentication
            api_base: TEI server URL (defaults to http://localhost:8080)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            truncate: Whether to truncate inputs to model's max length
            normalize: Whether to normalize embeddings
        """
        if httpx is None:
            raise ImportError(
                "httpx is required for TEI provider. "
                "Install with: pip install contextframe[tei]"
            )
            
        super().__init__(model, api_key)
        self.api_base = api_base or os.getenv("TEI_API_BASE", "http://localhost:8080")
        self.api_base = self.api_base.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.truncate = truncate
        self.normalize = normalize
        self._model_info = None
        self._client = None
        
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.Client(
                base_url=self.api_base,
                headers=headers,
                timeout=self.timeout,
            )
        return self._client
        
    def embed(self, texts: str | list[str], **kwargs) -> EmbeddingResult:
        """Generate embeddings using TEI server.
        
        Args:
            texts: Single text or list of texts to embed
            **kwargs: Additional parameters:
                - truncate: Override default truncation setting
                - normalize: Override default normalization setting
                
        Returns:
            EmbeddingResult with embeddings and metadata
            
        Raises:
            RuntimeError: If embedding generation fails after retries
        """
        texts = self.validate_texts(texts)
        
        # Prepare request payload
        payload = {
            "inputs": texts,
            "truncate": kwargs.get("truncate", self.truncate),
            "normalize": kwargs.get("normalize", self.normalize),
        }
        
        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.post("/embed", json=payload)
                response.raise_for_status()
                
                embeddings = response.json()
                
                # TEI returns list of embeddings directly
                dimension = len(embeddings[0]) if embeddings else None
                
                return EmbeddingResult(
                    embeddings=embeddings,
                    model=self.model,
                    dimension=dimension,
                    usage=None,  # TEI doesn't provide token usage
                    metadata={
                        "provider": "tei",
                        "api_base": self.api_base,
                        "truncate": payload["truncate"],
                        "normalize": payload["normalize"],
                    },
                )
                
            except httpx.ConnectError as e:
                last_error = f"Cannot connect to TEI server at {self.api_base}: {str(e)}"
            except httpx.TimeoutException as e:
                last_error = f"TEI request timed out after {self.timeout}s: {str(e)}"
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 413:
                    last_error = f"Input too large for TEI server: {e.response.text}"
                elif e.response.status_code == 503:
                    last_error = f"TEI server overloaded: {e.response.text}"
                else:
                    last_error = f"TEI request failed ({e.response.status_code}): {e.response.text}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                
        # All retries failed
        raise RuntimeError(
            f"Failed to generate embeddings with TEI after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )
                    
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model from TEI server.
        
        Returns:
            Dictionary with model information including dimension and capabilities
        """
        if self._model_info is None:
            try:
                # Query TEI info endpoint
                response = self.client.get("/info")
                response.raise_for_status()
                
                info = response.json()
                
                self._model_info = {
                    "model": info.get("model_id", self.model),
                    "provider": "tei",
                    "dimension": info.get("max_input_length"),  # TEI provides this
                    "max_tokens": info.get("max_input_length"),
                    "supports_batch": True,
                    "capabilities": ["text-embedding"],
                    "api_base": self.api_base,
                    "tei_version": info.get("version"),
                    "backend": info.get("backend"),  # e.g., "onnx", "candle"
                }
            except Exception:
                # Fallback if info endpoint not available or fails
                self._model_info = {
                    "model": self.model,
                    "provider": "tei",
                    "dimension": None,  # Will be determined from first embedding
                    "supports_batch": True,
                    "capabilities": ["text-embedding"],
                    "api_base": self.api_base,
                }
                
        return self._model_info
        
    @property
    def supports_batch(self) -> bool:
        """TEI supports batch embedding."""
        return True
        
    @property
    def max_batch_size(self) -> int | None:
        """TEI handles batching internally, we can send reasonable batches."""
        return 256  # Conservative default, TEI can handle more
        
    def health_check(self) -> dict[str, Any]:
        """Check if TEI server is healthy.
        
        Returns:
            Dictionary with health status information
        """
        try:
            response = self.client.get("/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "api_base": self.api_base,
                "response": response.json() if response.headers.get("content-type") == "application/json" else response.text
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "api_base": self.api_base,
                "error": str(e)
            }
            
    def __del__(self):
        """Clean up HTTP client on deletion."""
        if self._client is not None:
            self._client.close()