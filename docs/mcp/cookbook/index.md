# MCP Cookbook

Real-world examples and patterns for using the ContextFrame MCP server effectively. Each recipe demonstrates a complete, working solution to common use cases.

## Quick Examples

### Basic Document Search

```python
from contextframe.mcp import MCPClient

# Initialize client
client = MCPClient("http://localhost:8000")

# Simple search
results = client.search_documents(
    query="machine learning",
    limit=10
)

# Print results
for doc in results['documents']:
    print(f"Score: {doc['score']:.2f} - {doc['metadata'].get('title', 'Untitled')}")
```

### Create and Organize Documents

```python
# Create a collection
collection = client.collection_create(
    name="research-papers",
    description="ML research papers collection"
)

# Add documents to collection
doc_id = client.document_create(
    content="# Attention Is All You Need\n\nThe Transformer architecture...",
    metadata={
        "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."],
        "year": 2017,
        "tags": ["transformers", "attention", "nlp"]
    },
    collection_id=collection['id']
)

print(f"Document {doc_id} added to collection {collection['id']}")
```

## Recipe Categories

### 🔍 Search Patterns

#### Semantic Search with Filtering

```python
# Combine semantic search with metadata filters
results = client.search_documents(
    query="explain transformer architecture",
    search_type="hybrid",
    metadata_filter={
        "year": {"$gte": 2020},
        "tags": {"$contains": "nlp"}
    },
    limit=5
)
```

#### Multi-Collection Search

```python
# Search across specific collections
collections = ["research", "documentation", "tutorials"]
all_results = []

for coll_id in collections:
    results = client.search_within_collection(
        collection_id=coll_id,
        query="deployment best practices",
        limit=3
    )
    all_results.extend(results['documents'])

# Sort by relevance score
all_results.sort(key=lambda x: x['score'], reverse=True)
```

### 📝 Document Management

#### Bulk Import with Progress

```python
import json
from pathlib import Path

def import_documents_with_progress(directory_path):
    """Import all JSON documents from a directory"""
    documents = []
    
    # Prepare documents
    for file_path in Path(directory_path).glob("*.json"):
        with open(file_path) as f:
            data = json.load(f)
            documents.append({
                "content": data['content'],
                "metadata": {
                    **data.get('metadata', {}),
                    "source_file": file_path.name
                }
            })
    
    # Batch import
    result = client.document_create_batch(
        documents=documents,
        batch_size=50
    )
    
    print(f"Imported {result['created']} documents")
    print(f"Failed: {result['failed']}")
    
    return result['document_ids']
```

#### Document Versioning

```python
def create_document_version(doc_id, new_content, version_note):
    """Create a new version of a document"""
    
    # Get current document
    current = client.document_get(doc_id)
    
    # Create new version with updated content
    new_version = client.document_create(
        content=new_content,
        metadata={
            **current['metadata'],
            "previous_version": doc_id,
            "version_note": version_note,
            "version_date": datetime.utcnow().isoformat()
        }
    )
    
    # Update original to point to new version
    client.document_update(
        id=doc_id,
        metadata={
            **current['metadata'],
            "latest_version": new_version['id']
        }
    )
    
    return new_version['id']
```

### 🤖 AI Agent Patterns

#### RAG with Source Citations

```python
def rag_with_citations(question, llm_client):
    """Answer questions with source citations"""
    
    # Search for relevant context
    search_results = client.search_documents(
        query=question,
        limit=5,
        search_type="hybrid"
    )
    
    # Build context with citations
    context_parts = []
    citations = []
    
    for i, doc in enumerate(search_results['documents']):
        ref_num = i + 1
        context_parts.append(f"[{ref_num}] {doc['content'][:500]}...")
        citations.append({
            "ref": ref_num,
            "title": doc['metadata'].get('title', 'Untitled'),
            "id": doc['id']
        })
    
    # Generate answer with LLM
    prompt = f"""Answer this question using the provided context.
Include citation numbers [n] when referencing sources.

Context:
{chr(10).join(context_parts)}

Question: {question}

Answer:"""
    
    answer = llm_client.generate(prompt)
    
    return {
        "answer": answer,
        "citations": citations
    }
```

