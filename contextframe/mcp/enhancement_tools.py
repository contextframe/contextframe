"""Enhancement and extraction tools for MCP server."""

import os
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from contextframe.enhance import ContextEnhancer, EnhancementTools
from contextframe.extract import (
    BatchExtractor,
    MarkdownExtractor,
    JSONExtractor,
    YAMLExtractor,
    CSVExtractor,
    TextFileExtractor
)
from contextframe.mcp.errors import InvalidParams, InternalError
from contextframe.mcp.schemas import Tool


logger = logging.getLogger(__name__)


def register_enhancement_tools(tool_registry, dataset):
    """Register enhancement tools with the MCP tool registry."""
    
    # Initialize enhancer
    model = os.environ.get("CONTEXTFRAME_ENHANCE_MODEL", "gpt-4")
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.warning("No OpenAI API key found. Enhancement tools will be disabled.")
        return
    
    try:
        enhancer = ContextEnhancer(model=model, api_key=api_key)
        enhancement_tools = EnhancementTools(enhancer)
    except Exception as e:
        logger.warning(f"Failed to initialize enhancer: {e}")
        return
    
    # Register enhance_context tool
    tool_registry.register(
        "enhance_context",
        Tool(
            name="enhance_context",
            description="Add context to explain document relevance for a specific purpose",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document UUID to enhance"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "What the context should focus on"
                    },
                    "current_context": {
                        "type": "string",
                        "description": "Existing context if any"
                    }
                },
                "required": ["document_id", "purpose"]
            }
        ),
        lambda args: _enhance_context(dataset, enhancement_tools, args)
    )
    
    # Register extract_metadata tool
    tool_registry.register(
        "extract_metadata",
        Tool(
            name="extract_metadata",
            description="Extract custom metadata from document using LLM",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document UUID"
                    },
                    "schema": {
                        "type": "string",
                        "description": "What metadata to extract (as prompt)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "text"],
                        "default": "json",
                        "description": "Output format"
                    }
                },
                "required": ["document_id", "schema"]
            }
        ),
        lambda args: _extract_metadata(dataset, enhancement_tools, args)
    )
    
    # Register generate_tags tool
    tool_registry.register(
        "generate_tags",
        Tool(
            name="generate_tags",
            description="Generate relevant tags for a document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document UUID"
                    },
                    "tag_types": {
                        "type": "string",
                        "default": "topics, technologies, concepts",
                        "description": "Types of tags to generate"
                    },
                    "max_tags": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5,
                        "description": "Maximum number of tags"
                    }
                },
                "required": ["document_id"]
            }
        ),
        lambda args: _generate_tags(dataset, enhancement_tools, args)
    )
    
    # Register improve_title tool
    tool_registry.register(
        "improve_title",
        Tool(
            name="improve_title",
            description="Generate or improve document title",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document UUID"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["descriptive", "technical", "concise"],
                        "default": "descriptive",
                        "description": "Title style"
                    }
                },
                "required": ["document_id"]
            }
        ),
        lambda args: _improve_title(dataset, enhancement_tools, args)
    )
    
    # Register enhance_for_purpose tool
    tool_registry.register(
        "enhance_for_purpose",
        Tool(
            name="enhance_for_purpose",
            description="Enhance document with purpose-specific metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document UUID"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Purpose or use case for enhancement"
                    },
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["context", "tags", "custom_metadata"]
                        },
                        "default": ["context", "tags", "custom_metadata"],
                        "description": "Which fields to enhance"
                    }
                },
                "required": ["document_id", "purpose"]
            }
        ),
        lambda args: _enhance_for_purpose(dataset, enhancement_tools, args)
    )


