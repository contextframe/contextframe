# Search & Query

ContextFrame provides powerful search and query capabilities, combining full-text search, vector similarity search, and SQL-style filtering. This guide covers all search patterns and optimization techniques.

## Overview

Search capabilities include:
- Full-text search with relevance ranking
- Vector similarity search (KNN)
- SQL-style filtering with complex conditions
- Hybrid search combining multiple approaches
- Faceted search and aggregations
- Query optimization with indices

## Full-Text Search

### Basic Text Search

```python
from contextframe import FrameDataset

# Simple text search
results = dataset.full_text_search("machine learning")

# Convert to list of documents
docs = results.to_pylist()
for doc in docs:
    print(f"Title: {doc['title']}")
    print(f"Score: {doc.get('_score', 'N/A')}")

# Limit results
results = dataset.full_text_search(
    "python programming",
    limit=20
)
```

### Advanced Text Search

```python
# Search specific fields
results = dataset.full_text_search(
    "API documentation",
    columns=["title", "content", "summary"],  # Search only these fields
    limit=10
)

# Search with filters
results = dataset.full_text_search(
    "authentication",
    filter="status = 'published' AND record_type = 'document'",
    limit=20
)

# Complex query with multiple terms
results = dataset.full_text_search(
    "python async programming NOT threading",  # Exclude results with 'threading'
    filter="created_at > '2023-01-01'"
)
```

### Query Syntax

```python
# Phrase search
results = dataset.full_text_search('"exact phrase match"')

# Boolean operators
results = dataset.full_text_search("python AND (async OR await)")
results = dataset.full_text_search("machine learning NOT deep learning")

# Wildcard search
results = dataset.full_text_search("program*")  # Matches programming, programmer, etc.

# Field-specific search (if supported)
results = dataset.full_text_search("title:Python content:tutorial")
```

## Vector Search

### Basic KNN Search

```python
import numpy as np

# Generate or get query vector
query_vector = np.random.randn(1536).astype(np.float32)  # Example
# Or from text
query_vector = generate_embedding("How to implement caching in Python?")

# Find similar documents
results = dataset.knn_search(
    query_vector,
    k=10  # Return top 10 most similar
)

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"Distance: {result['_distance']}")
    print(f"Similarity: {1 - result['_distance']:.4f}")  # For cosine distance
```

### Filtered Vector Search

```python
# Vector search with metadata filters
results = dataset.knn_search(
    query_vector,
    k=20,
    filter="tags.contains('python') AND status = 'published'"
)

# Complex filtering
results = dataset.knn_search(
    query_vector,
    k=50,
    filter="""
    record_type = 'document' 
    AND created_at > '2023-06-01'
    AND (author = 'Expert' OR tags.contains('verified'))
    AND custom_metadata.difficulty IN ('beginner', 'intermediate')
    """
)

# With specific columns
results = dataset.knn_search(
    query_vector,
    k=10,
    columns=["uuid", "title", "summary", "tags", "_distance"],
    filter="collection = 'tutorials'"
)
```

### Multi-Vector Search

```python
def multi_vector_search(dataset, query_vectors, k=10):
    """Search using multiple query vectors."""
    all_results = {}
    
    # Search with each vector
    for i, vector in enumerate(query_vectors):
        results = dataset.knn_search(vector, k=k*2)  # Get more for merging
        
        for result in results:
            uuid = result['uuid']
            if uuid not in all_results:
                all_results[uuid] = {
                    'document': result,
                    'scores': [],
                    'min_distance': float('inf')
                }
            
            all_results[uuid]['scores'].append(result['_distance'])
            all_results[uuid]['min_distance'] = min(
                all_results[uuid]['min_distance'],
                result['_distance']
            )
    
    # Sort by minimum distance
    sorted_results = sorted(
        all_results.values(),
        key=lambda x: x['min_distance']
    )
    
    return sorted_results[:k]
```

