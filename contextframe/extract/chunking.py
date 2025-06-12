"""Text chunking functionality using LlamaIndex integration."""

from .base import ExtractionResult
from collections.abc import Callable
from typing import List, Optional, Tuple


def llama_index_splitter(
    texts: list[str],
    chunk_size: int = 512,
    chunk_overlap: int | None = None,
    separator: str = " ",
) -> list[tuple[int, str]]:
    """Split texts using LlamaIndex's SentenceSplitter.
    
    This function provides a lightweight integration with LlamaIndex for
    intelligent text splitting. It's designed to be used as a pluggable
    splitter function.
    
    Args:
        texts: List of text strings to split
        chunk_size: Maximum size of each chunk (default: 512)
        chunk_overlap: Number of overlapping characters between chunks.
                      If None, defaults to min(chunk_size/4, 64)
        separator: Separator to use for splitting (default: " ")
        
    Returns:
        List of tuples (text_index, chunk_content) where text_index
        indicates which input text the chunk came from
        
    Raises:
        ImportError: If llama-index is not installed
    """
    try:
        from llama_index.core import Document
        from llama_index.core.text_splitter import SentenceSplitter
    except ImportError:
        raise ImportError(
            "LlamaIndex is required for text splitting. "
            "Install with: pip install 'contextframe[extract]'"
        )
    
    if chunk_overlap is None:
        chunk_overlap = min(chunk_size // 4, 64)
    
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=separator,
    )
    
    chunks = []
    
    for idx, text in enumerate(texts):
        # Convert to LlamaIndex Document
        doc = Document(text=text)
        
        # Split the document
        nodes = splitter.get_nodes_from_documents([doc])
        
        # Extract chunks and maintain source index
        for node in nodes:
            chunks.append((idx, node.text))
    
    return chunks


def split_extraction_results(
    results: list[ExtractionResult],
    chunk_size: int = 512,
    chunk_overlap: int | None = None,
    splitter_fn: Callable | None = None,
) -> list[ExtractionResult]:
    """Split extraction results into smaller chunks.
    
    Args:
        results: List of ExtractionResult objects to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of overlapping characters between chunks
        splitter_fn: Optional custom splitter function. If None, uses llama_index_splitter.
                    Function should accept (texts, chunk_size, chunk_overlap) and
                    return List[Tuple[text_index, chunk_content]]
                    
    Returns:
        List of new ExtractionResult objects, one per chunk
    """
    if splitter_fn is None:
        splitter_fn = llama_index_splitter
    
    # Extract texts and track sources
    texts = []
    source_results = []
    
    for result in results:
        if result.success and result.content:
            texts.append(result.content)
            source_results.append(result)
    
    if not texts:
        return results
    
    # Split texts
    chunks = splitter_fn(texts, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Create new ExtractionResult objects for chunks
    chunked_results = []
    
    # Group chunks by source
    chunk_groups = {}
    for text_idx, chunk_content in chunks:
        if text_idx not in chunk_groups:
            chunk_groups[text_idx] = []
        chunk_groups[text_idx].append(chunk_content)
    
    # Create results maintaining source metadata
    for text_idx, chunk_list in chunk_groups.items():
        source_result = source_results[text_idx]
        
        for i, chunk_content in enumerate(chunk_list):
            # Create new metadata including chunk info
            chunk_metadata = source_result.metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_count": len(chunk_list),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap or 0,
                "original_content_length": len(source_result.content),
            })
            
            # Create new result for chunk
            chunk_result = ExtractionResult(
                content=chunk_content,
                metadata=chunk_metadata,
                source=source_result.source,
                format=source_result.format,
                chunks=None,  # Don't propagate chunks to avoid confusion
                error=None,
                warnings=source_result.warnings.copy() if source_result.warnings else [],
            )
            
            chunked_results.append(chunk_result)
    
    # Include any failed results unchanged
    for result in results:
        if not result.success:
            chunked_results.append(result)
    
    return chunked_results


class ChunkingMixin:
    """Mixin class to add chunking capability to extractors.
    
    This can be mixed into any TextExtractor subclass to add
    automatic chunking support.
    """
    
    def extract_with_chunking(
        self,
        source,
        chunk_size: int = 512,
        chunk_overlap: int | None = None,
        encoding: str = "utf-8",
        **kwargs
    ) -> ExtractionResult:
        """Extract and automatically chunk the content.
        
        Args:
            source: File path or content identifier
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of overlapping characters between chunks
            encoding: Text encoding
            **kwargs: Additional extractor-specific options
            
        Returns:
            ExtractionResult with chunks field populated
        """
        # First extract normally
        result = self.extract(source, encoding=encoding, **kwargs)
        
        if not result.success or not result.content:
            return result
        
        try:
            # Split the content
            chunks = llama_index_splitter(
                [result.content],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            
            # Extract just the chunk texts
            chunk_texts = [chunk_text for _, chunk_text in chunks]
            
            # Update the result
            result.chunks = chunk_texts
            result.metadata["chunk_size"] = chunk_size
            result.metadata["chunk_overlap"] = chunk_overlap or 0
            result.metadata["chunk_count"] = len(chunk_texts)
            
        except ImportError as e:
            result.warnings.append(f"Chunking unavailable: {str(e)}")
        except Exception as e:
            result.warnings.append(f"Chunking failed: {str(e)}")
        
        return result