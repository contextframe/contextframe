# Migrating from Vector Databases

This guide helps you migrate from popular vector databases to ContextFrame. Whether you're using Pinecone, Weaviate, Qdrant, Chroma, or Milvus, we'll show you how to seamlessly transition while preserving your embeddings, metadata, and search capabilities.

## Why Migrate from Vector Databases?

While vector databases excel at similarity search, ContextFrame provides:

- **Unified Storage**: Documents, embeddings, and metadata in one system
- **Richer Relationships**: Native support for hierarchical and graph-like structures
- **Advanced Querying**: Combine vector, full-text, and SQL-style queries
- **Better Economics**: Lower costs with efficient columnar storage
- **Version Control**: Built-in document history and change tracking

## Migration Strategies by Platform

### Pinecone Migration

#### Export from Pinecone

Pinecone doesn't provide a direct "export all" endpoint, so we need to use iterative approaches:

```python
import pinecone
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import numpy as np

def export_from_pinecone(api_key, environment, index_name, namespace=None):
    """Export vectors and metadata from Pinecone using query-based iteration."""
    
    # Initialize Pinecone
    pinecone.init(api_key=api_key, environment=environment)
    index = pinecone.Index(index_name)
    
    # Get index stats to know total vectors
    stats = index.describe_index_stats()
    dimension = stats.dimension
    total_vectors = stats.namespaces.get(namespace or '', {}).get('vector_count', 0)
    
    print(f"Exporting {total_vectors} vectors from Pinecone index '{index_name}'")
    
    exported_data = []
    exported_ids = set()
    
    # Query in batches (max 10,000 per query)
    while len(exported_ids) < total_vectors:
        # Use random vector to get diverse results
        random_vector = np.random.rand(dimension).tolist()
        
        results = index.query(
            vector=random_vector,
            top_k=10000,  # Maximum allowed
            namespace=namespace,
            include_values=True,
            include_metadata=True
        )
        
        new_items = 0
        for match in results.matches:
            if match.id not in exported_ids:
                exported_data.append({
                    'id': match.id,
                    'values': match.values,
                    'metadata': match.metadata or {}
                })
                exported_ids.add(match.id)
                new_items += 1
        
        print(f"Exported {len(exported_ids)}/{total_vectors} vectors")
        
        # Break if no new vectors found
        if new_items == 0:
            break
    
    return exported_data, dimension
```

#### Import to ContextFrame

```python
def migrate_pinecone_to_contextframe(pinecone_data, dimension, dataset_path="migrated_data.lance"):
    """Migrate Pinecone data to ContextFrame."""
    
    # Create or open dataset
    dataset = FrameDataset.create(dataset_path)
    
    records = []
    for item in pinecone_data:
        # Create metadata from Pinecone metadata
        metadata = create_metadata(
            title=item['metadata'].get('title', f"Document {item['id']}"),
            source="pinecone_migration",
            original_id=item['id'],
            **item['metadata']  # Preserve all original metadata
        )
        
        # Extract text content if available
        text_content = item['metadata'].get('text', item['metadata'].get('content', ''))
        
        # Create record with existing embedding
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=np.array(item['values'])  # Use existing embedding
        )
        
        records.append(record)
    
    # Batch import without regenerating embeddings
    dataset.add_many(records, generate_embeddings=False)
    
    print(f"Successfully migrated {len(records)} vectors to ContextFrame")
    return dataset

# Full migration workflow
api_key = "your-pinecone-api-key"
environment = "us-west1-gcp"
index_name = "my-index"

pinecone_data, dimension = export_from_pinecone(api_key, environment, index_name)
dataset = migrate_pinecone_to_contextframe(pinecone_data, dimension)
```

### Weaviate Migration

#### Export from Weaviate

Weaviate provides cursor-based pagination for efficient export:

```python
import weaviate
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import numpy as np

def export_from_weaviate(client, class_name, batch_size=100):
    """Export objects and vectors from Weaviate using cursor pagination."""
    
    exported_data = []
    cursor = None
    
    print(f"Exporting data from Weaviate class '{class_name}'")
    
    while True:
        # Build query with cursor
        query = (
            client.query
            .get(class_name)
            .with_additional(["id", "vector"])
            .with_limit(batch_size)
        )
        
        if cursor:
            query = query.with_after(cursor)
        
        result = query.do()
        
        # Check if we have results
        if not result['data']['Get'][class_name]:
            break
        
        # Process batch
        for obj in result['data']['Get'][class_name]:
            exported_data.append({
                'id': obj['_additional']['id'],
                'vector': obj['_additional']['vector'],
                'properties': {k: v for k, v in obj.items() 
                             if not k.startswith('_additional')}
            })
        
        print(f"Exported {len(exported_data)} objects")
        
        # Update cursor for next batch
        cursor = result['data']['Get'][class_name][-1]['_additional']['id']
        
        # Check if we've reached the end
        if len(result['data']['Get'][class_name]) < batch_size:
            break
    
    return exported_data

# For Weaviate v4 client
def export_from_weaviate_v4(client, collection_name):
    """Export using Weaviate v4 client iterator."""
    collection = client.collections.get(collection_name)
    
    exported_data = []
    for item in collection.iterator(include_vector=True):
        exported_data.append({
            'id': str(item.uuid),
            'vector': item.vector,
            'properties': item.properties
        })
    
    return exported_data
```

#### Import with Schema Mapping

```python
def migrate_weaviate_to_contextframe(weaviate_data, dataset_path="migrated_data.lance"):
    """Migrate Weaviate data with intelligent schema mapping."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Define common schema mappings
    schema_mapping = {
        'title': 'title',
        'content': 'text_content',
        'text': 'text_content',
        'author': 'author',
        'publicationDate': 'published_date',
        'publishedDate': 'published_date',
        'category': 'category',
        'tags': 'tags',
        'url': 'source_url',
        'source': 'source'
    }
    
    records = []
    for item in weaviate_data:
        # Map Weaviate properties to ContextFrame metadata
        mapped_metadata = {}
        unmapped_fields = {}
        
        for weaviate_field, value in item['properties'].items():
            if weaviate_field in schema_mapping:
                mapped_metadata[schema_mapping[weaviate_field]] = value
            else:
                unmapped_fields[weaviate_field] = value
        
        # Create metadata
        metadata = create_metadata(
            source="weaviate_migration",
            original_id=item['id'],
            **mapped_metadata,
            **unmapped_fields  # Add unmapped fields as custom metadata
        )
        
        # Extract text content
        text_content = item['properties'].get('content', 
                      item['properties'].get('text', 
                      item['properties'].get('description', '')))
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=np.array(item['vector'])
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=False)
    
    print(f"Migrated {len(records)} objects from Weaviate")
    return dataset
```

### Qdrant Migration

#### Export from Qdrant

Qdrant provides an efficient scroll API for data export:

```python
from qdrant_client import QdrantClient
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import numpy as np

def export_from_qdrant(client, collection_name, batch_size=1000):
    """Export vectors and payloads from Qdrant using scroll API."""
    
    exported_data = []
    offset = None
    
    print(f"Exporting data from Qdrant collection '{collection_name}'")
    
    while True:
        # Scroll through collection
        records, next_offset = client.scroll(
            collection_name=collection_name,
            offset=offset,
            limit=batch_size,
            with_payload=True,
            with_vectors=True,
            consistency="all"  # Ensure consistent reads
        )
        
        # Process batch
        for record in records:
            # Handle different vector formats
            if hasattr(record.vector, 'tolist'):
                vector = record.vector.tolist()
            elif isinstance(record.vector, dict):
                # Named vectors
                vector = record.vector
            else:
                vector = record.vector
            
            exported_data.append({
                'id': str(record.id),
                'vector': vector,
                'payload': record.payload or {}
            })
        
        print(f"Exported {len(exported_data)} points")
        
        # Check if we've reached the end
        if next_offset is None:
            break
            
        offset = next_offset
    
    return exported_data
```

#### Import with Named Vectors Support

