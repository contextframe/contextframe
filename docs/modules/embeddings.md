# Embeddings

ContextFrame provides comprehensive support for vector embeddings, enabling semantic search and similarity matching across your documents. This guide covers embedding generation, management, and search operations.

## Overview

Embeddings in ContextFrame:
- Convert text to high-dimensional vectors
- Enable semantic similarity search
- Support multiple embedding models
- Integrate with vector indices for fast retrieval
- Handle batch processing efficiently

## Supported Models

### OpenAI Models

```python
from contextframe.embed import embed_frames

# text-embedding-3-small (default)
docs = embed_frames(
    documents,
    model="text-embedding-3-small",
    embed_dim=1536
)

# text-embedding-3-large
docs = embed_frames(
    documents,
    model="text-embedding-3-large",
    embed_dim=3072
)

# Legacy model
docs = embed_frames(
    documents,
    model="text-embedding-ada-002",
    embed_dim=1536
)
```

### Model Comparison

| Model | Dimensions | Performance | Cost | Use Case |
|-------|------------|-------------|------|----------|
| text-embedding-3-small | 1536 | Fast | Low | General purpose |
| text-embedding-3-large | 3072 | High quality | Higher | Precision tasks |
| text-embedding-ada-002 | 1536 | Good | Medium | Legacy support |

