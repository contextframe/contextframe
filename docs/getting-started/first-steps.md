# First Steps with ContextFrame

This guide will walk you through your first interactions with ContextFrame, from creating a dataset to performing your first search. By the end, you'll understand the basic workflow and be ready to explore more advanced features.

## Creating Your First Dataset

ContextFrame stores documents in datasets, which are Lance-format directories on your filesystem or cloud storage.

```python
from contextframe import FrameDataset, FrameRecord

# Create a new dataset
dataset = FrameDataset.create("my_first_dataset.lance")
print(f"Created dataset at: {dataset.uri}")
```

!!! info "Dataset Location"
    The `.lance` extension is a directory, not a file. You can explore its contents, but never modify files directly inside it.

## Adding Your First Document

Let's create and add a simple document:

```python
# Create a document
doc = FrameRecord.create(
    title="Welcome to ContextFrame",
    content="""
    ContextFrame is a powerful system for managing documents 
    and their context for AI applications. It provides:
    
    - Structured document storage
    - Vector embeddings for semantic search
    - Rich metadata and relationships
    - Integration with external systems
    """,
    tags=["tutorial", "getting-started"],
    author="ContextFrame Team"
)

# Add to dataset
dataset.add(doc)
print(f"Added document with ID: {doc.uuid}")
```

## Retrieving Documents

### By UUID

```python
# Retrieve by ID
retrieved = dataset.get(doc.uuid)
print(f"Title: {retrieved.metadata['title']}")
print(f"Content preview: {retrieved.text_content[:100]}...")
```

### List All Documents

```python
# Get all documents
all_docs = dataset.to_pandas()
print(f"Total documents: {len(all_docs)}")
print(all_docs[['uuid', 'title', 'created_at']].head())
```

## Basic Search

### By Tags

```python
# Find documents by tag
tutorial_docs = dataset.find_by_tag("tutorial")
for doc in tutorial_docs:
    print(f"- {doc.metadata['title']}")
```

### By Author

```python
# Find documents by author
team_docs = dataset.find_by_author("ContextFrame Team")
print(f"Found {len(team_docs)} documents by the team")
```

### Full-Text Search

```python
# Search document content
results = dataset.full_text_search("semantic search", limit=5)
for doc in results:
    print(f"- {doc.metadata['title']} (score: {doc.score:.2f})")
```

## Adding Metadata

ContextFrame supports rich metadata for organizing and finding documents:

```python
# Create a document with extensive metadata
detailed_doc = FrameRecord.create(
    title="Python Best Practices",
    content="...",
    tags=["python", "programming", "best-practices"],
    author="Jane Developer",
    version="1.0.0",
    status="published",
    custom_metadata={
        "language": "python",
        "difficulty": "intermediate",
        "estimated_reading_time": "10 minutes",
        "last_reviewed": "2024-01-15"
    }
)

dataset.add(detailed_doc)
```

## Working with Collections

Collections help organize related documents:

```python
# Create a collection header
collection_header = FrameRecord.create(
    title="Python Tutorial Series",
    content="A comprehensive guide to Python programming",
    record_type="collection_header",
    collection="python-tutorials"
)
dataset.add(collection_header)

# Add documents to the collection
for i in range(1, 4):
    chapter = FrameRecord.create(
        title=f"Chapter {i}: Python Basics",
        content=f"Content for chapter {i}...",
        collection="python-tutorials",
        collection_position=i,
        tags=["python", "tutorial", f"chapter-{i}"]
    )
    # Create relationship to header
    chapter.add_relationship(collection_header.uuid, relationship_type="member_of")
    dataset.add(chapter)

# Retrieve collection members
members = dataset.get_collection_members("python-tutorials")
print(f"Collection has {len(members)} chapters")
```

## Updating Documents

Documents can be updated while preserving their UUID:

```python
# Retrieve a document
doc = dataset.get(doc.uuid)

# Modify it
doc.metadata['status'] = 'reviewed'
doc.metadata['version'] = '1.1.0'
doc.text_content += "\n\nUpdated: Added new section on advanced features."

# Update in dataset
dataset.update_record(doc.uuid, doc)
print("Document updated successfully")
```

