# Storage Layer

ContextFrame is built on Lance, a modern columnar data format designed for AI workloads. This page explains how the storage layer works, its benefits, and how to use it effectively.

## What is Lance?

Lance is an open-source columnar data format that provides:
- **Version control** for datasets
- **Native vector support** for embeddings
- **Zero-copy reads** via memory mapping
- **Cloud-native** storage (S3, GCS, Azure)
- **Self-contained** datasets as directories

## Lance vs Traditional Databases

### Advantages of Lance

| Feature | Lance | Traditional DB |
|---------|-------|----------------|
| **Deployment** | No server required | Database server needed |
| **Vector Search** | Native support | Extension/plugin required |
| **Versioning** | Built-in time travel | Manual implementation |
| **Cloud Storage** | Direct S3/GCS/Azure | Requires special setup |
| **Analytics** | Columnar optimized | Row-oriented (usually) |
| **Portability** | Copy directory | Export/import process |

### When to Use ContextFrame/Lance

**Ideal for:**
- Document collections with embeddings
- Analytical queries over many documents
- Version-controlled datasets
- Cloud-native applications
- Edge deployments

**Consider alternatives for:**
- High-frequency transactional updates
- Complex relational queries
- Real-time synchronization needs

## Storage Architecture

### Dataset Structure

A Lance dataset is a directory with a specific structure:

```
my_dataset.lance/
├── _versions/          # Version manifest files
│   ├── 1.manifest      # Version 1 metadata
│   ├── 2.manifest      # Version 2 metadata
│   └── ...
├── _fragments/         # Data fragments (Parquet files)
│   ├── 0.parquet       # Data fragment 0
│   ├── 1.parquet       # Data fragment 1
│   └── ...
├── _indices/           # Index files
│   ├── vector_index/   # Vector indices
│   └── scalar/         # Scalar indices
└── _deletions/         # Deletion vectors
    └── 0.deletions     # Soft deletes
```

### Columnar Storage Benefits

Lance stores data in columns rather than rows:

```
Traditional Row Storage:
┌────┬───────┬────────┬──────┐
│ ID │ Title │ Author │ Tags │
├────┼───────┼────────┼──────┤
│ 1  │ Doc A │ Alice  │ [...] │
│ 2  │ Doc B │ Bob    │ [...] │
└────┴───────┴────────┴──────┘

Columnar Storage (Lance):
┌────┬────┐    ┌───────┬───────┐    ┌────────┬────────┐
│ ID │    │    │ Title │       │    │ Author │        │
├────┼────┤    ├───────┼───────┤    ├────────┼────────┤
│ 1  │ 2  │    │ Doc A │ Doc B │    │ Alice  │ Bob    │
└────┴────┘    └───────┴───────┘    └────────┴────────┘
```

**Benefits:**
- **Compression**: Similar values compress better
- **Projection**: Read only needed columns
- **Analytics**: Efficient aggregations
- **Cache**: Better CPU cache utilization

## Working with Storage

### Local Storage

Default behavior uses local filesystem:

```python
from contextframe import FrameDataset

# Create local dataset
dataset = FrameDataset.create("local_data.lance")

# Opens in current directory
print(f"Dataset path: {dataset.uri}")  # ./local_data.lance

# Specify absolute path
dataset = FrameDataset.create("/data/datasets/my_data.lance")
```

### Cloud Storage

#### AWS S3

```python
# S3 configuration
dataset = FrameDataset(
    "s3://my-bucket/datasets/production.lance",
    storage_options={
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY",
        "aws_region": "us-east-1"
    }
)

# Using IAM role (recommended)
dataset = FrameDataset(
    "s3://my-bucket/datasets/production.lance",
    storage_options={
        "aws_region": "us-east-1"
    }
)
```

#### Google Cloud Storage

```python
# GCS configuration
dataset = FrameDataset(
    "gs://my-bucket/datasets/production.lance",
    storage_options={
        "service_account": "/path/to/service-account.json"
    }
)

# Using default credentials
dataset = FrameDataset("gs://my-bucket/datasets/production.lance")
```

#### Azure Blob Storage

```python
# Azure configuration
dataset = FrameDataset(
    "az://my-container/datasets/production.lance",
    storage_options={
        "azure_storage_account_name": "myaccount",
        "azure_storage_account_key": "YOUR_KEY"
    }
)

# Using Azure AD
dataset = FrameDataset(
    "az://my-container/datasets/production.lance",
    storage_options={
        "azure_storage_account_name": "myaccount",
        "azure_client_id": "YOUR_CLIENT_ID",
        "azure_client_secret": "YOUR_SECRET",
        "azure_tenant_id": "YOUR_TENANT_ID"
    }
)
```

