"""LiteLLM embedding provider for unified access to encoding models."""

import os
from typing import Any, List, Optional, Union

from .base import EmbeddingProvider, EmbeddingResult


class LiteLLMProvider(EmbeddingProvider):
    """Embedding provider using LiteLLM's unified interface.
    
    Supports 100+ embedding models through a single interface. Use provider
    prefixes to route to specific providers (e.g., "cohere/embed-english-v3.0").
    
    Major providers supported:
    - OpenAI: text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
    - Azure OpenAI: Use "azure/<deployment_name>" format
    - Cohere: embed-english-v3.0, embed-multilingual-v3.0, embed-english-light-v3.0
    - Voyage AI: voyage-01, voyage-02, voyage-large-2, voyage-code-2
    - Anthropic: via Vertex AI (vertex_ai/claude-3-sonnet@20240229)
    - Google: vertex_ai/textembedding-gecko, vertex_ai/textembedding-gecko-multilingual
    - Mistral: mistral/mistral-embed
    - Jina AI: jina-embeddings-v2-base-en, jina-embeddings-v2-small-en
    - HuggingFace: huggingface/sentence-transformers/all-MiniLM-L6-v2
    - Together AI: together_ai/togethercomputer/m2-bert-80M-8k-retrieval
    - Replicate: replicate/<model-id>
    - AWS Bedrock: bedrock/amazon.titan-embed-text-v1
    - Ollama: ollama/llama2 (local models)
    - And many more...
    
    Custom/Unlisted Models:
    ANY model supported by LiteLLM can be used, even if not listed in MODEL_DIMENSIONS.
    The provider will automatically detect the embedding dimension on first use.
    
    Examples:
        # OpenAI (default)
        provider = LiteLLMProvider("text-embedding-ada-002")
        
        # Cohere with explicit prefix
        provider = LiteLLMProvider("cohere/embed-english-v3.0")
        
        # Azure OpenAI
        provider = LiteLLMProvider(
            "azure/my-embedding-deployment",
            api_base="https://my-resource.openai.azure.com",
            api_version="2023-05-15"
        )
        
        # Custom HuggingFace model (e.g., ModernBERT)
        provider = LiteLLMProvider("huggingface/answerdotai/ModernBERT-base")
        
        # ColBERT via custom endpoint
        provider = LiteLLMProvider(
            "huggingface/colbert-ir/colbertv2.0",
            api_base="http://your-inference-server/v1"
        )
        
        # Local Ollama
        provider = LiteLLMProvider("ollama/all-minilm", api_base="http://localhost:11434")
        
        # Any custom model via OpenAI-compatible endpoint
        provider = LiteLLMProvider(
            "custom/your-model",
            api_base="http://your-server/v1",
            custom_llm_provider="openai"  # Use OpenAI format
        )
    """
    
    # Known model dimensions by provider
    MODEL_DIMENSIONS = {
        # OpenAI models
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        
        # Cohere models
        "embed-english-v3.0": 1024,
        "embed-multilingual-v3.0": 1024,
        "embed-english-v2.0": 4096,
        "embed-multilingual-v2.0": 768,
        "embed-english-light-v3.0": 384,
        "embed-multilingual-light-v3.0": 384,
        
        # Voyage AI models
        "voyage-01": 1024,
        "voyage-02": 1536,
        "voyage-lite-01": 1024,
        "voyage-lite-02": 1536,
        "voyage-large-2": 1536,
        "voyage-law-2": 1024,
        "voyage-code-2": 1536,
        
        # Jina AI models
        "jina-embeddings-v2-base-en": 768,
        "jina-embeddings-v2-small-en": 512,
        "jina-embeddings-v2-base-code": 768,
        
        # Mistral models
        "mistral-embed": 1024,
        
        # Together AI models (via together_ai/ prefix)
        "togethercomputer/m2-bert-80M-8k-retrieval": 768,
        "WhereIsAI/UAE-Large-V1": 1024,
        "BAAI/bge-large-en-v1.5": 1024,
        "BAAI/bge-base-en-v1.5": 768,
        
        # HuggingFace models (common ones)
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "BAAI/bge-small-en": 384,
        
        # Azure OpenAI (same as OpenAI)
        "text-embedding-ada-002-v2": 1536,
    }
    
    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        organization: Optional[str] = None,
        custom_llm_provider: Optional[str] = None,
        input_type: Optional[str] = None,
        encoding_format: Optional[str] = None,
    ):
        """Initialize LiteLLM provider.
        
        Args:
            model: Encoding model identifier (can include provider prefix)
            api_key: API key (optional, uses env var if not provided)
            api_base: API base URL for custom endpoints
            api_version: API version (for Azure OpenAI)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            organization: Organization ID (for OpenAI)
            custom_llm_provider: Override provider detection
            input_type: Input type hint for Cohere ("search_query" or "search_document")
            encoding_format: Output format ("float" or "base64")
        """
        super().__init__(model, api_key)
        self.api_base = api_base
        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        self.organization = organization
        self.custom_llm_provider = custom_llm_provider
        self.input_type = input_type
        self.encoding_format = encoding_format
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
        
        # Add configuration parameters
        if self.api_base:
            embed_kwargs["api_base"] = self.api_base
        if self.api_version:
            embed_kwargs["api_version"] = self.api_version
        if self.timeout:
            embed_kwargs["timeout"] = self.timeout
        if self.max_retries is not None:
            embed_kwargs["num_retries"] = self.max_retries
        if self.organization:
            embed_kwargs["organization"] = self.organization
        if self.custom_llm_provider:
            embed_kwargs["custom_llm_provider"] = self.custom_llm_provider
        if self.input_type:
            embed_kwargs["input_type"] = self.input_type
        if self.encoding_format:
            embed_kwargs["encoding_format"] = self.encoding_format
            
        # Merge with additional kwargs (allowing overrides)
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
    
    def get_model_info(self, skip_dimension_check: bool = False) -> dict[str, Any]:
        """Get information about the encoding model.
        
        Args:
            skip_dimension_check: Skip automatic dimension detection for unknown models
            
        Returns:
            Dictionary with model information
        """
        provider = self._detect_provider()
        
        # Get dimension from known models or make a test call
        # Check both with and without provider prefix
        model_name = self.model.split("/")[-1] if "/" in self.model else self.model
        dimension = self.MODEL_DIMENSIONS.get(model_name)
        
        # For unknown models, try to detect dimension dynamically
        if dimension is None and not skip_dimension_check:
            try:
                # Make a test embedding call to get dimension
                result = self.embed("test", skip_dimension_check=True)
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
        
        # Known limits by provider (from LiteLLM docs and provider APIs)
        batch_limits = {
            "openai": 2048,
            "azure": 2048,
            "cohere": 96,
            "voyage": 128,
            "jina": 2048,
            "mistral": 512,
            "together_ai": 100,
            "huggingface": 512,
            "bedrock": 512,
            "vertex_ai": 250,
            "replicate": 100,
            "ollama": 1,  # Usually processes one at a time
        }
        
        return batch_limits.get(provider, 100)  # Conservative default
    
    def _detect_provider(self) -> str:
        """Detect the provider from the model string.
        
        LiteLLM uses prefixes like 'provider/model' for explicit routing.
        For models without prefix, we infer based on naming patterns.
        """
        model = self.model.lower()
        
        # Check for explicit provider prefix
        if "/" in model:
            provider = model.split("/")[0]
            # Normalize some provider names
            provider_map = {
                "azure_openai": "azure",
                "vertex_ai": "vertex_ai",
                "bedrock": "bedrock",
                "together_ai": "together_ai",
                "huggingface": "huggingface",
            }
            return provider_map.get(provider, provider)
        
        # Infer provider from model name patterns
        if "voyage" in model:
            return "voyage"
        elif model.startswith("embed-"):
            return "cohere"
        elif "jina" in model:
            return "jina"
        elif "mistral-embed" in model:
            return "mistral"
        elif "bge-" in model or "gte-" in model:
            return "huggingface"
        elif "titan-embed" in model:
            return "bedrock"
        elif model.startswith(("text-embedding", "embedding")):
            return "openai"
        else:
            return "openai"  # Default to OpenAI
    
    def _set_api_key(self):
        """Set the appropriate environment variable for the API key.
        
        LiteLLM uses specific environment variables for each provider.
        Reference: https://docs.litellm.ai/docs/providers
        """
        provider = self._detect_provider()
        
        # Map provider to environment variable (from LiteLLM docs)
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "azure": "AZURE_API_KEY",  # or AZURE_OPENAI_API_KEY
            "cohere": "COHERE_API_KEY",
            "voyage": "VOYAGE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "jina": "JINA_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "together_ai": "TOGETHERAI_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "bedrock": "AWS_ACCESS_KEY_ID",  # Also needs AWS_SECRET_ACCESS_KEY
            "vertex_ai": "GOOGLE_APPLICATION_CREDENTIALS",  # Path to service account JSON
            "ollama": None,  # No API key needed for local
            "deepinfra": "DEEPINFRA_API_KEY",
            "ai21": "AI21_API_KEY",
            "nlp_cloud": "NLP_CLOUD_API_KEY",
        }
        
        env_var = env_vars.get(provider)
        if env_var and self.api_key:
            os.environ[env_var] = self.api_key
            
            # Special handling for AWS Bedrock
            if provider == "bedrock" and ":" in self.api_key:
                # Format: "access_key:secret_key"
                access_key, secret_key = self.api_key.split(":", 1)
                os.environ["AWS_ACCESS_KEY_ID"] = access_key
                os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key