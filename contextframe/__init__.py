"""
Context Frame is a file format and toolkit for working with
documents with structured metadata for AI workflows.
"""

# Direct imports for convenience
from .exceptions import (
    ConflictError,
    ContextFrameError,
    FormatError,
    RelationshipError,
    ValidationError,
    VersioningError,
)
from .frame import FrameDataset, FrameRecord

# Collection helpers are still applicable (operate via FrameDataset internally)
# from .collection import Collection  # type: ignore  # noqa: E402
# Convenience exports
from .helpers.metadata_utils import (
    add_relationship_to_metadata,
    compare_semantic_versions,
    create_metadata,
    create_relationship,
    generate_uuid,
    get_standard_fields,
    is_semantic_version,
    is_valid_uuid,
    next_version,
    validate_relationships,
)  # noqa: E402
from .schema import MimeTypes, RecordType, get_schema  # noqa: E402

# Define version
__version__ = "0.1.0"


# CLI entry point
def cli():
    """Command-line interface entry point."""
    from .cli import main

    main()


# Public re-exports
__all__ = [
    # Public API for the library
    "FrameRecord",
    "FrameDataset",
    # Metadata helpers re-exported for convenience
    "create_metadata",
    "create_relationship",
    "add_relationship_to_metadata",
    "validate_relationships",
    "is_semantic_version",
    "compare_semantic_versions",
    "next_version",
    "get_standard_fields",
    "generate_uuid",
    "is_valid_uuid",
    # Schema access
    "get_schema",
    "RecordType",
    "MimeTypes",
    # Exceptions
    "ContextFrameError",
    "ValidationError",
    "RelationshipError",
    "VersioningError",
    "ConflictError",
    "FormatError",
    # CLI entry point
    "cli",
]
