# Basic Examples

This guide provides practical examples of common ContextFrame use cases. Each example is self-contained and demonstrates key features.

## Vector Embeddings and Semantic Search

Add AI-powered semantic search to your documents:

```python
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames

# Create dataset and documents
dataset = FrameDataset.create("semantic_search.lance")

docs = [
    FrameRecord.create(
        title="Machine Learning Basics",
        content="Machine learning is a subset of artificial intelligence that enables systems to learn from data."
    ),
    FrameRecord.create(
        title="Deep Learning Introduction", 
        content="Deep learning uses neural networks with multiple layers to progressively extract features from raw input."
    ),
    FrameRecord.create(
        title="Natural Language Processing",
        content="NLP combines linguistics and machine learning to help computers understand human language."
    )
]

# Add embeddings (requires OPENAI_API_KEY)
embedded_docs = embed_frames(docs, model="text-embedding-3-small")
dataset.add_many(embedded_docs)

# Create vector index for fast search
dataset.create_vector_index(index_type="IVF_PQ", num_partitions=10)

# Semantic search
query = FrameRecord.create(content="How do computers understand text?")
query_embedded = embed_frames([query])[0]

results = dataset.knn_search(
    query_embedded.embedding,
    k=3,
    filter="status != 'archived'"  # Optional filter
)

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.metadata['title']} (similarity: {doc.score:.3f})")
```

## Document Processing Pipeline

Build a pipeline to process and enrich documents:

```python
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
import json

class DocumentPipeline:
    def __init__(self, dataset_name):
        self.dataset = FrameDataset.create(dataset_name)
        
    def process_document(self, title, content, source=None):
        """Process a single document through the pipeline."""
        
        # Step 1: Create base document
        doc = FrameRecord.create(
            title=title,
            content=content,
            source_file=source,
            status="processing"
        )
        
        # Step 2: Extract metadata
        doc.metadata['custom_metadata'] = {
            'word_count': len(content.split()),
            'char_count': len(content),
            'has_code': '```' in content,
            'language': self._detect_language(content)
        }
        
        # Step 3: Auto-tag
        doc.metadata['tags'] = self._generate_tags(content)
        
        # Step 4: Add embeddings
        doc = embed_frames([doc])[0]
        
        # Step 5: Mark as processed
        doc.metadata['status'] = 'processed'
        
        return doc
    
    def _detect_language(self, content):
        """Simple language detection based on keywords."""
        if 'def ' in content or 'import ' in content:
            return 'python'
        elif 'function ' in content or 'const ' in content:
            return 'javascript'
        return 'text'
    
    def _generate_tags(self, content):
        """Generate tags based on content."""
        tags = []
        
        # Language tags
        if 'python' in content.lower():
            tags.append('python')
        if 'javascript' in content.lower():
            tags.append('javascript')
            
        # Topic tags
        if 'machine learning' in content.lower():
            tags.append('ml')
        if 'api' in content.lower():
            tags.append('api')
            
        return tags
    
    def process_batch(self, documents):
        """Process multiple documents efficiently."""
        processed = []
        
        for doc_data in documents:
            doc = self.process_document(**doc_data)
            processed.append(doc)
        
        # Batch add for efficiency
        self.dataset.add_many(processed)
        return len(processed)

# Usage
pipeline = DocumentPipeline("processed_docs.lance")

documents = [
    {
        "title": "Python API Guide",
        "content": "Learn how to build REST APIs with Python...",
        "source": "docs/api-guide.md"
    },
    {
        "title": "ML Model Deployment",
        "content": "Deploy machine learning models to production...",
        "source": "docs/ml-deployment.md"
    }
]

count = pipeline.process_batch(documents)
print(f"Processed {count} documents")
```

## Working with External Connectors

Import documents from various sources:

### GitHub Repository Import

```python
from contextframe import FrameDataset
from contextframe.connectors import GitHubConnector, ConnectorConfig, AuthType
import os

# Setup dataset
dataset = FrameDataset.create("github_docs.lance")

# Configure GitHub connector
config = ConnectorConfig(
    name="React Docs Import",
    auth_type=AuthType.TOKEN,
    auth_config={"token": os.getenv("GITHUB_TOKEN")},
    sync_config={
        "owner": "facebook",
        "repo": "react",
        "branch": "main",
        "paths": ["/docs"],
        "file_patterns": ["*.md", "*.mdx"],
        "exclude_patterns": ["*test*", ".*"]
    }
)

# Connect and sync
connector = GitHubConnector(config, dataset)
if connector.validate_connection():
    result = connector.sync(incremental=True)
    print(f"Imported {result.frames_created} documents")
    print(f"Updated {result.frames_updated} documents")
    
    if result.errors:
        print("Errors:", result.errors)
```

### Notion Workspace Import

```python
from contextframe.connectors import NotionConnector

