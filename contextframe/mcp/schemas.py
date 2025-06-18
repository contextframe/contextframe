"""Pydantic schemas for MCP protocol messages and data structures."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


# JSON-RPC 2.0 schemas
class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request."""
    
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error object."""
    
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response."""
    
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[str, int]] = None


# MCP protocol schemas
class MCPCapabilities(BaseModel):
    """Server capabilities."""
    
    tools: Optional[bool] = None
    resources: Optional[bool] = None
    prompts: Optional[bool] = None
    logging: Optional[bool] = None


class InitializeParams(BaseModel):
    """Parameters for initialize method."""
    
    protocolVersion: str
    capabilities: MCPCapabilities
    clientInfo: Optional[Dict[str, Any]] = None


class InitializeResult(BaseModel):
    """Result of initialize method."""
    
    protocolVersion: str
    capabilities: MCPCapabilities
    serverInfo: Dict[str, Any]


class Tool(BaseModel):
    """Tool definition."""
    
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolCallParams(BaseModel):
    """Parameters for tools/call method."""
    
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class Resource(BaseModel):
    """Resource definition."""
    
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class ResourceReadParams(BaseModel):
    """Parameters for resources/read method."""
    
    uri: str


# ContextFrame-specific schemas
class SearchDocumentsParams(BaseModel):
    """Parameters for search_documents tool."""
    
    query: str
    search_type: Literal["vector", "text", "hybrid"] = "hybrid"
    limit: int = Field(default=10, ge=1, le=1000)
    filter: Optional[str] = None


class AddDocumentParams(BaseModel):
    """Parameters for add_document tool."""
    
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generate_embedding: bool = True
    collection: Optional[str] = None
    chunk_size: Optional[int] = Field(default=None, ge=100, le=10000)
    chunk_overlap: Optional[int] = Field(default=None, ge=0, le=1000)


class GetDocumentParams(BaseModel):
    """Parameters for get_document tool."""
    
    document_id: str
    include_content: bool = True
    include_metadata: bool = True
    include_embeddings: bool = False


class ListDocumentsParams(BaseModel):
    """Parameters for list_documents tool."""
    
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    filter: Optional[str] = None
    order_by: Optional[str] = None
    include_content: bool = False


class UpdateDocumentParams(BaseModel):
    """Parameters for update_document tool."""
    
    document_id: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    regenerate_embedding: bool = False


class DeleteDocumentParams(BaseModel):
    """Parameters for delete_document tool."""
    
    document_id: str


# Response schemas
class DocumentResult(BaseModel):
    """Result of a document operation."""
    
    model_config = ConfigDict(extra='allow')
    
    uuid: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    score: Optional[float] = None  # For search results


class SearchResult(BaseModel):
    """Result of a search operation."""
    
    documents: List[DocumentResult]
    total_count: int
    search_type_used: str


class ListResult(BaseModel):
    """Result of a list operation."""
    
    documents: List[DocumentResult]
    total_count: int
    offset: int
    limit: int


# Batch operation schemas
class BatchSearchQuery(BaseModel):
    """Individual search query for batch search."""
    
    query: str
    search_type: Literal["vector", "text", "hybrid"] = "hybrid"
    limit: int = Field(default=10, ge=1, le=100)
    filter: Optional[str] = None


class BatchSearchParams(BaseModel):
    """Execute multiple document searches in parallel."""
    
    queries: List[BatchSearchQuery]
    max_parallel: int = Field(default=5, ge=1, le=20)


class BatchDocument(BaseModel):
    """Document for batch operations."""
    
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SharedSettings(BaseModel):
    """Shared settings for batch operations."""
    
    generate_embeddings: bool = True
    collection: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchAddParams(BaseModel):
    """Add multiple documents efficiently."""
    
    documents: List[BatchDocument]
    shared_settings: SharedSettings = Field(default_factory=SharedSettings)
    atomic: bool = Field(default=True, description="Rollback all on any failure")


class UpdateSpec(BaseModel):
    """Specification for batch updates."""
    
    metadata_updates: Optional[Dict[str, Any]] = None
    content_template: Optional[str] = None
    regenerate_embeddings: bool = False


class BatchUpdateParams(BaseModel):
    """Update multiple documents matching criteria."""
    
    filter: Optional[str] = None
    document_ids: Optional[List[str]] = None
    updates: UpdateSpec
    max_documents: int = Field(default=1000, ge=1, le=10000)


class BatchDeleteParams(BaseModel):
    """Delete multiple documents with confirmation."""
    
    filter: Optional[str] = None
    document_ids: Optional[List[str]] = None
    dry_run: bool = Field(default=True, description="Preview what would be deleted")
    confirm_count: Optional[int] = Field(None, description="Expected number of deletions")


class BatchEnhanceParams(BaseModel):
    """Enhance multiple documents with LLM."""
    
    document_ids: Optional[List[str]] = None
    filter: Optional[str] = None
    enhancements: List[Literal["context", "tags", "title", "metadata"]]
    purpose: Optional[str] = None
    batch_size: int = Field(default=10, ge=1, le=50)


class SourceSpec(BaseModel):
    """Source specification for batch extract."""
    
    path: Optional[str] = None
    url: Optional[str] = None
    type: Literal["file", "url"]


class BatchExtractParams(BaseModel):
    """Extract from multiple files/URLs."""
    
    sources: List[SourceSpec]
    add_to_dataset: bool = True
    shared_metadata: Dict[str, Any] = Field(default_factory=dict)
    collection: Optional[str] = None
    continue_on_error: bool = True


class BatchExportParams(BaseModel):
    """Export documents in bulk."""
    
    filter: Optional[str] = None
    document_ids: Optional[List[str]] = None
    format: Literal["json", "jsonl", "csv", "parquet"]
    include_embeddings: bool = False
    output_path: str
    chunk_size: int = Field(default=1000, ge=100, le=10000)


class BatchImportParams(BaseModel):
    """Import documents from files."""
    
    source_path: str
    format: Literal["json", "jsonl", "csv", "parquet"]
    mapping: Optional[Dict[str, str]] = None
    validation: Dict[str, Any] = Field(default_factory=dict)
    generate_embeddings: bool = True