# Schema API Reference

The ContextFrame schema system defines the structure and validation rules for documents. It uses a dual-schema approach with JSON Schema for validation and Apache Arrow schema for storage.

## Core Schema Components

### get_schema()

::: contextframe.schema.get_schema
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

### RecordType

::: contextframe.schema.RecordType
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

### MimeTypes

::: contextframe.schema.MimeTypes
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

## Schema Structure

### Arrow Schema Fields

The ContextFrame Arrow schema defines the following fields:

```python
from contextframe import get_schema

# Get the Arrow schema
schema = get_schema()

# Print field information
for field in schema:
    print(f"{field.name}: {field.type}")
    if field.metadata:
        print(f"  Metadata: {field.metadata}")
```

#### Core Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `text_content` | `string` | Main document content | Yes |
| `metadata` | `string` (JSON) | Metadata as JSON string | Yes |
| `record_type` | `string` | Type of record | Yes |
| `unique_id` | `string` | Unique identifier | Yes |
| `timestamp` | `string` | ISO 8601 timestamp | Yes |
| `vector` | `fixed_size_list<float>[1536]` | Embedding vector | No |
| `context` | `string` (JSON) | Additional context | No |
| `raw_data` | `binary` | Binary data | No |

### JSON Schema

The JSON schema provides validation rules:

```python
{
    "type": "object",
    "properties": {
        "text_content": {
            "type": "string",
            "description": "Main text content"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "source": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "relationship_type": {"type": "string"},
                            "target_id": {"type": "string"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["relationship_type", "target_id"]
                    }
                }
            }
        },
        "record_type": {
            "type": "string",
            "enum": ["document", "collection_header", "dataset_header", "frameset"]
        },
        "unique_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "vector": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 1536,
            "maxItems": 1536
        },
        "context": {"type": "object"},
        "raw_data": {"type": "string", "contentEncoding": "base64"}
    },
    "required": ["text_content", "metadata", "record_type", "unique_id", "timestamp"]
}
```

## Working with Record Types

### Document Records

```python
from contextframe import FrameRecord, RecordType, create_metadata

# Standard document
doc = FrameRecord(
    text_content="Document content here",
    metadata=create_metadata(
        title="My Document",
        source="manual"
    ),
    record_type=RecordType.DOCUMENT  # Default
)
```

### Collection Headers

```python
# Collection header for grouping documents
collection = FrameRecord(
    text_content="Research papers on machine learning",
    metadata=create_metadata(
        title="ML Research Collection",
        description="Curated papers from 2020-2024",
        collection_size=150,
        tags=["machine-learning", "research", "ai"]
    ),
    record_type=RecordType.COLLECTION_HEADER,
    unique_id="collection_ml_research_2024"
)

# Documents reference the collection
paper = FrameRecord(
    text_content="Paper content...",
    metadata=create_metadata(
        title="Attention Is All You Need",
        relationships=[{
            "relationship_type": "member_of",
            "target_id": "collection_ml_research_2024",
            "metadata": {"position": 1}
        }]
    )
)
```

### Dataset Headers

```python
# Dataset header with schema information
dataset_header = FrameRecord(
    text_content="Technical documentation dataset",
    metadata=create_metadata(
        title="TechDocs Dataset",
        description="Company technical documentation",
        schema_version="1.0.0",
        created_by="data_team",
        statistics={
            "total_documents": 5000,
            "languages": ["en", "es", "fr"],
            "last_updated": "2024-01-15"
        }
    ),
    record_type=RecordType.DATASET_HEADER,
    unique_id="dataset_techdocs_v1"
)
```

### Frameset Records

```python
# Frameset for multi-part documents
frameset = FrameRecord(
    text_content="Multi-volume encyclopedia",
    metadata=create_metadata(
        title="Encyclopedia Britannica",
        volumes=32,
        total_pages=32640
    ),
    record_type=RecordType.FRAMESET,
    context={
        "frame_ids": ["vol_1", "vol_2", "vol_3", ...],
        "frame_count": 32
    }
)
```

## MIME Types

### Common MIME Types

```python
from contextframe import MimeTypes

# Text formats
text_plain = MimeTypes.TEXT_PLAIN          # "text/plain"
text_html = MimeTypes.TEXT_HTML            # "text/html"
text_markdown = MimeTypes.TEXT_MARKDOWN    # "text/markdown"

# Document formats
pdf = MimeTypes.APPLICATION_PDF            # "application/pdf"
json = MimeTypes.APPLICATION_JSON          # "application/json"
xml = MimeTypes.APPLICATION_XML            # "application/xml"

# Image formats
jpeg = MimeTypes.IMAGE_JPEG                # "image/jpeg"
png = MimeTypes.IMAGE_PNG                  # "image/png"

# Usage in metadata
record = FrameRecord(
    text_content="Extracted text",
    raw_data=pdf_bytes,
    metadata={
        "mime_type": MimeTypes.APPLICATION_PDF,
        "file_size": len(pdf_bytes)
    }
)
```

