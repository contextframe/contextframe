"""Batch embedding functionality for processing large text collections."""

import time
from typing import Callable, List, Optional, Union

from .base import EmbeddingProvider, EmbeddingResult


class BatchEmbedder:
    """Handles batch embedding with rate limiting and progress tracking.
    
    This class efficiently processes large collections of texts by:
    - Batching requests to respect API limits
    - Handling rate limiting and retries
    - Providing progress callbacks
    - Managing memory efficiently
    """
    
    def __init__(
        self,
        provider: EmbeddingProvider,
        batch_size: Optional[int] = None,
        rate_limit_delay: float = 0.1,
        max_retries: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """Initialize batch embedder.
        
        Args:
            provider: The embedding provider to use
            batch_size: Batch size (uses provider's max if not specified)
            rate_limit_delay: Delay between batches in seconds
            max_retries: Maximum retries for failed batches
            progress_callback: Callback function(completed, total) for progress
        """
        self.provider = provider
        self.batch_size = batch_size or provider.max_batch_size or 100
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.progress_callback = progress_callback
    
    def embed_batch(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResult:
        """Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Combined EmbeddingResult for all texts
        """
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        all_embeddings = []
        total_usage = {"prompt_tokens": 0, "total_tokens": 0}
        completed = 0
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Retry logic
            for attempt in range(self.max_retries):
                try:
                    # Generate embeddings for batch
                    result = self.provider.embed(batch, **kwargs)
                    
                    # Accumulate embeddings
                    all_embeddings.extend(result.embeddings)
                    
                    # Accumulate usage if available
                    if result.usage:
                        total_usage["prompt_tokens"] += result.usage.get("prompt_tokens", 0)
                        total_usage["total_tokens"] += result.usage.get("total_tokens", 0)
                    
                    # Update progress
                    completed += len(batch)
                    if self.progress_callback:
                        self.progress_callback(completed, len(texts))
                    
                    # Rate limit delay
                    if i + self.batch_size < len(texts):
                        time.sleep(self.rate_limit_delay)
                    
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(
                            f"Failed to embed batch after {self.max_retries} attempts: {str(e)}"
                        )
                    else:
                        # Exponential backoff
                        time.sleep(2 ** attempt)
        
        # Get model and dimension from the accumulated results
        if not all_embeddings:
            raise RuntimeError("No embeddings were generated")
            
        model = self.provider.model
        dimension = len(all_embeddings[0]) if all_embeddings else None
        
        return EmbeddingResult(
            embeddings=all_embeddings,
            model=model,
            dimension=dimension,
            usage=total_usage if total_usage["total_tokens"] > 0 else None,
            metadata={
                "batch_size": self.batch_size,
                "total_texts": len(texts),
                "provider": getattr(self.provider, "_detect_provider", lambda: "unknown")()
                if hasattr(self.provider, "_detect_provider") else "unknown"
            }
        )
    
    def embed_documents(
        self,
        documents: List[dict],
        text_field: str = "content",
        id_field: str = "id",
        **kwargs
    ) -> List[dict]:
        """Embed documents and return them with embeddings added.
        
        Args:
            documents: List of document dictionaries
            text_field: Field name containing text to embed
            id_field: Field name for document ID
            **kwargs: Additional arguments passed to provider
            
        Returns:
            List of documents with 'embedding' field added
        """
        # Extract texts
        texts = []
        valid_indices = []
        
        for i, doc in enumerate(documents):
            if text_field in doc and doc[text_field]:
                texts.append(doc[text_field])
                valid_indices.append(i)
        
        if not texts:
            raise ValueError(f"No documents contain non-empty '{text_field}' field")
        
        # Generate embeddings
        result = self.embed_batch(texts, **kwargs)
        
        # Create result documents
        result_docs = []
        embedding_idx = 0
        
        for i, doc in enumerate(documents):
            doc_copy = doc.copy()
            
            if i in valid_indices:
                doc_copy["embedding"] = result.embeddings[embedding_idx]
                doc_copy["embedding_model"] = result.model
                doc_copy["embedding_dimension"] = result.dimension
                embedding_idx += 1
            else:
                doc_copy["embedding"] = None
                doc_copy["embedding_error"] = "No text content"
            
            result_docs.append(doc_copy)
        
        return result_docs


def create_embedder(
    model: str = "text-embedding-ada-002",
    provider_type: str = "litellm",
    batch_size: Optional[int] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> BatchEmbedder:
    """Create a batch embedder with the specified provider.
    
    Args:
        model: Encoding model to use
        provider_type: Type of provider (currently only "litellm")
        batch_size: Batch size for processing
        api_key: API key for the provider
        **kwargs: Additional arguments for the provider
        
    Returns:
        Configured BatchEmbedder instance
    """
    if provider_type == "litellm":
        from .litellm_provider import LiteLLMProvider
        provider = LiteLLMProvider(model=model, api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return BatchEmbedder(provider, batch_size=batch_size)