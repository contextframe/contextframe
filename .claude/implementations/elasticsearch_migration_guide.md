# Elasticsearch Document Store and Vector Capabilities Migration Guide

## Table of Contents
1. [Elasticsearch Dense Vector Field Type and KNN Search](#1-elasticsearch-dense-vector-field-type-and-knn-search)
2. [Exporting Documents with Embeddings](#2-exporting-documents-with-embeddings)
3. [Scroll API and search_after for Pagination](#3-scroll-api-and-search_after-for-pagination)
4. [Bulk Export Methods and Tools](#4-bulk-export-methods-and-tools)
5. [Index Mappings and Document Structure](#5-index-mappings-and-document-structure)
6. [Authentication and Connection Setup](#6-authentication-and-connection-setup)
7. [Performance Considerations](#7-performance-considerations)
8. [Code Examples](#8-code-examples)

## 1. Elasticsearch Dense Vector Field Type and KNN Search

### Dense Vector Field Type
The `dense_vector` field type stores dense vectors of numeric values, primarily used for k-nearest neighbor (kNN) search.

**Key Characteristics:**
- Stores arrays of numeric values (float by default, but supports byte, float, and bit)
- Single-valued (cannot store multiple vectors in one field)
- Does not support aggregations or sorting
- Dimensions can range from 1 to 4096 (with 2048 being common for many embedding models)

**Example Mapping:**
```json
PUT my-index
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 1536,  // OpenAI text-embedding-ada-002 dimensions
        "similarity": "cosine",
        "index": true
      },
      "text": {
        "type": "text"
      }
    }
  }
}
```

### KNN Search Methods

**1. Approximate KNN (Recommended)**
- Uses HNSW algorithm for fast retrieval
- Lower latency, suitable for production
- Slight accuracy trade-off for speed

```json
POST my-index/_search
{
  "knn": {
    "field": "my_vector",
    "query_vector": [0.3, 0.1, 1.2, ...],
    "k": 10,
    "num_candidates": 100
  }
}
```

**2. Exact KNN (Brute Force)**
- Uses `script_score` query
- 100% accurate but slower
- Suitable for small datasets or filtered searches

```json
POST my-index/_search
{
  "query": {
    "script_score": {
      "query": {"match_all": {}},
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'my_vector') + 1.0",
        "params": {
          "query_vector": [0.3, 0.1, 1.2, ...]
        }
      }
    }
  }
}
```

### Similarity Metrics
- `cosine` (default): Measures angle between vectors
- `dot_product`: Raw dot product (requires normalized vectors)
- `l2_norm`: Euclidean distance

## 2. Exporting Documents with Embeddings

### Using Python elasticsearch-py Client

```python
from elasticsearch import Elasticsearch, helpers
import json

# Connect to Elasticsearch
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('username', 'password')
)

# Export with helpers.scan for efficient scrolling
def export_with_embeddings(index_name, output_file):
    # Define query to get documents with embeddings
    query = {
        "query": {"match_all": {}},
        "_source": ["text", "embedding", "metadata"]  # Specify fields
    }
    
    # Use scan helper for efficient export
    with open(output_file, 'w') as f:
        for doc in helpers.scan(es, 
                               index=index_name, 
                               query=query,
                               size=1000,
                               scroll='5m'):
            # Write as newline-delimited JSON
            f.write(json.dumps(doc['_source']) + '\n')
```

### Using Point in Time (PIT) API (Recommended for ES 7.10+)

```python
def export_with_pit(index_name, output_file):
    # Create a point in time
    pit = es.open_point_in_time(index=index_name, keep_alive='5m')
    pit_id = pit['id']
    
    # Initial search
    query = {
        "size": 10000,
        "query": {"match_all": {}},
        "pit": {
            "id": pit_id,
            "keep_alive": "5m"
        },
        "sort": [{"_doc": {"order": "asc"}}]
    }
    
    with open(output_file, 'w') as f:
        while True:
            response = es.search(body=query)
            hits = response['hits']['hits']
            
            if not hits:
                break
                
            for hit in hits:
                f.write(json.dumps(hit['_source']) + '\n')
            
            # Update search_after for next batch
            query['search_after'] = hits[-1]['sort']
    
    # Clean up PIT
    es.close_point_in_time(body={"id": pit_id})
```

## 3. Scroll API and search_after for Pagination

### Scroll API (Legacy, still supported)
```python
# Initialize scroll
response = es.search(
    index='my-index',
    scroll='2m',
    size=1000,
    body={
        "query": {"match_all": {}}
    }
)

scroll_id = response['_scroll_id']
scroll_size = response['hits']['total']['value']

# Retrieve batches
while len(response['hits']['hits']):
    # Process current batch
    for hit in response['hits']['hits']:
        process_document(hit)
    
    # Get next batch
    response = es.scroll(scroll_id=scroll_id, scroll='2m')

# Clear scroll
es.clear_scroll(scroll_id=scroll_id)
```

### search_after (Recommended)
```python
# First request
response = es.search(
    index='my-index',
    size=1000,
    body={
        "query": {"match_all": {}},
        "sort": [
            {"_doc": {"order": "asc"}}
        ]
    }
)

# Subsequent requests
while response['hits']['hits']:
    last_hit_sort = response['hits']['hits'][-1]['sort']
    
    response = es.search(
        index='my-index',
        size=1000,
        body={
            "query": {"match_all": {}},
            "sort": [{"_doc": {"order": "asc"}}],
            "search_after": last_hit_sort
        }
    )
```

## 4. Bulk Export Methods and Tools

### 1. elasticsearch-dump (Node.js)
```bash
# Install
npm install -g elasticsearch-dump

# Export with authentication
elasticdump \
  --input=https://username:password@localhost:9200/my-index \
  --output=my-index-export.json \
  --type=data \
  --limit=10000
```

### 2. esdump (Go - High Performance)
```bash
# Install
go install github.com/hchargois/esdump@latest

# Export with fields selection
esdump https://localhost:9200 my-index \
  --fields id,text,embedding \
  --scroll-size 5000 \
  > export.jsonl
```

### 3. Python elasticdump
```python
# Using py-elasticdump with slicing for performance
python elasticdump.py \
  --host http://localhost:9200 \
  --index my-index \
  --slices 10 \
  --size 5000 \
  --username elastic \
  --password password
```

### 4. Snapshot and Restore (Recommended for Large Datasets)
```bash
# Create repository
PUT _snapshot/my_backup
{
  "type": "fs",
  "settings": {
    "location": "/mount/backups/my_backup"
  }
}

# Create snapshot
PUT _snapshot/my_backup/snapshot_1?wait_for_completion=true
{
  "indices": "my-index-*",
  "include_global_state": false
}

# Restore to another cluster
POST _snapshot/my_backup/snapshot_1/_restore
{
  "indices": "my-index-*"
}
```

## 5. Index Mappings and Document Structure

### Retrieving Index Mappings
```python
# Get mapping
mapping = es.indices.get_mapping(index='my-index')

# Get settings
settings = es.indices.get_settings(index='my-index')

# Export both for recreation
export_config = {
    'mappings': mapping['my-index']['mappings'],
    'settings': settings['my-index']['settings']
}
```

### Common Vector Search Index Structure
```json
{
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "text": {"type": "text"},
      "title": {"type": "text"},
      "embedding": {
        "type": "dense_vector",
        "dims": 1536,
        "index": true,
        "similarity": "cosine"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "source": {"type": "keyword"},
          "timestamp": {"type": "date"},
          "category": {"type": "keyword"}
        }
      }
    }
  }
}
```

## 6. Authentication and Connection Setup

### Basic Authentication
```python
from elasticsearch import Elasticsearch

# Basic auth
es = Elasticsearch(
    ['https://localhost:9200'],
    basic_auth=('elastic', 'password'),
    verify_certs=True,
    ca_certs='/path/to/ca.crt'
)
```

### API Key Authentication
```python
# Generate API key
api_key_response = es.security.create_api_key(
    body={
        "name": "export-api-key",
        "role_descriptors": {
            "export_role": {
                "indices": [{
                    "names": ["my-index-*"],
                    "privileges": ["read"]
                }]
            }
        }
    }
)

# Use API key
es = Elasticsearch(
    ['https://localhost:9200'],
    api_key=(api_key_response['id'], api_key_response['api_key'])
)
```

### Cloud ID (Elastic Cloud)
```python
es = Elasticsearch(
    cloud_id='deployment-name:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ...',
    basic_auth=('elastic', 'password')
)
```

## 7. Performance Considerations

### 1. Sliced Scroll for Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
import threading

def export_slice(slice_id, max_slices):
    query = {
        "slice": {
            "id": slice_id,
            "max": max_slices
        },
        "query": {"match_all": {}}
    }
    
    # Export logic for this slice
    filename = f"export_slice_{slice_id}.jsonl"
    # ... export code ...

# Parallel export with 5 slices
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for i in range(5):
        future = executor.submit(export_slice, i, 5)
        futures.append(future)
```

### 2. Batch Size Optimization
- Start with 1000-5000 documents per batch
- Adjust based on document size and network capacity
- Monitor scroll context memory usage

### 3. Network Optimization
```python
# Enable HTTP compression
es = Elasticsearch(
    ['http://localhost:9200'],
    http_compress=True  # Reduces network traffic
)
```

### 4. Memory Management
- Use streaming/iterative approaches
- Avoid loading entire dataset into memory
- Clear scroll contexts after use

### 5. Performance Benchmarks
- **esdump (Go)**: Up to 1M docs/minute on single node
- **elasticsearch-dump**: 100-500K docs/minute
- **Python with helpers.scan**: 50-200K docs/minute
- **Snapshot/Restore**: Fastest for full index migration

## 8. Code Examples

### Complete Export Script with Vectors
```python
import json
import logging
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from typing import Dict, List, Optional

class ElasticsearchExporter:
    def __init__(self, hosts: List[str], auth: tuple, verify_certs: bool = True):
        self.es = Elasticsearch(
            hosts,
            basic_auth=auth,
            verify_certs=verify_certs,
            http_compress=True
        )
        self.logger = logging.getLogger(__name__)
    
    def export_with_vectors(self, 
                          index: str, 
                          output_file: str,
                          vector_field: str = 'embedding',
                          batch_size: int = 5000,
                          query: Optional[Dict] = None) -> int:
        """
        Export documents with embeddings from Elasticsearch
        
        Args:
            index: Index name or pattern
            output_file: Output file path
            vector_field: Name of the vector field
            batch_size: Number of documents per batch
            query: Optional query to filter documents
        
        Returns:
            Number of documents exported
        """
        if query is None:
            query = {"match_all": {}}
        
        # Ensure vector field is included
        body = {
            "query": query,
            "_source": True  # Get all fields
        }
        
        count = 0
        start_time = datetime.now()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Use helpers.scan for efficient scrolling
                for doc in helpers.scan(
                    self.es,
                    index=index,
                    query=body,
                    size=batch_size,
                    scroll='5m',
                    raise_on_error=False
                ):
                    # Include document metadata
                    export_doc = {
                        "_id": doc['_id'],
                        "_index": doc['_index'],
                        "_source": doc['_source']
                    }
                    
                    # Verify vector field exists
                    if vector_field in doc['_source']:
                        f.write(json.dumps(export_doc) + '\n')
                        count += 1
                        
                        if count % 10000 == 0:
                            elapsed = (datetime.now() - start_time).seconds
                            rate = count / elapsed if elapsed > 0 else 0
                            self.logger.info(
                                f"Exported {count} documents "
                                f"({rate:.0f} docs/sec)"
                            )
                    else:
                        self.logger.warning(
                            f"Document {doc['_id']} missing vector field"
                        )
            
            elapsed = (datetime.now() - start_time).seconds
            self.logger.info(
                f"Export completed: {count} documents in {elapsed}s "
                f"({count/elapsed if elapsed > 0 else 0:.0f} docs/sec)"
            )
            
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            raise
        
        return count
    
    def verify_vector_field(self, index: str, vector_field: str) -> Dict:
        """Verify vector field configuration"""
        mapping = self.es.indices.get_mapping(index=index)
        
        for idx, idx_mapping in mapping.items():
            properties = idx_mapping['mappings']['properties']
            if vector_field in properties:
                field_config = properties[vector_field]
                if field_config['type'] == 'dense_vector':
                    return {
                        'exists': True,
                        'dims': field_config.get('dims', 'dynamic'),
                        'similarity': field_config.get('similarity', 'cosine'),
                        'index': field_config.get('index', True)
                    }
        
        return {'exists': False}

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    exporter = ElasticsearchExporter(
        hosts=['https://localhost:9200'],
        auth=('elastic', 'password'),
        verify_certs=True
    )
    
    # Verify vector field exists
    vector_info = exporter.verify_vector_field('my-index', 'embedding')
    if vector_info['exists']:
        print(f"Vector field found: {vector_info}")
        
        # Export documents with vectors
        doc_count = exporter.export_with_vectors(
            index='my-index',
            output_file='vectors_export.jsonl',
            vector_field='embedding',
            batch_size=5000
        )
        
        print(f"Successfully exported {doc_count} documents")
    else:
        print("Vector field not found in index")
```

### Import to ContextFrame Example
```python
import json
from contextframe import FrameDataset, FrameRecord
import numpy as np

def import_elasticsearch_export(export_file: str, dataset_path: str):
    """Import Elasticsearch export into ContextFrame"""
    
    # Create or open dataset
    dataset = FrameDataset.create(dataset_path)
    
    with open(export_file, 'r') as f:
        for line in f:
            doc = json.loads(line)
            source = doc['_source']
            
            # Create FrameRecord
            record = FrameRecord(
                record_id=doc['_id'],
                content=source.get('text', ''),
                content_type='text/plain',
                embedding=np.array(source.get('embedding', [])),
                metadata={
                    'original_index': doc['_index'],
                    'title': source.get('title', ''),
                    **source.get('metadata', {})
                }
            )
            
            # Add to dataset
            dataset.add_records([record])
    
    print(f"Imported {len(dataset)} records")
```

## Best Practices for Migration

1. **Pre-migration Checks**
   - Verify source and target cluster versions
   - Calculate required storage space
   - Test with small sample first

2. **Data Validation**
   - Compare document counts
   - Verify vector dimensions match
   - Sample and test vector similarity searches

3. **Incremental Migration**
   - Use time-based queries for large datasets
   - Implement checkpointing for resume capability
   - Monitor progress and performance

4. **Post-migration Verification**
   - Run test queries on both clusters
   - Compare search results
   - Verify all indices and mappings

5. **Security Considerations**
   - Use encrypted connections (HTTPS)
   - Implement least-privilege access
   - Rotate credentials after migration