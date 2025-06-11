"""
Schema module for ContextFrame.

This module provides schema validation and definition functionality for ContextFrame.
"""

# Public re-exports for convenience
from .contextframe_schema import get_schema, RecordType, MimeTypes  # noqa: F401

__all__ = [
    "get_schema",
    "RecordType",
    "MimeTypes",
]
