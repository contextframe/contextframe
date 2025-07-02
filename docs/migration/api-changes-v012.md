# API Changes in v0.1.2

This document outlines important API changes and corrections in ContextFrame v0.1.2.

## Installation Changes

### Dependency Fix

**Old**: The package incorrectly depended on `lance` which caused import errors.

**New**: Fixed to use `pylance` dependency.

```bash
# Install the corrected version
pip install contextframe==0.1.2
```

## FrameRecord API Changes

### Creating Records

**Recommended**: Use the `create()` factory method instead of direct constructor.

```python
# Recommended approach
record = FrameRecord.create(
    title="Document Title",
    content="Document content",  # Maps to text_content internally
    author="John Doe",
    tags=["tag1", "tag2"],
    status="published"
)

# Direct constructor (still works but more complex)
record = FrameRecord(
    text_content="Document content",
    metadata={
        "title": "Document Title",
        "author": "John Doe",
        "tags": ["tag1", "tag2"],
        "status": "published"
    }
)
```

### Field Access Patterns

#### Content Field
```python
# Correct: Use content property
content = record.content
record.content = "New content"

# Note: This maps to text_content in the Lance schema
```

#### Status Field
```python
# Correct: Access via metadata
status = record.metadata.get('status', 'draft')
record.metadata['status'] = 'published'

# Incorrect: Direct property (doesn't exist)
# record.status = 'published'  # AttributeError
```

#### Custom Metadata Constraints
```python
# Correct: All values must be strings
custom_metadata = {
    "priority": "high",      # String
    "count": "42",          # String, not int
    "enabled": "true"       # String, not boolean
}

# Incorrect: Mixed types cause validation errors
# custom_metadata = {
#     "priority": 1,        # int not allowed
#     "enabled": True       # boolean not allowed
# }
```

#### Raw Data Access
```python
# Correct: Direct properties
raw_data = record.raw_data
mime_type = record.raw_data_type

# Incorrect: Via metadata
# raw_data = record.metadata['raw_data']  # Not stored there
```

### UUID Handling
```python
# Correct: UUID is read-only
uuid = record.uuid

# Incorrect: Cannot set UUID after creation
# record.uuid = "new-uuid"  # AttributeError: can't set attribute
```

## FrameDataset API Changes

### Method Names

#### Record Retrieval
```python
# Correct
record = dataset.get_by_uuid(uuid)

# Incorrect (old documentation)
# record = dataset.from_dataset_row(uuid)  # Method doesn't exist
```

#### Dataset Creation
```python
# Correct: Specify embedding dimension
dataset = FrameDataset.create("path.lance", embed_dim=1536)

# Opening existing datasets
dataset = FrameDataset.open("path.lance")
```

#### Batch Operations
```python
# Correct method name
dataset.add_many([record1, record2, record3])

# Incorrect (some docs may show)
# dataset.add_batch([record1, record2, record3])  # Method doesn't exist
```

## Relationship API Changes

### Valid Relationship Types

Only these relationship types are supported:

- `parent`
- `child` 
- `related`
- `reference`
- `contains`

```python
# Correct
record1.add_relationship(record2, relationship_type="reference")

# Incorrect: Invalid types
# record1.add_relationship(record2, relationship_type="member_of")  # Not supported
# record1.add_relationship(record2, relationship_type="translation_of")  # Not supported
```

### Relationship Structure
```python
# Access relationships
relationships = record.metadata.get("relationships", [])
for rel in relationships:
    rel_type = rel["relationship_type"]  # Note: not "type"
    target = rel["target_uuid"]
```

## Vector Operations

### Embedding Dimensions

Vector dimensions must be consistent within a dataset:

```python
# Correct: Consistent dimensions
dataset = FrameDataset.create("docs.lance", embed_dim=1536)
record1 = FrameRecord.create("Title 1", vector=np.random.rand(1536))
record2 = FrameRecord.create("Title 2", vector=np.random.rand(1536))

# Incorrect: Mismatched dimensions
# record3 = FrameRecord.create("Title 3", vector=np.random.rand(384))  # Error
```

### Search Methods
```python
# Vector search
import numpy as np
query_vector = np.random.rand(1536).astype(np.float32)
results = dataset.knn_search(query_vector, k=5)

# Note: Some versions may have "Task aborted" errors in vector operations
# This is a Lance version compatibility issue

# Full-text search (requires index)
dataset.create_fts_index()  # Create inverted index on text_content
results = dataset.full_text_search("machine learning", k=10)

# Create index on custom column
dataset.create_fts_index("title")
results = dataset.full_text_search("tutorial", columns=["title"])
```

## Schema Field Names

### Internal vs External Names

The Lance schema uses different field names than the Python API:

| Python API | Lance Schema |
|------------|--------------|
| `content` property | `text_content` field |
| `status` (in metadata) | `status` field |
| `custom_metadata` dict | `custom_metadata` struct list |

## Common Error Patterns

### Import Errors
```python
# If you see: ModuleNotFoundError: No module named 'lance.dataset'
# Solution: Upgrade to contextframe>=0.1.2
pip install --upgrade contextframe
```

### Validation Errors
```python
# If you see: "is not of type 'string'" in custom_metadata
# Solution: Convert all values to strings
custom_metadata = {k: str(v) for k, v in original_dict.items()}
```

### Relationship Errors
```python
# If you see: "is not one of ['parent', 'child', 'related', 'reference', 'contains']"
# Solution: Use only valid relationship types
valid_types = ["parent", "child", "related", "reference", "contains"]
```

## Testing Your Migration

Run this simple test to verify your setup:

```python
from contextframe import FrameRecord, FrameDataset
import numpy as np

# Test basic functionality
record = FrameRecord.create(
    title="Test Document",
    content="Test content",
    status="draft",
    custom_metadata={"test": "value"}
)

# Test dataset operations
dataset = FrameDataset.create("test.lance", embed_dim=1536)
dataset.add(record)
retrieved = dataset.get_by_uuid(record.uuid)

print("✅ Migration successful!")
print(f"Record UUID: {retrieved.uuid}")
print(f"Content: {retrieved.content}")
print(f"Status: {retrieved.metadata.get('status')}")
```

If this runs without errors, your migration is complete!