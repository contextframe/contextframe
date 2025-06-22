"""Text chunking functionality using semantic-text-splitter."""

from .base import ExtractionResult
from collections.abc import Callable
from typing import List, Literal, Optional, Tuple, Union


def semantic_splitter(
    texts: list[str],
    chunk_size: int = 512,
    chunk_overlap: int | None = None,
    splitter_type: Literal["text", "markdown", "code"] = "text",
    tokenizer_model: str | None = None,
    language: str | None = None,
) -> list[tuple[int, str]]:
    """Split texts using semantic-text-splitter.

    This function provides high-performance text splitting using the Rust-based
    semantic-text-splitter library. It supports character, token, and semantic
    splitting for text, markdown, and code.

    Args:
        texts: List of text strings to split
        chunk_size: Maximum size of each chunk (default: 512)
        chunk_overlap: Number of overlapping characters between chunks.
                      If None, defaults to 0 (no overlap by default)
        splitter_type: Type of splitter - "text", "markdown", or "code"
        tokenizer_model: Optional tokenizer model name:
                        - OpenAI models: "gpt-3.5-turbo", "gpt-4", etc.
                        - HuggingFace models: "bert-base-uncased", etc.
                        - None for character-based splitting
        language: Required for code splitting (e.g., "python", "javascript")

    Returns:
        List of tuples (text_index, chunk_content) where text_index
        indicates which input text the chunk came from

    Raises:
        ImportError: If semantic-text-splitter is not installed
        ValueError: If invalid parameters are provided
    """
    try:
        from semantic_text_splitter import CodeSplitter, MarkdownSplitter, TextSplitter
    except ImportError:
        raise ImportError(
            "semantic-text-splitter is required for text splitting. "
            "Install with: pip install semantic-text-splitter"
        )

    if chunk_overlap is None:
        chunk_overlap = 0

    # Create appropriate splitter based on type
    if splitter_type == "code":
        if not language:
            raise ValueError("Language parameter is required for code splitting")

        # Import appropriate tree-sitter language
        # Map common file extensions to language names if needed
        language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "rs": "rust",
            "go": "go",
            "cpp": "cpp",
            "c": "c",
            "java": "java",
            "rb": "ruby",
            "php": "php",
            "html": "html",
            "css": "css",
            "json": "json",
            "yaml": "yaml",
            "yml": "yaml",
            "toml": "toml",
            "xml": "xml",
            "sh": "bash",
            "bash": "bash",
        }

        # Normalize language name
        lang_name = language_map.get(language.lower(), language.lower())

        try:
            lang_module = __import__(f"tree_sitter_{lang_name}")
            splitter = CodeSplitter(lang_module.language(), chunk_size)
        except ImportError:
            raise ImportError(
                f"tree-sitter-{lang_name} is required for {language} code splitting. "
                f"Install with: pip install tree-sitter-{lang_name}"
            )
    else:
        # Choose between TextSplitter and MarkdownSplitter
        SplitterClass = (
            MarkdownSplitter if splitter_type == "markdown" else TextSplitter
        )

        # Create splitter with appropriate sizing strategy
        if tokenizer_model:
            if tokenizer_model.startswith(("gpt", "claude", "text-embedding")):
                # OpenAI-style models using tiktoken
                splitter = SplitterClass.from_tiktoken_model(
                    tokenizer_model, chunk_size
                )
            else:
                # HuggingFace tokenizer
                try:
                    from tokenizers import Tokenizer

                    tokenizer = Tokenizer.from_pretrained(tokenizer_model)
                    splitter = SplitterClass.from_huggingface_tokenizer(
                        tokenizer, chunk_size
                    )
                except ImportError:
                    raise ImportError(
                        f"tokenizers package is required for HuggingFace tokenizer '{tokenizer_model}'. "
                        "Install with: pip install tokenizers"
                    )
                except Exception as e:
                    # Fallback to character-based if model not found
                    import warnings

                    warnings.warn(
                        f"Failed to load tokenizer '{tokenizer_model}': {e}. "
                        "Falling back to character-based splitting."
                    )
                    splitter = SplitterClass(chunk_size)
        else:
            # Character-based splitting
            splitter = SplitterClass(chunk_size)

    chunks = []

    # Process each text
    for idx, text in enumerate(texts):
        # Get chunks with indices for potential overlap support
        text_chunks = splitter.chunks(text)

        # Add chunks with source index
        for chunk_text in text_chunks:
            chunks.append((idx, chunk_text))

    return chunks


