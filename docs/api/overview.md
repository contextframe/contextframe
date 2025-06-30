# API Reference Overview

The ContextFrame API provides a comprehensive set of tools for managing document collections with semantic search capabilities. This reference documents all public classes, functions, and utilities available in the library.

## Organization

The API is organized into several main components:

### Core Components

- **[FrameDataset](frame-dataset.md)** - High-level interface for managing document collections
- **[FrameRecord](frame-record.md)** - Document representation with metadata and embeddings
- **[Schema](schema.md)** - Data model and validation system
- **[Connectors](connectors.md)** - External system integration interfaces
- **[Utilities](utilities.md)** - Helper functions and metadata tools

### Supporting Modules

- **Embeddings** - Vector embedding generation and management
- **Extraction** - Content extraction from various formats
- **Enhancement** - LLM-powered document enrichment
- **I/O** - Import/export functionality
- **MCP Server** - Model Context Protocol integration

## Import Structure

ContextFrame follows a simple import pattern. Most common classes and functions are available from the top-level module:

```python
from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    RecordType,
    MimeTypes
)
```

For specialized functionality, import from submodules:

```python
from contextframe.connectors import GitHubConnector
from contextframe.embed import create_embedder
from contextframe.extract import MarkdownExtractor
from contextframe.io import FrameSetExporter, ExportFormat
```

## Type Annotations

The entire API is fully type-annotated, providing excellent IDE support and type checking capabilities. We use standard Python types and typing module constructs:

```python
from typing import List, Dict, Optional, Union
from pathlib import Path
```

## Error Handling

ContextFrame defines specific exception types for different error scenarios:

```python
from contextframe import (
    ContextFrameError,      # Base exception
    ValidationError,        # Schema validation failures
    RelationshipError,      # Invalid relationships
    VersioningError,        # Version conflicts
    ConflictError,         # Data conflicts
    FormatError           # Format conversion errors
)
```

## Async Support

While the core API is synchronous, certain operations support async execution:

- Batch embedding generation
- Concurrent connector synchronization
- Parallel content extraction

## Thread Safety

FrameDataset operations are thread-safe at the Lance level. However, when using connectors or embedders, consider:

- Each thread should have its own connector instance
- Embedding providers may have rate limits
- Use appropriate locking for shared resources

## Performance Considerations

- **Batch Operations**: Use batch methods for processing multiple records
- **Lazy Loading**: Large datasets support iterator patterns
- **Indexing**: Create indexes for frequently queried fields
- **Caching**: Embeddings are cached automatically

## Versioning

ContextFrame follows semantic versioning. The API maintains backward compatibility within major versions:

- **Major**: Breaking changes to public API
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes and improvements

## Quick Reference

### Creating a Dataset

```python
from contextframe import FrameDataset

# Create new dataset
dataset = FrameDataset.create("my_docs.lance")

# Open existing dataset
dataset = FrameDataset("my_docs.lance")
```

### Adding Documents

```python
from contextframe import FrameRecord, create_metadata

# Create a record
record = FrameRecord(
    text_content="Document content",
    metadata=create_metadata(
        title="My Document",
        source="manual"
    )
)

# Add to dataset
dataset.add(record)
```

### Searching

```python
# Semantic search
results = dataset.search("query", limit=10)

# SQL filtering
results = dataset.sql_filter(
    "metadata.source = 'github'",
    limit=20
)

# Combined search
results = dataset.search(
    "machine learning",
    filter="metadata.created_at > '2024-01-01'"
)
```

### Using Connectors

```python
from contextframe.connectors import GitHubConnector

# Setup connector
connector = GitHubConnector(token="github_token")

# Sync repository
issues = connector.sync_issues(
    owner="myorg",
    repo="myrepo"
)

# Convert to records
for issue in issues:
    record = connector.map_to_frame_record(issue)
    dataset.add(record)
```

## Next Steps

- Explore detailed class documentation in the following sections
- See the [Cookbook](../cookbook/index.md) for practical examples
- Review [Module Guides](../modules/frame-dataset.md) for in-depth explanations
- Check [Integration Guides](../integration/overview.md) for connector usage