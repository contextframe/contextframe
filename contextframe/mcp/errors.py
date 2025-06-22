"""Error handling for MCP server implementation."""

from typing import Any, Dict, Optional

# Standard JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# Custom error codes (reserved range: -32000 to -32099)
DATASET_NOT_FOUND = -32000
DOCUMENT_NOT_FOUND = -32001
EMBEDDING_ERROR = -32002
INVALID_SEARCH_TYPE = -32003
FILTER_ERROR = -32004


class MCPError(Exception):
    """Base class for MCP errors with JSON-RPC error formatting."""

    def __init__(self, code: int, message: str, data: Any | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def to_json_rpc(self) -> dict[str, Any]:
        """Convert error to JSON-RPC error format."""
        error_dict = {"code": self.code, "message": self.message}
        if self.data is not None:
            error_dict["data"] = self.data
        return error_dict


class ParseError(MCPError):
    """Invalid JSON was received by the server."""

    def __init__(self, data: Any | None = None):
        super().__init__(PARSE_ERROR, "Parse error", data)


class InvalidRequest(MCPError):
    """The JSON sent is not a valid Request object."""

    def __init__(self, data: Any | None = None):
        super().__init__(INVALID_REQUEST, "Invalid Request", data)


class MethodNotFound(MCPError):
    """The method does not exist / is not available."""

    def __init__(self, method: str):
        super().__init__(
            METHOD_NOT_FOUND, f"Method not found: {method}", {"method": method}
        )


class InvalidParams(MCPError):
    """Invalid method parameter(s)."""

    def __init__(self, message: str, data: Any | None = None):
        super().__init__(INVALID_PARAMS, f"Invalid params: {message}", data)


class InternalError(MCPError):
    """Internal JSON-RPC error."""

    def __init__(self, message: str, data: Any | None = None):
        super().__init__(INTERNAL_ERROR, f"Internal error: {message}", data)


class DatasetNotFound(MCPError):
    """Dataset not found or cannot be opened."""

    def __init__(self, path: str):
        super().__init__(
            DATASET_NOT_FOUND, f"Dataset not found: {path}", {"path": path}
        )


class DocumentNotFound(MCPError):
    """Document not found in dataset."""

    def __init__(self, document_id: str):
        super().__init__(
            DOCUMENT_NOT_FOUND,
            f"Document not found: {document_id}",
            {"document_id": document_id},
        )


class EmbeddingError(MCPError):
    """Error generating embeddings."""

    def __init__(self, message: str, data: Any | None = None):
        super().__init__(EMBEDDING_ERROR, f"Embedding error: {message}", data)


class InvalidSearchType(MCPError):
    """Invalid search type specified."""

    def __init__(self, search_type: str):
        super().__init__(
            INVALID_SEARCH_TYPE,
            f"Invalid search type: {search_type}",
            {"search_type": search_type, "valid_types": ["vector", "text", "hybrid"]},
        )


class FilterError(MCPError):
    """Error parsing or applying filter expression."""

    def __init__(self, message: str, filter_expr: str):
        super().__init__(
            FILTER_ERROR,
            f"Filter error: {message}",
            {"filter": filter_expr, "error": message},
        )


class ToolError(MCPError):
    """Error executing MCP tool."""

    def __init__(self, message: str, data: Any | None = None):
        super().__init__(INTERNAL_ERROR, f"Tool error: {message}", data)