def register_extraction_tools(tool_registry, dataset):
    """Register extraction tools with the MCP tool registry."""
    
    # Register extract_from_file tool
    tool_registry.register(
        "extract_from_file",
        Tool(
            name="extract_from_file",
            description="Extract content and metadata from various file formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file to extract"
                    },
                    "add_to_dataset": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to add extracted content to dataset"
                    },
                    "generate_embedding": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to generate embeddings"
                    },
                    "collection": {
                        "type": "string",
                        "description": "Collection to add document to"
                    }
                },
                "required": ["file_path"]
            }
        ),
        lambda args: _extract_from_file(dataset, args)
    )
    
    # Register batch_extract tool
    tool_registry.register(
        "batch_extract",
        Tool(
            name="batch_extract",
            description="Extract content from multiple files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to process"
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
                        "description": "File patterns to match"
                    },
                    "recursive": {
                        "type": "boolean",
                        "default": True,
                        "description": "Process subdirectories"
                    },
                    "add_to_dataset": {
                        "type": "boolean",
                        "default": True,
                        "description": "Add to dataset"
                    },
                    "collection": {
                        "type": "string",
                        "description": "Collection name"
                    }
                },
                "required": ["directory"]
            }
        ),
        lambda args: _batch_extract(dataset, args)
    )