```python
def migrate_qdrant_to_contextframe(qdrant_data, dataset_path="migrated_data.lance"):
    """Migrate Qdrant data supporting both single and named vectors."""
    
    dataset = FrameDataset.create(dataset_path)
    
    records = []
    for item in qdrant_data:
        # Create metadata from payload
        metadata = create_metadata(
            title=item['payload'].get('title', f"Document {item['id']}"),
            source="qdrant_migration",
            original_id=item['id'],
            **{k: v for k, v in item['payload'].items() 
               if k not in ['title', 'text', 'content']}
        )
        
        # Extract text content
        text_content = item['payload'].get('text', 
                      item['payload'].get('content', 
                      item['payload'].get('description', '')))
        
        # Handle vector formats
        if isinstance(item['vector'], dict):
            # Named vectors - use the first one or a specific one
            vector_name = list(item['vector'].keys())[0]
            embedding = np.array(item['vector'][vector_name])
            metadata.custom_metadata['vector_type'] = vector_name
        else:
            # Single vector
            embedding = np.array(item['vector'])
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=embedding
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=False)
    
    print(f"Migrated {len(records)} points from Qdrant")
    return dataset
```

### Chroma Migration

#### Export from Chroma

Chroma allows direct access to all data with pagination:

```python
import chromadb
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import numpy as np

def export_from_chroma(collection_name, persist_directory=None, batch_size=1000):
    """Export embeddings and metadata from Chroma."""
    
    # Initialize Chroma client
    if persist_directory:
        client = chromadb.PersistentClient(path=persist_directory)
    else:
        client = chromadb.Client()
    
    collection = client.get_collection(name=collection_name)
    
    # Get total count
    total_count = collection.count()
    print(f"Exporting {total_count} documents from Chroma collection '{collection_name}'")
    
    exported_data = []
    
    # Export in batches using pagination
    for offset in range(0, total_count, batch_size):
        batch = collection.get(
            offset=offset,
            limit=min(batch_size, total_count - offset),
            include=["embeddings", "metadatas", "documents"]
        )
        
        # Convert batch to records
        for i in range(len(batch["ids"])):
            exported_data.append({
                'id': batch["ids"][i],
                'embedding': batch["embeddings"][i] if batch["embeddings"] else None,
                'metadata': batch["metadatas"][i] if batch["metadatas"] else {},
                'document': batch["documents"][i] if batch["documents"] else None
            })
        
        print(f"Exported {len(exported_data)}/{total_count} documents")
    
    return exported_data
```

#### Import with Collection Preservation

```python
def migrate_chroma_to_contextframe(chroma_data, collection_name, 
                                  dataset_path="migrated_data.lance"):
    """Migrate Chroma collection preserving structure."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Create collection header for organization
    collection_metadata = create_metadata(
        title=f"Collection: {collection_name}",
        source="chroma_migration",
        collection_name=collection_name,
        item_count=len(chroma_data),
        migrated_date=datetime.now().isoformat()
    )
    
    collection_record = FrameRecord(
        text_content=f"Migrated collection from Chroma: {collection_name}",
        metadata=collection_metadata,
        unique_id=generate_uuid(),
        record_type="collection_header"
    )
    
    dataset.add(collection_record)
    
    # Add documents
    records = []
    for item in chroma_data:
        # Create metadata
        metadata = create_metadata(
            source="chroma_migration",
            original_id=item['id'],
            collection_id=collection_record.unique_id,
            **item['metadata']
        )
        
        # Use document text if available
        text_content = item['document'] or item['metadata'].get('text', '')
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=np.array(item['embedding']) if item['embedding'] else None,
            record_type="document"
        )
        
        # Add collection relationship
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=collection_record.unique_id,
                relationship_type="member_of"
            )
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=False)
    
    print(f"Migrated {len(records)} documents from Chroma")
    return dataset
```

### Milvus Migration

#### Export from Milvus

Milvus 2.3+ provides efficient query iterators:

```python
from pymilvus import connections, Collection, utility
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import numpy as np
import json

def export_from_milvus(host, port, collection_name, output_file=None):
    """Export vectors and metadata from Milvus using query iterator."""
    
    # Connect to Milvus
    connections.connect("default", host=host, port=port)
    
    # Check if collection exists
    if not utility.has_collection(collection_name):
        raise ValueError(f"Collection {collection_name} not found")
    
    collection = Collection(collection_name)
    collection.load()
    
    print(f"Exporting from Milvus collection '{collection_name}'")
    print(f"Total entities: {collection.num_entities}")
    
    # Get schema information
    schema_info = []
    for field in collection.schema.fields:
        field_info = {
            "name": field.name,
            "type": str(field.dtype),
            "is_primary": field.is_primary
        }
        if hasattr(field, 'dim'):
            field_info["dimension"] = field.dim
        schema_info.append(field_info)
    
    # Export data using iterator
    exported_data = []
    
    # For Milvus 2.3+
    iterator = collection.query_iterator(
        batch_size=1000,
        expr="",  # No filter - export all
        output_fields=["*"]  # Get all fields
    )
    
    batch_count = 0
    while True:
        batch = iterator.next()
        if not batch:
            iterator.close()
            break
        
        # Convert numpy arrays to lists for JSON serialization
        for entity in batch:
            for key, value in entity.items():
                if isinstance(value, np.ndarray):
                    entity[key] = value.tolist()
        
        exported_data.extend(batch)
        batch_count += 1
        
        if batch_count % 10 == 0:
            print(f"Exported {len(exported_data)} entities...")
    
    print(f"Export completed. Total entities: {len(exported_data)}")
    
    # Save to file if requested
    if output_file:
        export_package = {
            "schema": schema_info,
            "data": exported_data,
            "collection_name": collection_name,
            "total_entities": len(exported_data)
        }
        with open(output_file, 'w') as f:
            json.dump(export_package, f, indent=2)
    
    return exported_data, schema_info
```

#### Import with Schema Preservation

```python
def migrate_milvus_to_contextframe(milvus_data, schema_info, 
                                  collection_name, dataset_path="migrated_data.lance"):
    """Migrate Milvus data preserving schema information."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Find vector field from schema
    vector_field = None
    primary_field = None
    for field in schema_info:
        if field['type'] in ['DataType.FLOAT_VECTOR', 'FLOAT_VECTOR']:
            vector_field = field['name']
        if field.get('is_primary'):
            primary_field = field['name']
    
    if not vector_field:
        raise ValueError("No vector field found in schema")
    
    records = []
    for entity in milvus_data:
        # Extract primary key
        entity_id = entity.get(primary_field, generate_uuid())
        
        # Extract vector
        embedding = np.array(entity[vector_field])
        
        # Create metadata from all non-vector fields
        metadata_fields = {k: v for k, v in entity.items() 
                          if k != vector_field}
        
        metadata = create_metadata(
            source="milvus_migration",
            original_id=str(entity_id),
            collection_name=collection_name,
            **metadata_fields
        )
        
        # Extract text content if available
        text_content = ""
        text_fields = ['text', 'content', 'description', 'document']
        for field in text_fields:
            if field in entity:
                text_content = str(entity[field])
                break
        
        # Create record
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=embedding
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=False)
    
    print(f"Migrated {len(records)} entities from Milvus")
    return dataset
```

## Advanced Migration Patterns

### Incremental Migration with Verification