## Deleting Documents

```python
# Delete by UUID
dataset.delete_record(doc.uuid)

# Verify deletion
try:
    deleted = dataset.get(doc.uuid)
except KeyError:
    print("Document successfully deleted")
```

## Exploring Dataset Information

```python
# Dataset statistics
print(f"Total documents: {len(dataset)}")
print(f"Dataset size: {dataset.size_bytes() / 1024 / 1024:.2f} MB")
print(f"Schema version: {dataset.schema.version}")

# List all tags in use
all_tags = set()
for doc in dataset.to_table().to_pylist():
    if doc.get('tags'):
        all_tags.update(doc['tags'])
print(f"Unique tags: {sorted(all_tags)}")

# Count by status
status_counts = {}
for doc in dataset.to_table().to_pylist():
    status = doc.get('status', 'unknown')
    status_counts[status] = status_counts.get(status, 0) + 1
print(f"Documents by status: {status_counts}")
```

## Saving and Loading Datasets

Datasets are automatically persisted to disk:

```python
# Close and reopen dataset
dataset = None  # Close reference

# Open existing dataset
dataset = FrameDataset("my_first_dataset.lance")
print(f"Reopened dataset with {len(dataset)} documents")
```

## Best Practices

### 1. Use Descriptive Titles
```python
# Good
title = "API Authentication Guide - OAuth 2.0 Flow"

# Less descriptive
title = "Auth Guide"
```

### 2. Tag Consistently
```python
# Define a tagging scheme
tags = [
    "category:tutorial",      # Category prefix
    "lang:python",           # Language prefix
    "level:beginner",        # Difficulty level
    "auth",                  # Topic tags
    "oauth2"
]
```

### 3. Leverage Custom Metadata
```python
custom_metadata = {
    "internal_id": "DOC-2024-001",
    "department": "Engineering",
    "review_cycle": "quarterly",
    "compliance": ["SOC2", "GDPR"]
}
```

### 4. Batch Operations
```python
# Instead of adding one by one
docs = []
for i in range(100):
    docs.append(FrameRecord.create(
        title=f"Document {i}",
        content=f"Content {i}"
    ))

# Add all at once
dataset.add_many(docs)
```

## Common Patterns

### Document Templates
```python
def create_blog_post(title, content, author, tags):
    """Create a blog post with standard metadata."""
    return FrameRecord.create(
        title=title,
        content=content,
        author=author,
        tags=tags + ["blog"],
        record_type="document",
        status="draft",
        custom_metadata={
            "content_type": "blog_post",
            "word_count": len(content.split()),
            "created_date": datetime.now().isoformat()
        }
    )
```

### Import from Files
```python
from pathlib import Path

def import_markdown_files(directory, dataset):
    """Import all markdown files from a directory."""
    for md_file in Path(directory).glob("**/*.md"):
        content = md_file.read_text()
        
        # Extract title from first line
        lines = content.split('\n')
        title = lines[0].replace('#', '').strip() if lines else md_file.stem
        
        doc = FrameRecord.create(
            title=title,
            content=content,
            source_file=str(md_file),
            tags=["imported", "markdown"]
        )
        dataset.add(doc)
```

## Next Steps

Now that you understand the basics:

1. Learn about [Adding Embeddings](basic-examples.md#vector-embeddings) for semantic search
2. Explore [External Connectors](../integration/connectors/introduction.md) to import from GitHub, Notion, etc.
3. Understand the [Data Model](../core-concepts/data-model.md) in depth
4. Try [Advanced Search](../modules/search-query.md) techniques

## Quick Reference

```python
# Create dataset
dataset = FrameDataset.create("name.lance")

# Add document
doc = FrameRecord.create(title="...", content="...")
dataset.add(doc)

# Search
dataset.find_by_tag("tag")
dataset.find_by_author("author")
dataset.full_text_search("query")

# Update
dataset.update_record(uuid, updated_doc)

# Delete
dataset.delete_record(uuid)

# Get stats
len(dataset)  # Count
dataset.size_bytes()  # Size
```