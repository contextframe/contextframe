# Migrating from Document Stores

This guide helps you migrate from traditional document storage systems to ContextFrame. Whether you're using Elasticsearch, MongoDB, PostgreSQL with pgvector, DynamoDB, or traditional filesystems, we'll show you how to preserve your documents, metadata, and search capabilities while gaining ContextFrame's advanced features.

## Why Migrate from Document Stores?

Traditional document stores have limitations that ContextFrame addresses:

- **Unified Schema**: Standardized document structure with rich metadata
- **Native Embeddings**: First-class support for vector search alongside full-text
- **Relationships**: Built-in document hierarchies and connections
- **Performance**: Columnar storage optimized for analytical queries
- **Version Control**: Automatic document versioning and history

## Migration Strategies by Platform

### Elasticsearch Migration

#### Export from Elasticsearch

Elasticsearch provides robust export capabilities through scroll API or snapshots:

```python
from elasticsearch import Elasticsearch
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import json

def export_from_elasticsearch(host, index_name, batch_size=1000):
    """Export documents from Elasticsearch using scroll API."""
    
    es = Elasticsearch([host])
    
    # Get index mapping to understand structure
    mapping = es.indices.get_mapping(index=index_name)
    
    # Initialize scroll
    response = es.search(
        index=index_name,
        size=batch_size,
        scroll='2m',  # Keep scroll context alive for 2 minutes
        body={
            "query": {"match_all": {}},
            "_source": True
        }
    )
    
    scroll_id = response['_scroll_id']
    total_docs = response['hits']['total']['value']
    
    print(f"Exporting {total_docs} documents from Elasticsearch index '{index_name}'")
    
    exported_data = []
    
    # Process initial batch
    for hit in response['hits']['hits']:
        exported_data.append({
            'id': hit['_id'],
            'source': hit['_source'],
            'score': hit.get('_score'),
            'index': hit['_index']
        })
    
    # Continue scrolling
    while len(response['hits']['hits']) > 0:
        response = es.scroll(scroll_id=scroll_id, scroll='2m')
        
        for hit in response['hits']['hits']:
            exported_data.append({
                'id': hit['_id'],
                'source': hit['_source'],
                'score': hit.get('_score'),
                'index': hit['_index']
            })
        
        print(f"Exported {len(exported_data)}/{total_docs} documents")
    
    # Clear scroll context
    es.clear_scroll(scroll_id=scroll_id)
    
    return exported_data, mapping
```

#### Import to ContextFrame

```python
def migrate_elasticsearch_to_contextframe(es_data, mapping, dataset_path="migrated_data.lance"):
    """Migrate Elasticsearch data to ContextFrame."""
    
    dataset = FrameDataset.create(dataset_path)
    
    records = []
    for doc in es_data:
        source = doc['source']
        
        # Extract common fields
        title = source.get('title', source.get('name', f"Document {doc['id']}"))
        
        # Handle different content field names
        text_content = (source.get('content') or 
                       source.get('text') or 
                       source.get('body') or 
                       source.get('description', ''))
        
        # Build metadata from remaining fields
        metadata_fields = {k: v for k, v in source.items() 
                          if k not in ['title', 'content', 'text', 'body', 'description']}
        
        metadata = create_metadata(
            title=title,
            source="elasticsearch_migration",
            original_id=doc['id'],
            index_name=doc['index'],
            **metadata_fields
        )
        
        # Handle existing embeddings if present
        embedding = None
        if 'embedding' in source or 'vector' in source:
            embedding = source.get('embedding', source.get('vector'))
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=embedding
        )
        
        records.append(record)
    
    # Add records (generate embeddings only if not present)
    dataset.add_many(records, generate_embeddings=(embedding is None))
    
    print(f"Migrated {len(records)} documents from Elasticsearch")
    return dataset
```

#### Preserve Search Functionality

```python
def setup_search_compatibility(dataset):
    """Configure ContextFrame to match Elasticsearch search patterns."""
    
    # Create indices for common search patterns
    dataset.create_index("text_content", index_type="fts")  # Full-text search
    
    # Example: Replicate Elasticsearch query
    def search_like_elasticsearch(query, size=10, from_=0):
        # Combine vector and full-text search
        results = dataset.search_hybrid(
            query=query,
            limit=size,
            offset=from_,
            alpha=0.5  # Balance between vector and text search
        )
        
        # Format results similar to Elasticsearch
        hits = []
        for idx, record in enumerate(results):
            hits.append({
                '_index': 'contextframe',
                '_id': str(record.unique_id),
                '_score': 1.0 - (idx * 0.1),  # Simulated relevance score
                '_source': {
                    'title': record.metadata.title,
                    'content': record.text_content,
                    **record.metadata.custom_metadata
                }
            })
        
        return {
            'hits': {
                'total': {'value': len(hits)},
                'hits': hits
            }
        }
    
    return search_like_elasticsearch
```