## SQL-Style Filtering

### Filter Syntax

```python
# Comparison operators
dataset.scanner(filter="created_at > '2024-01-01'")
dataset.scanner(filter="word_count >= 500")
dataset.scanner(filter="status != 'draft'")
dataset.scanner(filter="version <= '2.0.0'")

# String operations
dataset.scanner(filter="title LIKE '%Python%'")  # Contains
dataset.scanner(filter="title LIKE 'Python%'")   # Starts with
dataset.scanner(filter="author IN ('Alice', 'Bob', 'Charlie')")

# Array operations
dataset.scanner(filter="tags.contains('tutorial')")
dataset.scanner(filter="array_length(tags) > 3")
dataset.scanner(filter="'python' = ANY(tags)")  # Alternative syntax

# Null checks
dataset.scanner(filter="summary IS NOT NULL")
dataset.scanner(filter="embedding IS NULL")

# Boolean logic
dataset.scanner(filter="status = 'published' AND author = 'Expert'")
dataset.scanner(filter="tags.contains('python') OR tags.contains('javascript')")
dataset.scanner(filter="NOT (status = 'draft')")

# Complex conditions
dataset.scanner(filter="""
    (status = 'published' OR status = 'archived')
    AND created_at > '2023-01-01'
    AND (
        tags.contains('important') 
        OR custom_metadata.priority = 'high'
    )
""")
```

### Working with Custom Metadata

```python
# Access nested fields
dataset.scanner(filter="custom_metadata.department = 'Engineering'")
dataset.scanner(filter="custom_metadata.priority IN ('high', 'critical')")
dataset.scanner(filter="custom_metadata.score > 0.8")

# JSON operations (if supported)
dataset.scanner(filter="custom_metadata.keywords.contains('machine-learning')")
dataset.scanner(filter="json_extract(custom_metadata, '$.version') = '2.0'")

# Complex custom metadata queries
results = dataset.scanner(
    filter="""
    custom_metadata.department = 'Engineering'
    AND custom_metadata.tech_stack.contains('python')
    AND custom_metadata.difficulty != 'expert'
    """,
    columns=["uuid", "title", "custom_metadata"]
).to_table()
```

## Query Building

### Dynamic Query Builder

```python
class QueryBuilder:
    """Build complex queries dynamically."""
    
    def __init__(self):
        self.conditions = []
        self.params = {}
    
    def add_condition(self, condition, param=None):
        """Add a condition to the query."""
        self.conditions.append(condition)
        if param:
            self.params.update(param)
        return self
    
    def add_text_filter(self, field, value, operator='='):
        """Add text field filter."""
        if operator == 'contains':
            condition = f"{field} LIKE '%{value}%'"
        elif operator == 'starts_with':
            condition = f"{field} LIKE '{value}%'"
        else:
            condition = f"{field} {operator} '{value}'"
        
        self.conditions.append(condition)
        return self
    
    def add_array_filter(self, field, value):
        """Add array contains filter."""
        condition = f"{field}.contains('{value}')"
        self.conditions.append(condition)
        return self
    
    def add_date_filter(self, field, date, operator='>'):
        """Add date filter."""
        condition = f"{field} {operator} '{date}'"
        self.conditions.append(condition)
        return self
    
    def add_custom_metadata_filter(self, key, value, operator='='):
        """Add custom metadata filter."""
        if operator == '=':
            condition = f"custom_metadata.{key} = '{value}'"
        else:
            condition = f"custom_metadata.{key} {operator} {value}"
        
        self.conditions.append(condition)
        return self
    
    def build(self, logic='AND'):
        """Build the final query."""
        if not self.conditions:
            return None
        return f" {logic} ".join(f"({cond})" for cond in self.conditions)

# Usage
query = QueryBuilder()
query.add_text_filter('status', 'published')
query.add_array_filter('tags', 'python')
query.add_date_filter('created_at', '2023-01-01', '>')
query.add_custom_metadata_filter('priority', 'high')

filter_string = query.build()  # Build with AND logic
results = dataset.scanner(filter=filter_string).to_table()
```