## Vector Storage and Indices

### Native Vector Support

Lance stores embeddings as fixed-size arrays:

```python
# Vectors stored efficiently
doc = FrameRecord.create(
    title="AI Research Paper",
    content="...",
    embedding=np.array([0.1, 0.2, ...])  # 1536 dimensions
)

# Automatic vector column detection
dataset.add(doc)  # Recognizes embedding field
```

### Vector Index Types

#### IVF_PQ (Default)
Inverted File with Product Quantization:
```python
dataset.create_vector_index(
    index_type="IVF_PQ",
    num_partitions=256,      # Number of clusters
    num_sub_quantizers=16,   # PQ compression
    metric_type="cosine"     # Distance metric
)
```

**Characteristics:**
- Good balance of speed and memory
- Lossy compression for space efficiency
- Suitable for large datasets

#### IVF_FLAT
Inverted File with exact storage:
```python
dataset.create_vector_index(
    index_type="IVF_FLAT",
    num_partitions=100,
    metric_type="l2"
)
```

**Characteristics:**
- Higher accuracy (no compression)
- More memory usage
- Better for smaller datasets

### Scalar Indices

Create indices on metadata fields:

```python
# Create scalar indices
dataset.create_scalar_index("status")
dataset.create_scalar_index("author")
dataset.create_scalar_index("created_at")

# Bitmap index for low-cardinality fields
dataset.create_scalar_index("status", index_type="BITMAP")
```

## Query Performance

### Efficient Filtering

Lance pushes filters to the storage layer:

```python
# Efficient - uses index and column pruning
results = dataset.scanner(
    filter="status = 'published' AND author = 'Alice'",
    columns=["uuid", "title", "content"]  # Only read needed columns
).to_table()

# Less efficient - reads all columns
docs = dataset.to_pandas()
filtered = docs[docs['status'] == 'published']
```

### Projection Pushdown

Read only the columns you need:

```python
# Good - minimal data transfer
titles = dataset.scanner(
    columns=["uuid", "title"]
).to_table()

# Avoid - reads everything
all_data = dataset.to_pandas()
titles = all_data[["uuid", "title"]]
```

### Batch Processing

Process large datasets efficiently:

```python
# Stream in batches
for batch in dataset.to_batches(batch_size=1000):
    # Process batch (PyArrow RecordBatch)
    process_batch(batch)

# Memory-efficient aggregation
def count_by_status(dataset):
    status_counts = {}
    for batch in dataset.to_batches():
        for status in batch['status']:
            status = status.as_py()
            status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts
```

## Version Control

### How Versioning Works

Every write operation creates a new version:

```python
# Version 1: Initial documents
dataset.add_many(initial_docs)
print(f"Version: {dataset.version}")  # 1

# Version 2: Add more documents
dataset.add_many(more_docs)
print(f"Version: {dataset.version}")  # 2

# Version 3: Update a document
dataset.update_record(uuid, updated_doc)
print(f"Version: {dataset.version}")  # 3
```

### Time Travel

Query historical versions:

```python
# Get current version
current_version = dataset.version

# Checkout older version
dataset.checkout(version=1)
old_docs = dataset.to_pandas()

# Return to latest
dataset.checkout_latest()

# Query specific version without changing state
old_dataset = FrameDataset("my_data.lance", version=1)
```

### Version Management

```python
# List versions
versions = dataset.list_versions()
for v in versions:
    print(f"Version {v['version']}: {v['timestamp']} - {v['message']}")

# Tag important versions
dataset.tag_version("v1.0", "Initial production release")

# Cleanup old versions (keep last 10)
dataset.cleanup_old_versions(
    older_than=timedelta(days=7),
    delete_untagged=True
)
```

## Storage Optimization

### Compaction

Merge small files for better performance:

```python
# Check fragmentation
stats = dataset.stats()
print(f"Number of fragments: {stats.num_fragments}")

# Compact if needed
if stats.num_fragments > 100:
    dataset.compact_files(
        target_rows_per_fragment=1024 * 1024,  # 1M rows per file
        max_rows_per_group=1024                # Row group size
    )
```

### Deletion Cleanup

Remove deleted records permanently:

```python
# Soft deletes accumulate
dataset.delete_record(uuid1)
dataset.delete_record(uuid2)

# Clean up periodically
dataset.cleanup_deletions()
```

### Index Optimization

```python
# Rebuild indices for better performance
dataset.optimize_indices()

# Drop unused indices
dataset.drop_index("old_field")
```

## Blob Storage

### How Blobs Work

Large binary data uses special storage:

