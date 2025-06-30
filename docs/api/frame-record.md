# FrameRecord API Reference

The `FrameRecord` class represents an individual document in ContextFrame. It encapsulates content, metadata, embeddings, and relationships in a structured format.

## Class Definition

::: contextframe.FrameRecord
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      merge_init_into_class: true
      show_if_no_docstring: false
      inherited_members: false
      filters:
        - "!^_"  # Exclude private members
      docstring_options:
        ignore_init_summary: false
        trim_doctest_flags: true

## Usage Examples

### Creating Records

```python
from contextframe import FrameRecord, create_metadata, RecordType
from datetime import datetime

# Basic record
record = FrameRecord(
    text_content="This is the document content",
    metadata=create_metadata(
        title="My Document",
        source="manual",
        author="John Doe"
    )
)

# Full record with all fields
record = FrameRecord(
    text_content="Document content here",
    metadata={
        "title": "Technical Report",
        "source": "research",
        "created_at": "2024-01-15T10:30:00Z",
        "custom_field": "custom_value"
    },
    record_type=RecordType.DOCUMENT,
    unique_id="report_2024_001",
    timestamp=datetime.now().isoformat(),
    vector=[0.1, 0.2, 0.3, ...],  # 1536-dim embedding
    context={
        "section": "Introduction",
        "page_number": 1
    },
    raw_data=b"Binary content if needed"
)

# Collection header record
header = FrameRecord(
    text_content="Collection of research papers",
    metadata=create_metadata(
        title="ML Research Collection",
        description="Papers on machine learning"
    ),
    record_type=RecordType.COLLECTION_HEADER,
    unique_id="collection_ml_research"
)
```

### Working with Metadata

```python
from contextframe import create_metadata, add_relationship_to_metadata

# Create metadata with relationships
metadata = create_metadata(
    title="Chapter 2",
    source="book",
    relationships=[
        {
            "relationship_type": "parent",
            "target_id": "book_001",
            "metadata": {"chapter_number": 2}
        },
        {
            "relationship_type": "next",
            "target_id": "chapter_003"
        }
    ]
)

# Add relationship to existing metadata
metadata = add_relationship_to_metadata(
    metadata,
    relationship_type="references",
    target_id="paper_123",
    metadata={"citation_type": "journal"}
)

# Access metadata
print(record.metadata["title"])
print(record.metadata.get("author", "Unknown"))
```

### Record Types

```python
from contextframe import RecordType

# Document (default)
doc = FrameRecord(
    text_content="Regular document",
    record_type=RecordType.DOCUMENT
)

# Collection header
collection = FrameRecord(
    text_content="Collection description",
    record_type=RecordType.COLLECTION_HEADER,
    metadata={"collection_size": 150}
)

# Dataset header
dataset_header = FrameRecord(
    text_content="Dataset documentation",
    record_type=RecordType.DATASET_HEADER,
    metadata={
        "schema_version": "1.0.0",
        "total_records": 10000
    }
)

# Frameset record
frameset = FrameRecord(
    text_content="Frameset metadata",
    record_type=RecordType.FRAMESET,
    context={"frame_count": 5}
)
```

### Embeddings and Vectors

```python
import numpy as np

# With pre-computed embedding
embedding = np.random.rand(1536).tolist()  # OpenAI dimension
record = FrameRecord(
    text_content="Content to embed",
    vector=embedding
)

# Check if record has embedding
if record.vector is not None:
    print(f"Embedding dimension: {len(record.vector)}")

# Add embedding later
record.vector = compute_embedding(record.text_content)
```

### Context and Raw Data

```python
# Context for additional structured data
record = FrameRecord(
    text_content="Meeting transcript",
    context={
        "meeting_id": "2024-01-15-standup",
        "attendees": ["Alice", "Bob", "Charlie"],
        "duration_minutes": 30,
        "action_items": [
            {"task": "Review PR", "assignee": "Alice"},
            {"task": "Update docs", "assignee": "Bob"}
        ]
    }
)

# Raw data for binary content
with open("document.pdf", "rb") as f:
    pdf_bytes = f.read()

record = FrameRecord(
    text_content="Extracted text from PDF",
    raw_data=pdf_bytes,
    metadata={
        "mime_type": "application/pdf",
        "file_size": len(pdf_bytes)
    }
)
```

### Validation