#### Interactive Document Assistant

```python
class DocumentAssistant:
    def __init__(self, mcp_client, llm_client):
        self.mcp = mcp_client
        self.llm = llm_client
        self.context_collection = None
    
    def set_context(self, collection_name):
        """Focus on a specific collection"""
        collections = self.mcp.collection_list()
        for coll in collections['collections']:
            if coll['name'] == collection_name:
                self.context_collection = coll['id']
                return f"Context set to: {collection_name}"
        return f"Collection '{collection_name}' not found"
    
    def ask(self, question):
        """Answer questions about the documents"""
        search_params = {
            "query": question,
            "limit": 5
        }
        
        if self.context_collection:
            search_params["collection_id"] = self.context_collection
        
        results = self.mcp.search_documents(**search_params)
        
        if not results['documents']:
            return "I couldn't find any relevant documents."
        
        # Use LLM to synthesize answer
        context = "\n---\n".join([
            doc['content'][:1000] for doc in results['documents']
        ])
        
        response = self.llm.generate(
            f"Based on these documents, {question}\n\nDocuments:\n{context}"
        )
        
        return response
    
    def summarize_collection(self):
        """Provide collection overview"""
        if not self.context_collection:
            return "No collection selected"
        
        stats = self.mcp.collection_stats(self.context_collection)
        recent = self.mcp.collection_list_documents(
            collection_id=self.context_collection,
            limit=5,
            sort_by="updated_at"
        )
        
        summary = f"""Collection Overview:
- Total documents: {stats['document_count']}
- Total size: {stats['total_size_bytes'] / 1024 / 1024:.1f} MB
- Created: {stats['created_at']}

Recent documents:"""
        
        for doc in recent['documents']:
            summary += f"\n- {doc['metadata'].get('title', doc['id'])}"
        
        return summary
```

### 📊 Analytics Patterns

#### Usage Analytics Dashboard

```python
def generate_usage_report(time_range="day"):
    """Generate usage analytics report"""
    
    # Get usage metrics
    metrics = client.usage_metrics(time_range=time_range)
    
    # Get popular searches
    search_analytics = client.search_analytics(
        time_range=time_range,
        limit=10
    )
    
    # Get dataset growth
    stats = client.dataset_stats()
    
    report = f"""## Usage Report - {time_range}

### Activity Summary
- Total API calls: {metrics['metrics']['total_requests']:,}
- Unique users: {metrics['metrics']['unique_users']}
- Average response time: {metrics['metrics']['avg_response_time_ms']}ms
- Error rate: {metrics['metrics']['error_rate']:.2%}

### Popular Tools
"""
    
    for tool, count in metrics['metrics']['by_tool'].items():
        report += f"- {tool}: {count:,} calls\n"
    
    report += f"\n### Top Search Queries\n"
    for query in search_analytics['queries']:
        report += f"- \"{query['query']}\" ({query['count']} searches)\n"
    
    report += f"\n### Dataset Growth
- Total documents: {stats['total_documents']:,}
- Storage used: {stats['storage_size_bytes'] / 1024 / 1024 / 1024:.2f} GB
- Collections: {stats['total_collections']}
"""
    
    return report
```

#### Cost Attribution

```python
def calculate_operation_costs(user_id, date_range):
    """Calculate costs for a specific user"""
    
    # Define cost model
    costs = {
        "search_documents": 0.002,
        "document_create": 0.001,
        "document_update": 0.001,
        "vector_search": 0.005,
        "import_documents": 0.01
    }
    
    # Get user's usage
    usage = client.usage_metrics(
        time_range="custom",
        start_date=date_range[0],
        end_date=date_range[1],
        user_id=user_id
    )
    
    total_cost = 0
    breakdown = {}
    
    for tool, count in usage['by_tool'].items():
        cost = costs.get(tool, 0.001) * count
        total_cost += cost
        breakdown[tool] = {
            "count": count,
            "unit_cost": costs.get(tool, 0.001),
            "total": cost
        }
    
    return {
        "user_id": user_id,
        "period": date_range,
        "total_cost": round(total_cost, 2),
        "breakdown": breakdown
    }
```

### 🔒 Security Patterns

#### Secure Document Sharing

