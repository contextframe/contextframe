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

    def __init__(self, message: str, field: str | None = None, errors: dict[str, str] | None = None):
        """Initialize ValidationError with field context.
        
        Parameters
        ----------
        message : str
            The error message
        field : str | None
            The field that failed validation (e.g., "custom_metadata.priority")
        errors : dict[str, str] | None
            Dictionary of field names to error messages for multiple validation errors
        """
        self.field = field
        self.errors = errors or {}
        
        # Build enhanced error message
        if errors:
            # Multiple validation errors
            error_details = []
            for field_name, field_error in errors.items():
                # Enhance field-specific error messages
                enhanced_msg = self._enhance_error_message(field_name, field_error)
                error_details.append(f"  - {field_name}: {enhanced_msg}")
            
            full_message = f"{message}:\n" + "\n".join(error_details)
        elif field:
            # Single field error
            enhanced_msg = self._enhance_error_message(field, message)
            full_message = f"Field '{field}': {enhanced_msg}"
        else:
            # Generic error
            full_message = message
            
        super().__init__(full_message)
    
    def _enhance_error_message(self, field: str, error: str) -> str:
        """Enhance error message with helpful context."""
        # Check for common validation patterns and add helpful hints
        if "is not of type 'string'" in error and "custom_metadata" in field:
            # Extract the value type from the error message
            import re
            match = re.search(r"(\w+) is not of type 'string'", error)
            if match:
                value = match.group(1)
                return (f"{error}. All custom_metadata values must be strings. "
                       f"Convert {value} to string or wait for v0.2.0 which will support native types.")
        
        elif "is not valid under any of the given schemas" in error and field == "relationships":
            return (f"{error}. Relationships must include 'relationship_type' and at least one identifier "
                   "(target_uuid, target_uri, target_path, or target_cid).")
        
        elif "Invalid relationship type" in error:
            return (f"{error}. Valid types are: parent, child, related, reference, contains, member_of.")
        
        elif "is a required property" in error:
            return f"{error}. This field must be provided for the current validation profile."
        
        elif "does not match" in error and "uuid" in field:
            return f"{error}. UUID must be in format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        
        elif "does not match" in error and "date" in field:
            return f"{error}. Date must be in ISO 8601 format (YYYY-MM-DD)."
        
        # Return original error if no enhancement applies
        return error


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
