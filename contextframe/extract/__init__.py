"""Lightweight document extraction module for ContextFrame.

This module provides utilities for extracting content and metadata from 
lightweight text-based formats. For heavy document processing (PDFs, images),
see the documentation for recommended external tools and integration patterns.
"""

from .base import ExtractionResult, TextExtractor
from .batch import BatchExtractor
from .extractors import (
    CSVExtractor,
    JSONExtractor,
    MarkdownExtractor,
    TextFileExtractor,
    YAMLExtractor,
)

__all__ = [
    "TextExtractor",
    "ExtractionResult",
    "BatchExtractor",
    "MarkdownExtractor",
    "JSONExtractor",
    "TextFileExtractor",
    "YAMLExtractor",
    "CSVExtractor",
]