```python
from contextframe import ValidationError

# Records are validated on creation
try:
    record = FrameRecord(
        text_content="",  # Empty content
        metadata={}  # Missing required fields
    )
except ValidationError as e:
    print(f"Validation failed: {e}")

# Manual validation
def validate_custom_record(record):
    if not record.metadata.get("category"):
        raise ValueError("Category is required")
    if len(record.text_content) < 10:
        raise ValueError("Content too short")
```

### Serialization

```python
# Convert to dictionary
record_dict = record.to_dict()

# Create from dictionary
new_record = FrameRecord.from_dict(record_dict)

# For storage/transmission
import json
json_str = json.dumps(record_dict)
loaded = FrameRecord.from_dict(json.loads(json_str))
```

## Field Reference

### Required Fields

- **text_content** (`str`): The main textual content of the document. Can be empty string but must be provided.

### Optional Fields

- **metadata** (`Dict[str, Any]`): Arbitrary metadata as key-value pairs. Common fields include:
  - `title`: Document title
  - `source`: Origin system or method
  - `created_at`: Creation timestamp
  - `modified_at`: Last modification timestamp
  - `author`: Document author
  - `relationships`: List of relationships to other records

- **record_type** (`RecordType`): Type of record, defaults to `DOCUMENT`. Options:
  - `DOCUMENT`: Regular document (default)
  - `COLLECTION_HEADER`: Header for a collection
  - `DATASET_HEADER`: Header for entire dataset
  - `FRAMESET`: Frameset metadata record

- **unique_id** (`Optional[str]`): Unique identifier for the record. Auto-generated if not provided.

- **timestamp** (`Optional[str]`): ISO 8601 timestamp. Defaults to current time if not provided.

- **vector** (`Optional[List[float]]`): Embedding vector for semantic search. Typically 1536 dimensions for OpenAI embeddings.

- **context** (`Optional[Dict[str, Any]]`): Additional structured context that doesn't fit in metadata.

- **raw_data** (`Optional[bytes]`): Binary data like original files, images, etc.

## Methods

### Instance Methods

- **to_dict()** → `Dict[str, Any]`: Convert record to dictionary representation
- **from_dict(data: Dict[str, Any])** → `FrameRecord`: Create record from dictionary (class method)

### Properties

All fields are accessible as properties:

```python
print(record.text_content)
print(record.metadata)
print(record.record_type)
print(record.unique_id)
print(record.timestamp)
print(record.vector)
print(record.context)
print(record.raw_data)
```

## Relationships

Records can define relationships to other records through metadata:

```python
# Parent-child relationship
child_record = FrameRecord(
    text_content="Chapter content",
    metadata=create_metadata(
        title="Chapter 1",
        relationships=[{
            "relationship_type": "parent",
            "target_id": "book_001",
            "metadata": {"position": 1}
        }]
    )
)

# Many-to-many relationships
record = FrameRecord(
    text_content="Research paper",
    metadata=create_metadata(
        title="ML Paper",
        relationships=[
            {
                "relationship_type": "references",
                "target_id": "paper_123"
            },
            {
                "relationship_type": "references", 
                "target_id": "paper_456"
            },
            {
                "relationship_type": "author",
                "target_id": "person_789"
            }
        ]
    )
)
```

## Best Practices

1. **Always provide text_content**: Even if empty, this field is required
2. **Use consistent unique_ids**: If managing external data, provide stable IDs
3. **Standardize metadata fields**: Use consistent field names across records
4. **Validate relationships**: Ensure target_ids exist before creating relationships
5. **Compress large raw_data**: Consider compression for large binary data
6. **Normalize timestamps**: Use ISO 8601 format for all timestamps

## Performance Considerations

- **Vector size**: Embeddings can be large; consider dimensionality reduction
- **Raw data**: Store large files externally and reference them
- **Metadata size**: Keep metadata focused; use context for extensive data
- **Batch operations**: Create multiple records and add in batches

## Error Handling

```python
from contextframe import ValidationError, ContextFrameError

# Handle validation errors
try:
    record = FrameRecord(
        text_content=None,  # Invalid
        metadata="not a dict"  # Invalid
    )
except ValidationError as e:
    print(f"Invalid record: {e}")

# Check before operations
if not record.vector:
    print("No embedding available")
    
if not record.unique_id:
    print("No ID assigned yet")
```

## See Also

- [FrameDataset](frame-dataset.md) - Dataset operations
- [Schema Reference](schema.md) - Detailed schema documentation
- [Metadata Utilities](utilities.md#metadata-functions) - Helper functions
- [Module Guide](../modules/frame-record.md) - Conceptual overview