```python
def incremental_migration_with_verification(
    source_type, source_config, dataset_path, batch_size=1000):
    """Perform incremental migration with verification at each step."""
    
    dataset = FrameDataset.create(dataset_path)
    migration_log = []
    failed_items = []
    
    # Initialize source connection based on type
    if source_type == "pinecone":
        total_items = get_pinecone_count(source_config)
        export_func = export_pinecone_batch
    elif source_type == "weaviate":
        total_items = get_weaviate_count(source_config)
        export_func = export_weaviate_batch
    # ... other sources
    
    processed = 0
    
    while processed < total_items:
        try:
            # Export batch from source
            batch = export_func(source_config, offset=processed, limit=batch_size)
            
            # Transform to ContextFrame records
            records = transform_batch(batch, source_type)
            
            # Import to ContextFrame
            dataset.add_many(records, generate_embeddings=False)
            
            # Verify batch
            verification = verify_batch_migration(batch, dataset)
            
            migration_log.append({
                'batch': processed // batch_size,
                'items': len(batch),
                'success': verification['success'],
                'errors': verification.get('errors', [])
            })
            
            if not verification['success']:
                failed_items.extend(verification['failed_ids'])
            
            processed += len(batch)
            
            # Progress update
            progress = (processed / total_items) * 100
            print(f"Migration progress: {progress:.1f}%")
            
        except Exception as e:
            print(f"Error in batch starting at {processed}: {e}")
            migration_log.append({
                'batch': processed // batch_size,
                'error': str(e)
            })
            break
    
    # Generate report
    report = {
        'total_items': total_items,
        'successful_items': processed - len(failed_items),
        'failed_items': len(failed_items),
        'migration_log': migration_log
    }
    
    return dataset, report

def verify_batch_migration(source_batch, dataset):
    """Verify migrated batch integrity."""
    
    verification = {
        'success': True,
        'failed_ids': [],
        'errors': []
    }
    
    for item in source_batch:
        # Check if item exists in dataset
        results = dataset.filter({'metadata.original_id': str(item['id'])})
        
        if not results:
            verification['success'] = False
            verification['failed_ids'].append(item['id'])
            verification['errors'].append(f"Item {item['id']} not found")
            continue
        
        # Verify embedding similarity
        migrated_embedding = results[0].embedding
        source_embedding = np.array(item.get('vector', item.get('values', [])))
        
        if migrated_embedding is not None and len(source_embedding) > 0:
            # Calculate cosine similarity
            similarity = np.dot(migrated_embedding, source_embedding) / (
                np.linalg.norm(migrated_embedding) * np.linalg.norm(source_embedding)
            )
            
            if similarity < 0.99:  # Allow small numerical differences
                verification['errors'].append(
                    f"Embedding mismatch for {item['id']}: similarity={similarity:.4f}"
                )
    
    return verification
```

### Parallel Migration for Large Datasets

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

def parallel_vector_migration(source_type, source_config, dataset_path, 
                            num_workers=None, chunk_size=10000):
    """Migrate vectors using parallel processing for better performance."""
    
    if num_workers is None:
        num_workers = min(mp.cpu_count(), 8)  # Cap at 8 workers
    
    print(f"Starting parallel migration with {num_workers} workers")
    
    # Get total count and partition work
    if source_type == "qdrant":
        client = QdrantClient(**source_config)
        collection_info = client.get_collection(source_config['collection_name'])
        total_items = collection_info.points_count
    # ... handle other source types
    
    # Create work chunks
    chunks = []
    for i in range(0, total_items, chunk_size):
        chunks.append({
            'start': i,
            'end': min(i + chunk_size, total_items),
            'chunk_id': i // chunk_size
        })
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {}
        
        for chunk in chunks:
            future = executor.submit(
                process_migration_chunk,
                source_type,
                source_config,
                chunk,
                f"{dataset_path}_chunk_{chunk['chunk_id']}"
            )
            futures[future] = chunk
        
        # Track progress
        completed_chunks = 0
        for future in as_completed(futures):
            chunk = futures[future]
            try:
                result = future.result()
                completed_chunks += 1
                print(f"Completed chunk {chunk['chunk_id']} ({completed_chunks}/{len(chunks)})")
            except Exception as e:
                print(f"Error in chunk {chunk['chunk_id']}: {e}")
    
    # Merge all chunks into final dataset
    final_dataset = merge_dataset_chunks(dataset_path, len(chunks))
    
    return final_dataset

def process_migration_chunk(source_type, source_config, chunk, temp_path):
    """Process a single chunk of migration."""
    
    # Export data for this chunk
    if source_type == "qdrant":
        client = QdrantClient(**source_config)
        data = export_qdrant_range(client, source_config['collection_name'], 
                                  chunk['start'], chunk['end'])
    # ... handle other sources
    
    # Create temporary dataset
    temp_dataset = FrameDataset.create(temp_path)
    
    # Transform and import
    records = transform_batch(data, source_type)
    temp_dataset.add_many(records, generate_embeddings=False)
    
    return {'chunk_id': chunk['chunk_id'], 'count': len(records)}

