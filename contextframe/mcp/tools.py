"""Tool registry and implementations for MCP server."""

import os
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from pydantic import ValidationError

from contextframe.frame import FrameDataset, FrameRecord
from contextframe.embed import LiteLLMProvider
from contextframe.mcp.errors import (
    MCPError,
    InvalidParams,
    InvalidSearchType,
    DocumentNotFound,
    EmbeddingError,
    FilterError
)
from contextframe.mcp.schemas import (
    Tool,
    SearchDocumentsParams,
    AddDocumentParams,
    GetDocumentParams,
    ListDocumentsParams,
    UpdateDocumentParams,
    DeleteDocumentParams,
    DocumentResult,
    SearchResult,
    ListResult
)


logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools."""

    def __init__(self, dataset: FrameDataset, transport: Optional[Any] = None):
        self.dataset = dataset
        self.transport = transport
        self._tools: Dict[str, Tool] = {}
        self._handlers: Dict[str, Callable] = {}
        
        # Create document tools instance
        self._doc_tools = self  # For now, self contains the document tools
        
        self._register_default_tools()
        
        # Register enhancement and extraction tools if available
        try:
            from contextframe.mcp.enhancement_tools import (
                register_enhancement_tools,
                register_extraction_tools
            )
            register_enhancement_tools(self, dataset)
            register_extraction_tools(self, dataset)
        except ImportError:
            logger.warning("Enhancement tools not available")
        
        # Register batch tools if transport is available
        if transport:
            try:
                from contextframe.mcp.batch.tools import BatchTools
                batch_tools = BatchTools(dataset, transport, self._doc_tools)
                batch_tools.register_tools(self)
            except ImportError:
                logger.warning("Batch tools not available")
            
            # Register collection tools
            try:
                from contextframe.mcp.collections.tools import CollectionTools
                from contextframe.mcp.collections.templates import TemplateRegistry
                template_registry = TemplateRegistry()
                collection_tools = CollectionTools(dataset, transport, template_registry)
                collection_tools.register_tools(self)
            except ImportError:
                logger.warning("Collection tools not available")
            
            # Register subscription tools
            try:
                from contextframe.mcp.subscriptions.tools import (
                    subscribe_changes,
                    poll_changes,
                    unsubscribe,
                    get_subscriptions,
                    SUBSCRIPTION_TOOLS
                )
                from contextframe.mcp.schemas import (
                    SubscribeChangesParams,
                    PollChangesParams,
                    UnsubscribeParams,
                    GetSubscriptionsParams
                )
                
                # Register each subscription tool
                self.register_tool(
                    "subscribe_changes",
                    subscribe_changes,
                    SubscribeChangesParams,
                    "Create a subscription to monitor dataset changes"
                )
                self.register_tool(
                    "poll_changes",
                    poll_changes,
                    PollChangesParams,
                    "Poll for changes since the last poll"
                )
                self.register_tool(
                    "unsubscribe",
                    unsubscribe,
                    UnsubscribeParams,
                    "Cancel an active subscription"
                )
                self.register_tool(
                    "get_subscriptions",
                    get_subscriptions,
                    GetSubscriptionsParams,
                    "Get list of active subscriptions"
                )
            except ImportError:
                logger.warning("Subscription tools not available")

    def _register_default_tools(self):
        """Register the default set of tools."""
        # Search documents tool
        self.register(
            "search_documents",
            Tool(
                name="search_documents",
                description="Search documents using vector, text, or hybrid search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["vector", "text", "hybrid"],
                            "default": "hybrid",
                            "description": "Type of search to perform"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 10,
                            "description": "Maximum number of results"
                        },
                        "filter": {
                            "type": "string",
                            "description": "SQL filter expression"
                        }
                    },
                    "required": ["query"]
                }
            ),
            self._search_documents
        )

        # Add document tool
        self.register(
            "add_document",
            Tool(
                name="add_document",
                description="Add a new document to the dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Document content"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Document metadata"
                        },
                        "generate_embedding": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to generate embeddings"
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to add document to"
                        },
                        "chunk_size": {
                            "type": "integer",
                            "minimum": 100,
                            "maximum": 10000,
                            "description": "Size of chunks for large documents"
                        },
                        "chunk_overlap": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 1000,
                            "description": "Overlap between chunks"
                        }
                    },
                    "required": ["content"]
                }
            ),
            self._add_document
        )

        # Get document tool
        self.register(
            "get_document",
            Tool(
                name="get_document",
                description="Retrieve a document by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document UUID"
                        },
                        "include_content": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include document content"
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include document metadata"
                        },
                        "include_embeddings": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include embeddings"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            self._get_document
        )

        # List documents tool
        self.register(
            "list_documents",
            Tool(
                name="list_documents",
                description="List documents with pagination and filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 100,
                            "description": "Maximum number of results"
                        },
                        "offset": {
                            "type": "integer",
                            "minimum": 0,
                            "default": 0,
                            "description": "Number of results to skip"
                        },
                        "filter": {
                            "type": "string",
                            "description": "SQL filter expression"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Order by expression"
                        },
                        "include_content": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include document content"
                        }
                    }
                }
            ),
            self._list_documents
        )

        # Update document tool
        self.register(
            "update_document",
            Tool(
                name="update_document",
                description="Update an existing document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document UUID"
                        },
                        "content": {
                            "type": "string",
                            "description": "New document content"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "New or updated metadata"
                        },
                        "regenerate_embedding": {
                            "type": "boolean",
                            "default": False,
                            "description": "Regenerate embeddings if content changed"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            self._update_document
        )

        # Delete document tool
        self.register(
            "delete_document",
            Tool(
                name="delete_document",
                description="Delete a document from the dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document UUID"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            self._delete_document
        )

    def register(self, name: str, tool: Tool, handler: Callable):
        """Register a new tool."""
        self._tools[name] = tool
        self._handlers[name] = handler
    
    def register_tool(
        self,
        name: str,
        handler: Callable,
        schema: Optional[Any] = None,
        description: Optional[str] = None
    ):
        """Register a tool with flexible parameters.
        
        Args:
            name: Tool name
            handler: Async callable handler
            schema: Pydantic model or dict schema
            description: Tool description
        """
        # Build input schema from pydantic model if provided
        if schema and hasattr(schema, 'model_json_schema'):
            input_schema = schema.model_json_schema()
            # Remove title if present
            input_schema.pop('title', None)
        elif isinstance(schema, dict):
            input_schema = schema
        else:
            input_schema = {"type": "object", "properties": {}}
        
        # Create tool
        tool = Tool(
            name=name,
            description=description or f"{name} tool",
            inputSchema=input_schema
        )
        
        self.register(name, tool, handler)

    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by name with arguments."""
        if name not in self._handlers:
            raise InvalidParams(f"Unknown tool: {name}")

        handler = self._handlers[name]
        try:
            return await handler(arguments)
        except ValidationError as e:
            # Convert pydantic validation errors to InvalidParams
            raise InvalidParams(f"Invalid parameters for {name}: {str(e)}")
        except InvalidParams:
            # Re-raise InvalidParams as-is
            raise
        except MCPError:
            # Re-raise other MCP errors as-is
            raise
        except Exception as e:
            logger.exception(f"Error calling tool {name}")
            raise

    # Tool implementations
    async def _search_documents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Implement document search."""
        params = SearchDocumentsParams(**arguments)
        
        results = []
        search_type_used = params.search_type
        
        try:
            if params.search_type == "vector":
                results = await self._vector_search(
                    params.query, params.limit, params.filter
                )
            elif params.search_type == "text":
                results = await self._text_search(
                    params.query, params.limit, params.filter
                )
            else:  # hybrid
                # Try vector first, fall back to text
                try:
                    results = await self._vector_search(
                        params.query, params.limit, params.filter
                    )
                    search_type_used = "vector"
                except Exception as e:
                    logger.warning(f"Vector search failed, falling back to text: {e}")
                    results = await self._text_search(
                        params.query, params.limit, params.filter
                    )
                    search_type_used = "text"
                    
        except Exception as e:
            if "filter" in str(e).lower():
                raise FilterError(str(e), params.filter or "")
            raise

        # Convert results to response format
        documents = []
        for record in results:
            doc = DocumentResult(
                uuid=record.uuid,
                content=record.text_content,
                metadata=record.metadata,
                score=getattr(record, '_score', None)
            )
            documents.append(doc)

        return SearchResult(
            documents=documents,
            total_count=len(documents),
            search_type_used=search_type_used
        ).model_dump()

    async def _vector_search(
        self, query: str, limit: int, filter_expr: Optional[str]
    ) -> List[FrameRecord]:
        """Perform vector search with embedding generation."""
        # Get embedding model configuration
        model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            raise EmbeddingError(
                "No API key found. Set OPENAI_API_KEY environment variable.",
                {"model": model}
            )
        
        try:
            # Generate query embedding
            provider = LiteLLMProvider(model, api_key=api_key)
            result = provider.embed(query)
            query_vector = np.array(result.embeddings[0], dtype=np.float32)
            
            # Perform KNN search
            return self.dataset.knn_search(
                query_vector=query_vector,
                k=limit,
                filter=filter_expr
            )
        except Exception as e:
            raise EmbeddingError(str(e), {"model": model})

    async def _text_search(
        self, query: str, limit: int, filter_expr: Optional[str]
    ) -> List[FrameRecord]:
        """Perform text search with optional filtering."""
        # If no filter, use the simpler full_text_search
        if not filter_expr:
            return self.dataset.full_text_search(query, k=limit)
        
        # With filter, use scanner with both full_text_query and filter
        ftq = {"query": query, "columns": ["text_content"]}
        scanner_kwargs = {
            "full_text_query": ftq,
            "filter": filter_expr,
            "limit": limit
        }
        
        try:
            tbl = self.dataset.scanner(**scanner_kwargs).to_table()
            return [
                FrameRecord.from_arrow(
                    tbl.slice(i, 1), 
                    dataset_path=Path(self.dataset._dataset.uri)
                )
                for i in range(tbl.num_rows)
            ]
        except Exception as e:
            if "filter" in str(e).lower():
                raise FilterError(str(e), filter_expr)
            raise

    async def _add_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new document."""
        params = AddDocumentParams(**arguments)
        
        # Check if we need to chunk the document
        if params.chunk_size and len(params.content) > params.chunk_size:
            chunks = self._chunk_text(
                params.content,
                params.chunk_size,
                params.chunk_overlap or 100
            )
            
            # Add each chunk as a separate document
            added_docs = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = params.metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "original_length": len(params.content)
                })
                
                doc = await self._add_single_document(
                    chunk,
                    chunk_metadata,
                    params.generate_embedding,
                    params.collection
                )
                added_docs.append(doc)
            
            return {
                "documents": added_docs,
                "total_chunks": len(chunks)
            }
        else:
            # Add single document
            doc = await self._add_single_document(
                params.content,
                params.metadata,
                params.generate_embedding,
                params.collection
            )
            return {"document": doc}

    async def _add_single_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        generate_embedding: bool,
        collection: Optional[str]
    ) -> Dict[str, Any]:
        """Add a single document to the dataset."""
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=metadata
        )
        
        if collection:
            record.metadata["collection"] = collection
        
        # Generate embedding if requested
        if generate_embedding:
            model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
            api_key = os.environ.get("OPENAI_API_KEY")
            
            if api_key:
                try:
                    provider = LiteLLMProvider(model, api_key=api_key)
                    result = provider.embed(content)
                    record.vector = np.array(result.embeddings[0], dtype=np.float32)
                except Exception as e:
                    logger.warning(f"Failed to generate embedding: {e}")
        
        # Add to dataset
        self.dataset.add(record)
        
        return DocumentResult(
            uuid=record.uuid,
            content=record.text_content,
            metadata=record.metadata
        ).model_dump()

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence or paragraph boundary
            if end < len(text):
                last_period = chunk.rfind('. ')
                last_newline = chunk.rfind('\n')
                boundary = max(last_period, last_newline)
                if boundary > chunk_size * 0.5:
                    chunk = text[start:start + boundary + 1]
                    end = start + boundary + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [c for c in chunks if c]

    async def _get_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a document by ID."""
        params = GetDocumentParams(**arguments)
        
        # Query for the document
        results = self.dataset.query(f"uuid = '{params.document_id}'", limit=1)
        
        if not results:
            raise DocumentNotFound(params.document_id)
        
        record = results[0]
        
        # Build response based on requested fields
        doc = DocumentResult(
            uuid=record.uuid,
            metadata=record.metadata if params.include_metadata else {}
        )
        
        if params.include_content:
            doc.content = record.text_content
            
        if params.include_embeddings and record.vector is not None:
            doc.embedding = record.vector.tolist()
        
        return {"document": doc.model_dump()}

    async def _list_documents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List documents with pagination."""
        params = ListDocumentsParams(**arguments)
        
        # Build query
        if params.filter:
            try:
                results = self.dataset.query(
                    params.filter,
                    limit=params.limit,
                    offset=params.offset
                )
            except Exception as e:
                raise FilterError(str(e), params.filter)
        else:
            # No filter, get all documents
            # Note: This is a simplified approach, ideally we'd have a list method
            results = self.dataset.query("1=1", limit=params.limit, offset=params.offset)
        
        # Get total count (simplified - in production, use separate count query)
        total_count = len(results)
        
        # Convert to response format
        documents = []
        for record in results:
            doc = DocumentResult(
                uuid=record.uuid,
                metadata=record.metadata
            )
            if params.include_content:
                doc.content = record.text_content
            documents.append(doc)
        
        return ListResult(
            documents=documents,
            total_count=total_count,
            offset=params.offset,
            limit=params.limit
        ).model_dump()

    async def _update_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document."""
        params = UpdateDocumentParams(**arguments)
        
        # Get existing document
        results = self.dataset.query(f"uuid = '{params.document_id}'", limit=1)
        if not results:
            raise DocumentNotFound(params.document_id)
        
        record = results[0]
        
        # Update fields
        updated = False
        if params.content is not None:
            record.text_content = params.content
            updated = True
            
        if params.metadata is not None:
            record.metadata.update(params.metadata)
            updated = True
        
        if not updated:
            raise InvalidParams("No updates provided")
        
        # Regenerate embedding if requested and content changed
        if params.regenerate_embedding and params.content:
            model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
            api_key = os.environ.get("OPENAI_API_KEY")
            
            if api_key:
                try:
                    provider = LiteLLMProvider(model, api_key=api_key)
                    result = provider.embed(record.text_content)
                    record.vector = np.array(result.embeddings[0], dtype=np.float32)
                except Exception as e:
                    logger.warning(f"Failed to regenerate embedding: {e}")
        
        # Update in dataset (atomic delete + add)
        self.dataset.delete(f"uuid = '{params.document_id}'")
        self.dataset.add([record])
        
        return {
            "document": DocumentResult(
                uuid=record.uuid,
                content=record.text_content,
                metadata=record.metadata
            ).model_dump()
        }

    async def _delete_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a document."""
        params = DeleteDocumentParams(**arguments)
        
        # Check document exists
        results = self.dataset.query(f"uuid = '{params.document_id}'", limit=1)
        if not results:
            raise DocumentNotFound(params.document_id)
        
        # Delete
        self.dataset.delete(f"uuid = '{params.document_id}'")
        
        return {"deleted": True, "document_id": params.document_id}