### Query Templates

```python
class QueryTemplates:
    """Common query patterns."""
    
    @staticmethod
    def recent_documents(days=7, status='published'):
        """Get recent documents."""
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return f"created_at > '{cutoff}' AND status = '{status}'"
    
    @staticmethod
    def by_author_and_tags(author, tags):
        """Find documents by author with any of the tags."""
        tag_conditions = " OR ".join(f"tags.contains('{tag}')" for tag in tags)
        return f"author = '{author}' AND ({tag_conditions})"
    
    @staticmethod
    def high_quality_documents(min_score=80):
        """Get high quality documents."""
        return f"""
        custom_metadata.quality_score.score >= {min_score}
        AND status = 'published'
        AND embedding IS NOT NULL
        """
    
    @staticmethod
    def collection_documents(collection_name, record_type='document'):
        """Get documents from a collection."""
        return f"""
        collection = '{collection_name}'
        AND record_type = '{record_type}'
        """
    
    @staticmethod
    def similar_metadata(reference_doc):
        """Find documents with similar metadata."""
        conditions = []
        
        if reference_doc.metadata.get('author'):
            conditions.append(f"author = '{reference_doc.metadata['author']}'")
        
        if reference_doc.metadata.get('tags'):
            tag_conds = [f"tags.contains('{tag}')" for tag in reference_doc.metadata['tags'][:3]]
            conditions.append(f"({' OR '.join(tag_conds)})")
        
        return " OR ".join(conditions)
```

## Hybrid Search

### Combining Text and Vector

```python
def hybrid_search(dataset, query_text, alpha=0.5, k=20):
    """
    Combine text and vector search.
    
    Args:
        alpha: Weight for text search (0.0-1.0)
               0.0 = pure vector search
               1.0 = pure text search
    """
    # Generate embedding for query
    query_embedding = generate_embedding(query_text)
    
    # Perform both searches
    text_results = dataset.full_text_search(query_text, limit=k*2).to_pylist()
    vector_results = dataset.knn_search(query_embedding, k=k*2)
    
    # Combine scores
    scores = {}
    
    # Process text results with rank-based scoring
    for rank, doc in enumerate(text_results):
        score = 1.0 - (rank / len(text_results))  # Normalize rank to 0-1
        scores[doc['uuid']] = {
            'text_score': score,
            'vector_score': 0.0,
            'document': doc
        }
    
    # Process vector results
    for doc in vector_results:
        uuid = doc['uuid']
        # Convert distance to similarity (assuming cosine distance)
        similarity = 1.0 - doc['_distance']
        
        if uuid in scores:
            scores[uuid]['vector_score'] = similarity
        else:
            scores[uuid] = {
                'text_score': 0.0,
                'vector_score': similarity,
                'document': doc
            }
    
    # Calculate combined scores
    final_scores = []
    for uuid, score_data in scores.items():
        combined = (alpha * score_data['text_score'] + 
                   (1 - alpha) * score_data['vector_score'])
        final_scores.append({
            'uuid': uuid,
            'score': combined,
            'text_score': score_data['text_score'],
            'vector_score': score_data['vector_score'],
            'document': score_data['document']
        })
    
    # Sort by combined score
    final_scores.sort(key=lambda x: x['score'], reverse=True)
    
    return final_scores[:k]
```

### Multi-Stage Search

