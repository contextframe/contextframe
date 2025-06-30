# FrameDataset

The `FrameDataset` class is the primary interface for working with ContextFrame datasets. It provides high-level operations for managing documents, performing searches, and handling vector operations, all built on top of the Lance columnar storage format.

## Overview

`FrameDataset` wraps a Lance dataset and provides:
- Document CRUD operations (Create, Read, Update, Delete)
- Full-text and vector search capabilities
- Batch operations for efficiency
- Version control and time travel
- Query optimization with indices
- Cloud storage support

## Creating and Opening Datasets

### Creating a New Dataset

```python
from contextframe import FrameDataset, FrameRecord

# Create a local dataset
dataset = FrameDataset.create("my_documents.lance")

# Create with specific configuration
dataset = FrameDataset.create(
    "my_documents.lance",
    mode="create",  # or "overwrite"
    storage_options={
        "timeout": "60s",
        "max_retries": 3
    }
)

# Create in cloud storage
dataset = FrameDataset.create(
    "s3://my-bucket/datasets/production.lance",
    storage_options={
        "aws_region": "us-east-1"
    }
)
```

### Opening an Existing Dataset

```python
# Open existing dataset
dataset = FrameDataset("my_documents.lance")

# Open specific version
dataset = FrameDataset("my_documents.lance", version=5)

# Open with custom storage options
dataset = FrameDataset(
    "gs://my-bucket/datasets/production.lance",
    storage_options={
        "service_account": "/path/to/key.json"
    }
)
```

### Dataset Properties

```python
# Basic properties
print(f"URI: {dataset.uri}")
print(f"Version: {dataset.version}")
print(f"Number of documents: {len(dataset)}")
print(f"Schema: {dataset.schema}")

# Storage statistics
stats = dataset.stats()
print(f"Size: {stats.dataset_size / 1024 / 1024:.2f} MB")
print(f"Fragments: {stats.num_fragments}")
```

## Document Operations

### Adding Documents

```python
# Add single document
doc = FrameRecord.create(
    title="Getting Started with Python",
    content="Python is a versatile programming language...",
    tags=["python", "tutorial", "beginner"]
)
dataset.add(doc)

# Add multiple documents
docs = [
    FrameRecord.create(title="Doc 1", content="..."),
    FrameRecord.create(title="Doc 2", content="..."),
    FrameRecord.create(title="Doc 3", content="...")
]
dataset.add_many(docs)

# Add with batch size control
dataset.add_many(docs, batch_size=1000)
```

### Retrieving Documents

```python
# Get by UUID
doc = dataset.get("123e4567-e89b-12d3-a456-426614174000")

# Get multiple documents
uuids = ["uuid1", "uuid2", "uuid3"]
docs = dataset.get_many(uuids)

# Check existence
if dataset.exists("some-uuid"):
    doc = dataset.get("some-uuid")
```

### Updating Documents

```python
# Update single document
doc = dataset.get(uuid)
doc.metadata['status'] = 'published'
doc.metadata['updated_at'] = datetime.now().isoformat()
dataset.update_record(uuid, doc)

# Update with new content
updated_doc = FrameRecord.create(
    title="Updated Title",
    content="New content...",
    tags=["updated"],
    uuid=existing_uuid  # Preserve UUID
)
dataset.update_record(existing_uuid, updated_doc)
```

### Deleting Documents

```python
# Delete single document
dataset.delete_record("uuid-to-delete")

# Delete multiple documents
uuids_to_delete = ["uuid1", "uuid2", "uuid3"]
for uuid in uuids_to_delete:
    dataset.delete_record(uuid)

# Soft delete (marks as deleted)
doc = dataset.get(uuid)
doc.metadata['status'] = 'deleted'
dataset.update_record(uuid, doc)
```

### Upsert Operations

```python
# Upsert - insert or update
doc = FrameRecord.create(
    title="Configuration Guide",
    content="...",
    uuid="known-uuid"  # Will update if exists
)
dataset.upsert(doc)

# Batch upsert
docs = load_documents_from_source()
dataset.upsert_many(docs)
```

## Query Operations

### Scanner Interface

The scanner provides efficient filtering and projection:

```python
# Basic filtering
results = dataset.scanner(
    filter="status = 'published'"
).to_table()

# Multiple conditions
results = dataset.scanner(
    filter="status = 'published' AND author = 'Alice'"
).to_table()

# Column projection
results = dataset.scanner(
    columns=["uuid", "title", "created_at"],
    filter="tags.contains('python')"
).to_table()

# Limit results
results = dataset.scanner(
    filter="record_type = 'document'",
    limit=100
).to_table()
```

### SQL-Style Filters

```python
# Comparison operators
dataset.scanner(filter="created_at > '2024-01-01'")
dataset.scanner(filter="word_count >= 500")
dataset.scanner(filter="status != 'draft'")

# String operations
dataset.scanner(filter="title LIKE '%Python%'")
dataset.scanner(filter="author IN ('Alice', 'Bob', 'Charlie')")

# Array operations
dataset.scanner(filter="tags.contains('tutorial')")
dataset.scanner(filter="array_length(tags) > 3")

# Null checks
dataset.scanner(filter="description IS NOT NULL")
dataset.scanner(filter="embedding IS NULL")

# Complex conditions
dataset.scanner(
    filter="""
    (status = 'published' OR status = 'archived') 
    AND created_at > '2023-01-01'
    AND tags.contains('important')
    """
)
```

### Full-Text Search

```python
# Basic text search
results = dataset.full_text_search("python programming")

# Search with filters
results = dataset.full_text_search(
    "machine learning",
    filter="status = 'published'",
    limit=20
)

# Search specific fields
results = dataset.full_text_search(
    query="API documentation",
    columns=["title", "content"],  # Search only these fields
    filter="record_type = 'document'"
)
```

### Converting Results

```python
# To PyArrow Table
table = dataset.scanner().to_table()

# To Pandas DataFrame
df = dataset.to_pandas()

# To Python list
docs = dataset.scanner(limit=10).to_table().to_pylist()

# To FrameRecord objects
records = []
for batch in dataset.to_batches():
    for row in batch.to_pylist():
        records.append(FrameRecord.from_arrow(row))
```

## Vector Operations

### Creating Vector Indices

```python
# Create IVF_PQ index (default)
dataset.create_vector_index(
    column="embedding",
    index_type="IVF_PQ",
    num_partitions=256,     # Number of clusters
    num_sub_quantizers=16,  # PQ compression
    metric_type="cosine"    # or "l2", "dot"
)

# Create IVF_FLAT index (more accurate, more memory)
dataset.create_vector_index(
    column="embedding",
    index_type="IVF_FLAT",
    num_partitions=100,
    metric_type="l2"
)

# Auto-calculate partitions
num_docs = len(dataset)
num_partitions = int(np.sqrt(num_docs))
dataset.create_vector_index(num_partitions=num_partitions)
```

### KNN Search

```python
# Simple KNN search
query_vector = embed_text("How to use Python async/await")
results = dataset.knn_search(
    query_vector,
    k=10  # Return top 10
)

# KNN with filter
results = dataset.knn_search(
    query_vector,
    k=10,
    filter="status = 'published' AND tags.contains('python')"
)

# KNN with specific columns
results = dataset.knn_search(
    query_vector,
    k=10,
    columns=["uuid", "title", "content", "_distance"]
)

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"Distance: {result['_distance']}")
    print(f"Content: {result['content'][:200]}...")
    print("---")
```

### Hybrid Search

Combine text and vector search:

```python
def hybrid_search(dataset, query_text, query_vector, alpha=0.5):
    """
    Hybrid search combining text and vector similarity.
    
    Args:
        alpha: Weight for text search (0.0 = pure vector, 1.0 = pure text)
    """
    # Get text search results
    text_results = dataset.full_text_search(
        query_text,
        limit=50
    ).to_pylist()
    
    # Get vector search results
    vector_results = dataset.knn_search(
        query_vector,
        k=50
    ).to_pylist()
    
    # Combine scores
    scores = {}
    
    # Add text scores
    for i, result in enumerate(text_results):
        uuid = result['uuid']
        # Normalize rank to score
        text_score = 1.0 - (i / len(text_results))
        scores[uuid] = alpha * text_score
    
    # Add vector scores
    for result in vector_results:
        uuid = result['uuid']
        # Normalize distance to score (assumes cosine distance)
        vector_score = 1.0 - result['_distance']
        if uuid in scores:
            scores[uuid] += (1 - alpha) * vector_score
        else:
            scores[uuid] = (1 - alpha) * vector_score
    
    # Sort by combined score
    sorted_uuids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top results
    return [dataset.get(uuid) for uuid, _ in sorted_uuids[:10]]
```

