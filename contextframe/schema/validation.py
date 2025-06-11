"""
Enhanced schema validation for **Context Frame** documents.

This module provides advanced schema validation capabilities for Context Frame
metadata, including support for validation profiles, conditional validation,
and custom rules.
"""

import json
import jsonschema
import os
import re
from ..exceptions import ValidationError
from collections.abc import Callable
from jsonschema import Draft7Validator, validators
from pathlib import Path
from typing import Any, Optional, Union

# Default schema path (canonical JSON schema for Context Frame metadata)
DEFAULT_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "schema",
    "contextframe_schema.json",
)

# Cache for loaded schemas
_schema_cache: dict[str, dict[str, Any]] = {}

# Validation profiles
VALIDATION_PROFILES = {
    'minimal': ['title'],
    'standard': ['title', 'uuid', 'created_at', 'updated_at'],
    'publication': ['title', 'uuid', 'author', 'created_at', 'updated_at', 'status'],
    'collection': [
        'title',
        'uuid',
        'created_at',
        'updated_at',
        'collection',
        'collection_id',
    ],
    'archival': [
        'title',
        'uuid',
        'author',
        'created_at',
        'updated_at',
        'tags',
        'status',
    ],
}


# Custom validation functions
def is_semantic_version(instance):
    """Check if a string follows semantic versioning format (X.Y.Z)."""
    if not isinstance(instance, str):
        return False
    return bool(re.match(r'^\d+\.\d+\.\d+$', instance))


def extend_with_semantic_version(validator_class):
    """Extend jsonschema validator with 'semantic-version' format."""
    # Make sure FORMAT_CHECKER exists and has a checks method
    if not hasattr(validator_class, 'FORMAT_CHECKER') or not hasattr(
        validator_class.FORMAT_CHECKER, 'checks'
    ):
        # Create a copy of the validator class to avoid modifying the original
        return validator_class

    try:
        validate_format = validator_class.FORMAT_CHECKER.checks("format")

        @validate_format.checks('semantic-version')
        def is_semantic_version_format(instance):
            return is_semantic_version(instance)
    except (AttributeError, TypeError):
        # If there's an error, just return the original validator class
        pass

    return validator_class


# Create extended validator with custom formats
try:
    ExtendedValidator = extend_with_semantic_version(Draft7Validator)
except Exception:
    # Fallback to the original validator if extension fails
    ExtendedValidator = Draft7Validator


def extend_with_default(validator_class):
    """Extend jsonschema validator to set default values."""
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if (
                "default" in subschema
                and instance is not None
                and property not in instance
            ):
                instance[property] = subschema["default"]

        yield from validate_properties(validator, properties, instance, schema)

    return validators.extend(validator_class, {"properties": set_defaults})


# Create validator with default value support
DefaultSettingValidator = extend_with_default(ExtendedValidator)


def load_schema(schema_path: str | None = None) -> dict[str, Any]:
    """
    Load a JSON schema from a file, with caching for performance.

    Args:
        schema_path: Path to the schema file. If None, uses the default schema.

    Returns:
        The loaded schema as a dictionary.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        ValidationError: If the schema is not valid JSON.
    """
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    # Use cached schema if available
    if schema_path in _schema_cache:
        return _schema_cache[schema_path]

    try:
        with open(schema_path, encoding='utf-8') as f:
            schema = json.load(f)

        # Cache the schema
        _schema_cache[schema_path] = schema
        return schema
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON schema: {e}") from e