def split_extraction_results(
    results: list[ExtractionResult],
    chunk_size: int = 512,
    chunk_overlap: int | None = None,
    splitter_fn: Callable | None = None,
    splitter_type: Literal["text", "markdown", "code"] = "text",
    tokenizer_model: str | None = None,
) -> list[ExtractionResult]:
    """Split extraction results into smaller chunks.

    Args:
        results: List of ExtractionResult objects to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of overlapping characters between chunks
        splitter_fn: Optional custom splitter function. If None, uses semantic_splitter.
                    Function should accept (texts, chunk_size, chunk_overlap, **kwargs) and
                    return List[Tuple[text_index, chunk_content]]
        splitter_type: Type of splitter - "text", "markdown", or "code"
        tokenizer_model: Optional tokenizer model name for token-based splitting

    Returns:
        List of new ExtractionResult objects, one per chunk
    """
    if splitter_fn is None:
        splitter_fn = semantic_splitter

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
    chunks = splitter_fn(
        texts,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        splitter_type=splitter_type,
        tokenizer_model=tokenizer_model,
    )

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
            chunk_metadata.update(
                {
                    "chunk_index": i,
                    "chunk_count": len(chunk_list),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap or 0,
                    "original_content_length": len(source_result.content),
                }
            )

            # Create new result for chunk
            chunk_result = ExtractionResult(
                content=chunk_content,
                metadata=chunk_metadata,
                source=source_result.source,
                format=source_result.format,
                chunks=None,  # Don't propagate chunks to avoid confusion
                error=None,
                warnings=source_result.warnings.copy()
                if source_result.warnings
                else [],
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
    automatic chunking support using semantic-text-splitter.
    """

    def extract_with_chunking(
        self,
        source,
        chunk_size: int = 512,
        chunk_overlap: int | None = None,
        encoding: str = "utf-8",
        splitter_type: Literal["text", "markdown", "code"] = "text",
        tokenizer_model: str | None = None,
        **kwargs,
    ) -> ExtractionResult:
        """Extract and automatically chunk the content.

        Args:
            source: File path or content identifier
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of overlapping characters between chunks
            encoding: Text encoding
            splitter_type: Type of splitter - "text", "markdown", or "code"
            tokenizer_model: Optional tokenizer model name for token-based splitting
            **kwargs: Additional extractor-specific options

        Returns:
            ExtractionResult with chunks field populated
        """
        # First extract normally
        result = self.extract(source, encoding=encoding, **kwargs)

        if not result.success or not result.content:
            return result

        try:
            # Detect format for splitter type if not specified
            if splitter_type == "text" and result.format:
                if result.format.lower() in ["markdown", "md"]:
                    splitter_type = "markdown"
                elif result.format.lower() in [
                    "py",
                    "js",
                    "ts",
                    "java",
                    "cpp",
                    "c",
                    "go",
                    "rust",
                ]:
                    splitter_type = "code"

            # Split the content
            chunks = semantic_splitter(
                [result.content],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                splitter_type=splitter_type,
                tokenizer_model=tokenizer_model,
                language=result.format.lower() if splitter_type == "code" else None,
            )

            # Extract just the chunk texts
            chunk_texts = [chunk_text for _, chunk_text in chunks]

            # Update the result
            result.chunks = chunk_texts
            result.metadata["chunk_size"] = chunk_size
            result.metadata["chunk_overlap"] = chunk_overlap or 0
            result.metadata["chunk_count"] = len(chunk_texts)
            result.metadata["splitter_type"] = splitter_type
            if tokenizer_model:
                result.metadata["tokenizer_model"] = tokenizer_model

        except ImportError as e:
            result.warnings.append(f"Chunking unavailable: {str(e)}")
        except Exception as e:
            result.warnings.append(f"Chunking failed: {str(e)}")

        return result

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int | None = None,
        splitter_type: Literal["text", "markdown"] = "text",
        tokenizer_model: str | None = None,
    ) -> list[str]:
        """Convenience method to chunk a single text string.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of overlapping characters between chunks
            splitter_type: Type of splitter - "text" or "markdown"
            tokenizer_model: Optional tokenizer model name

        Returns:
            List of chunk strings
        """
        chunks = semantic_splitter(
            [text],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            splitter_type=splitter_type,
            tokenizer_model=tokenizer_model,
        )
        return [chunk_text for _, chunk_text in chunks]