```python
def multi_stage_search(dataset, query, stages):
    """
    Multi-stage search with progressive filtering.
    
    Example stages:
    [
        {'type': 'text', 'limit': 100},
        {'type': 'filter', 'condition': "status = 'published'"},
        {'type': 'vector', 'k': 20},
        {'type': 'rerank', 'k': 10}
    ]
    """
    results = None
    
    for stage in stages:
        if stage['type'] == 'text':
            results = dataset.full_text_search(
                query['text'],
                limit=stage['limit']
            ).to_pylist()
        
        elif stage['type'] == 'filter' and results:
            # Filter existing results
            filtered = []
            for doc in results:
                # Simple evaluation (in practice, use proper expression evaluation)
                if evaluate_condition(doc, stage['condition']):
                    filtered.append(doc)
            results = filtered
        
        elif stage['type'] == 'vector' and results:
            # Re-rank using vector similarity
            doc_ids = [r['uuid'] for r in results]
            vector_scores = {}
            
            # Get vector similarities
            vector_results = dataset.knn_search(
                query['embedding'],
                k=len(results)
            )
            
            for vr in vector_results:
                if vr['uuid'] in doc_ids:
                    vector_scores[vr['uuid']] = 1 - vr['_distance']
            
            # Re-score results
            for result in results:
                result['vector_score'] = vector_scores.get(result['uuid'], 0)
            
            # Sort by vector score
            results.sort(key=lambda x: x['vector_score'], reverse=True)
            results = results[:stage['k']]
        
        elif stage['type'] == 'rerank' and results:
            # Final reranking (could use cross-encoder)
            results = rerank_results(query['text'], results, stage['k'])
    
    return results
```

## Faceted Search

### Aggregations

```python
def get_facets(dataset, base_filter=None):
    """Get facets for search refinement."""
    facets = {
        'status': {},
        'author': {},
        'tags': {},
        'record_type': {},
        'year': {}
    }
    
    # Base scanner
    scanner = dataset.scanner(filter=base_filter) if base_filter else dataset.scanner()
    
    # Process all documents
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            # Status facet
            status = row.get('status', 'unknown')
            facets['status'][status] = facets['status'].get(status, 0) + 1
            
            # Author facet
            author = row.get('author', 'unknown')
            facets['author'][author] = facets['author'].get(author, 0) + 1
            
            # Tags facet
            for tag in row.get('tags', []):
                facets['tags'][tag] = facets['tags'].get(tag, 0) + 1
            
            # Record type facet
            record_type = row.get('record_type', 'document')
            facets['record_type'][record_type] = facets['record_type'].get(record_type, 0) + 1
            
            # Year facet
            created = row.get('created_at', '')
            if created:
                year = created[:4]
                facets['year'][year] = facets['year'].get(year, 0) + 1
    
    # Sort facets by count
    for facet_name, facet_values in facets.items():
        facets[facet_name] = dict(
            sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
        )
    
    return facets
```

### Search with Facets

```python
class FacetedSearch:
    """Search with facet filtering."""
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.filters = {}
    
    def add_facet_filter(self, facet, value):
        """Add a facet filter."""
        if facet not in self.filters:
            self.filters[facet] = []
        self.filters[facet].append(value)
        return self
    
    def remove_facet_filter(self, facet, value=None):
        """Remove a facet filter."""
        if facet in self.filters:
            if value:
                self.filters[facet].remove(value)
            else:
                del self.filters[facet]
        return self
    
    def build_filter(self):
        """Build filter string from facets."""
        conditions = []
        
        for facet, values in self.filters.items():
            if facet == 'tags':
                # Handle array fields
                tag_conditions = [f"tags.contains('{v}')" for v in values]
                conditions.append(f"({' OR '.join(tag_conditions)})")
            elif len(values) == 1:
                conditions.append(f"{facet} = '{values[0]}'")
            else:
                # Multiple values
                value_list = ', '.join(f"'{v}'" for v in values)
                conditions.append(f"{facet} IN ({value_list})")
        
        return ' AND '.join(conditions) if conditions else None
    
    def search(self, query_text=None, query_vector=None, limit=20):
        """Perform search with current facets."""
        filter_string = self.build_filter()
        
        if query_text:
            return self.dataset.full_text_search(
                query_text,
                filter=filter_string,
                limit=limit
            )
        elif query_vector is not None:
            return self.dataset.knn_search(
                query_vector,
                k=limit,
                filter=filter_string
            )
        else:
            return self.dataset.scanner(
                filter=filter_string,
                limit=limit
            ).to_table()
    
    def get_facets(self):
        """Get available facets with current filters."""
        return get_facets(self.dataset, self.build_filter())
```