### Custom MIME Types

```python
# Using non-standard MIME types
record = FrameRecord(
    text_content="Custom data",
    raw_data=custom_bytes,
    metadata={
        "mime_type": "application/x-custom-format",
        "format_version": "2.0"
    }
)
```

## Schema Validation

### Automatic Validation

FrameRecord creation automatically validates against the schema:

```python
from contextframe import ValidationError

try:
    # Missing required field
    record = FrameRecord(
        metadata={"title": "Test"}
        # Missing text_content!
    )
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # Invalid record type
    record = FrameRecord(
        text_content="Test",
        record_type="invalid_type"  # Not in enum
    )
except ValidationError as e:
    print(f"Invalid record type: {e}")
```

### Manual Validation

```python
from contextframe.schema import validate_record

# Validate a dictionary before creating record
data = {
    "text_content": "Content",
    "metadata": {"title": "Test"},
    "record_type": "document",
    "unique_id": "test_123",
    "timestamp": "2024-01-15T10:30:00Z"
}

try:
    validate_record(data)
    record = FrameRecord.from_dict(data)
except ValidationError as e:
    print(f"Invalid data: {e}")
```

## Schema Evolution

### Version Management

```python
from contextframe import compare_semantic_versions, next_version

# Check schema versions
current = "1.0.0"
required = "1.1.0"

if compare_semantic_versions(current, required) < 0:
    print("Schema upgrade needed")

# Generate next version
patch_version = next_version(current, "patch")  # "1.0.1"
minor_version = next_version(current, "minor")  # "1.1.0"
major_version = next_version(current, "major")  # "2.0.0"
```

### Backward Compatibility

```python
# Read old format
def migrate_v1_to_v2(old_record):
    """Migrate record from v1 to v2 schema."""
    # Map old fields to new structure
    return FrameRecord(
        text_content=old_record.get("content", ""),
        metadata={
            **old_record.get("metadata", {}),
            "migrated_from": "v1",
            "migration_date": datetime.now().isoformat()
        }
    )
```

## Custom Schema Extensions

### Adding Custom Fields

```python
# Extend schema with custom metadata fields
def create_research_record(title, abstract, authors, doi):
    """Create record with research paper schema."""
    return FrameRecord(
        text_content=abstract,
        metadata=create_metadata(
            title=title,
            source="research",
            # Standard fields
            created_at=datetime.now().isoformat(),
            # Custom research fields
            authors=authors,
            doi=doi,
            peer_reviewed=True,
            citations_count=0
        ),
        context={
            "research_fields": ["ML", "NLP"],
            "institutions": ["MIT", "Stanford"]
        }
    )
```

### Schema Documentation

```python
# Document custom schema
CUSTOM_SCHEMA = {
    "research_paper": {
        "required": ["title", "abstract", "authors", "doi"],
        "optional": ["keywords", "citations_count", "venue"],
        "relationships": ["references", "cited_by", "authors"]
    },
    "code_snippet": {
        "required": ["title", "code", "language"],
        "optional": ["description", "tags", "dependencies"],
        "relationships": ["uses", "used_by", "part_of"]
    }
}

def validate_custom_schema(record, schema_type):
    """Validate record against custom schema."""
    schema = CUSTOM_SCHEMA.get(schema_type)
    if not schema:
        raise ValueError(f"Unknown schema type: {schema_type}")
    
    # Check required fields
    for field in schema["required"]:
        if field not in record.metadata:
            raise ValidationError(f"Missing required field: {field}")
```

## Performance Considerations

1. **Metadata Size**: Keep metadata under 1MB for optimal performance
2. **Vector Dimensions**: Standard is 1536 (OpenAI), but can be configured
3. **Raw Data**: Consider external storage for files > 10MB
4. **JSON Parsing**: Metadata and context are stored as JSON strings
5. **Indexing**: Create indexes on frequently queried metadata fields

## Best Practices

1. **Use Standard Fields**: Stick to common metadata fields when possible
2. **Document Custom Fields**: Maintain documentation for custom schemas
3. **Validate Early**: Validate data before creating records
4. **Version Schemas**: Track schema versions for migrations
5. **Consistent Types**: Use consistent data types for same fields
6. **Relationship Integrity**: Ensure relationship targets exist

## See Also

- [Core Concepts: Schema System](../core-concepts/schema-system.md) - Conceptual overview
- [FrameRecord API](frame-record.md) - Record creation and management
- [Utilities API](utilities.md) - Schema helper functions
- [Migration Guides](../migration/overview.md) - Schema migration strategies