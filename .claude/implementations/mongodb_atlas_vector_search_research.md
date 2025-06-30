# MongoDB Atlas Vector Search Research

## Table of Contents
1. [MongoDB Atlas Vector Search Features and Limitations](#mongodb-atlas-vector-search-features-and-limitations)
2. [Storing and Querying Vector Embeddings](#storing-and-querying-vector-embeddings)
3. [Export Methods Using PyMongo](#export-methods-using-pymongo)
4. [MongoDB Export Tools](#mongodb-export-tools)
5. [Document Structure with Embeddings](#document-structure-with-embeddings)
6. [Index Configuration for Vector Search](#index-configuration-for-vector-search)
7. [Authentication and Connection](#authentication-and-connection)
8. [Code Examples](#code-examples)

## 1. MongoDB Atlas Vector Search Features and Limitations

### Features
- **Native Vector Search**: Built directly into MongoDB Atlas, supporting semantic search alongside traditional queries
- **Algorithm**: Uses Hierarchical Navigable Small Worlds (HNSW) algorithm for approximate nearest neighbor (ANN) search
- **Version Requirements**: Requires MongoDB 6.0.11, 7.0.2, or later for ANN search; 6.0.16, 7.0.10, 7.3.2+ for exact nearest neighbor (ENN) search
- **Dimension Support**: Supports up to 8192 dimensions for vector embeddings
- **Similarity Functions**: Supports euclidean, cosine, and dotProduct similarity metrics
- **Data Types**: Supports BSON int32, int64, and double for vector values
- **Quantization**: Supports scalar (int8) and binary (1-bit) quantization for memory optimization
- **Integration**: Works with aggregation pipelines using `$vectorSearch` stage

### Limitations
- **Cluster Tiers**: 
  - M0 (free) clusters: Maximum 3 indexes (search or vector combined)
  - Flex clusters: Maximum 10 indexes
- **Not Supported**: Time series collections
- **Array Limitations**: Cannot index fields inside arrays of documents or embedded documents as knnVector type
- **Memory Limits**: Pipeline stages have 100MB memory limit by default (can use allowDiskUse)
- **Index Requirement**: Must create a vector search index before querying

## 2. Storing and Querying Vector Embeddings

### Storage Format
```python
# Document structure with embeddings
{
    "_id": ObjectId("..."),
    "title": "Document Title",
    "content": "Document content...",
    "metadata": {
        "category": "example",
        "tags": ["tag1", "tag2"]
    },
    "embedding": [0.123, -0.456, 0.789, ...],  # Vector as array of floats
    "created_at": datetime.now()
}
```

### Query Methods
```python
# Using $vectorSearch aggregation stage
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 150,  # Number of candidates to consider
            "limit": 10  # Number of results to return
        }
    },
    {
        "$project": {
            "_id": 1,
            "title": 1,
            "content": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]
```

## 3. Export Methods Using PyMongo

### Method 1: Cursor-based Export
```python
import pymongo
from pymongo import MongoClient
import json

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://username:password@cluster.mongodb.net/")
db = client["database_name"]
collection = db["collection_name"]

# Export with cursor
def export_with_cursor(output_file, batch_size=1000):
    with open(output_file, 'w') as f:
        cursor = collection.find({})
        
        for doc in cursor.batch_size(batch_size):
            # Convert ObjectId to string for JSON serialization
            doc['_id'] = str(doc['_id'])
            
            # Handle vector embeddings (already stored as lists)
            if 'embedding' in doc:
                # Embeddings are already in list format
                pass
                
            f.write(json.dumps(doc) + '\n')
```

### Method 2: Aggregation Pipeline Export
```python
def export_with_aggregation(output_file, filters=None):
    pipeline = []
    
    # Add match stage if filters provided
    if filters:
        pipeline.append({"$match": filters})
    
    # Add any transformations
    pipeline.append({
        "$project": {
            "_id": {"$toString": "$_id"},
            "title": 1,
            "content": 1,
            "embedding": 1,
            "metadata": 1
        }
    })
    
    # Execute aggregation
    with open(output_file, 'w') as f:
        for doc in collection.aggregate(pipeline, allowDiskUse=True):
            f.write(json.dumps(doc) + '\n')
```

### Method 3: Batch Export with Progress
```python
from tqdm import tqdm

def export_with_progress(output_file, batch_size=1000):
    total_docs = collection.count_documents({})
    
    with open(output_file, 'w') as f:
        with tqdm(total=total_docs, desc="Exporting documents") as pbar:
            cursor = collection.find({}).batch_size(batch_size)
            
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                f.write(json.dumps(doc) + '\n')
                pbar.update(1)
```

## 4. MongoDB Export Tools

### mongodump
```bash
# Basic mongodump for entire database
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/database" --out=dump/

# Export specific collection with query
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/database" \
          --collection=collection_name \
          --query='{"category": "example"}' \
          --out=dump/

# Export with authentication
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/database" \
          --authenticationDatabase=admin \
          --ssl
```

### mongoexport
```bash
# Export to JSON (one document per line)
mongoexport --uri="mongodb+srv://username:password@cluster.mongodb.net/database" \
            --collection=collection_name \
            --out=export.json

# Export to CSV (excluding embeddings due to array limitation)
mongoexport --uri="mongodb+srv://username:password@cluster.mongodb.net/database" \
            --collection=collection_name \
            --type=csv \
            --fields=_id,title,content,metadata.category \
            --out=export.csv

# Export with query
mongoexport --uri="mongodb+srv://username:password@cluster.mongodb.net/database" \
            --collection=collection_name \
            --query='{"metadata.category": "example"}' \
            --out=filtered_export.json
```

## 5. Document Structure with Embeddings

### Standard Structure
```python
document_schema = {
    "_id": ObjectId,
    "title": str,
    "content": str,
    "embedding": list,  # Vector embedding as array of floats
    "metadata": {
        "source": str,
        "category": str,
        "tags": list,
        "created_at": datetime,
        "updated_at": datetime
    },
    "search_metadata": {
        "indexed_at": datetime,
        "embedding_model": str,
        "embedding_dimensions": int
    }
}
```

### With Quantized Embeddings
```python
# Using BSON Binary subtype for quantized vectors
from bson.binary import Binary, BinaryVectorDtype

# For int8 quantization
quantized_doc = {
    "_id": ObjectId(),
    "title": "Document Title",
    "content": "Content...",
    "embedding": Binary(
        quantized_vector_bytes,
        subtype=BinaryVectorDtype.INT8_VECTOR
    ),
    "embedding_float32": original_embedding  # Optional: keep original
}
```

## 6. Index Configuration for Vector Search

### Basic Vector Index
```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

### Advanced Index with HNSW Parameters
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine",
        "numNeighbors": 50,
        "ef": 100
      },
      "metadata.category": {
        "type": "string"
      },
      "metadata.tags": {
        "type": "string"
      }
    }
  }
}
```

### Creating Index via PyMongo
```python
from pymongo.operations import SearchIndexModel

# Define the search index
search_index_model = SearchIndexModel(
    definition={
        "mappings": {
            "dynamic": True,
            "fields": {
                "embedding": {
                    "type": "knnVector",
                    "dimensions": 1536,
                    "similarity": "cosine"
                }
            }
        }
    },
    name="vector_index",
)

# Create the search index
collection.create_search_index(model=search_index_model)
```

## 7. Authentication and Connection

### Connection String Format
```python
# Standard connection string
uri = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"

# With specific auth database
uri = "mongodb+srv://username:password@cluster.mongodb.net/database?authSource=admin"

# With connection options
uri = "mongodb+srv://username:password@cluster.mongodb.net/?ssl=true&replicaSet=atlas-replica-set&authSource=admin"
```

### PyMongo Connection with Options
```python
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Basic connection
client = MongoClient(uri)

# With server API version
client = MongoClient(uri, server_api=ServerApi('1'))

# With connection pooling
client = MongoClient(
    uri,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)

# Test connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Store sensitive data in environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]
collection = db[MONGODB_COLLECTION]
```

## 8. Code Examples

### Complete Export Script with Vector Embeddings
```python
import pymongo
import json
import numpy as np
from datetime import datetime
from tqdm import tqdm
import argparse

class MongoDBVectorExporter:
    def __init__(self, connection_string, database, collection):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]
    
    def export_to_json(self, output_file, query=None, batch_size=1000):
        """Export collection with embeddings to JSON"""
        total = self.collection.count_documents(query or {})
        
        with open(output_file, 'w') as f:
            cursor = self.collection.find(query or {}).batch_size(batch_size)
            
            for doc in tqdm(cursor, total=total, desc="Exporting"):
                # Handle ObjectId
                doc['_id'] = str(doc['_id'])
                
                # Handle datetime objects
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                
                # Write as JSON line
                f.write(json.dumps(doc) + '\n')
    
    def export_embeddings_only(self, output_file, format='npy'):
        """Export only embeddings in optimized format"""
        embeddings = []
        ids = []
        
        for doc in tqdm(self.collection.find({"embedding": {"$exists": True}})):
            embeddings.append(doc['embedding'])
            ids.append(str(doc['_id']))
        
        if format == 'npy':
            np.save(output_file, np.array(embeddings))
            with open(output_file.replace('.npy', '_ids.json'), 'w') as f:
                json.dump(ids, f)
        elif format == 'json':
            with open(output_file, 'w') as f:
                json.dump({"ids": ids, "embeddings": embeddings}, f)
    
    def export_with_vector_search(self, query_vector, output_file, limit=100):
        """Export documents based on vector similarity"""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "title": 1,
                    "content": 1,
                    "embedding": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def close(self):
        self.client.close()

# Usage example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export MongoDB collection with embeddings')
    parser.add_argument('--uri', required=True, help='MongoDB connection URI')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--collection', required=True, help='Collection name')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--format', choices=['json', 'npy'], default='json')
    
    args = parser.parse_args()
    
    exporter = MongoDBVectorExporter(args.uri, args.database, args.collection)
    
    try:
        if args.format == 'json':
            exporter.export_to_json(args.output)
        else:
            exporter.export_embeddings_only(args.output, format='npy')
    finally:
        exporter.close()
```

### Vector Search Query Example
```python
import openai
from pymongo import MongoClient

class VectorSearchClient:
    def __init__(self, mongo_uri, database, collection):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.collection = self.db[collection]
    
    def search(self, query_text, limit=10):
        # Generate query embedding
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query_text
        )
        query_embedding = response['data'][0]['embedding']
        
        # Perform vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "title": 1,
                    "content": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "metadata": 1
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results
    
    def hybrid_search(self, query_text, filters, limit=10):
        """Combine vector search with metadata filtering"""
        # Generate embedding
        query_embedding = self._get_embedding(query_text)
        
        # Hybrid search pipeline
        pipeline = [
            {"$match": filters},  # Pre-filter
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            }
        ]
        
        return list(self.collection.aggregate(pipeline))
```

### Batch Import with Embeddings
```python
import openai
from pymongo import MongoClient
from typing import List, Dict
import time

class EmbeddingImporter:
    def __init__(self, mongo_uri, database, collection, embedding_model="text-embedding-3-small"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.embedding_model = embedding_model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        response = openai.Embedding.create(
            model=self.embedding_model,
            input=texts
        )
        return [item['embedding'] for item in response['data']]
    
    def import_documents(self, documents: List[Dict], batch_size=100):
        """Import documents with embeddings in batches"""
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Extract texts for embedding
            texts = [doc.get('content', doc.get('title', '')) for doc in batch]
            
            # Generate embeddings
            try:
                embeddings = self.generate_embeddings(texts)
                
                # Add embeddings to documents
                for doc, embedding in zip(batch, embeddings):
                    doc['embedding'] = embedding
                    doc['embedding_model'] = self.embedding_model
                    doc['embedded_at'] = datetime.now()
                
                # Insert batch
                self.collection.insert_many(batch)
                
                print(f"Imported batch {i//batch_size + 1}/{total_batches}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in batch {i//batch_size + 1}: {e}")
```

## Best Practices

1. **Connection Management**:
   - Use connection pooling for production applications
   - Implement retry logic for network failures
   - Close connections properly

2. **Export Optimization**:
   - Use batch_size for large collections
   - Implement pagination for web-based exports
   - Consider using projections to limit field selection

3. **Vector Storage**:
   - Store embedding model information with vectors
   - Consider quantization for large-scale deployments
   - Keep original vectors if using quantization

4. **Security**:
   - Never hardcode credentials
   - Use environment variables or secret management
   - Implement proper authentication and authorization

5. **Performance**:
   - Create appropriate indexes before querying
   - Use numCandidates parameter wisely (10x limit is common)
   - Monitor index build progress for large collections

This research provides a comprehensive overview of MongoDB Atlas Vector Search capabilities, export methods, and practical implementation examples for working with vector embeddings in MongoDB.