## Batch Operations

### Batch Processing

```python
# Process in batches to manage memory
def process_large_dataset(dataset, process_fn):
    """Process dataset in batches."""
    processed = 0
    
    for batch in dataset.to_batches(batch_size=1000):
        # Convert batch to records
        records = [FrameRecord.from_arrow(row) for row in batch.to_pylist()]
        
        # Process records
        updated_records = [process_fn(record) for record in records]
        
        # Update in dataset
        for record in updated_records:
            dataset.update_record(record.uuid, record)
        
        processed += len(records)
        print(f"Processed {processed} documents...")

# Example: Add word count to all documents
def add_word_count(record):
    word_count = len(record.text_content.split())
    record.metadata['custom_metadata']['word_count'] = word_count
    return record

process_large_dataset(dataset, add_word_count)
```

### Bulk Import

```python
def bulk_import_json(dataset, json_file, batch_size=5000):
    """Import documents from JSON file."""
    import json
    
    with open(json_file, 'r') as f:
        documents = json.load(f)
    
    # Process in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        records = []
        for doc in batch:
            record = FrameRecord.create(
                title=doc['title'],
                content=doc['content'],
                tags=doc.get('tags', []),
                custom_metadata=doc.get('metadata', {})
            )
            records.append(record)
        
        dataset.add_many(records)
        print(f"Imported {i + len(batch)} / {len(documents)} documents")
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def parallel_embedding(dataset, docs, embed_fn, num_workers=4):
    """Add embeddings to documents in parallel."""
    
    def process_chunk(chunk):
        return [embed_fn(doc) for doc in chunk]
    
    # Split documents into chunks
    chunks = np.array_split(docs, num_workers)
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        
        embedded_docs = []
        for future in futures:
            embedded_docs.extend(future.result())
    
    # Add to dataset
    dataset.add_many(embedded_docs)
    return embedded_docs
```

## Version Control

### Working with Versions

```python
# Get current version
current_version = dataset.version
print(f"Current version: {current_version}")

# List all versions
versions = dataset.list_versions()
for v in versions:
    print(f"Version {v['version']}: {v['timestamp']}")

# Checkout specific version
dataset.checkout(version=10)

# Checkout by timestamp
dataset.checkout(as_of="2024-01-15T10:00:00")

# Return to latest
dataset.checkout_latest()
```

### Version Tags

```python
# Tag important versions
dataset.tag_version("v1.0", "Initial production release")
dataset.tag_version("pre-migration", "Before schema update")

# List tags
tags = dataset.list_tags()
for tag in tags:
    print(f"{tag['name']}: version {tag['version']}")

# Checkout by tag
dataset.checkout(tag="v1.0")
```

### Time Travel Queries

```python
# Query historical data without changing current version
old_dataset = FrameDataset("my_docs.lance", version=5)
old_count = len(old_dataset)

# Compare versions
def compare_versions(uri, v1, v2):
    """Compare two versions of a dataset."""
    ds1 = FrameDataset(uri, version=v1)
    ds2 = FrameDataset(uri, version=v2)
    
    # Get all UUIDs
    uuids1 = set(row['uuid'] for row in ds1.to_table(['uuid']).to_pylist())
    uuids2 = set(row['uuid'] for row in ds2.to_table(['uuid']).to_pylist())
    
    added = uuids2 - uuids1
    removed = uuids1 - uuids2
    
    print(f"Version {v1} → {v2}:")
    print(f"  Added: {len(added)} documents")
    print(f"  Removed: {len(removed)} documents")
    print(f"  Total: {len(ds1)} → {len(ds2)}")
    
    return added, removed
```

## Performance Optimization

### Index Management