### MongoDB Migration

#### Export from MongoDB

MongoDB's flexible schema requires careful handling:

```python
from pymongo import MongoClient
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import datetime

def export_from_mongodb(connection_string, database, collection, batch_size=1000):
    """Export documents from MongoDB collection."""
    
    client = MongoClient(connection_string)
    db = client[database]
    coll = db[collection]
    
    total_docs = coll.count_documents({})
    print(f"Exporting {total_docs} documents from MongoDB {database}.{collection}")
    
    exported_data = []
    
    # Use cursor with batch size for memory efficiency
    cursor = coll.find({}).batch_size(batch_size)
    
    for doc in cursor:
        # Convert ObjectId to string
        doc['_id'] = str(doc['_id'])
        
        # Handle dates
        for key, value in doc.items():
            if isinstance(value, datetime.datetime):
                doc[key] = value.isoformat()
        
        exported_data.append(doc)
        
        if len(exported_data) % batch_size == 0:
            print(f"Exported {len(exported_data)}/{total_docs} documents")
    
    return exported_data
```

#### Import with Schema Mapping

```python
def migrate_mongodb_to_contextframe(mongo_data, dataset_path="migrated_data.lance",
                                   content_fields=None, title_fields=None):
    """Migrate MongoDB data with flexible schema mapping."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Default field mappings
    content_fields = content_fields or ['content', 'text', 'body', 'description']
    title_fields = title_fields or ['title', 'name', 'subject', 'headline']
    
    records = []
    for doc in mongo_data:
        # Find content field
        text_content = ''
        for field in content_fields:
            if field in doc and doc[field]:
                text_content = str(doc[field])
                break
        
        # Find title field
        title = f"Document {doc['_id']}"
        for field in title_fields:
            if field in doc and doc[field]:
                title = str(doc[field])
                break
        
        # Extract metadata
        metadata_fields = {k: v for k, v in doc.items() 
                          if k not in ['_id'] + content_fields + title_fields}
        
        # Handle nested documents
        flattened_metadata = flatten_nested_dict(metadata_fields)
        
        metadata = create_metadata(
            title=title,
            source="mongodb_migration",
            original_id=doc['_id'],
            **flattened_metadata
        )
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid()
        )
        
        records.append(record)
    
    dataset.add_many(records)
    
    print(f"Migrated {len(records)} documents from MongoDB")
    return dataset

def flatten_nested_dict(d, parent_key='', sep='_'):
    """Flatten nested MongoDB documents for metadata."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to JSON strings
            items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    return dict(items)
```

### PostgreSQL with pgvector Migration

#### Export from pgvector

PostgreSQL with pgvector combines relational data with vectors:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid

def export_from_pgvector(connection_params, table_name, vector_column='embedding',
                        text_column='content', batch_size=1000):
    """Export documents and vectors from PostgreSQL with pgvector."""
    
    conn = psycopg2.connect(**connection_params)
    
    # Get table schema
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        schema = cur.fetchall()
    
    # Count total rows
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cur.fetchone()[0]
    
    print(f"Exporting {total_rows} rows from PostgreSQL table '{table_name}'")
    
    exported_data = []
    
    # Export in batches
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            
            for row in rows:
                # Convert pgvector to numpy array
                if vector_column in row and row[vector_column]:
                    # pgvector format: '[0.1, 0.2, 0.3]'
                    vector_str = row[vector_column]
                    if isinstance(vector_str, str):
                        vector_str = vector_str.strip('[]')
                        row[vector_column] = np.array([float(x) for x in vector_str.split(',')])
                
                exported_data.append(row)
            
            print(f"Exported {len(exported_data)}/{total_rows} rows")
    
    conn.close()
    return exported_data, schema