## Search Optimization

### Index Usage

```python
def optimize_search_indices(dataset):
    """Create indices for common search patterns."""
    # Text search benefits from full-text index (automatic in Lance)
    
    # Create scalar indices for common filters
    common_filter_fields = [
        'status',
        'author', 
        'record_type',
        'collection',
        'created_at'
    ]
    
    for field in common_filter_fields:
        try:
            dataset.create_scalar_index(field)
            print(f"Created index on {field}")
        except:
            print(f"Index on {field} already exists or failed")
    
    # Bitmap index for low-cardinality fields
    low_cardinality_fields = ['status', 'record_type']
    for field in low_cardinality_fields:
        try:
            dataset.create_scalar_index(field, index_type='BITMAP')
            print(f"Created bitmap index on {field}")
        except:
            pass
    
    # Vector index for similarity search
    if check_has_embeddings(dataset):
        num_partitions = int(np.sqrt(len(dataset)))
        dataset.create_vector_index(
            column='embedding',
            num_partitions=min(num_partitions, 256),
            metric_type='cosine'
        )
        print("Created vector index")
```

### Query Performance

```python
import time

def benchmark_query(dataset, query_func, name="Query"):
    """Benchmark query performance."""
    start = time.time()
    results = query_func()
    end = time.time()
    
    duration = end - start
    count = len(results) if hasattr(results, '__len__') else results.num_rows
    
    print(f"{name}:")
    print(f"  Duration: {duration:.3f}s")
    print(f"  Results: {count}")
    print(f"  Time per result: {duration/count*1000:.2f}ms" if count > 0 else "N/A")
    
    return results, duration

# Benchmark different search approaches
def compare_search_methods(dataset, query_text):
    """Compare different search methods."""
    query_vector = generate_embedding(query_text)
    
    # Full-text search
    benchmark_query(
        dataset,
        lambda: dataset.full_text_search(query_text, limit=20),
        "Full-text search"
    )
    
    # Vector search
    benchmark_query(
        dataset,
        lambda: dataset.knn_search(query_vector, k=20),
        "Vector search"
    )
    
    # Filtered search
    benchmark_query(
        dataset,
        lambda: dataset.full_text_search(
            query_text,
            filter="status = 'published'",
            limit=20
        ),
        "Filtered text search"
    )
    
    # Hybrid search
    benchmark_query(
        dataset,
        lambda: hybrid_search(dataset, query_text, alpha=0.5, k=20),
        "Hybrid search"
    )
```

## Advanced Search Patterns

### Semantic Search with Context

```python
def contextual_search(dataset, query, context_docs, weight=0.3):
    """
    Search with context from related documents.
    
    Args:
        query: Search query text
        context_docs: List of document UUIDs for context
        weight: Weight for context influence (0-1)
    """
    # Get context documents
    context_embeddings = []
    for uuid in context_docs:
        doc = dataset.get(uuid)
        if doc.vector is not None:
            context_embeddings.append(doc.vector)
    
    # Create query embedding
    query_embedding = generate_embedding(query)
    
    # Combine with context
    if context_embeddings:
        context_vector = np.mean(context_embeddings, axis=0)
        combined_embedding = ((1 - weight) * query_embedding + 
                             weight * context_vector)
        combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
    else:
        combined_embedding = query_embedding
    
    # Search with combined embedding
    return dataset.knn_search(combined_embedding, k=20)
```

### Query Expansion