def validate_metadata_with_schema(
    metadata: dict[str, Any],
    schema_path: str | None = None,
    profile: str | None = None,
    set_defaults: bool = True,
    additional_properties: bool = False,
) -> tuple[bool, dict[str, str]]:
    """
    Validate metadata against a JSON schema with extended capabilities.

    Args:
        metadata: The metadata to validate.
        schema_path: Path to the schema file. If None, uses the default schema.
        profile: Validation profile to use ('minimal', 'standard', 'publication', 'collection', 'archival').
        set_defaults: Whether to set default values for missing properties.
        additional_properties: Whether to allow additional properties not defined in the schema.

    Returns:
        A tuple containing (is_valid, error_messages).

    Raises:
        ValidationError: If the schema file cannot be loaded.
    """
    # Load the schema
    schema = load_schema(schema_path)

    # Make a copy of the schema and metadata to avoid modifying the originals
    schema_copy = schema.copy()
    metadata_copy = metadata.copy()

    # Apply validation profile if specified
    if profile and profile in VALIDATION_PROFILES:
        # Override required fields based on profile
        schema_copy["required"] = VALIDATION_PROFILES[profile]

    # Set additionalProperties based on parameter
    schema_copy["additionalProperties"] = additional_properties

    # Validate using the appropriate validator
    validator_class = DefaultSettingValidator if set_defaults else ExtendedValidator
    validator = validator_class(schema_copy)

    # Collect all validation errors
    errors = {}
    for error in validator.iter_errors(metadata_copy):
        # Create user-friendly error message
        if error.path:
            field = ".".join(str(path) for path in error.path)
        else:
            field = "(document)"

        errors[field] = error.message

    # If defaults were set, update the original metadata
    if set_defaults and not errors:
        metadata.update(metadata_copy)

    return (len(errors) == 0, errors)


def create_validation_rule(
    field_name: str, validation_func: Callable[[Any], bool], error_message: str
) -> Callable[[dict[str, Any]], str | None]:
    """
    Create a custom validation rule function.

    Args:
        field_name: The name of the field to validate.
        validation_func: A function that takes the field value and returns True if valid.
        error_message: The error message if validation fails.

    Returns:
        A validation function that takes metadata and returns None or an error message.
    """

    def validation_rule(metadata: dict[str, Any]) -> str | None:
        # Skip validation if field is not present
        if field_name not in metadata:
            return None

        # Apply validation function
        if not validation_func(metadata[field_name]):
            return error_message

        return None

    return validation_rule


def validate_metadata_with_rules(
    metadata: dict[str, Any], rules: list[Callable[[dict[str, Any]], str | None]]
) -> tuple[bool, dict[str, str]]:
    """
    Validate metadata using custom validation rules.

    Args:
        metadata: The metadata to validate.
        rules: List of validation rule functions.

    Returns:
        A tuple containing (is_valid, error_messages).
    """
    errors = {}

    for rule in rules:
        error = rule(metadata)
        if error:
            # Use function name as key if available, otherwise use a sequential number
            key = getattr(rule, '__name__', f"rule_{len(errors)}")
            errors[key] = error

    return (len(errors) == 0, errors)


def validate_metadata_conditional(
    metadata: dict[str, Any], conditions: dict[str, dict[str, list[str]]]
) -> tuple[bool, dict[str, str]]:
    """
    Validate metadata with conditional requirements.

    Args:
        metadata: The metadata to validate.
        conditions: A dictionary mapping field names to conditions that make other fields required.
            Example: {'status': {'published': ['author', 'updated_at']}}

    Returns:
        A tuple containing (is_valid, error_messages).
    """
    errors = {}

    for field, condition_map in conditions.items():
        # Skip if the conditional field is not in metadata
        if field not in metadata:
            continue

        value = metadata[field]

        # Check if this value has any conditions
        if value in condition_map:
            # These fields are now required
            required_fields = condition_map[value]

            for required_field in required_fields:
                if (
                    required_field not in metadata
                    or metadata[required_field] is None
                    or metadata[required_field] == ""
                ):
                    errors[required_field] = (
                        f"'{required_field}' is required when '{field}' is '{value}'"
                    )

    return (len(errors) == 0, errors)