```python
# Blobs stored separately from columnar data
doc = FrameRecord.create(
    title="Product Image",
    content="High-resolution product photo",
    raw_data=large_image_bytes,      # 10MB image
    raw_data_type="image/jpeg"
)

# Efficient scanning without loading blobs
for batch in dataset.to_batches():
    # Process metadata without loading images
    process_metadata(batch)
```

### Lazy Loading

Blobs are loaded only when accessed:

```python
# Metadata query - fast
docs = dataset.scanner(
    columns=["uuid", "title", "raw_data_type"],
    filter="raw_data_type = 'image/jpeg'"
).to_table()

# Blob access - loads on demand
doc = dataset.get(uuid)
if doc.raw_data:
    image = process_image(doc.raw_data)
```

## Backup and Migration

### Local Backup

```python
import shutil

# Simple directory copy
shutil.copytree("production.lance", "backup/production_2024_01_20.lance")

# Compressed backup
import tarfile
with tarfile.open("backup.tar.gz", "w:gz") as tar:
    tar.add("production.lance")
```

### Cloud Backup

```python
# S3 sync
import subprocess
subprocess.run([
    "aws", "s3", "sync",
    "production.lance",
    "s3://backup-bucket/datasets/production.lance"
])

# Cross-region replication
dataset_primary = FrameDataset("s3://us-east-1/prod.lance")
dataset_backup = FrameDataset.create("s3://eu-west-1/prod-backup.lance")

# Copy data
for batch in dataset_primary.to_batches():
    docs = [FrameRecord.from_arrow(row) for row in batch]
    dataset_backup.add_many(docs)
```

### Migration Patterns

```python
# Lance to Lance (different schema)
def migrate_dataset(source_path, target_path, transform_fn):
    source = FrameDataset(source_path)
    target = FrameDataset.create(target_path)
    
    for batch in source.to_batches(batch_size=10000):
        docs = []
        for row in batch:
            doc = FrameRecord.from_arrow(row)
            transformed = transform_fn(doc)
            docs.append(transformed)
        
        target.add_many(docs)
    
    return target

# Export to Parquet
dataset.to_table().to_parquet("export.parquet")

# Export to JSON
docs = dataset.to_pandas()
docs.to_json("export.json", orient="records")
```

## Monitoring and Debugging

### Dataset Statistics

```python
# Get storage statistics
stats = dataset.stats()
print(f"""
Dataset Statistics:
- Version: {stats.version}
- Fragments: {stats.num_fragments}
- Rows: {stats.num_rows}
- Size: {stats.dataset_size / 1024 / 1024:.2f} MB
- Indices: {stats.indices}
""")
```

### Fragment Analysis

```python
# Analyze fragment distribution
fragments = dataset.get_fragments()
for frag in fragments:
    print(f"Fragment {frag.id}: {frag.count_rows()} rows")
```

### Performance Profiling

```python
import time

# Profile query performance
start = time.time()
results = dataset.knn_search(query_vector, k=10)
print(f"Vector search took: {time.time() - start:.3f}s")

# Profile with explanation
explain = dataset.scanner(
    filter="status = 'published'"
).explain()
print(explain)
```

## Best Practices

### 1. Right-size Fragments
```python
# Target 100-500MB per fragment
dataset.compact_files(
    target_rows_per_fragment=500_000
)
```

### 2. Use Appropriate Indices
```python
# High-cardinality fields: B-tree
dataset.create_scalar_index("uuid")

# Low-cardinality fields: Bitmap
dataset.create_scalar_index("status", index_type="BITMAP")

# Vector fields: IVF index
dataset.create_vector_index(num_partitions=int(np.sqrt(len(dataset))))
```

### 3. Batch Operations
```python
# Always batch when possible
docs = [create_doc(i) for i in range(10000)]
dataset.add_many(docs, batch_size=1000)
```

### 4. Cloud Storage Configuration
```python
# Use appropriate timeouts and retries
storage_options = {
    "aws_region": "us-east-1",
    "timeout": "60s",
    "max_retries": 3
}
```

### 5. Regular Maintenance
```python
# Weekly maintenance routine
def maintain_dataset(dataset):
    # Compact fragments
    dataset.compact_files()
    
    # Cleanup old versions
    dataset.cleanup_old_versions(older_than=timedelta(days=30))
    
    # Optimize indices
    dataset.optimize_indices()
    
    # Verify integrity
    dataset.validate()
```

## Next Steps

- Learn about [Collections & Relationships](collections-relationships.md)
- Understand [Record Types](record-types.md)
- Explore [Performance Tuning](../mcp/guides/performance.md)
- See [Cloud Deployment](../integration/object_storage.md) guides