```python
# List current indices
indices = dataset.list_indices()
for idx in indices:
    print(f"Index: {idx['column']} ({idx['type']})")

# Create scalar indices for faster filtering
dataset.create_scalar_index("status")
dataset.create_scalar_index("author")
dataset.create_scalar_index("created_at")

# Bitmap index for low-cardinality fields
dataset.create_scalar_index("status", index_type="BITMAP")
dataset.create_scalar_index("record_type", index_type="BITMAP")

# Drop unused indices
dataset.drop_index("old_field")

# Optimize all indices
dataset.optimize_indices()
```

### Dataset Maintenance

```python
def maintain_dataset(dataset):
    """Perform regular maintenance tasks."""
    
    # 1. Compact fragments
    stats = dataset.stats()
    if stats.num_fragments > 100:
        print("Compacting fragments...")
        dataset.compact_files(
            target_rows_per_fragment=500_000,
            max_rows_per_group=8192
        )
    
    # 2. Clean up old versions
    print("Cleaning old versions...")
    dataset.cleanup_old_versions(
        older_than=timedelta(days=30),
        delete_untagged=True
    )
    
    # 3. Optimize indices
    print("Optimizing indices...")
    dataset.optimize_indices()
    
    # 4. Update statistics
    print("Updating statistics...")
    dataset.update_stats()
    
    # 5. Validate integrity
    print("Validating dataset...")
    dataset.validate()
    
    print("Maintenance complete!")
```

### Query Optimization

```python
# Use column projection
# Good - only reads needed columns
light_docs = dataset.scanner(
    columns=["uuid", "title", "tags"],
    filter="status = 'published'"
).to_table()

# Avoid - reads all columns
all_docs = dataset.to_pandas()
filtered = all_docs[all_docs['status'] == 'published']

# Use appropriate batch sizes
# For large operations
for batch in dataset.to_batches(batch_size=10000):
    process_batch(batch)

# For memory-constrained environments
for batch in dataset.to_batches(batch_size=100):
    process_batch(batch)

# Pre-filter with indices
# Ensure indices exist on filter columns
dataset.create_scalar_index("department")
results = dataset.scanner(
    filter="department = 'Engineering'"
).to_table()
```

## Working with FrameSets

FrameSets are AI-generated documents created from queries:

```python
# Create a frameset from a query
frameset = dataset.create_frameset(
    prompt="Summarize all documents about Python async programming",
    max_results=20,  # Limit source documents
    filter="tags.contains('python') AND content LIKE '%async%'"
)

# Create with specific LLM parameters
frameset = dataset.create_frameset(
    prompt="What are the best practices for API security?",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    system_prompt="You are a security expert. Be concise and actionable."
)

# Access frameset data
print(f"Title: {frameset.metadata['title']}")
print(f"Query: {frameset.metadata['query']}")
print(f"Content: {frameset.text_content}")

# Get source documents
for rel in frameset.metadata.get('relationships', []):
    if rel['type'] == 'contains':
        source = dataset.get(rel['id'])
        print(f"Source: {source.metadata['title']}")
```

## Best Practices

### 1. Resource Management

```python
# Use context manager for automatic cleanup
with FrameDataset("my_docs.lance") as dataset:
    # Operations here
    results = dataset.full_text_search("query")
# Dataset automatically closed

# Or explicitly close
dataset = FrameDataset("my_docs.lance")
try:
    # Operations
    pass
finally:
    dataset.close()
```

### 2. Error Handling

```python
def safe_get_document(dataset, uuid):
    """Safely retrieve a document with error handling."""
    try:
        return dataset.get(uuid)
    except KeyError:
        print(f"Document {uuid} not found")
        return None
    except Exception as e:
        print(f"Error retrieving document: {e}")
        return None

def safe_batch_operation(dataset, docs):
    """Perform batch operation with rollback on error."""
    version_before = dataset.version
    
    try:
        dataset.add_many(docs)
        print(f"Successfully added {len(docs)} documents")
    except Exception as e:
        print(f"Error during batch operation: {e}")
        # Rollback to previous version
        dataset.checkout(version=version_before)
        raise
```

### 3. Efficient Patterns