def validate_relationships_advanced(
    metadata: dict[str, Any],
    validate_references: bool = False,
    base_dir: str | None = None,
) -> tuple[bool, dict[str, str]]:
    """
    Perform advanced validation of relationship references.

    Args:
        metadata: The metadata to validate.
        validate_references: Whether to check if referenced documents exist.
        base_dir: Base directory for resolving relative paths.

    Returns:
        A tuple containing (is_valid, error_messages).
    """
    if "relationships" not in metadata or not metadata["relationships"]:
        return (True, {})

    errors = {}

    for i, rel in enumerate(metadata["relationships"]):
        # Basic structure validation
        if not isinstance(rel, dict):
            errors[f"relationships[{i}]"] = "Relationship must be an object"
            continue

        if "type" not in rel:
            errors[f"relationships[{i}].type"] = "Relationship type is required"
            continue

        if rel["type"] not in ["parent", "child", "related", "reference"]:
            errors[f"relationships[{i}].type"] = (
                f"Invalid relationship type: {rel['type']}"
            )
            continue

        # Check for at least one identifier
        has_id = any(key in rel for key in ["id", "uri", "path", "cid"])
        if not has_id:
            errors[f"relationships[{i}]"] = (
                "Relationship must have at least one of: id, uri, path, or cid"
            )
            continue

        # Validate reference existence if requested
        if validate_references and base_dir and "path" in rel:
            path = rel["path"]
            full_path = os.path.join(base_dir, path)

            if not os.path.exists(full_path):
                errors[f"relationships[{i}].path"] = (
                    f"Referenced document does not exist: {path}"
                )

    return (len(errors) == 0, errors)


def validate_metadata_complete(
    metadata: dict[str, Any],
    schema_path: str | None = None,
    profile: str | None = None,
    custom_rules: list[Callable] | None = None,
    conditions: dict[str, dict[str, list[str]]] | None = None,
    validate_references: bool = False,
    base_dir: str | None = None,
    set_defaults: bool = True,
    additional_properties: bool = False,
) -> tuple[bool, dict[str, str]]:
    """
    Comprehensive metadata validation with all validation mechanisms.

    Args:
        metadata: The metadata to validate.
        schema_path: Path to the schema file. If None, uses the default schema.
        profile: Validation profile to use.
        custom_rules: List of custom validation rule functions.
        conditions: Dictionary of conditional requirements.
        validate_references: Whether to check if referenced documents exist.
        base_dir: Base directory for resolving relative paths.
        set_defaults: Whether to set default values for missing properties.
        additional_properties: Whether to allow additional properties not defined in the schema.

    Returns:
        A tuple containing (is_valid, error_messages).
    """
    all_errors = {}

    # Step 1: Schema validation
    schema_valid, schema_errors = validate_metadata_with_schema(
        metadata,
        schema_path=schema_path,
        profile=profile,
        set_defaults=set_defaults,
        additional_properties=additional_properties,
    )
    all_errors.update(schema_errors)

    # Step 2: Custom rule validation
    if custom_rules:
        rules_valid, rule_errors = validate_metadata_with_rules(metadata, custom_rules)
        all_errors.update(rule_errors)

    # Step 3: Conditional validation
    if conditions:
        cond_valid, cond_errors = validate_metadata_conditional(metadata, conditions)
        all_errors.update(cond_errors)

    # Step 4: Advanced relationship validation
    rel_valid, rel_errors = validate_relationships_advanced(
        metadata, validate_references=validate_references, base_dir=base_dir
    )
    all_errors.update(rel_errors)

    return (len(all_errors) == 0, all_errors)


def validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Validate metadata using schema validation.
    This is a compatibility function that delegates to validate_metadata_with_schema.

    Args:
        metadata: The metadata dictionary to validate.

    Returns:
        The original metadata dictionary if valid, otherwise raises ValueError.
    """
    # Add the checks attribute to the function to prevent AttributeError
    validate_metadata.checks = {}

    is_valid, errors = validate_metadata_with_schema(metadata)

    if not is_valid:
        error_msg = "; ".join([f"{field}: {msg}" for field, msg in errors.items()])
        raise ValueError(f"Invalid metadata: {error_msg}")

    return metadata