def merge_dataset_chunks(base_path, num_chunks):
    """Merge temporary datasets into final dataset."""
    
    final_dataset = FrameDataset.create(base_path)
    
    for i in range(num_chunks):
        chunk_path = f"{base_path}_chunk_{i}"
        
        try:
            chunk_dataset = FrameDataset(chunk_path)
            
            # Copy all records
            for record in chunk_dataset.filter({}):
                final_dataset.add(record, generate_embedding=False)
            
            # Clean up temporary dataset
            import shutil
            shutil.rmtree(chunk_path)
            
        except Exception as e:
            print(f"Error merging chunk {i}: {e}")
    
    return final_dataset
```

### Search Quality Comparison

```python
def compare_search_quality(source_client, source_config, contextframe_dataset, 
                          test_queries, top_k=10):
    """Compare search results between source and migrated system."""
    
    comparison_results = []
    
    for query in test_queries:
        # Search in source system
        if source_config['type'] == 'pinecone':
            source_results = source_client.query(
                vector=query['vector'],
                top_k=top_k,
                namespace=source_config.get('namespace')
            ).matches
            source_ids = [r.id for r in source_results]
            
        elif source_config['type'] == 'weaviate':
            source_results = source_client.query.get(
                source_config['class_name']
            ).with_near_vector({
                'vector': query['vector']
            }).with_limit(top_k).do()
            source_ids = [r['_additional']['id'] for r in 
                         source_results['data']['Get'][source_config['class_name']]]
        # ... handle other sources
        
        # Search in ContextFrame
        frame_results = contextframe_dataset.search(
            query=query.get('text', ''),
            embedding=np.array(query['vector']),
            limit=top_k
        )
        
        frame_ids = [r.metadata.custom_metadata.get('original_id') 
                    for r in frame_results]
        
        # Calculate metrics
        source_set = set(source_ids)
        frame_set = set(frame_ids)
        
        overlap = len(source_set & frame_set)
        precision = overlap / len(frame_set) if frame_set else 0
        recall = overlap / len(source_set) if source_set else 0
        
        # Check order preservation (top-5)
        order_preserved = source_ids[:5] == frame_ids[:5]
        
        comparison_results.append({
            'query_id': query.get('id', 'unknown'),
            'source_results': len(source_ids),
            'frame_results': len(frame_ids),
            'overlap': overlap,
            'precision': precision,
            'recall': recall,
            'f1_score': 2 * (precision * recall) / (precision + recall) 
                       if (precision + recall) > 0 else 0,
            'order_preserved_top5': order_preserved
        })
    
    # Generate summary report
    avg_metrics = {
        'avg_precision': np.mean([r['precision'] for r in comparison_results]),
        'avg_recall': np.mean([r['recall'] for r in comparison_results]),
        'avg_f1': np.mean([r['f1_score'] for r in comparison_results]),
        'perfect_matches': sum(1 for r in comparison_results if r['f1_score'] == 1.0),
        'order_preserved_count': sum(1 for r in comparison_results 
                                   if r['order_preserved_top5'])
    }
    
    return {
        'summary': avg_metrics,
        'details': comparison_results
    }
