# Data Model

ContextFrame's data model is designed to be both flexible and structured, providing a solid foundation for document management while allowing extensibility for diverse use cases.

## Overview

At its core, ContextFrame represents documents as **FrameRecords** - rich objects that combine:
- **Content**: The primary text or data
- **Metadata**: Structured information about the document
- **Embeddings**: Vector representations for semantic search
- **Binary Data**: Optional raw data (images, PDFs, etc.)
- **Relationships**: Links between documents

## The FrameRecord Class

The `FrameRecord` is the fundamental unit of data in ContextFrame:

```python
from contextframe import FrameRecord
import numpy as np

# Basic structure
class FrameRecord:
    text_content: str                    # Primary textual content
    metadata: dict[str, Any]             # Structured metadata
    vector: np.ndarray | None = None    # Embedding vector
    embed_dim: int = 1536               # Vector dimension
    raw_data: bytes | None = None       # Binary data
    raw_data_type: str | None = None    # MIME type
    path: Path | None = None            # Dataset reference
```

### Creating FrameRecords

The recommended way to create records is using the factory method:

```python
# Simple creation
doc = FrameRecord.create(
    title="Introduction to ContextFrame",
    content="ContextFrame is a powerful document management system...",
    tags=["documentation", "intro"],
    author="Jane Developer"
)

# With all options
doc = FrameRecord.create(
    # Required
    title="Advanced Configuration Guide",
    
    # Content
    content="Detailed configuration options...",
    
    # Standard metadata
    author="Senior Developer",
    version="2.1.0",
    tags=["configuration", "advanced", "guide"],
    status="published",
    
    # Collection membership
    collection="technical-docs",
    collection_id="uuid-of-collection-header",
    collection_position=3,
    
    # Custom metadata
    custom_metadata={
        "difficulty": "advanced",
        "estimated_time": "30 minutes",
        "prerequisites": ["basic-setup", "networking"],
        "last_technical_review": "2024-01-15"
    },
    
    # Record type
    record_type="document",  # or collection_header, dataset_header, frameset
    
    # Binary data
    raw_data=pdf_bytes,
    raw_data_type="application/pdf"
)
```

## Metadata Structure

### Required Fields

Every FrameRecord must have these fields:

| Field | Type | Description | Auto-generated |
|-------|------|-------------|----------------|
| `uuid` | string | Unique identifier | Yes (if not provided) |
| `title` | string | Document title | No |
| `created_at` | ISO datetime | Creation timestamp | Yes |
| `updated_at` | ISO datetime | Last update timestamp | Yes |

### Standard Optional Fields

Commonly used metadata fields:

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Additional context about the document |
| `version` | string | Semantic version (e.g., "1.2.3") |
| `author` | string | Primary author |
| `contributors` | list[string] | Additional contributors |
| `tags` | list[string] | Categorization tags |
| `status` | string | Workflow status (draft, published, archived) |
| `source_type` | string | Origin type (file, api, manual) |
| `source_file` | string | Original file path |
| `source_url` | string | Web URL if applicable |
| `collection` | string | Collection name |
| `collection_id` | string | UUID of collection header |
| `collection_position` | integer | Order within collection |

### Custom Metadata

The `custom_metadata` field allows arbitrary key-value pairs:

```python
custom_metadata = {
    # Domain-specific fields
    "department": "Engineering",
    "project_code": "PROJ-2024-001",
    "compliance": ["SOC2", "HIPAA"],
    
    # Processing metadata
    "word_count": 1523,
    "language": "en",
    "sentiment_score": 0.85,
    
    # External references
    "jira_ticket": "ENG-4521",
    "confluence_page": "12345",
    
    # Workflow data
    "review_status": "pending",
    "reviewers": ["alice", "bob"],
    "due_date": "2024-02-01"
}
```

**Storage Note**: Custom metadata is stored as a list of key-value structs in Lance for efficient columnar storage.

## Record Types

The `record_type` field categorizes documents logically:

### 1. Document (Default)
Standard content documents:
```python
doc = FrameRecord.create(
    title="API Reference",
    content="...",
    record_type="document"  # Usually omitted as it's default
)
```

### 2. Collection Header
Metadata document describing a collection:
```python
header = FrameRecord.create(
    title="Q1 2024 Reports",
    content="Quarterly financial and operational reports",
    record_type="collection_header",
    collection="q1-2024-reports",
    custom_metadata={
        "collection_type": "quarterly_reports",
        "fiscal_year": 2024,
        "quarter": 1
    }
)
```

### 3. Dataset Header
Self-describing dataset metadata:
```python
dataset_header = FrameRecord.create(
    title="Customer Support Knowledge Base",
    content="Contains support articles, FAQs, and troubleshooting guides",
    record_type="dataset_header",
    custom_metadata={
        "dataset_version": "2.0",
        "last_full_update": "2024-01-01",
        "primary_language": "en",
        "total_documents": 1523
    }
)
```

### 4. FrameSet
LLM-generated analysis documents:
```python
# Usually created by dataset.create_frameset()
frameset = FrameRecord(
    text_content="Analysis of Q4 performance shows...",
    metadata={
        "title": "Q4 Performance Analysis",
        "record_type": "frameset",
        "query": "Analyze Q4 performance metrics",
        "relationships": [
            {"type": "contains", "id": "doc1-uuid"},
            {"type": "contains", "id": "doc2-uuid"}
        ]
    }
)
```

## Embeddings and Vectors

ContextFrame has first-class support for vector embeddings:

```python
from contextframe.embed import embed_frames

# Add embeddings to documents
docs = [doc1, doc2, doc3]
embedded_docs = embed_frames(
    docs,
    model="text-embedding-3-small",  # OpenAI model
    embed_dim=1536,                   # Dimension
    batch_size=100                    # Process in batches
)

# Access embeddings
vector = embedded_docs[0].vector  # numpy array
dimension = embedded_docs[0].embed_dim  # 1536
```

### Supported Embedding Models

- **OpenAI**: text-embedding-3-small, text-embedding-3-large
- **Cohere**: embed-english-v3.0, embed-multilingual-v3.0
- **Local**: Sentence transformers, custom models

## Binary Data Support

Store images, PDFs, and other binary content:

```python
# Store an image
with open("diagram.png", "rb") as f:
    image_data = f.read()

doc = FrameRecord.create(
    title="System Architecture Diagram",
    content="High-level system architecture showing all components",
    raw_data=image_data,
    raw_data_type="image/png"
)

# Store a PDF
with open("report.pdf", "rb") as f:
    pdf_data = f.read()

doc = FrameRecord.create(
    title="Annual Report 2023",
    content="Complete annual report including financials",
    raw_data=pdf_data,
    raw_data_type="application/pdf"
)
```

**Note**: Binary data is stored in Lance blob columns, enabling lazy loading for efficiency.

## Relationships

Documents can be linked through the relationships array:

### Relationship Structure

```python
relationship = {
    "type": str,           # Relationship type
    "id": str,            # Target UUID (one of these)
    "uri": str,           # Target URI
    "path": str,          # Target path
    "cid": str,           # IPFS CID
    "title": str,         # Optional title
    "description": str    # Optional description
}
```

### Relationship Types

1. **parent/child**: Hierarchical organization
```python
chapter.add_relationship(
    book.uuid,
    relationship_type="child",
    title="Chapter 3: Advanced Topics"
)
```

2. **related**: General association
```python
doc.add_relationship(
    other_doc.uuid,
    relationship_type="related",
    description="Alternative implementation approach"
)
```

3. **reference**: Citation or dependency
```python
article.add_relationship(
    source.uuid,
    relationship_type="reference",
    title="Smith et al., 2023"
)
```

4. **member_of**: Collection membership
```python
doc.add_relationship(
    collection_header.uuid,
    relationship_type="member_of"
)
```

