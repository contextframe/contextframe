"""Base classes for the document extraction module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class ExtractionResult:
    """Result of a document extraction operation.

    Attributes:
        content: The extracted text content
        metadata: Extracted or inferred metadata
        source: Source file path or identifier
        format: The detected or specified format
        chunks: Optional list of text chunks if splitting was performed
        error: Error message if extraction failed
        warnings: List of non-fatal warnings during extraction
    """

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str | Path | None = None
    format: str | None = None
    chunks: list[str] | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if extraction was successful."""
        return self.error is None and bool(self.content)

    def to_frame_record_kwargs(self) -> dict[str, Any]:
        """Convert extraction result to kwargs for FrameRecord creation.

        Maps extraction metadata to proper ContextFrame schema fields:
        - source -> source_file or source_url (based on URI scheme)
        - format -> source_type
        - Other custom fields -> custom_metadata object

        Returns:
            Dictionary suitable for FrameRecord(**kwargs)
        """
        # Extract title from metadata or generate from source
        metadata = self.metadata.copy()
        title = metadata.pop("title", None)
        if not title and self.source:
            title = Path(str(self.source)).stem
        if not title:
            title = "Untitled Document"

        # Prepare kwargs with required fields
        kwargs = {
            "title": title,
            "content": self.content,
        }

        # Map extraction fields to schema fields
        if self.source:
            source_str = str(self.source)
            if source_str.startswith(("http://", "https://", "ftp://")):
                metadata["source_url"] = source_str
            else:
                metadata["source_file"] = source_str

        if self.format:
            metadata["source_type"] = self.format

        # Identify standard schema fields
        standard_fields = {
            "source_file",
            "source_type",
            "source_url",
            "created_at",
            "modified_at",
            "author",
            "description",
            "custom_metadata",
            "tags",
            "context",
            "parent_id",
            "related_ids",
            "reference_ids",
            "member_of",
            "version",
            "language",
            "revision",
        }

        # Move non-standard fields to custom_metadata
        custom_metadata = metadata.get("custom_metadata", {})
        fields_to_move = []

        for key, value in metadata.items():
            if key not in standard_fields and not key.startswith("x_"):
                fields_to_move.append(key)
                # Convert all values to strings for custom_metadata
                if isinstance(value, (int, float, bool)):
                    custom_metadata[key] = str(value)
                elif isinstance(value, (list, dict)):
                    # For complex types, convert to JSON string
                    import json

                    custom_metadata[key] = json.dumps(value)
                else:
                    custom_metadata[key] = str(value)

        # Remove moved fields from top-level metadata
        for key in fields_to_move:
            del metadata[key]

        # Only add custom_metadata if it has content
        if custom_metadata:
            metadata["custom_metadata"] = custom_metadata

        # Add all metadata to kwargs
        kwargs.update(metadata)

        return kwargs


class TextExtractor(ABC):
    """Abstract base class for text extractors.

    Each extractor implementation should handle a specific file format
    or content type.
    """

    def __init__(self):
        """Initialize the extractor."""
        self.supported_extensions: list[str] = []
        self.format_name: str = "unknown"

    @abstractmethod
    def can_extract(self, source: str | Path) -> bool:
        """Check if this extractor can handle the given source.

        Args:
            source: File path or content identifier

        Returns:
            True if this extractor can handle the source
        """
        pass

    @abstractmethod
    def extract(
        self, source: str | Path, encoding: str = "utf-8", **kwargs
    ) -> ExtractionResult:
        """Extract content and metadata from the source.

        Args:
            source: File path or content identifier
            encoding: Text encoding to use
            **kwargs: Additional extractor-specific options

        Returns:
            ExtractionResult containing the extracted data
        """
        pass

    def extract_from_string(
        self, content: str, source: str | Path | None = None, **kwargs
    ) -> ExtractionResult:
        """Extract from string content instead of file.

        Args:
            content: The text content to process
            source: Optional source identifier
            **kwargs: Additional extractor-specific options

        Returns:
            ExtractionResult containing the extracted data
        """
        # Default implementation - subclasses can override for format-specific parsing
        return ExtractionResult(content=content, source=source, format=self.format_name)

    def validate_source(self, source: str | Path) -> Path:
        """Validate and convert source to Path object.

        Args:
            source: File path or content identifier

        Returns:
            Path object

        Raises:
            ValueError: If source is invalid or doesn't exist
        """
        path = Path(source) if not isinstance(source, Path) else source

        if not path.exists():
            raise ValueError(f"Source file does not exist: {path}")

        if not path.is_file():
            raise ValueError(f"Source is not a file: {path}")

        return path


class ExtractorRegistry:
    """Registry for managing available extractors."""

    def __init__(self):
        """Initialize the registry."""
        self._extractors: list[TextExtractor] = []

    def register(self, extractor: TextExtractor) -> None:
        """Register an extractor.

        Args:
            extractor: The extractor instance to register
        """
        self._extractors.append(extractor)

    def find_extractor(self, source: str | Path) -> TextExtractor | None:
        """Find an appropriate extractor for the given source.

        Args:
            source: File path or content identifier

        Returns:
            The first extractor that can handle the source, or None
        """
        for extractor in self._extractors:
            if extractor.can_extract(source):
                return extractor
        return None

    def get_supported_formats(self) -> dict[str, list[str]]:
        """Get all supported formats and their extensions.

        Returns:
            Dictionary mapping format names to lists of extensions
        """
        formats = {}
        for extractor in self._extractors:
            formats[extractor.format_name] = extractor.supported_extensions
        return formats


# Global registry instance
registry = ExtractorRegistry()
