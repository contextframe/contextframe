# FrameDataset API Reference

The `FrameDataset` class is the primary interface for working with ContextFrame document collections. It provides high-level methods for creating, querying, and managing datasets backed by the Lance columnar storage format.

## Class Definition

::: contextframe.FrameDataset
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

### Creating and Opening Datasets

```python
from contextframe import FrameDataset

# Create a new dataset
dataset = FrameDataset.create("documents.lance")

# Open an existing dataset
dataset = FrameDataset("documents.lance")

# Create with custom schema
dataset = FrameDataset.create(
    "custom.lance",
    schema=my_schema  # Arrow schema
)
```

### Adding Records

```python
from contextframe import FrameRecord, create_metadata

# Single record
record = FrameRecord(
    text_content="Content here",
    metadata=create_metadata(title="Doc 1")
)
dataset.add(record)

# Batch add
records = [
    FrameRecord(text_content=f"Doc {i}") 
    for i in range(100)
]
dataset.add_batch(records)

# With embeddings
dataset.add(record, generate_embedding=True)
```

### Searching and Filtering

```python
# Semantic search
results = dataset.search("machine learning", limit=10)

# Search with metadata filter
results = dataset.search(
    "python tutorial",
    filter="metadata.language = 'en'",
    limit=20
)

# SQL filtering
docs = dataset.sql_filter(
    "metadata.created_at > '2024-01-01' AND metadata.author = 'john'",
    limit=50
)

# Full-text search
results = dataset.full_text_search(
    "exact phrase match",
    columns=["text_content", "metadata.title"]
)
```

### KNN Vector Search

```python
import numpy as np

# Search by vector
query_vector = np.random.rand(1536)  # OpenAI embedding dimension
similar = dataset.knn_search(
    query_vector,
    k=10,
    filter="metadata.type = 'article'"
)

# Search by record ID
similar = dataset.find_similar(
    record_id="doc_123",
    k=5
)
```

### Dataset Operations

```python
# Get dataset info
print(f"Total records: {len(dataset)}")
print(f"Schema: {dataset.schema}")

# Update records
dataset.update(
    record_id="doc_123",
    metadata={"status": "reviewed"}
)

# Delete records
dataset.delete("doc_123")
dataset.delete_many(["doc_1", "doc_2", "doc_3"])

# Create index for performance
dataset.create_index(
    vector_column="vector",
    metric="cosine",
    index_type="IVF_PQ"
)
```

### Version Control

```python
# List versions
versions = dataset.list_versions()
for v in versions:
    print(f"Version {v.version}: {v.timestamp}")

# Checkout specific version
dataset.checkout_version(5)

# Get version history
history = dataset.get_version_history(limit=10)
```

### Advanced Features

```python
# Iterate over all records
for record in dataset.iter_records(batch_size=1000):
    process(record)

# Export to different formats
dataset.to_pandas()  # Returns DataFrame
dataset.to_parquet("export.parquet")

# Direct Lance dataset access
lance_dataset = dataset.dataset
table = lance_dataset.to_table()  # Arrow table

# Add with auto-generated ID
dataset.add(record, generate_id=True)

# Upsert (update or insert)
dataset.upsert(record, key_field="metadata.external_id")
```

## Method Categories

### Dataset Management
- `create()` - Create new dataset
- `exists()` - Check if dataset exists
- `list_datasets()` - List datasets in directory

### CRUD Operations
- `add()` - Add single record
- `add_batch()` - Add multiple records
- `update()` - Update existing record
- `delete()` - Delete by ID
- `delete_many()` - Delete multiple records
- `upsert()` - Update or insert

### Search and Query
- `search()` - Semantic search with optional filters
- `knn_search()` - K-nearest neighbors by vector
- `find_similar()` - Find similar to existing record
- `sql_filter()` - Filter using SQL WHERE clause
- `full_text_search()` - Text search across columns
- `get()` - Retrieve by ID
- `get_many()` - Retrieve multiple by IDs

### Collection Operations
- `get_collection()` - Get all records in collection
- `list_collections()` - List all collections
- `delete_collection()` - Remove entire collection

### Dataset Information
- `__len__()` - Total record count
- `schema` - Dataset Arrow schema
- `lance_schema` - Underlying Lance schema

### Iteration and Export
- `iter_records()` - Iterate over records
- `to_pandas()` - Export to DataFrame
- `to_parquet()` - Export to Parquet file
- `to_table()` - Get Arrow table

### Indexing
- `create_index()` - Create vector/scalar index
- `list_indexes()` - Show existing indexes

### Version Control
- `list_versions()` - List dataset versions
- `checkout_version()` - Switch to version
- `get_version_history()` - Get version details

## Performance Tips

1. **Batch Operations**: Always prefer batch methods when working with multiple records
2. **Indexing**: Create indexes on frequently queried columns and vectors
3. **Filtering**: Use SQL filters to reduce data scanned
4. **Projections**: Select only needed columns when querying
5. **Version Cleanup**: Periodically compact old versions

## Error Handling

```python
from contextframe import ValidationError, ContextFrameError

try:
    dataset.add(invalid_record)
except ValidationError as e:
    print(f"Schema validation failed: {e}")
except ContextFrameError as e:
    print(f"Operation failed: {e}")
```

## Thread Safety

FrameDataset is thread-safe for read operations. For write operations:

```python
import threading

lock = threading.Lock()

def add_record(record):
    with lock:
        dataset.add(record)
```

## See Also

- [FrameRecord](frame-record.md) - Document representation
- [Schema Reference](schema.md) - Data model details
- [Module Guide](../modules/frame-dataset.md) - In-depth guide
- [Search & Query Guide](../modules/search-query.md) - Advanced search techniques