"""Integration between extraction and embedding modules."""

from typing import List, Optional

import numpy as np

from ..extract.base import ExtractionResult
from ..frame import FrameRecord
from .base import EmbeddingProvider
from .batch import BatchEmbedder


def embed_extraction_results(
    results: List[ExtractionResult],
    provider: EmbeddingProvider,
    embed_content: bool = True,
    embed_chunks: bool = False,
    **kwargs
) -> List[ExtractionResult]:
    """Add embeddings to extraction results.
    
    Args:
        results: List of extraction results
        provider: Embedding provider to use
        embed_content: Whether to embed the main content
        embed_chunks: Whether to embed chunks (if present)
        **kwargs: Additional arguments for embedding
        
    Returns:
        List of extraction results with embeddings added to metadata
    """
    if not embed_content and not embed_chunks:
        return results
    
    # Create batch embedder
    embedder = BatchEmbedder(provider)
    
    # Collect texts to embed
    texts_to_embed = []
    text_sources = []  # Track which result and type each text comes from
    
    for i, result in enumerate(results):
        if embed_content and result.content:
            texts_to_embed.append(result.content)
            text_sources.append((i, "content", None))
        
        if embed_chunks and result.chunks:
            for j, chunk in enumerate(result.chunks):
                texts_to_embed.append(chunk)
                text_sources.append((i, "chunk", j))
    
    if not texts_to_embed:
        return results
    
    # Generate embeddings
    embedding_result = embedder.embed_batch(texts_to_embed, **kwargs)
    
    # Add embeddings to results
    enhanced_results = []
    
    for i, result in enumerate(results):
        # Copy result
        enhanced = ExtractionResult(
            content=result.content,
            metadata=result.metadata.copy(),
            source=result.source,
            format=result.format,
            chunks=result.chunks,
            error=result.error,
            warnings=result.warnings.copy(),
        )
        
        # Add embedding metadata
        for j, (source_idx, source_type, chunk_idx) in enumerate(text_sources):
            if source_idx != i:
                continue
                
            if source_type == "content":
                enhanced.metadata["content_embedding"] = embedding_result.embeddings[j]
                enhanced.metadata["embedding_model"] = embedding_result.model
                enhanced.metadata["embedding_dimension"] = embedding_result.dimension
            elif source_type == "chunk" and chunk_idx is not None:
                if "chunk_embeddings" not in enhanced.metadata:
                    enhanced.metadata["chunk_embeddings"] = []
                enhanced.metadata["chunk_embeddings"].append({
                    "index": chunk_idx,
                    "embedding": embedding_result.embeddings[j]
                })
        
        enhanced_results.append(enhanced)
    
    return enhanced_results


def create_frame_records_with_embeddings(
    extraction_results: List[ExtractionResult],
    provider: EmbeddingProvider,
    record_type: str = "document",
    embed_dimension: Optional[int] = None,
    **kwargs
) -> List[FrameRecord]:
    """Create FrameRecords from extraction results with embeddings.
    
    This function combines extraction and embedding to create FrameRecords
    ready for storage in a ContextFrame dataset.
    
    Args:
        extraction_results: List of extraction results
        provider: Embedding provider to use
        record_type: Type of record to create
        embed_dimension: Expected embedding dimension (for validation)
        **kwargs: Additional arguments for embedding
        
    Returns:
        List of FrameRecords with embeddings
    """
    # Add embeddings to extraction results
    results_with_embeddings = embed_extraction_results(
        extraction_results,
        provider,
        embed_content=True,
        embed_chunks=False,  # Don't embed chunks for main records
        **kwargs
    )
    
    # Create FrameRecords
    frame_records = []
    
    for result in results_with_embeddings:
        # Get frame record kwargs
        frame_kwargs = result.to_frame_record_kwargs()
        frame_kwargs["record_type"] = record_type
        
        # Extract embedding if present
        embedding = None
        if "content_embedding" in result.metadata:
            embedding = result.metadata["content_embedding"]
            # Remove from metadata to avoid duplication
            del result.metadata["content_embedding"]
            
            # Convert to numpy array for FrameRecord
            embedding = np.array(embedding, dtype=np.float32)
            
            # Validate dimension if specified
            if embed_dimension and len(embedding) != embed_dimension:
                raise ValueError(
                    f"Embedding dimension {len(embedding)} does not match "
                    f"expected dimension {embed_dimension}"
                )
        
        # Create FrameRecord with embedding
        if embedding is not None:
            frame_kwargs["vector"] = embedding
            frame_kwargs["embed_dim"] = len(embedding)
        
        frame = FrameRecord.create(**frame_kwargs)
        frame_records.append(frame)
    
    return frame_records