```python
def create_shared_collection(documents, allowed_users, expiry_days=7):
    """Create a time-limited shared collection"""
    
    # Create collection with expiry
    expiry_date = (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
    
    collection = client.collection_create(
        name=f"shared_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        metadata={
            "type": "shared",
            "expires_at": expiry_date,
            "allowed_users": allowed_users,
            "created_by": "current_user"
        }
    )
    
    # Add documents to collection
    doc_ids = []
    for doc in documents:
        doc_id = client.document_create(
            content=doc['content'],
            metadata={
                **doc.get('metadata', {}),
                "shared": True,
                "expires_at": expiry_date
            },
            collection_id=collection['id']
        )
        doc_ids.append(doc_id)
    
    # Generate share token (implement in your auth system)
    share_token = generate_share_token(
        collection_id=collection['id'],
        allowed_users=allowed_users,
        expiry=expiry_date
    )
    
    return {
        "collection_id": collection['id'],
        "share_token": share_token,
        "expires_at": expiry_date,
        "document_count": len(doc_ids)
    }
```

### 🚀 Performance Patterns

#### Parallel Processing

```python
import asyncio
from contextframe.mcp.async_client import AsyncMCPClient

async def parallel_document_processing(file_paths):
    """Process multiple documents in parallel"""
    
    async with AsyncMCPClient("http://localhost:8000") as client:
        tasks = []
        
        for path in file_paths:
            task = process_single_document(client, path)
            tasks.append(task)
        
        # Process in parallel with concurrency limit
        sem = asyncio.Semaphore(10)  # Max 10 concurrent
        
        async def bounded_process(task):
            async with sem:
                return await task
        
        results = await asyncio.gather(
            *[bounded_process(task) for task in tasks],
            return_exceptions=True
        )
        
        # Handle results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        print(f"Processed {len(successful)} documents successfully")
        print(f"Failed: {len(failed)}")
        
        return successful

async def process_single_document(client, file_path):
    """Process a single document"""
    with open(file_path) as f:
        content = f.read()
    
    # Extract metadata (example)
    metadata = {
        "source": file_path,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    # Create document
    result = await client.document_create(
        content=content,
        metadata=metadata
    )
    
    return result
```

## Testing Patterns

### Integration Testing

```python
import pytest
from contextframe.mcp import MCPClient

@pytest.fixture
def mcp_test_client():
    """Test client with isolated dataset"""
    client = MCPClient("http://localhost:8000/test")
    yield client
    # Cleanup
    client.clear_dataset()

def test_search_functionality(mcp_test_client):
    """Test search returns relevant results"""
    # Create test documents
    docs = [
        {"content": "Python programming guide", "metadata": {"type": "guide"}},
        {"content": "JavaScript tutorial", "metadata": {"type": "tutorial"}},
        {"content": "Python data science", "metadata": {"type": "guide"}}
    ]
    
    doc_ids = []
    for doc in docs:
        result = mcp_test_client.document_create(**doc)
        doc_ids.append(result['id'])
    
    # Test search
    results = mcp_test_client.search_documents(
        query="Python",
        limit=10
    )
    
    assert results['total_count'] == 2
    assert all("Python" in doc['content'] for doc in results['documents'])
    
    # Cleanup
    for doc_id in doc_ids:
        mcp_test_client.document_delete(doc_id)
```

## Error Handling Patterns

### Resilient Client

```python
class ResilientMCPClient:
    def __init__(self, base_url, max_retries=3):
        self.client = MCPClient(base_url)
        self.max_retries = max_retries
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                # Wait for rate limit reset
                time.sleep(e.retry_after)
            except NetworkError as e:
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                last_error = e
            except Exception as e:
                # Don't retry on other errors
                raise
        
        raise last_error
    
    def search_documents(self, **kwargs):
        return self.execute_with_retry(
            self.client.search_documents,
            **kwargs
        )
```

## Next Steps

- [API Reference](../api/tools.md) - Complete tool documentation
- [Integration Guide](../guides/agent-integration.md) - Connect your AI agents
- [Security Guide](../configuration/security.md) - Secure your deployment
- [Performance Guide](../guides/performance.md) - Optimize for scale