```python
def expand_query(query, method='synonyms'):
    """Expand query with related terms."""
    expanded_terms = [query]
    
    if method == 'synonyms':
        # Use WordNet or similar
        from nltk.corpus import wordnet
        
        words = query.split()
        for word in words:
            synsets = wordnet.synsets(word)
            for syn in synsets[:2]:  # Limit synonyms
                for lemma in syn.lemmas()[:3]:
                    if lemma.name() != word:
                        expanded_terms.append(lemma.name().replace('_', ' '))
    
    elif method == 'related':
        # Use word embeddings to find related terms
        # This is a simplified example
        related_terms = {
            'python': ['programming', 'code', 'script'],
            'machine learning': ['ML', 'AI', 'deep learning'],
            'api': ['interface', 'endpoint', 'REST']
        }
        
        for term, related in related_terms.items():
            if term in query.lower():
                expanded_terms.extend(related)
    
    # Build expanded query
    unique_terms = list(set(expanded_terms))
    expanded_query = ' OR '.join(f'"{term}"' for term in unique_terms)
    
    return expanded_query

# Usage
original_query = "python machine learning"
expanded = expand_query(original_query)
results = dataset.full_text_search(expanded)
```

### Learning to Rank

```python
class SearchRanker:
    """Learn to rank search results based on user feedback."""
    
    def __init__(self):
        self.feedback = {}  # query -> [(doc_id, relevance)]
    
    def add_feedback(self, query, doc_id, relevant=True):
        """Add relevance feedback."""
        if query not in self.feedback:
            self.feedback[query] = []
        self.feedback[query].append((doc_id, relevant))
    
    def rerank_results(self, query, results):
        """Rerank based on historical feedback."""
        if query not in self.feedback:
            return results
        
        # Create relevance scores
        relevance_scores = {}
        for doc_id, relevant in self.feedback[query]:
            relevance_scores[doc_id] = relevance_scores.get(doc_id, 0)
            relevance_scores[doc_id] += 1 if relevant else -1
        
        # Adjust result scores
        reranked = []
        for result in results:
            doc_id = result.get('uuid', result.get('id'))
            base_score = result.get('score', result.get('_distance', 0))
            
            # Boost or penalize based on feedback
            feedback_score = relevance_scores.get(doc_id, 0)
            adjusted_score = base_score + (feedback_score * 0.1)
            
            result['adjusted_score'] = adjusted_score
            reranked.append(result)
        
        # Sort by adjusted score
        reranked.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        return reranked
```

## Best Practices

### 1. Query Optimization

```python
def optimize_query_performance(dataset, query_text):
    """Optimize query for performance."""
    optimization_tips = []
    
    # Check if query is too broad
    if len(query_text.split()) < 2:
        optimization_tips.append("Consider using more specific search terms")
    
    # Check for common words
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}
    query_words = set(query_text.lower().split())
    if len(query_words & common_words) > len(query_words) / 2:
        optimization_tips.append("Query contains many common words that may reduce precision")
    
    # Suggest filters
    total_docs = len(dataset)
    if total_docs > 10000:
        optimization_tips.append("Consider adding filters to narrow results")
    
    # Check index usage
    indices = dataset.list_indices()
    if not any(idx['column'] == 'embedding' for idx in indices):
        optimization_tips.append("No vector index found - vector search may be slow")
    
    return optimization_tips
```

### 2. Result Caching

