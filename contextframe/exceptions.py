"""
Exceptions used throughout the ContextFrame package.

This module defines custom exceptions that are raised by various components
of the ContextFrame package.
"""


class ContextFrameError(Exception):
    """Base exception for all ContextFrame-related errors."""

    pass


class ValidationError(ContextFrameError):
    """Raised when validation of ContextFrame metadata or content fails."""

    pass


class RelationshipError(ContextFrameError):
    """Raised when there's an issue with ContextFrame relationships."""

    pass


class VersioningError(ContextFrameError):
    """Raised when there's an issue with ContextFrame versioning."""

    pass


class ConflictError(ContextFrameError):
    """Raised when there's a conflict during ContextFrame operations."""

    pass


class FormatError(ContextFrameError):
    """Raised when there's an issue with ContextFrame formatting."""

    pass