```

## Multi-Source Consolidation

```python
def consolidate_multiple_vector_dbs(sources, dataset_path):
    """Consolidate multiple vector databases into a single ContextFrame dataset."""
    
    dataset = FrameDataset.create(dataset_path)
    source_collections = {}
    
    for source_name, source_config in sources.items():
        print(f"\nMigrating from {source_name}...")
        
        # Create source collection header
        collection_metadata = create_metadata(
            title=f"Source: {source_name}",
            source="multi_db_migration",
            source_type=source_config['type'],
            source_name=source_name,
            migrated_date=datetime.now().isoformat()
        )
        
        collection = FrameRecord(
            text_content=f"Documents from {source_name} ({source_config['type']})",
            metadata=collection_metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        dataset.add(collection)
        source_collections[source_name] = collection.unique_id
        
        # Export and migrate data based on source type
        if source_config['type'] == 'pinecone':
            data, dim = export_from_pinecone(
                source_config['api_key'],
                source_config['environment'],
                source_config['index_name']
            )
            
        elif source_config['type'] == 'weaviate':
            client = weaviate.Client(source_config['url'])
            data = export_from_weaviate(client, source_config['class_name'])
            
        elif source_config['type'] == 'qdrant':
            client = QdrantClient(
                host=source_config['host'],
                port=source_config['port']
            )
            data = export_from_qdrant(client, source_config['collection_name'])
            
        elif source_config['type'] == 'chroma':
            data = export_from_chroma(
                source_config['collection_name'],
                source_config.get('persist_directory')
            )
            
        elif source_config['type'] == 'milvus':
            data, schema = export_from_milvus(
                source_config['host'],
                source_config['port'],
                source_config['collection_name']
            )
        
        # Import data with source tracking
        migrate_with_source_tracking(
            data, dataset, source_name, 
            collection.unique_id, source_config['type']
        )
    
    print(f"\nConsolidation complete. Total sources: {len(sources)}")
    return dataset

def migrate_with_source_tracking(data, dataset, source_name, 
                               collection_id, source_type):
    """Migrate data while tracking its source."""
    
    records = []
    
    for item in data:
        # Create metadata with source information
        metadata = create_metadata(
            source=f"{source_type}_migration",
            source_name=source_name,
            collection_id=collection_id,
            migrated_date=datetime.now().isoformat()
        )
        
        # Extract common fields based on source type
        if source_type == 'pinecone':
            metadata.custom_metadata.update(item.get('metadata', {}))
            text_content = metadata.custom_metadata.get('text', '')
            embedding = np.array(item['values'])
            
        elif source_type == 'weaviate':
            metadata.custom_metadata.update(item.get('properties', {}))
            text_content = item['properties'].get('content', '')
            embedding = np.array(item['vector'])
        # ... handle other types
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=embedding
        )
        
        # Add collection relationship
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=collection_id,
                relationship_type="member_of"
            )
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=False)
    print(f"Migrated {len(records)} items from {source_name}")
```

## Performance Optimization Tips

### Memory-Efficient Streaming

```python
def stream_large_vector_db(source_config, dataset_path, buffer_size=5000):
    """Stream large vector databases without loading everything into memory."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Create appropriate streamer based on source
    if source_config['type'] == 'qdrant':
        streamer = QdrantStreamer(source_config)
    elif source_config['type'] == 'milvus':
        streamer = MilvusStreamer(source_config)
    # ... other streamers
    
    buffer = []
    total_processed = 0
    
    for item in streamer:
        # Transform item
        record = transform_to_frame_record(item, source_config['type'])
        buffer.append(record)
        
        # Flush buffer when full
        if len(buffer) >= buffer_size:
            dataset.add_many(buffer, generate_embeddings=False)
            total_processed += len(buffer)
            buffer = []
            
            print(f"Processed {total_processed} vectors...")
    
    # Flush remaining items
    if buffer:
        dataset.add_many(buffer, generate_embeddings=False)
        total_processed += len(buffer)
    
    print(f"Migration complete: {total_processed} vectors")
    return dataset

class QdrantStreamer:
    """Stream vectors from Qdrant without loading all into memory."""
    
    def __init__(self, config):
        self.client = QdrantClient(
            host=config['host'],
            port=config['port']
        )
        self.collection_name = config['collection_name']
        self.batch_size = config.get('batch_size', 1000)
    
    def __iter__(self):
        offset = None
        
        while True:
            records, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                offset=offset,
                limit=self.batch_size,
                with_payload=True,
                with_vectors=True
            )
            
            for record in records:
                yield {
                    'id': str(record.id),
                    'vector': record.vector,
                    'payload': record.payload
                }
            
            if next_offset is None:
                break
                
            offset = next_offset
```

## Troubleshooting Common Issues

### Embedding Dimension Mismatch

```python
def handle_dimension_mismatch(source_embeddings, target_dimension):
    """Handle cases where embedding dimensions don't match."""
    
    source_dim = len(source_embeddings[0])
    
    if source_dim == target_dimension:
        return source_embeddings
    
    if source_dim > target_dimension:
        # Use PCA for dimensionality reduction
        from sklearn.decomposition import PCA
        
        print(f"Reducing embeddings from {source_dim} to {target_dimension} dimensions")
        
        pca = PCA(n_components=target_dimension)
        reduced_embeddings = pca.fit_transform(source_embeddings)
        
        print(f"Variance preserved: {sum(pca.explained_variance_ratio_):.2%}")
        
        return reduced_embeddings
    
    else:
        # Pad with zeros for dimension increase
        print(f"Padding embeddings from {source_dim} to {target_dimension} dimensions")
        
        padded_embeddings = np.pad(
            source_embeddings,
            ((0, 0), (0, target_dimension - source_dim)),
            mode='constant'
        )
        
        return padded_embeddings