# Implementation functions
async def _enhance_context(dataset, enhancement_tools, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement enhance_context tool."""
    # Get document
    doc_id = args["document_id"]
    results = dataset.query(f"uuid = '{doc_id}'", limit=1)
    if not results:
        raise InvalidParams(f"Document not found: {doc_id}")
    
    record = results[0]
    
    # Enhance context
    new_context = enhancement_tools.enhance_context(
        content=record.content,
        purpose=args["purpose"],
        current_context=args.get("current_context", record.metadata.get("context"))
    )
    
    # Update document
    record.metadata["context"] = new_context
    dataset.delete(f"uuid = '{doc_id}'")
    dataset.add([record])
    
    return {
        "document_id": doc_id,
        "context": new_context
    }


async def _extract_metadata(dataset, enhancement_tools, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement extract_metadata tool."""
    doc_id = args["document_id"]
    results = dataset.query(f"uuid = '{doc_id}'", limit=1)
    if not results:
        raise InvalidParams(f"Document not found: {doc_id}")
    
    record = results[0]
    
    # Extract metadata
    metadata = enhancement_tools.extract_metadata(
        content=record.content,
        schema=args["schema"],
        format=args.get("format", "json")
    )
    
    # Update document
    if isinstance(metadata, dict):
        record.metadata.get("custom_metadata", {}).update(metadata)
    else:
        record.metadata["custom_metadata"] = metadata
    
    dataset.delete(f"uuid = '{doc_id}'")
    dataset.add([record])
    
    return {
        "document_id": doc_id,
        "metadata": metadata
    }


async def _generate_tags(dataset, enhancement_tools, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement generate_tags tool."""
    doc_id = args["document_id"]
    results = dataset.query(f"uuid = '{doc_id}'", limit=1)
    if not results:
        raise InvalidParams(f"Document not found: {doc_id}")
    
    record = results[0]
    
    # Generate tags
    tags = enhancement_tools.generate_tags(
        content=record.content,
        tag_types=args.get("tag_types", "topics, technologies, concepts"),
        max_tags=args.get("max_tags", 5)
    )
    
    # Update document
    record.metadata["tags"] = tags
    dataset.delete(f"uuid = '{doc_id}'")
    dataset.add([record])
    
    return {
        "document_id": doc_id,
        "tags": tags
    }


async def _improve_title(dataset, enhancement_tools, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement improve_title tool."""
    doc_id = args["document_id"]
    results = dataset.query(f"uuid = '{doc_id}'", limit=1)
    if not results:
        raise InvalidParams(f"Document not found: {doc_id}")
    
    record = results[0]
    
    # Improve title
    new_title = enhancement_tools.improve_title(
        content=record.content,
        current_title=record.metadata.get("title"),
        style=args.get("style", "descriptive")
    )
    
    # Update document
    record.metadata["title"] = new_title
    dataset.delete(f"uuid = '{doc_id}'")
    dataset.add([record])
    
    return {
        "document_id": doc_id,
        "title": new_title
    }


async def _enhance_for_purpose(dataset, enhancement_tools, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement enhance_for_purpose tool."""
    doc_id = args["document_id"]
    results = dataset.query(f"uuid = '{doc_id}'", limit=1)
    if not results:
        raise InvalidParams(f"Document not found: {doc_id}")
    
    record = results[0]
    
    # Enhance for purpose
    enhancements = enhancement_tools.enhance_for_purpose(
        content=record.content,
        purpose=args["purpose"],
        fields=args.get("fields")
    )
    
    # Update document with enhancements
    for field, value in enhancements.items():
        if field == "custom_metadata" and isinstance(value, dict):
            record.metadata.get("custom_metadata", {}).update(value)
        else:
            record.metadata[field] = value
    
    dataset.delete(f"uuid = '{doc_id}'")
    dataset.add([record])
    
    return {
        "document_id": doc_id,
        "enhancements": enhancements
    }


async def _extract_from_file(dataset, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement extract_from_file tool."""
    file_path = Path(args["file_path"])
    
    if not file_path.exists():
        raise InvalidParams(f"File not found: {file_path}")
    
    # Determine extractor based on file extension
    ext = file_path.suffix.lower()
    
    if ext == ".md":
        extractor = MarkdownExtractor()
    elif ext == ".json":
        extractor = JSONExtractor()
    elif ext in [".yaml", ".yml"]:
        extractor = YAMLExtractor()
    elif ext == ".csv":
        extractor = CSVExtractor()
    else:
        extractor = TextFileExtractor()
    
    try:
        # Extract content
        result = extractor.extract(str(file_path))
        
        if args.get("add_to_dataset", True):
            # Create record from extraction
            from contextframe.frame import FrameRecord
            
            record = FrameRecord(
                content=result.content,
                metadata=result.metadata
            )
            
            # Add collection if specified
            if args.get("collection"):
                record.metadata["collection"] = args["collection"]
            
            # Generate embedding if requested
            if args.get("generate_embedding", True):
                model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
                api_key = os.environ.get("OPENAI_API_KEY")
                
                if api_key:
                    from contextframe.embed import LiteLLMProvider
                    provider = LiteLLMProvider(model, api_key=api_key)
                    embed_result = provider.embed(record.content)
                    record.embeddings = embed_result.embeddings[0]
            
            # Add to dataset
            dataset.add([record])
            
            return {
                "file_path": str(file_path),
                "document_id": record.uuid,
                "content_length": len(result.content),
                "metadata": result.metadata
            }
        else:
            return {
                "file_path": str(file_path),
                "content": result.content,
                "metadata": result.metadata
            }
            
    except Exception as e:
        raise InternalError(f"Extraction failed: {str(e)}")


async def _batch_extract(dataset, args: Dict[str, Any]) -> Dict[str, Any]:
    """Implement batch_extract tool."""
    directory = Path(args["directory"])
    
    if not directory.exists() or not directory.is_dir():
        raise InvalidParams(f"Directory not found: {directory}")
    
    batch_extractor = BatchExtractor()
    patterns = args.get("patterns", ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"])
    
    try:
        # Extract from directory
        results = batch_extractor.extract_directory(
            str(directory),
            patterns=patterns,
            recursive=args.get("recursive", True)
        )
        
        added_documents = []
        
        if args.get("add_to_dataset", True):
            from contextframe.frame import FrameRecord
            
            for result in results:
                record = FrameRecord(
                    content=result.content,
                    metadata=result.metadata
                )
                
                # Add collection if specified
                if args.get("collection"):
                    record.metadata["collection"] = args["collection"]
                
                # Generate embeddings in batch if API key available
                if args.get("generate_embedding", True):
                    model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
                    api_key = os.environ.get("OPENAI_API_KEY")
                    
                    if api_key:
                        from contextframe.embed import LiteLLMProvider
                        provider = LiteLLMProvider(model, api_key=api_key)
                        embed_result = provider.embed(record.content)
                        record.embeddings = embed_result.embeddings[0]
                
                added_documents.append(record)
            
            # Add all documents
            dataset.add(added_documents)
            
            return {
                "directory": str(directory),
                "files_processed": len(results),
                "documents_added": len(added_documents),
                "patterns": patterns
            }
        else:
            return {
                "directory": str(directory),
                "files_processed": len(results),
                "results": [
                    {
                        "file_path": r.metadata.get("source", "unknown"),
                        "content_length": len(r.content),
                        "metadata": r.metadata
                    }
                    for r in results
                ]
            }
            
    except Exception as e:
        raise InternalError(f"Batch extraction failed: {str(e)}")