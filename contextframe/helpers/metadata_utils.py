"""Light-weight metadata helpers for ContextFrame.

This module provides a set of utilities for working with Lance‐backed Frame records.

Public surface
--------------
create_metadata           – apply defaults, ensure a UUID
create_relationship        – small helper to build a relationship dict
add_relationship_to_metadata
get_standard_fields        – expose STANDARD_METADATA_FIELDS
is_semantic_version        – version helpers (compare / next_version)
compare_semantic_versions
next_version
validate_relationships     – validate a list of relationship objects

All functions are intentionally *pure* (no I/O).
"""

from __future__ import annotations

import datetime as _dt
import re
import uuid as _uuid
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants / basic validation helpers
# ---------------------------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d"

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

STANDARD_METADATA_FIELDS: dict[str, dict[str, Any]] = {
    "title": {"type": str, "required": True, "description": "Document title"},
    "version": {"type": str, "required": False, "description": "Semantic version"},
    "context": {"type": str, "required": False},
    # Identification
    "uuid": {"type": str, "required": False},
    "uri": {"type": str, "required": False},
    "collection": {"type": str, "required": False},
    "author": {"type": str, "required": False},
    "created_at": {"type": str, "required": False},
    "updated_at": {"type": str, "required": False},
    "tags": {"type": list, "required": False},
    "status": {"type": str, "required": False},
    "record_type": {
        "type": str,
        "required": False,
        "description": "Logical type of row (see RecordType enum)",
    },
}

VALID_RELATIONSHIP_TYPES = {
    "parent",
    "child",
    "related",
    "reference",
    "member_of",
    "contains",
}

# ---------------------------------------------------------------------------
# Simple primitives
# ---------------------------------------------------------------------------


def generate_uuid() -> str:
    """Generate a fresh v4 UUID as a string."""
    return str(_uuid.uuid4())


def is_valid_uuid(value: str) -> bool:  # noqa: D401
    """Check if a string is a valid UUID."""
    try:
        _uuid.UUID(value)
        return True
    except ValueError:
        return False


def is_semantic_version(v: str) -> bool:
    """Check if a string matches the semantic version pattern (X.Y.Z)."""
    return bool(SEMVER_RE.match(v))


def compare_semantic_versions(v1: str, v2: str) -> int:
    """Return -1 / 0 / +1 if *v1* <, ==, > *v2*."""
    m1 = SEMVER_RE.match(v1)
    m2 = SEMVER_RE.match(v2)
    if not (m1 and m2):
        raise ValueError("Invalid semantic version string(s)")
    t1 = tuple(map(int, m1.groups()))
    t2 = tuple(map(int, m2.groups()))
    return (t1 > t2) - (t1 < t2)


def next_version(current: str, *, version_type: str = "patch") -> str:
    """Increment a semantic version string.

    Parameters
    ----------
    current : str
        The current semantic version string (e.g., "1.0.3").
    version_type : str, optional
        The type of version bump: "major", "minor", or "patch".
        Defaults to "patch".

    Returns
    -------
    str
        The next semantic version string.

    Raises
    ------
    ValueError
        If `current` is not a valid semantic version string.
    """
    match = SEMVER_RE.match(current)
    if not match:
        raise ValueError(f"Invalid semantic version string: {current}")
    major, minor, patch = map(int, match.groups())
    if version_type == "major":
        major += 1
        minor = patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    return f"{major}.{minor}.{patch}"


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

DEFAULT_METADATA = {
    "created_at": _dt.date.today().strftime(DATE_FORMAT),
}


def _merge(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
    out = d1.copy()
    for k, v in d2.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def create_metadata(
    base: dict[str, Any] | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Return a new metadata dict with defaults applied and a UUID ensured."""
    meta = _merge(DEFAULT_METADATA, base or {})
    meta = _merge(meta, kwargs)
    if "uuid" not in meta or not is_valid_uuid(meta["uuid"]):
        meta["uuid"] = generate_uuid()
    return meta


# ---------------------------------------------------------------------------
# Relationship helpers
# ---------------------------------------------------------------------------


def create_relationship(
    reference: str,
    *,
    rel_type: str = "related",
    title: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a relationship object compatible with the JSON schema."""
    if rel_type not in VALID_RELATIONSHIP_TYPES:
        raise ValueError(f"rel_type must be one of {sorted(VALID_RELATIONSHIP_TYPES)}")

    rel: dict[str, Any] = {"type": rel_type}
    if is_valid_uuid(reference):
        rel["id"] = reference
    else:
        # Assume path for simplicity.  Caller can still put a URI in *reference*
        rel["path"] = reference
    if title:
        rel["title"] = title
    if description:
        rel["description"] = description
    return rel


def add_relationship_to_metadata(meta: dict[str, Any], rel: dict[str, Any]) -> None:
    """Append a relationship dictionary to the 'relationships' list in metadata.

    If the 'relationships' key does not exist in `meta`, it will be created.

    Parameters
    ----------
    meta : dict[str, Any]
        The metadata dictionary to modify.
    rel : dict[str, Any]
        The relationship dictionary to add.
    """
    meta.setdefault("relationships", []).append(rel)


def validate_relationships(rels: list[dict[str, Any]]) -> None:
    """Validate a list of relationship objects.

    Ensures each relationship has a valid type and at least one identifier.

    Parameters
    ----------
    rels : list[dict[str, Any]]
        A list of relationship dictionaries to validate.

    Raises
    ------
    ValueError
        If any relationship is invalid.
    """
    for r in rels:
        if "type" not in r or r["type"] not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid relationship type in {r}")
        # Ensure at least one identifier field is present.
        if not any(k in r for k in ("id", "path", "uri", "cid")):
            raise ValueError(f"Relationship missing identifier (id|path|uri|cid): {r}")


# ---------------------------------------------------------------------------
# Public re-exports for package root convenience
# ---------------------------------------------------------------------------

__all__ = [
    "create_metadata",
    "get_standard_fields",
    "create_relationship",
    "add_relationship_to_metadata",
    "validate_relationships",
    "is_semantic_version",
    "compare_semantic_versions",
    "next_version",
    "generate_uuid",
    "is_valid_uuid",
]


def get_standard_fields():  # noqa: D401
    """Return a copy of the standard metadata fields."""
    return STANDARD_METADATA_FIELDS.copy()