# Configure Notion connector
notion_config = ConnectorConfig(
    name="Team Knowledge Base",
    auth_type=AuthType.TOKEN,
    auth_config={"token": os.getenv("NOTION_TOKEN")},
    sync_config={
        "sync_databases": True,
        "sync_pages": True,
        "include_archived": False
    }
)

# Import from Notion
notion = NotionConnector(notion_config, dataset)
if notion.validate_connection():
    # Discover available content
    discovery = notion.discover_content()
    print(f"Found {discovery['stats']['total_pages']} pages")
    print(f"Found {discovery['stats']['total_databases']} databases")
    
    # Sync content
    result = notion.sync()
    print(f"Synced {result.frames_created + result.frames_updated} items")
```

## Building a Q&A System

Create a question-answering system over your documents:

```python
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
import openai

class QASystem:
    def __init__(self, dataset_path):
        self.dataset = FrameDataset(dataset_path)
        self.client = openai.OpenAI()
        
    def answer_question(self, question, k=5):
        """Answer a question using relevant documents."""
        
        # 1. Embed the question
        query_doc = FrameRecord.create(content=question)
        query_embedded = embed_frames([query_doc])[0]
        
        # 2. Find relevant documents
        relevant_docs = self.dataset.knn_search(
            query_embedded.embedding,
            k=k
        )
        
        # 3. Build context from documents
        context = "\n\n".join([
            f"Document: {doc.metadata['title']}\n{doc.text_content[:500]}"
            for doc in relevant_docs
        ])
        
        # 4. Generate answer using LLM
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Answer questions based on the provided context. If the answer isn't in the context, say so."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ]
        )
        
        answer = response.choices[0].message.content
        
        # 5. Create and store the Q&A as a frameset
        frameset = self.dataset.create_frameset(
            title=f"Q&A: {question[:50]}...",
            content=answer,
            query=question,
            source_records=[(doc.uuid, doc.text_content[:200]) for doc in relevant_docs],
            tags=["qa", "generated"]
        )
        
        return {
            "answer": answer,
            "sources": [doc.metadata['title'] for doc in relevant_docs],
            "frameset_id": frameset.uuid
        }

# Usage
qa = QASystem("knowledge_base.lance")

result = qa.answer_question("What are the best practices for API design?")
print("Answer:", result['answer'])
print("\nSources:")
for source in result['sources']:
    print(f"- {source}")
```

## Document Enrichment with LLMs

Automatically enrich documents with AI-generated metadata:

```python
# Simple enrichment
dataset.enrich({
    "summary": "Write a 2-3 sentence summary",
    "key_points": "List 3-5 key points as a JSON array",
    "tags": "Generate 5-7 relevant tags",
    "custom_metadata": {
        "prompt": "Extract: {topics: [], difficulty: 'beginner|intermediate|advanced', type: 'tutorial|reference|guide'}",
        "format": "json"
    }
})

# Advanced enrichment with custom prompts
enrichment_config = {
    "context": {
        "prompt": "Explain who would benefit from reading this document and why",
        "max_tokens": 150
    },
    "custom_metadata": {
        "technical_terms": {
            "prompt": "List all technical terms and acronyms used",
            "format": "json"
        },
        "prerequisites": {
            "prompt": "What knowledge is required to understand this document?",
            "format": "text"
        }
    }
}

dataset.enrich(enrichment_config, where="status = 'published'")
```

## Batch Import from Files

Import documents from a directory:

```python
from pathlib import Path
import frontmatter  # pip install python-frontmatter

def import_markdown_directory(directory, dataset):
    """Import all markdown files with frontmatter."""
    
    imported = []
    errors = []
    
    for md_file in Path(directory).rglob("*.md"):
        try:
            # Parse frontmatter
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Create document
            doc = FrameRecord.create(
                title=post.get('title', md_file.stem),
                content=post.content,
                author=post.get('author', 'Unknown'),
                tags=post.get('tags', []),
                source_file=str(md_file),
                custom_metadata={
                    'date': str(post.get('date', '')),
                    'category': post.get('category', 'uncategorized'),
                    'frontmatter': dict(post.metadata)
                }
            )
            
            imported.append(doc)
            
        except Exception as e:
            errors.append((str(md_file), str(e)))
    
    # Add embeddings in batch
    if imported:
        embedded = embed_frames(imported, batch_size=50, show_progress=True)
        dataset.add_many(embedded)
    
    return {
        'imported': len(imported),
        'errors': errors
    }

# Usage
result = import_markdown_directory("./blog", dataset)
print(f"Imported {result['imported']} documents")
if result['errors']:
    print(f"Errors: {len(result['errors'])}")
```

## Export and Backup

Export documents in various formats:

```python
from contextframe.io import FrameSetExporter, ExportFormat

# Create exporter
exporter = FrameSetExporter(dataset)

# Export a collection to Markdown
exporter.export_collection(
    "python-tutorials",
    "exports/python-tutorials/",
    format=ExportFormat.MARKDOWN,
    single_file=False  # One file per document
)