```python
# Cache frequently accessed data
class DatasetCache:
    def __init__(self, dataset):
        self.dataset = dataset
        self._cache = {}
        self._collection_cache = {}
    
    def get_document(self, uuid):
        if uuid not in self._cache:
            self._cache[uuid] = self.dataset.get(uuid)
        return self._cache[uuid]
    
    def get_collection(self, name):
        if name not in self._collection_cache:
            docs = self.dataset.scanner(
                filter=f"collection = '{name}'"
            ).to_table().to_pylist()
            self._collection_cache[name] = docs
        return self._collection_cache[name]

# Batch similar operations
def batch_update_status(dataset, uuids, new_status):
    """Update status for multiple documents efficiently."""
    # Get all documents first
    docs = dataset.get_many(uuids)
    
    # Update in memory
    for doc in docs:
        doc.metadata['status'] = new_status
        doc.metadata['updated_at'] = datetime.now().isoformat()
    
    # Write back in one operation
    for uuid, doc in zip(uuids, docs):
        dataset.update_record(uuid, doc)
```

### 4. Monitoring

```python
def monitor_dataset_health(dataset):
    """Monitor dataset health metrics."""
    stats = dataset.stats()
    
    health_report = {
        'version': dataset.version,
        'documents': len(dataset),
        'size_mb': stats.dataset_size / 1024 / 1024,
        'fragments': stats.num_fragments,
        'indices': len(dataset.list_indices()),
        'fragmentation_ratio': stats.num_fragments / max(len(dataset) / 1000, 1)
    }
    
    # Check for issues
    issues = []
    if health_report['fragmentation_ratio'] > 10:
        issues.append("High fragmentation - consider compaction")
    
    if health_report['size_mb'] > 10000:  # 10GB
        issues.append("Large dataset - consider partitioning")
    
    if health_report['fragments'] > 1000:
        issues.append("Too many fragments - run compact_files()")
    
    health_report['issues'] = issues
    return health_report
```

## Advanced Examples

### Multi-Tenant Dataset

```python
class MultiTenantDataset:
    """Wrapper for multi-tenant document management."""
    
    def __init__(self, uri):
        self.dataset = FrameDataset(uri)
    
    def add_document(self, tenant_id, doc):
        """Add document for specific tenant."""
        doc.metadata['tenant_id'] = tenant_id
        self.dataset.add(doc)
    
    def get_tenant_documents(self, tenant_id):
        """Get all documents for a tenant."""
        return self.dataset.scanner(
            filter=f"tenant_id = '{tenant_id}'"
        ).to_table()
    
    def search_tenant(self, tenant_id, query):
        """Search within tenant's documents."""
        return self.dataset.full_text_search(
            query,
            filter=f"tenant_id = '{tenant_id}'"
        )
    
    def delete_tenant_data(self, tenant_id):
        """Remove all tenant data (GDPR compliance)."""
        docs = self.get_tenant_documents(tenant_id)
        for doc in docs.to_pylist():
            self.dataset.delete_record(doc['uuid'])
```

### Change Detection

```python
def track_changes(dataset, since_version):
    """Track changes since a specific version."""
    current_version = dataset.version
    
    # Get documents from both versions
    old_ds = FrameDataset(dataset.uri, version=since_version)
    
    old_docs = {doc['uuid']: doc for doc in old_ds.to_table().to_pylist()}
    new_docs = {doc['uuid']: doc for doc in dataset.to_table().to_pylist()}
    
    changes = {
        'added': [],
        'modified': [],
        'deleted': []
    }
    
    # Find added and modified
    for uuid, doc in new_docs.items():
        if uuid not in old_docs:
            changes['added'].append(doc)
        elif doc['updated_at'] > old_docs[uuid]['updated_at']:
            changes['modified'].append({
                'old': old_docs[uuid],
                'new': doc
            })
    
    # Find deleted
    for uuid in old_docs:
        if uuid not in new_docs:
            changes['deleted'].append(old_docs[uuid])
    
    return changes
```

## Next Steps

- Learn about [FrameRecord](frame-record.md) operations in detail
- Explore [Embeddings](embeddings.md) for semantic search
- Understand [Search & Query](search-query.md) patterns
- See [Import/Export](import-export.md) for data migration
- Check the [API Reference](../api/frame-dataset.md) for all methods