```

#### Import with Relationship Preservation

```python
def migrate_pgvector_to_contextframe(pg_data, schema, dataset_path="migrated_data.lance",
                                    id_column='id', vector_column='embedding',
                                    text_column='content', title_column='title'):
    """Migrate PostgreSQL pgvector data preserving relationships."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # First pass: Create all records
    id_to_uuid = {}  # Map original IDs to ContextFrame UUIDs
    records = []
    
    for row in pg_data:
        # Extract core fields
        original_id = str(row.get(id_column, ''))
        text_content = row.get(text_column, '')
        title = row.get(title_column, f"Document {original_id}")
        embedding = row.get(vector_column)
        
        # Build metadata from other columns
        metadata_fields = {k: v for k, v in row.items() 
                          if k not in [id_column, vector_column, text_column, title_column]
                          and v is not None}
        
        metadata = create_metadata(
            title=title,
            source="pgvector_migration",
            original_id=original_id,
            **metadata_fields
        )
        
        # Create record
        unique_id = generate_uuid()
        id_to_uuid[original_id] = unique_id
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=unique_id,
            embedding=embedding
        )
        
        records.append(record)
    
    # Second pass: Handle relationships
    for i, row in enumerate(pg_data):
        # Look for foreign key columns
        for col, value in row.items():
            if col.endswith('_id') and col != id_column and value:
                referenced_id = str(value)
                if referenced_id in id_to_uuid:
                    # Create relationship
                    records[i].relationships.append({
                        'type': 'reference',
                        'target_id': id_to_uuid[referenced_id],
                        'label': col.replace('_id', '')
                    })
    
    # Add all records
    dataset.add_many(records, generate_embeddings=(vector_column not in pg_data[0]))
    
    print(f"Migrated {len(records)} documents from PostgreSQL")
    return dataset
```

### DynamoDB Migration

#### Export from DynamoDB

DynamoDB's NoSQL structure requires special handling:

```python
import boto3
from decimal import Decimal
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import json

def export_from_dynamodb(table_name, region='us-east-1', profile=None):
    """Export items from DynamoDB table."""
    
    # Initialize DynamoDB client
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    dynamodb = session.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Get table info
    table_info = table.describe()
    print(f"Exporting from DynamoDB table '{table_name}' ({table.item_count} items)")
    
    exported_data = []
    
    # Scan with pagination
    last_evaluated_key = None
    
    while True:
        if last_evaluated_key:
            response = table.scan(ExclusiveStartKey=last_evaluated_key)
        else:
            response = table.scan()
        
        # Convert Decimal to float for JSON serialization
        for item in response['Items']:
            converted_item = convert_decimals(item)
            exported_data.append(converted_item)
        
        print(f"Exported {len(exported_data)} items")
        
        # Check if more pages
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break
    
    return exported_data, table_info

def convert_decimals(obj):
    """Convert DynamoDB Decimal types to Python floats."""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj
```

#### Import with Type Preservation

```python
def migrate_dynamodb_to_contextframe(dynamo_data, table_info, dataset_path="migrated_data.lance",
                                    partition_key=None, sort_key=None):
    """Migrate DynamoDB data preserving item structure."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Extract key schema if not provided
    if not partition_key:
        for key in table_info['Table']['KeySchema']:
            if key['KeyType'] == 'HASH':
                partition_key = key['AttributeName']
            elif key['KeyType'] == 'RANGE':
                sort_key = key['AttributeName']
    
    records = []
    for item in dynamo_data:
        # Build unique identifier
        item_id = str(item.get(partition_key, ''))
        if sort_key and sort_key in item:
            item_id += f"#{item[sort_key]}"
        
        # Extract content - DynamoDB items are often fully structured
        # so we'll serialize non-key attributes as content
        content_dict = {k: v for k, v in item.items() 
                       if k not in [partition_key, sort_key]}
        
        text_content = json.dumps(content_dict, indent=2)
        
        # Use partition key as title
        title = f"{partition_key}: {item.get(partition_key, 'Unknown')}"
        
        metadata = create_metadata(
            title=title,
            source="dynamodb_migration",
            table_name=table_info['Table']['TableName'],
            partition_key=str(item.get(partition_key, '')),
            sort_key=str(item.get(sort_key, '')) if sort_key else None,
            original_id=item_id
        )
        
        # Add global secondary index attributes to metadata
        for gsi in table_info['Table'].get('GlobalSecondaryIndexes', []):
            for key in gsi['KeySchema']:
                attr_name = key['AttributeName']
                if attr_name in item:
                    metadata.custom_metadata[f"gsi_{attr_name}"] = str(item[attr_name])
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid()
        )
        
        records.append(record)
    
    dataset.add_many(records)
    
    print(f"Migrated {len(records)} items from DynamoDB")
    return dataset