```

### Handling Missing or Corrupt Data

```python
def migrate_with_error_handling(source_data, dataset_path):
    """Migrate data with robust error handling."""
    
    dataset = FrameDataset.create(dataset_path)
    
    successful = 0
    failed = []
    
    for item in source_data:
        try:
            # Validate item
            if not item.get('id'):
                raise ValueError("Missing ID")
            
            if 'vector' not in item and 'values' not in item and 'embedding' not in item:
                raise ValueError("Missing vector data")
            
            # Extract vector
            vector = item.get('vector', item.get('values', item.get('embedding')))
            if isinstance(vector, list):
                vector = np.array(vector)
            
            # Validate vector
            if np.isnan(vector).any():
                raise ValueError("Vector contains NaN values")
            
            # Create record
            metadata = create_metadata(
                source="migration",
                original_id=str(item['id']),
                **item.get('metadata', {})
            )
            
            record = FrameRecord(
                text_content=item.get('text', ''),
                metadata=metadata,
                unique_id=generate_uuid(),
                embedding=vector
            )
            
            dataset.add(record, generate_embedding=False)
            successful += 1
            
        except Exception as e:
            failed.append({
                'id': item.get('id', 'unknown'),
                'error': str(e)
            })
    
    print(f"Migration complete: {successful} successful, {len(failed)} failed")
    
    if failed:
        # Save failed items for manual review
        import json
        with open('migration_errors.json', 'w') as f:
            json.dump(failed, f, indent=2)
    
    return dataset
```

## Post-Migration Steps

After successfully migrating your data:

### 1. Rebuild Indices
```python
# Optimize vector index for your data
dataset.create_index(
    column="embedding",
    config={
        'metric': 'cosine',
        'index_type': 'IVF_PQ' if dataset.count() > 100000 else 'FLAT'
    }
)
```

### 2. Verify Data Integrity
```python
# Run verification checks
def verify_migration(dataset, expected_count):
    actual_count = dataset.count()
    
    print(f"Expected: {expected_count}, Actual: {actual_count}")
    
    # Sample and verify random records
    sample_size = min(100, actual_count)
    sample = dataset.filter({}).limit(sample_size)
    
    issues = []
    for record in sample:
        if record.embedding is None:
            issues.append(f"Missing embedding: {record.unique_id}")
        if not record.text_content and not record.metadata.custom_metadata:
            issues.append(f"Empty record: {record.unique_id}")
    
    if issues:
        print(f"Found {len(issues)} issues in sample")
    else:
        print("Sample verification passed")
    
    return len(issues) == 0
```

### 3. Set Up Monitoring
```python
# Track search performance
def benchmark_search_performance(dataset, num_queries=100):
    import time
    
    # Generate random queries
    dimension = dataset.filter({}).limit(1)[0].embedding.shape[0]
    queries = [np.random.rand(dimension) for _ in range(num_queries)]
    
    start = time.time()
    for query in queries:
        dataset.search(embedding=query, limit=10)
    
    avg_time = (time.time() - start) / num_queries * 1000  # ms
    
    print(f"Average search time: {avg_time:.2f}ms")
    print(f"Queries per second: {1000/avg_time:.0f}")
```

## Next Steps

1. **Explore Advanced Features**: Leverage ContextFrame's relationships and metadata
2. **Optimize Performance**: Fine-tune indices and query parameters
3. **Enable Versioning**: Track document changes over time
4. **Implement Hybrid Search**: Combine vector and keyword search

For specific migration help, see our [Community Support](../community/support.md) or [API Reference](../api/overview.md).