5. **contains**: Inverse of member_of
```python
frameset.add_relationship(
    source_doc.uuid,
    relationship_type="contains",
    description="Excerpt used in analysis"
)
```

### Working with Relationships

```python
# Add relationships
doc.add_relationship("uuid-123", "related", title="See also")
doc.add_relationship("uuid-456", "reference")

# Access relationships
for rel in doc.metadata.get("relationships", []):
    print(f"{rel['type']}: {rel.get('title', rel['id'])}")

# Query by relationship
related_docs = dataset.find_related(doc.uuid)
children = dataset.find_children(parent.uuid)
```

## Schema Validation

All FrameRecords are validated against the ContextFrame schema:

```python
# Validation happens automatically
try:
    doc = FrameRecord.create(
        # Missing required 'title'
        content="Some content"
    )
except ValueError as e:
    print(f"Validation error: {e}")

# Manual validation
from contextframe.schema import validate_record

is_valid, errors = validate_record(doc.metadata)
if not is_valid:
    print(f"Schema errors: {errors}")
```

## Best Practices

### 1. Use Descriptive Titles
```python
# Good
title = "PostgreSQL Connection Pooling Best Practices"

# Too vague
title = "Database Tips"
```

### 2. Consistent Tagging
```python
# Develop a taxonomy
tags = [
    "category:tutorial",     # Category prefix
    "tech:postgresql",       # Technology
    "level:intermediate",    # Difficulty
    "topic:performance"      # Specific topic
]
```

### 3. Rich Custom Metadata
```python
custom_metadata = {
    # Searchable fields
    "keywords": ["pooling", "connection", "performance"],
    
    # Structured data
    "target_versions": ["14.x", "15.x", "16.x"],
    
    # Metrics
    "view_count": 0,
    "helpful_votes": 0,
    
    # Workflow
    "needs_update": False,
    "update_frequency": "quarterly"
}
```

### 4. Relationship Documentation
```python
# Always include title/description for clarity
doc.add_relationship(
    target_id,
    relationship_type="reference",
    title="Original research paper",
    description="Foundational work this tutorial is based on"
)
```

### 5. Version Management
```python
# Use semantic versioning
doc = FrameRecord.create(
    title="Configuration Guide",
    version="2.1.0",  # major.minor.patch
    custom_metadata={
        "changelog": "Added cloud deployment section",
        "previous_version": "2.0.3"
    }
)
```

## Advanced Patterns

### Document Templates
```python
class DocumentTemplates:
    @staticmethod
    def technical_article(title, content, author, tech_stack):
        return FrameRecord.create(
            title=title,
            content=content,
            author=author,
            tags=["article", "technical"] + tech_stack,
            status="draft",
            record_type="document",
            custom_metadata={
                "content_type": "technical_article",
                "tech_stack": tech_stack,
                "peer_reviewed": False,
                "code_examples": content.count("```")
            }
        )
    
    @staticmethod
    def meeting_notes(title, date, attendees, content):
        return FrameRecord.create(
            title=f"Meeting Notes: {title}",
            content=content,
            author=attendees[0],  # First attendee as author
            contributors=attendees[1:],  # Rest as contributors
            tags=["meeting", "notes"],
            custom_metadata={
                "meeting_date": date.isoformat(),
                "attendees": attendees,
                "content_type": "meeting_notes"
            }
        )
```

### Computed Fields
```python
def enrich_document(doc):
    """Add computed metadata to document."""
    content = doc.text_content
    
    # Add computed fields
    doc.metadata['custom_metadata'].update({
        'word_count': len(content.split()),
        'char_count': len(content),
        'estimated_reading_time': f"{len(content.split()) // 200} minutes",
        'has_code': '```' in content,
        'has_links': 'http' in content or 'https' in content,
        'complexity_score': calculate_complexity(content)
    })
    
    return doc
```

## Next Steps

- Learn about the [Schema System](schema-system.md)
- Understand the [Storage Layer](storage-layer.md)
- Explore [Collections & Relationships](collections-relationships.md)
- See [Record Types](record-types.md) in detail