# Export search results to JSON
results = dataset.full_text_search("API design")
doc_ids = [doc.uuid for doc in results]

exporter.export_documents(
    doc_ids,
    "exports/api-design-docs.json",
    format=ExportFormat.JSON
)

# Backup entire dataset
import shutil
shutil.copytree("my_dataset.lance", "backups/my_dataset_backup.lance")
```

## Performance Optimization

Tips for working with large datasets:

```python
# 1. Use batch operations
docs = [create_document(i) for i in range(10000)]
dataset.add_many(docs, batch_size=1000)

# 2. Create indices for faster queries
dataset.create_vector_index(
    index_type="IVF_PQ",
    num_partitions=256,
    num_sub_quantizers=16
)
dataset.create_scalar_index("status")
dataset.create_scalar_index("author")

# 3. Use projections to read only needed columns
scanner = dataset.scanner(
    columns=["uuid", "title", "tags"],
    filter="status = 'published'"
)
for batch in scanner.to_batches():
    process_batch(batch)

# 4. Compact dataset periodically
dataset.compact_files()
dataset.cleanup_old_versions()

# 5. Monitor dataset health
stats = dataset.stats()
print(f"Fragments: {stats.num_fragments}")
print(f"Version: {stats.version}")
print(f"Size: {stats.dataset_size / 1024 / 1024:.2f} MB")
```

## Next Steps

These examples demonstrate core ContextFrame capabilities. To learn more:

1. Explore [Advanced Search Techniques](../modules/search-query.md)
2. Learn about [Custom Connectors](../integration/connectors/custom.md)
3. Understand [Performance Tuning](../mcp/guides/performance.md)
4. Browse the [Cookbook](../cookbook/index.md) for more examples

## Complete Example: Research Paper Manager

Here's a complete example combining multiple features:

```python
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from datetime import datetime
import json

class ResearchPaperManager:
    def __init__(self, dataset_name="research_papers.lance"):
        self.dataset = FrameDataset.create(dataset_name)
        self._ensure_indices()
        
    def _ensure_indices(self):
        """Create indices if they don't exist."""
        try:
            self.dataset.create_vector_index()
            self.dataset.create_scalar_index("year")
            self.dataset.create_scalar_index("field")
        except:
            pass  # Indices already exist
            
    def add_paper(self, title, abstract, authors, year, field, pdf_path=None):
        """Add a research paper to the collection."""
        
        paper = FrameRecord.create(
            title=title,
            content=abstract,
            author=authors[0] if authors else "Unknown",
            record_type="document",
            tags=[field, f"year:{year}", "research-paper"],
            custom_metadata={
                "all_authors": authors,
                "year": year,
                "field": field,
                "pdf_path": pdf_path,
                "added_date": datetime.now().isoformat()
            }
        )
        
        # Add embeddings
        paper = embed_frames([paper])[0]
        
        self.dataset.add(paper)
        return paper.uuid
        
    def find_similar_papers(self, paper_id, k=5):
        """Find papers similar to a given paper."""
        
        paper = self.dataset.get(paper_id)
        similar = self.dataset.knn_search(
            paper.embedding,
            k=k+1,  # +1 because it will include itself
            filter=f"uuid != '{paper_id}'"
        )
        
        return similar[:k]
        
    def search_by_year_range(self, start_year, end_year):
        """Find papers within a year range."""
        
        results = self.dataset.scanner(
            filter=f"custom_metadata.year >= {start_year} AND custom_metadata.year <= {end_year}"
        ).to_table()
        
        return [self.dataset.get(row['uuid']) for row in results.to_pylist()]
        
    def generate_reading_list(self, topic, max_papers=10):
        """Generate a reading list on a topic."""
        
        # Search for relevant papers
        query = FrameRecord.create(content=topic)
        query_embedded = embed_frames([query])[0]
        
        papers = self.dataset.knn_search(
            query_embedded.embedding,
            k=max_papers
        )
        
        # Create a frameset for the reading list
        reading_list = self.dataset.create_frameset(
            title=f"Reading List: {topic}",
            content=f"Curated papers on: {topic}",
            query=topic,
            source_records=[(p.uuid, p.metadata['title']) for p in papers],
            tags=["reading-list", "generated"]
        )
        
        return papers, reading_list.uuid

# Usage
manager = ResearchPaperManager()

# Add papers
paper_id = manager.add_paper(
    title="Attention Is All You Need",
    abstract="The dominant sequence transduction models...",
    authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
    year=2017,
    field="machine-learning"
)

# Find similar papers
similar = manager.find_similar_papers(paper_id)
print("Similar papers:")
for paper in similar:
    print(f"- {paper.metadata['title']} ({paper.metadata['custom_metadata']['year']})")

# Generate reading list
papers, list_id = manager.generate_reading_list("transformer architectures")
print(f"\nReading list created: {list_id}")
```