### Custom Models

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class CustomEmbedder:
    """Custom embedding provider using sentence-transformers."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embed_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_documents(self, docs):
        """Embed a list of FrameRecords."""
        texts = [doc.text_content for doc in docs]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Add embeddings to documents
        for doc, embedding in zip(docs, embeddings):
            doc.vector = np.array(embedding, dtype=np.float32)
            doc.embed_dim = self.embed_dim
        
        return docs
```

## Generating Embeddings

### Basic Embedding

```python
from contextframe import FrameRecord
from contextframe.embed import embed_frames

# Single document
doc = FrameRecord.create(
    title="Machine Learning Guide",
    content="Introduction to neural networks and deep learning..."
)

# Generate embedding
embedded_docs = embed_frames([doc])
embedded_doc = embedded_docs[0]

print(f"Embedding shape: {embedded_doc.vector.shape}")
print(f"Embedding dimension: {embedded_doc.embed_dim}")
```

### Batch Processing

```python
# Batch embedding for efficiency
docs = [
    FrameRecord.create(title=f"Doc {i}", content=f"Content {i}...")
    for i in range(100)
]

# Process in batches
embedded_docs = embed_frames(
    docs,
    model="text-embedding-3-small",
    batch_size=50,  # Process 50 at a time
    show_progress=True
)

# Add to dataset
dataset.add_many(embedded_docs)
```

### Handling Large Datasets

```python
def embed_large_dataset(dataset, batch_size=100):
    """Embed documents in a large dataset efficiently."""
    from tqdm import tqdm
    
    total_docs = len(dataset)
    processed = 0
    
    # Process in chunks
    for batch in tqdm(dataset.to_batches(batch_size=batch_size)):
        # Convert to FrameRecords
        docs = [FrameRecord.from_arrow(row) for row in batch.to_pylist()]
        
        # Skip already embedded documents
        docs_to_embed = [doc for doc in docs if doc.vector is None]
        
        if docs_to_embed:
            # Generate embeddings
            embedded = embed_frames(docs_to_embed)
            
            # Update in dataset
            for doc in embedded:
                dataset.update_record(doc.uuid, doc)
        
        processed += len(docs)
        print(f"Processed {processed}/{total_docs} documents")
```

### Selective Embedding

```python
def selective_embed(docs, content_threshold=100):
    """Only embed documents meeting certain criteria."""
    docs_to_embed = []
    skipped = []
    
    for doc in docs:
        # Skip short documents
        if len(doc.text_content) < content_threshold:
            skipped.append(doc)
            continue
        
        # Skip certain types
        if doc.metadata.get('record_type') == 'collection_header':
            skipped.append(doc)
            continue
        
        # Skip if already has embedding
        if doc.vector is not None:
            skipped.append(doc)
            continue
        
        docs_to_embed.append(doc)
    
    # Embed selected documents
    if docs_to_embed:
        embedded = embed_frames(docs_to_embed)
        return embedded + skipped
    
    return skipped
```

## Content Preparation

### Text Preprocessing

```python
def prepare_text_for_embedding(text, max_length=8192):
    """Prepare text for embedding generation."""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Remove special characters that might affect embedding
    text = text.replace('\x00', '')  # Null bytes
    text = text.replace('\ufffd', '')  # Replacement character
    
    return text

def prepare_document_for_embedding(doc):
    """Prepare document content for embedding."""
    # Combine relevant fields
    parts = []
    
    # Title is important for context
    if doc.metadata.get('title'):
        parts.append(f"Title: {doc.metadata['title']}")
    
    # Add metadata context
    if doc.metadata.get('tags'):
        parts.append(f"Tags: {', '.join(doc.metadata['tags'])}")
    
    # Main content
    if doc.text_content:
        parts.append(doc.text_content)
    
    # Combine and prepare
    combined_text = '\n\n'.join(parts)
    return prepare_text_for_embedding(combined_text)
```

### Chunking Long Documents

```python
def chunk_document(doc, chunk_size=1000, overlap=200):
    """Split long documents into chunks for embedding."""
    text = doc.text_content
    chunks = []
    
    # Split into sentences
    sentences = text.split('. ')
    
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence.split())
        
        if current_size + sentence_size > chunk_size and current_chunk:
            # Create chunk
            chunk_text = '. '.join(current_chunk) + '.'
            chunk = FrameRecord.create(
                title=f"{doc.metadata['title']} - Chunk {len(chunks) + 1}",
                content=chunk_text,
                tags=doc.metadata.get('tags', []) + ['chunk'],
                custom_metadata={
                    'parent_document': doc.uuid,
                    'chunk_index': len(chunks),
                    'chunk_size': current_size
                }
            )
            chunks.append(chunk)
            
            # Start new chunk with overlap
            overlap_sentences = int(len(current_chunk) * (overlap / current_size))
            current_chunk = current_chunk[-overlap_sentences:]
            current_size = sum(len(s.split()) for s in current_chunk)
        
        current_chunk.append(sentence)
        current_size += sentence_size
    
    # Add final chunk
    if current_chunk:
        chunk_text = '. '.join(current_chunk) + '.'
        chunk = FrameRecord.create(
            title=f"{doc.metadata['title']} - Chunk {len(chunks) + 1}",
            content=chunk_text,
            tags=doc.metadata.get('tags', []) + ['chunk'],
            custom_metadata={
                'parent_document': doc.uuid,
                'chunk_index': len(chunks),
                'chunk_size': current_size
            }
        )
        chunks.append(chunk)
    
    return chunks
```

## Vector Search

### Basic KNN Search

```python
# Generate query embedding
query = "How to implement authentication in Python?"
query_embedding = generate_embedding(query)  # Your embedding function

# Search for similar documents
results = dataset.knn_search(
    query_embedding,
    k=10  # Return top 10 results
)

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"Score: {1 - result['_distance']:.4f}")  # Convert distance to similarity
    print(f"Content: {result['text_content'][:200]}...")
    print("---")
```

### Filtered Vector Search

```python
# Search with metadata filters
results = dataset.knn_search(
    query_embedding,
    k=10,
    filter="status = 'published' AND tags.contains('python')"
)

# Complex filtering
results = dataset.knn_search(
    query_embedding,
    k=20,
    filter="""
    record_type = 'document' 
    AND created_at > '2023-01-01'
    AND (author = 'Expert' OR tags.contains('verified'))
    """
)
```

### Similarity Thresholds

```python
def search_with_threshold(dataset, query_embedding, threshold=0.8, max_results=50):
    """Return only results above similarity threshold."""
    # Get more results than needed
    results = dataset.knn_search(query_embedding, k=max_results)
    
    # Filter by similarity threshold
    filtered_results = []
    for result in results:
        # Convert distance to similarity (for cosine distance)
        similarity = 1 - result['_distance']
        
        if similarity >= threshold:
            result['similarity'] = similarity
            filtered_results.append(result)
        else:
            # Results are ordered, so we can break early
            break
    
    return filtered_results
```

## Similarity Operations

### Document Similarity

```python
def find_similar_documents(dataset, doc_uuid, k=10):
    """Find documents similar to a given document."""
    # Get the document
    doc = dataset.get(doc_uuid)
    
    if doc.vector is None:
        raise ValueError("Document has no embedding")
    
    # Search for similar (excluding self)
    results = dataset.knn_search(doc.vector, k=k+1)
    
    # Remove self from results
    similar = [r for r in results if r['uuid'] != doc_uuid]
    
    return similar[:k]

def find_duplicates(dataset, threshold=0.95):
    """Find potential duplicate documents."""
    duplicates = []
    
    # Get all documents with embeddings
    docs = dataset.scanner(
        filter="embedding IS NOT NULL",
        columns=['uuid', 'title', 'embedding']
    ).to_table().to_pylist()
    
    # Compare all pairs (expensive for large datasets!)
    for i, doc1 in enumerate(docs):
        for doc2 in docs[i+1:]:
            similarity = cosine_similarity(
                np.array(doc1['embedding']),
                np.array(doc2['embedding'])
            )
            
            if similarity >= threshold:
                duplicates.append({
                    'doc1': doc1['uuid'],
                    'doc2': doc2['uuid'],
                    'title1': doc1['title'],
                    'title2': doc2['title'],
                    'similarity': similarity
                })
    
    return duplicates
```

### Clustering

```python
from sklearn.cluster import KMeans
import numpy as np

def cluster_documents(dataset, n_clusters=10):
    """Cluster documents based on embeddings."""
    # Get all embeddings
    embeddings = []
    uuids = []
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            if row.get('embedding'):
                embeddings.append(row['embedding'])
                uuids.append(row['uuid'])
    
    # Convert to numpy array
    X = np.array(embeddings)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)
    
    # Create cluster mapping
    cluster_map = {}
    for uuid, cluster_id in zip(uuids, clusters):
        if cluster_id not in cluster_map:
            cluster_map[cluster_id] = []
        cluster_map[cluster_id].append(uuid)
    
    # Find cluster centers (most representative documents)
    cluster_centers = {}
    for cluster_id, cluster_uuids in cluster_map.items():
        # Find document closest to cluster center
        center = kmeans.cluster_centers_[cluster_id]
        
        min_distance = float('inf')
        representative_uuid = None
        
        for uuid in cluster_uuids:
            doc = dataset.get(uuid)
            distance = np.linalg.norm(doc.vector - center)
            if distance < min_distance:
                min_distance = distance
                representative_uuid = uuid
        
        cluster_centers[cluster_id] = representative_uuid
    
    return cluster_map, cluster_centers
```

## Index Management

### Creating Indices

```python
# Calculate optimal partitions
num_docs = len(dataset)
num_partitions = int(np.sqrt(num_docs))  # Square root heuristic

# Create IVF_PQ index
dataset.create_vector_index(
    column="embedding",
    index_type="IVF_PQ",
    num_partitions=num_partitions,
    num_sub_quantizers=16,
    metric_type="cosine"
)

# For smaller datasets, use IVF_FLAT
if num_docs < 100000:
    dataset.create_vector_index(
        column="embedding",
        index_type="IVF_FLAT",
        num_partitions=min(num_partitions, 100),
        metric_type="cosine"
    )
```

### Index Performance

```python
import time

def benchmark_vector_search(dataset, num_queries=100):
    """Benchmark vector search performance."""
    # Generate random query vectors
    embed_dim = 1536
    queries = [np.random.randn(embed_dim).astype(np.float32) 
               for _ in range(num_queries)]
    
    # Without index
    start = time.time()
    for query in queries:
        results = dataset.knn_search(query, k=10)
    without_index = time.time() - start
    
    # Create index
    dataset.create_vector_index(
        num_partitions=int(np.sqrt(len(dataset)))
    )
    
    # With index
    start = time.time()
    for query in queries:
        results = dataset.knn_search(query, k=10)
    with_index = time.time() - start
    
    print(f"Without index: {without_index:.2f}s ({without_index/num_queries*1000:.2f}ms per query)")
    print(f"With index: {with_index:.2f}s ({with_index/num_queries*1000:.2f}ms per query)")
    print(f"Speedup: {without_index/with_index:.2f}x")
```

## Hybrid Search

### Combining Text and Vector Search

```python
def hybrid_search(dataset, query_text, alpha=0.7):
    """
    Combine text and vector search results.
    
    Args:
        alpha: Weight for text search (0-1)
               0 = pure vector search
               1 = pure text search
    """
    # Generate query embedding
    query_embedding = generate_embedding(query_text)
    
    # Perform both searches
    text_results = dataset.full_text_search(query_text, limit=50)
    vector_results = dataset.knn_search(query_embedding, k=50)
    
    # Score combination
    scores = {}
    
    # Process text results
    text_docs = text_results.to_pylist()
    for i, doc in enumerate(text_docs):
        # Normalize rank to score (1.0 for first, 0.0 for last)
        score = 1.0 - (i / len(text_docs))
        scores[doc['uuid']] = alpha * score
    
    # Process vector results  
    for i, doc in enumerate(vector_results):
        # Convert distance to similarity
        similarity = 1.0 - doc['_distance']
        vector_score = (1 - alpha) * similarity
        
        if doc['uuid'] in scores:
            scores[doc['uuid']] += vector_score
        else:
            scores[doc['uuid']] = vector_score
    
    # Sort by combined score
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top results with documents
    top_results = []
    for uuid, score in sorted_results[:10]:
        doc = dataset.get(uuid)
        top_results.append({
            'document': doc,
            'score': score,
            'uuid': uuid
        })
    
    return top_results
```

### Re-ranking Results

```python
from sentence_transformers import CrossEncoder

def rerank_results(query, results, top_k=10):
    """Re-rank search results using a cross-encoder."""
    # Initialize cross-encoder for re-ranking
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Prepare pairs for re-ranking
    pairs = []
    for result in results:
        text = result['document'].text_content
        pairs.append([query, text])
    
    # Get re-ranking scores
    scores = reranker.predict(pairs)
    
    # Sort by new scores
    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Return top k with new scores
    top_results = []
    for (result, score) in reranked[:top_k]:
        result['rerank_score'] = float(score)
        top_results.append(result)
    
    return top_results
```

## Best Practices

### 1. Embedding Strategy

```python
class EmbeddingStrategy:
    """Best practices for embedding generation."""
    
    @staticmethod
    def should_embed(doc):
        """Determine if document should be embedded."""
        # Skip short documents
        if len(doc.text_content) < 50:
            return False
        
        # Skip certain types
        skip_types = ['dataset_header', 'collection_header']
        if doc.metadata.get('record_type') in skip_types:
            return False
        
        # Skip if marked
        if doc.metadata.get('custom_metadata', {}).get('skip_embedding'):
            return False
        
        return True
    
    @staticmethod
    def prepare_content(doc):
        """Prepare content for optimal embedding."""
        parts = []
        
        # Include structured metadata
        if doc.metadata.get('title'):
            parts.append(f"Title: {doc.metadata['title']}")
        
        if doc.metadata.get('tags'):
            parts.append(f"Topics: {', '.join(doc.metadata['tags'])}")
        
        if doc.metadata.get('summary'):
            parts.append(f"Summary: {doc.metadata['summary']}")
        
        # Main content
        parts.append(doc.text_content)
        
        return '\n\n'.join(parts)
```

### 2. Batch Processing

```python
def efficient_batch_embedding(documents, batch_size=100):
    """Process embeddings efficiently in batches."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    # Thread-safe queue for results
    embedded_docs = []
    lock = threading.Lock()
    
    def process_batch(batch):
        """Process a single batch."""
        try:
            embedded = embed_frames(batch)
            with lock:
                embedded_docs.extend(embedded)
        except Exception as e:
            print(f"Error processing batch: {e}")
    
    # Split into batches
    batches = [documents[i:i+batch_size] 
               for i in range(0, len(documents), batch_size)]
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_batch, batch) 
                  for batch in batches]
        
        # Wait for completion
        for future in futures:
            future.result()
    
    return embedded_docs
