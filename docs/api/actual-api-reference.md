# ContextFrame API Reference - Actual Implementation

This document reflects the actual API behavior based on integration testing and code analysis.

## FrameRecord

### Creating Records

The correct way to create a FrameRecord:

```python
from contextframe import FrameRecord
import numpy as np

# Basic record creation
record = FrameRecord.create(
    title="Document Title",
    content="Document content here",  # Maps to text_content internally
    author="John Doe",
    tags=["tag1", "tag2"],
    status="published",  # Stored in metadata
    custom_metadata={
        "key1": "value1",  # All values must be strings
        "key2": "value2"
    }
)

# With vector embedding
record = FrameRecord.create(
    title="Document with Embedding",
    content="Content",
    vector=np.random.rand(1536).astype(np.float32),  # Must be 1536 dims
    embed_dim=1536
)

# With raw binary data
record = FrameRecord.create(
    title="Image Document",
    content="Description",
    raw_data=image_bytes,
    raw_data_type="image/jpeg"
)
```

### Important Field Mappings

- `content` property → `text_content` field in schema
- `status` → stored in `metadata['status']`
- `custom_metadata` → values must all be strings
- `raw_data` and `raw_data_type` → direct properties, not in metadata

### Property Access

```python
# Content access (property that maps to text_content)
content = record.content
record.content = "New content"

# Metadata access
title = record.title  # Direct property
author = record.author  # Direct property from metadata
tags = record.tags  # Direct property from metadata

# Status access (stored in metadata)
status = record.metadata.get('status', 'draft')
record.metadata['status'] = 'published'

# Custom metadata (string values only)
record.metadata['custom_metadata'] = {
    "priority": "high",  # String, not boolean
    "count": "42"  # String, not integer
}

# Raw data access
data = record.raw_data  # Direct property
mime_type = record.raw_data_type  # Direct property

# UUID is read-only
uuid = record.uuid  # Can read
# record.uuid = "new-uuid"  # ERROR: Cannot set
```

### Relationships

Valid relationship types: `parent`, `child`, `related`, `reference`, `contains`

```python
# Add relationship
record1.add_relationship(
    record2,
    relationship_type="reference"  # Must be from valid types
)

# Check relationships
relationships = record1.metadata.get("relationships", [])
for rel in relationships:
    print(f"Type: {rel['relationship_type']}")
    print(f"Target: {rel['target_uuid']}")
```

## FrameDataset

### Creating and Opening Datasets

```python
from contextframe import FrameDataset

# Create new dataset
dataset = FrameDataset.create("/path/to/dataset.lance", embed_dim=1536)

# Open existing dataset
dataset = FrameDataset.open("/path/to/dataset.lance")
```

### CRUD Operations

```python
# Add single record
dataset.add(record)

# Add multiple records
dataset.add_many([record1, record2, record3])

# Retrieve by UUID
retrieved = dataset.get_by_uuid(record.uuid)  # Note: get_by_uuid not from_dataset_row

# Update record
record.title = "Updated Title"
record.metadata['status'] = 'published'
dataset.update_record(record)

# Delete record
dataset.delete_record(record.uuid)

# Upsert (insert or update)
dataset.upsert_record(record)
```

### Search Operations

```python
# Vector search (may have "Task aborted" issues in some Lance versions)
query_vector = np.random.rand(1536).astype(np.float32)
results = dataset.knn_search(query_vector, k=5)

# Find by metadata
by_status = dataset.find_by_status("published")
by_tag = dataset.find_by_tag("important")
by_author = dataset.find_by_author("John Doe")

# Find related documents
related = dataset.find_related_to(record.uuid)
```

## Schema Information

### Field Names in Lance Schema

The actual field names in the Lance schema:

- `text_content` (not `content`)
- `vector` (fixed-size list of 1536 float32)
- `custom_metadata` (list of key-value structs with string values)
- `relationships` (list of relationship structs)
- `raw_data` (large_binary with blob encoding)
- `raw_data_type` (string MIME type)

### Data Type Constraints

1. **Custom Metadata**: All values must be strings
2. **Vector Dimensions**: Must match dataset embedding dimension (typically 1536)
3. **Relationship Types**: Limited to predefined set
4. **UUID**: Read-only after creation

## Dependencies

### Correct Package Dependencies

```toml
dependencies = [
    "jsonschema",
    "pylance>=0.7.0",  # Note: pylance not lance
    "pyarrow>=14.0.2",
    "numpy>=1.24",
    "pyyaml>=6.0.0",
]
```

## Common Issues and Solutions

### 1. Import Errors
```bash
# Wrong: lance package
pip install lance  

# Correct: pylance package
pip install pylance
```

### 2. Vector Dimension Mismatches
```python
# Wrong: Varying dimensions
record1 = FrameRecord.create("Title", vector=np.random.rand(384))
record2 = FrameRecord.create("Title", vector=np.random.rand(1536))

# Correct: Consistent dimensions
embed_dim = 1536
record1 = FrameRecord.create("Title", vector=np.random.rand(embed_dim))
record2 = FrameRecord.create("Title", vector=np.random.rand(embed_dim))
```

### 3. Custom Metadata Types
```python
# Wrong: Mixed types
custom_metadata = {
    "count": 42,
    "enabled": True,
    "score": 3.14
}

# Correct: String values
custom_metadata = {
    "count": "42",
    "enabled": "true", 
    "score": "3.14"
}
```

### 4. Relationship Types
```python
# Wrong: Invalid type
record.add_relationship(other, relationship_type="member_of")  # Not supported

# Correct: Valid types
record.add_relationship(other, relationship_type="reference")
```

### 5. Status Access
```python
# Wrong: Direct property
record.status = "published"

# Correct: Via metadata
record.metadata['status'] = "published"
```

## Migration Notes

If migrating from earlier documentation or examples:

1. Replace `from_dataset_row` with `get_by_uuid`
2. Use `content` property instead of direct `text_content` access
3. Access `status` via `metadata.get('status')`
4. Ensure all custom metadata values are strings
5. Use valid relationship types only
6. Install `pylance` not `lance` package