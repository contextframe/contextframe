"""
Schema module for ContextFrame.

This module provides schema validation and definition functionality for ContextFrame.
"""

# Public re-exports for convenience
from .contextframe_schema import MimeTypes, RecordType, get_schema  # noqa: F401

__all__ = [
    "get_schema",
    "RecordType",
    "MimeTypes",
]