```python
from functools import lru_cache
import hashlib

class SearchCache:
    """Cache search results."""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def _make_key(self, query_type, query, filters=None):
        """Create cache key."""
        key_parts = [query_type, str(query)]
        if filters:
            key_parts.append(filters)
        
        key_str = '|'.join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query_type, query, filters=None):
        """Get cached results."""
        key = self._make_key(query_type, query, filters)
        return self.cache.get(key)
    
    def set(self, query_type, query, results, filters=None):
        """Cache results."""
        if len(self.cache) >= self.max_size:
            # Remove oldest (simple FIFO)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        key = self._make_key(query_type, query, filters)
        self.cache[key] = {
            'results': results,
            'timestamp': time.time()
        }
    
    def search_with_cache(self, dataset, query_type, query, **kwargs):
        """Search with caching."""
        filters = kwargs.get('filter')
        
        # Check cache
        cached = self.get(query_type, query, filters)
        if cached and time.time() - cached['timestamp'] < 300:  # 5 min TTL
            return cached['results']
        
        # Perform search
        if query_type == 'text':
            results = dataset.full_text_search(query, **kwargs)
        elif query_type == 'vector':
            results = dataset.knn_search(query, **kwargs)
        else:
            results = dataset.scanner(**kwargs).to_table()
        
        # Cache results
        self.set(query_type, query, results, filters)
        
        return results
```

### 3. Search Analytics

```python
class SearchAnalytics:
    """Track and analyze search patterns."""
    
    def __init__(self):
        self.queries = []
        self.zero_results = []
        self.slow_queries = []
    
    def log_search(self, query, results_count, duration, search_type):
        """Log search query."""
        entry = {
            'query': query,
            'results_count': results_count,
            'duration': duration,
            'search_type': search_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.queries.append(entry)
        
        # Track zero results
        if results_count == 0:
            self.zero_results.append(entry)
        
        # Track slow queries
        if duration > 1.0:  # 1 second threshold
            self.slow_queries.append(entry)
    
    def get_popular_queries(self, limit=10):
        """Get most popular queries."""
        from collections import Counter
        
        query_texts = [q['query'] for q in self.queries if isinstance(q['query'], str)]
        return Counter(query_texts).most_common(limit)
    
    def get_search_metrics(self):
        """Get search performance metrics."""
        if not self.queries:
            return {}
        
        durations = [q['duration'] for q in self.queries]
        results_counts = [q['results_count'] for q in self.queries]
        
        return {
            'total_searches': len(self.queries),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'avg_results': sum(results_counts) / len(results_counts),
            'zero_results_rate': len(self.zero_results) / len(self.queries),
            'slow_query_rate': len(self.slow_queries) / len(self.queries)
        }
```

## Troubleshooting

### Common Issues

```python
def diagnose_search_issues(dataset, query):
    """Diagnose common search problems."""
    issues = []
    
    # Check if dataset is empty
    if len(dataset) == 0:
        issues.append("Dataset is empty")
        return issues
    
    # Check query
    if not query or (isinstance(query, str) and not query.strip()):
        issues.append("Query is empty")
    
    # Check for special characters that might need escaping
    if isinstance(query, str):
        special_chars = ['(', ')', '[', ']', '{', '}', '"', "'"]
        if any(char in query for char in special_chars):
            issues.append("Query contains special characters that may need escaping")
    
    # Check indices
    indices = dataset.list_indices()
    if not indices:
        issues.append("No indices created - searches may be slow")
    
    # Check for embeddings if doing vector search
    sample = dataset.scanner(limit=1).to_table().to_pylist()
    if sample and 'embedding' not in sample[0]:
        issues.append("No embeddings found - vector search won't work")
    
    return issues

def fix_common_search_issues(dataset):
    """Fix common search issues."""
    fixes_applied = []
    
    # Create missing indices
    try:
        dataset.create_scalar_index('status')
        dataset.create_scalar_index('created_at')
        fixes_applied.append("Created scalar indices")
    except:
        pass
    
    # Create vector index if embeddings exist
    sample = dataset.scanner(limit=1).to_table().to_pylist()
    if sample and 'embedding' in sample[0]:
        try:
            dataset.create_vector_index()
            fixes_applied.append("Created vector index")
        except:
            pass
    
    return fixes_applied
```

## Next Steps

- Explore [Import/Export](import-export.md) for data migration
- See [Performance Optimization](../mcp/guides/performance.md)
- Check [Cookbook Examples](../cookbook/advanced-search.md)
- Review the [API Reference](../api/search.md)