```

### Filesystem Migration

#### Scan Directory Structure

```python
import os
import mimetypes
from pathlib import Path
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import hashlib

def scan_filesystem(root_path, extensions=None, exclude_patterns=None):
    """Scan filesystem for documents to migrate."""
    
    root_path = Path(root_path)
    exclude_patterns = exclude_patterns or ['.git', '__pycache__', 'node_modules']
    
    documents = []
    
    for path in root_path.rglob('*'):
        # Skip directories
        if path.is_dir():
            continue
        
        # Skip excluded patterns
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue
        
        # Filter by extension if specified
        if extensions and path.suffix.lower() not in extensions:
            continue
        
        # Get file metadata
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        # Calculate file hash for deduplication
        with open(path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        documents.append({
            'path': path,
            'relative_path': path.relative_to(root_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'mime_type': mime_type,
            'hash': file_hash
        })
    
    print(f"Found {len(documents)} documents in {root_path}")
    return documents
```

#### Import with Content Extraction

```python
def migrate_filesystem_to_contextframe(documents, root_path, dataset_path="migrated_data.lance",
                                      preserve_structure=True):
    """Migrate filesystem documents to ContextFrame."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Group documents by directory for collection creation
    if preserve_structure:
        from collections import defaultdict
        dir_groups = defaultdict(list)
        for doc in documents:
            dir_groups[doc['path'].parent].append(doc)
    
    records = []
    
    for doc in documents:
        path = doc['path']
        
        # Read content based on file type
        try:
            if doc['mime_type'] and doc['mime_type'].startswith('text/'):
                with open(path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                # For binary files, store path reference
                text_content = f"Binary file: {doc['relative_path']}"
        except Exception as e:
            text_content = f"Error reading file: {str(e)}"
        
        # Build metadata
        metadata = create_metadata(
            title=path.name,
            source="filesystem_migration",
            file_path=str(doc['relative_path']),
            file_size=doc['size'],
            mime_type=doc['mime_type'] or 'application/octet-stream',
            file_hash=doc['hash'],
            modified_timestamp=doc['modified'],
            created_timestamp=doc['created']
        )
        
        # Add directory hierarchy to metadata
        parts = list(doc['relative_path'].parts[:-1])
        if parts:
            metadata.custom_metadata['directory_path'] = '/'.join(parts)
        
        # Determine record type
        record_type = 'document'
        if path.name in ['README.md', 'index.md', 'index.html']:
            record_type = 'collection_header'
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type=record_type
        )
        
        # Create relationships for directory structure
        if preserve_structure and doc['relative_path'].parts[:-1]:
            parent_dir = '/'.join(doc['relative_path'].parts[:-1])
            record.relationships.append({
                'type': 'member_of',
                'target_id': parent_dir,  # Will be resolved later
                'label': 'directory'
            })
        
        records.append(record)
    
    dataset.add_many(records)
    
    print(f"Migrated {len(records)} documents from filesystem")
    return dataset
```

## Advanced Migration Patterns

### Incremental Migration

For large document stores, use incremental migration:

```python
def incremental_migration(source_system, migrate_func, checkpoint_file="migration_checkpoint.json"):
    """Perform incremental migration with checkpointing."""
    
    import json
    from datetime import datetime
    
    # Load checkpoint
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
    
    last_processed = checkpoint.get('last_processed_id')
    last_timestamp = checkpoint.get('last_timestamp', 0)
    
    # Query only new/updated documents
    if source_system == 'elasticsearch':
        query = {
            "query": {
                "range": {
                    "updated_at": {
                        "gt": last_timestamp
                    }
                }
            }
        }
    elif source_system == 'mongodb':
        query = {"updated_at": {"$gt": datetime.fromtimestamp(last_timestamp)}}
    
    # Migrate batch
    new_docs = export_with_query(source_system, query)
    if new_docs:
        migrate_func(new_docs)
        
        # Update checkpoint
        checkpoint['last_processed_id'] = new_docs[-1]['id']
        checkpoint['last_timestamp'] = time.time()
        checkpoint['total_processed'] = checkpoint.get('total_processed', 0) + len(new_docs)
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
    
    return checkpoint
```

### Schema Evolution Handling

Handle schema changes during migration:

```python
def handle_schema_evolution(source_docs, schema_mappings=None):
    """Handle documents with evolving schemas."""
    
    schema_mappings = schema_mappings or {}
    normalized_docs = []
    
    for doc in source_docs:
        # Detect schema version
        schema_version = detect_schema_version(doc)
        
        # Apply appropriate transformation
        if schema_version in schema_mappings:
            mapping = schema_mappings[schema_version]
            normalized_doc = apply_mapping(doc, mapping)
        else:
            # Use default mapping
            normalized_doc = default_normalization(doc)
        
        normalized_docs.append(normalized_doc)
    
    return normalized_docs

def detect_schema_version(doc):
    """Detect document schema version based on field presence."""
    if 'schema_version' in doc:
        return doc['schema_version']
    elif 'version' in doc:
        return f"v{doc['version']}"
    elif 'content' in doc and 'body' not in doc:
        return 'v1'
    elif 'body' in doc:
        return 'v2'
    else:
        return 'unknown'
```

### Performance Optimization

Optimize migration for large datasets:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

def parallel_migration(source_data, migrate_func, num_workers=None):
    """Perform parallel migration for better performance."""
    
    num_workers = num_workers or multiprocessing.cpu_count()
    
    # Split data into chunks
    chunk_size = len(source_data) // num_workers
    chunks = [source_data[i:i + chunk_size] 
              for i in range(0, len(source_data), chunk_size)]
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i, chunk in enumerate(chunks):
            future = executor.submit(migrate_func, chunk, f"chunk_{i}.lance")
            futures.append(future)
        
        # Wait for completion
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
    
    # Merge results
    final_dataset = merge_datasets(results)
    return final_dataset

def merge_datasets(dataset_paths):
    """Merge multiple Lance datasets into one."""
    # Implementation depends on Lance merge capabilities
    pass
```

## Post-Migration Validation

### Data Integrity Checks

```python
def validate_migration(source_system, target_dataset):
    """Validate migration completeness and accuracy."""
    
    validations = {
        'count': check_document_count(source_system, target_dataset),
        'content': check_content_preservation(source_system, target_dataset),
        'metadata': check_metadata_mapping(source_system, target_dataset),
        'search': check_search_quality(source_system, target_dataset)
    }
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'source': source_system,
        'target': target_dataset.path,
        'validations': validations,
        'passed': all(v['passed'] for v in validations.values())
    }
    
    return report

def check_content_preservation(source_system, target_dataset, sample_size=100):
    """Verify content was preserved accurately."""
    import random
    
    # Sample random documents
    source_samples = get_random_samples(source_system, sample_size)
    
    results = []
    for sample in source_samples:
        # Find in target
        target_doc = target_dataset.search(
            query=f"original_id:{sample['id']}",
            limit=1
        )
        
        if target_doc:
            # Compare content
            match = compare_content(sample['content'], target_doc[0].text_content)
            results.append(match)
    
    return {
        'passed': sum(results) / len(results) > 0.95,  # 95% accuracy threshold
        'accuracy': sum(results) / len(results),
        'sample_size': sample_size
    }
```

## Migration Checklist

Before starting migration:

- [ ] **Analyze Source System**
  - Document current schema
  - Identify unique fields and relationships
  - Measure data volume and growth rate
  - Note any custom features or plugins

- [ ] **Plan Target Schema**
  - Map fields to ContextFrame schema
  - Design collection structure
  - Plan relationship types
  - Define custom metadata fields

- [ ] **Test Migration Process**
  - Start with small dataset
  - Validate all field mappings
  - Test search functionality
  - Benchmark performance

- [ ] **Execute Migration**
  - Use appropriate batch sizes
  - Implement checkpointing
  - Monitor resource usage
  - Validate incrementally

- [ ] **Post-Migration Tasks**
  - Run validation checks
  - Update application code
  - Configure access patterns
  - Set up monitoring

## Next Steps

1. **Choose your migration path** based on your current system
2. **Review the code examples** and adapt them to your needs
3. **Test with a small dataset** before full migration
4. **Refer to the [Data Import/Export Guide](data-import-export.md)** for additional options

For specific questions or complex migration scenarios, consult the [API Reference](../api/overview.md) or reach out to the community for support.