```

### 3. Caching Embeddings

```python
import hashlib
import pickle
from pathlib import Path

class EmbeddingCache:
    """Cache embeddings to avoid recomputation."""
    
    def __init__(self, cache_dir="./embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, text, model):
        """Generate cache key for text and model."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, text, model):
        """Get cached embedding if available."""
        key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, text, model, embedding):
        """Cache an embedding."""
        key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
    
    def embed_with_cache(self, docs, model="text-embedding-3-small"):
        """Embed documents using cache."""
        to_embed = []
        cached_indices = []
        
        # Check cache
        for i, doc in enumerate(docs):
            cached = self.get(doc.text_content, model)
            if cached is not None:
                doc.vector = cached
                doc.embed_dim = len(cached)
                cached_indices.append(i)
            else:
                to_embed.append(doc)
        
        # Embed uncached
        if to_embed:
            embedded = embed_frames(to_embed, model=model)
            
            # Cache results
            for doc in embedded:
                self.set(doc.text_content, model, doc.vector)
        
        # Combine results
        result = docs.copy()
        embed_idx = 0
        for i in range(len(docs)):
            if i not in cached_indices:
                result[i] = to_embed[embed_idx]
                embed_idx += 1
        
        return result
```

### 4. Monitoring Quality

```python
def analyze_embedding_quality(dataset):
    """Analyze the quality of embeddings in dataset."""
    stats = {
        'total_documents': 0,
        'documents_with_embeddings': 0,
        'embedding_dimensions': {},
        'zero_vectors': 0,
        'duplicate_embeddings': 0
    }
    
    embeddings_seen = {}
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            stats['total_documents'] += 1
            
            if row.get('embedding'):
                stats['documents_with_embeddings'] += 1
                
                # Check dimension
                dim = len(row['embedding'])
                stats['embedding_dimensions'][dim] = \
                    stats['embedding_dimensions'].get(dim, 0) + 1
                
                # Check for zero vector
                if np.allclose(row['embedding'], 0):
                    stats['zero_vectors'] += 1
                
                # Check for duplicates
                embedding_hash = hashlib.md5(
                    np.array(row['embedding']).tobytes()
                ).hexdigest()
                
                if embedding_hash in embeddings_seen:
                    stats['duplicate_embeddings'] += 1
                embeddings_seen[embedding_hash] = row['uuid']
    
    # Calculate coverage
    stats['embedding_coverage'] = (
        stats['documents_with_embeddings'] / stats['total_documents'] * 100
    )
    
    return stats
```

## Troubleshooting

### Common Issues

```python
def diagnose_embedding_issues(doc):
    """Diagnose common embedding problems."""
    issues = []
    
    # Check if embedding exists
    if doc.vector is None:
        issues.append("No embedding generated")
        
        # Check content
        if not doc.text_content:
            issues.append("No text content to embed")
        elif len(doc.text_content) < 10:
            issues.append("Text content too short")
    
    else:
        # Check embedding quality
        if np.allclose(doc.vector, 0):
            issues.append("Embedding is all zeros")
        
        if np.isnan(doc.vector).any():
            issues.append("Embedding contains NaN values")
        
        if np.isinf(doc.vector).any():
            issues.append("Embedding contains infinite values")
        
        # Check dimension
        expected_dims = [384, 768, 1536, 3072]  # Common dimensions
        if doc.embed_dim not in expected_dims:
            issues.append(f"Unusual embedding dimension: {doc.embed_dim}")
    
    return issues

def fix_embedding_issues(dataset):
    """Fix common embedding issues in dataset."""
    fixed = 0
    
    for batch in dataset.to_batches():
        docs = [FrameRecord.from_arrow(row) for row in batch.to_pylist()]
        
        for doc in docs:
            issues = diagnose_embedding_issues(doc)
            
            if issues:
                print(f"Document {doc.uuid}: {issues}")
                
                # Try to fix
                if "No embedding generated" in issues and doc.text_content:
                    # Re-embed
                    try:
                        embedded = embed_frames([doc])[0]
                        dataset.update_record(doc.uuid, embedded)
                        fixed += 1
                    except Exception as e:
                        print(f"Failed to fix {doc.uuid}: {e}")
    
    print(f"Fixed {fixed} documents")
```

## Next Steps

- Explore [Enrichment](enrichment.md) for content enhancement
- Learn about [Search & Query](search-query.md) patterns
- See [Performance Optimization](../mcp/guides/performance.md)
- Check the [API Reference](../api/embeddings.md) for all functions