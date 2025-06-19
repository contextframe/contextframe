# ContextFrame MCP Server

Model Context Protocol (MCP) server implementation for ContextFrame, providing standardized access to document datasets for LLMs and AI agents.

## Overview

The MCP server exposes ContextFrame datasets through a JSON-RPC 2.0 interface, enabling:
- Document search (vector, text, hybrid)
- CRUD operations on documents
- Collection management
- Dataset exploration via resources

## Quick Start

### Running the Server

```bash
# Basic usage
python -m contextframe.mcp /path/to/dataset.lance

# With logging
python -m contextframe.mcp /path/to/dataset.lance --log-level DEBUG

# With environment variables for embeddings
OPENAI_API_KEY=sk-... python -m contextframe.mcp /path/to/dataset.lance
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "contextframe": {
      "command": "python",
      "args": ["-m", "contextframe.mcp", "/path/to/dataset.lance"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## Available Tools

### Core Document Tools

#### 1. search_documents
Search documents using vector, text, or hybrid search.

```json
{
  "name": "search_documents",
  "arguments": {
    "query": "machine learning",
    "search_type": "hybrid",
    "limit": 10,
    "filter": "collection = 'papers'"
  }
}
```

### 2. add_document
Add new documents with optional embeddings and chunking.

```json
{
  "name": "add_document",
  "arguments": {
    "content": "Document content here...",
    "metadata": {
      "title": "My Document",
      "author": "John Doe"
    },
    "generate_embedding": true,
    "chunk_size": 1000,
    "chunk_overlap": 100
  }
}
```

### 3. get_document
Retrieve a specific document by UUID.

```json
{
  "name": "get_document",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "include_content": true,
    "include_metadata": true,
    "include_embeddings": false
  }
}
```

### 4. list_documents
List documents with pagination and filtering.

```json
{
  "name": "list_documents",
  "arguments": {
    "limit": 50,
    "offset": 0,
    "filter": "metadata.author = 'John Doe'",
    "include_content": false
  }
}
```

### 5. update_document
Update existing document content or metadata.

```json
{
  "name": "update_document",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "Updated content",
    "metadata": {"version": 2},
    "regenerate_embedding": true
  }
}
```

#### 6. delete_document
Delete a document from the dataset.

```json
{
  "name": "delete_document",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Enhancement Tools (Requires API Key)

These tools use LLMs to enhance document metadata and context.

#### 7. enhance_context
Add purpose-specific context to explain document relevance.

```json
{
  "name": "enhance_context",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "purpose": "understanding machine learning deployment",
    "current_context": "Technical documentation about model serving"
  }
}
```

#### 8. extract_metadata
Extract custom metadata from documents using LLM analysis.

```json
{
  "name": "extract_metadata",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema": "Extract: main topic, key technologies mentioned, target audience, difficulty level",
    "format": "json"
  }
}
```

#### 9. generate_tags
Auto-generate relevant tags for documents.

```json
{
  "name": "generate_tags",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "tag_types": "technologies, concepts, frameworks",
    "max_tags": 8
  }
}
```

#### 10. improve_title
Generate or improve document titles.

```json
{
  "name": "improve_title",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "style": "technical"
  }
}
```

#### 11. enhance_for_purpose
Enhance multiple document fields for a specific use case.

```json
{
  "name": "enhance_for_purpose",
  "arguments": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "purpose": "technical onboarding for new engineers",
    "fields": ["context", "tags", "custom_metadata"]
  }
}
```

### Extraction Tools

Tools for extracting content from files and adding to the dataset.

#### 12. extract_from_file
Extract content and metadata from various file formats.

```json
{
  "name": "extract_from_file",
  "arguments": {
    "file_path": "/path/to/document.md",
    "add_to_dataset": true,
    "generate_embedding": true,
    "collection": "documentation"
  }
}
```

Supported formats:
- Markdown (.md)
- JSON (.json)
- YAML (.yaml, .yml)
- CSV (.csv)
- Text files (.txt)

#### 13. batch_extract
Extract content from multiple files in a directory.

```json
{
  "name": "batch_extract",
  "arguments": {
    "directory": "/path/to/docs",
    "patterns": ["*.md", "*.txt"],
    "recursive": true,
    "add_to_dataset": true,
    "collection": "knowledge-base"
  }
}
```

## Available Resources

Resources provide read-only access to dataset information:

- `contextframe://dataset/info` - General dataset information
- `contextframe://dataset/schema` - Arrow schema details
- `contextframe://dataset/stats` - Statistical information
- `contextframe://collections` - Document collections
- `contextframe://relationships` - Document relationships

## Environment Variables

- `OPENAI_API_KEY` - API key for OpenAI embeddings and enhancement
- `CONTEXTFRAME_EMBED_MODEL` - Embedding model (default: text-embedding-ada-002)
- `CONTEXTFRAME_ENHANCE_MODEL` - Enhancement model (default: gpt-4)

## Architecture

```
contextframe/mcp/
├── __init__.py          # Package exports
├── __main__.py          # Module entry point
├── server.py            # Main server class
├── transport.py         # Stdio transport layer
├── handlers.py          # Message routing
├── tools.py            # Tool implementations
├── resources.py        # Resource handlers
├── schemas.py          # Pydantic schemas
└── errors.py           # Error definitions
```

## Testing

Run the test suite:

```bash
pytest contextframe/tests/test_mcp/
```

Test with example client:

```bash
# Terminal 1: Start server
python -m contextframe.mcp test.lance

# Terminal 2: Run client
python contextframe/mcp/example_client.py
```

## Error Handling

The server follows JSON-RPC 2.0 error codes:
- `-32700` - Parse error
- `-32600` - Invalid request
- `-32601` - Method not found
- `-32602` - Invalid params
- `-32603` - Internal error

Custom error codes:
- `-32000` - Dataset not found
- `-32001` - Document not found
- `-32002` - Embedding error
- `-32003` - Invalid search type
- `-32004` - Filter error

## Performance Considerations

- Vector search requires embedding generation (adds latency)
- Large result sets should use pagination
- Chunking large documents prevents memory issues
- Hybrid search falls back gracefully from vector to text

## Security

- No authentication built-in (rely on transport security)
- SQL injection prevention in filter expressions
- Environment variables for sensitive configuration
- Dataset access controlled by file permissions

## Next Steps

Phase 3 will add:
- Streaming support for large results
- Subscription to dataset changes
- Batch operations
- HTTP transport option
- Advanced collection management