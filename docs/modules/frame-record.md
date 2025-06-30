# FrameRecord

The `FrameRecord` class represents individual documents in ContextFrame. It combines content, metadata, embeddings, and relationships into a unified structure that can be efficiently stored and queried.

## Overview

A `FrameRecord` consists of:
- **Text Content**: The primary document content
- **Metadata**: Structured information (title, author, tags, etc.)
- **Vector**: Optional embedding for semantic search
- **Binary Data**: Optional raw data (PDFs, images, etc.)
- **Relationships**: Links to other documents

## Creating Records

### Basic Creation

```python
from contextframe import FrameRecord
from datetime import datetime

# Simple document
doc = FrameRecord.create(
    title="Introduction to Python",
    content="Python is a high-level programming language..."
)

# With additional metadata
doc = FrameRecord.create(
    title="Advanced Python Patterns",
    content="This guide covers advanced Python design patterns...",
    author="Jane Developer",
    tags=["python", "advanced", "patterns"],
    version="2.0.0",
    status="published"
)
```

### Complete Example

```python
# All available parameters
doc = FrameRecord.create(
    # Required
    title="Comprehensive API Guide",
    
    # Content fields
    content="Detailed description of the API...",
    text_content="Full text content for indexing...",  # If different from content
    
    # Standard metadata
    author="Senior Developer",
    contributors=["Dev1", "Dev2"],
    version="3.1.0",
    tags=["api", "guide", "reference"],
    status="published",  # draft, published, archived, deleted
    
    # Source tracking
    source_type="file",  # file, api, manual
    source_file="/docs/api-guide.md",
    source_url="https://example.com/api-guide",
    
    # Collection membership
    collection="technical-documentation",
    collection_id="uuid-of-collection-header",
    collection_position=5,
    
    # Record type
    record_type="document",  # document, collection_header, dataset_header, frameset
    
    # Custom metadata
    custom_metadata={
        "department": "Engineering",
        "difficulty": "intermediate",
        "estimated_time": "45 minutes",
        "prerequisites": ["rest-api-basics", "authentication"],
        "last_reviewed": "2024-01-15"
    },
    
    # Binary data
    raw_data=pdf_bytes,
    raw_data_type="application/pdf",
    
    # System fields (usually auto-generated)
    uuid="custom-uuid-if-needed",
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)
```

## Working with Metadata

### Accessing Metadata

```python
# Access standard fields
print(f"Title: {doc.metadata['title']}")
print(f"Author: {doc.metadata.get('author', 'Unknown')}")
print(f"Tags: {doc.metadata.get('tags', [])}")
print(f"Created: {doc.metadata['created_at']}")

# Access custom metadata
custom = doc.metadata.get('custom_metadata', {})
print(f"Department: {custom.get('department')}")
print(f"Priority: {custom.get('priority', 'normal')}")

# Safe access with defaults
status = doc.metadata.get('status', 'draft')
version = doc.metadata.get('version', '1.0.0')
```

### Modifying Metadata

```python
# Update standard fields
doc.metadata['status'] = 'archived'
doc.metadata['updated_at'] = datetime.now().isoformat()

# Add or update tags
if 'tags' not in doc.metadata:
    doc.metadata['tags'] = []
doc.metadata['tags'].append('important')
doc.metadata['tags'] = list(set(doc.metadata['tags']))  # Remove duplicates

# Update custom metadata
if 'custom_metadata' not in doc.metadata:
    doc.metadata['custom_metadata'] = {}
doc.metadata['custom_metadata']['reviewed'] = True
doc.metadata['custom_metadata']['review_date'] = datetime.now().isoformat()

# Add contributor
if 'contributors' not in doc.metadata:
    doc.metadata['contributors'] = []
doc.metadata['contributors'].append('New Contributor')
```

### Metadata Validation

```python
def validate_document_metadata(doc):
    """Validate document metadata completeness."""
    errors = []
    warnings = []
    
    # Required fields
    if not doc.metadata.get('title'):
        errors.append("Missing required field: title")
    
    if not doc.metadata.get('uuid'):
        errors.append("Missing required field: uuid")
    
    # Recommended fields
    if not doc.metadata.get('author'):
        warnings.append("Missing recommended field: author")
    
    if not doc.metadata.get('tags'):
        warnings.append("No tags specified")
    
    # Custom validation
    custom = doc.metadata.get('custom_metadata', {})
    if custom.get('difficulty') not in ['beginner', 'intermediate', 'advanced', None]:
        errors.append("Invalid difficulty level")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

# Usage
validation = validate_document_metadata(doc)
if not validation['valid']:
    print("Errors:", validation['errors'])
```

## Content Management

### Text Content

```python
# Set content
doc = FrameRecord.create(
    title="My Document",
    content="Brief description",
    text_content="Full document text that will be indexed for search..."
)

# Access content
print(f"Content: {doc.text_content}")
print(f"Length: {len(doc.text_content)} characters")
print(f"Word count: {len(doc.text_content.split())} words")

# Update content
doc.text_content = "Updated content..."
doc.metadata['updated_at'] = datetime.now().isoformat()
```

### Binary Data

```python
# Store image
with open("diagram.png", "rb") as f:
    image_data = f.read()

doc = FrameRecord.create(
    title="Architecture Diagram",
    content="System architecture overview",
    raw_data=image_data,
    raw_data_type="image/png"
)

# Store PDF
with open("report.pdf", "rb") as f:
    pdf_data = f.read()

doc = FrameRecord.create(
    title="Annual Report",
    content="2023 Annual Report",
    raw_data=pdf_data,
    raw_data_type="application/pdf"
)

# Access binary data
if doc.raw_data:
    print(f"Binary data type: {doc.raw_data_type}")
    print(f"Binary data size: {len(doc.raw_data)} bytes")
    
    # Save to file
    with open("output.pdf", "wb") as f:
        f.write(doc.raw_data)
```

### Content Processing

```python
def process_document_content(doc):
    """Process and enrich document content."""
    content = doc.text_content
    
    # Extract and add metadata
    doc.metadata['custom_metadata'].update({
        'word_count': len(content.split()),
        'char_count': len(content),
        'line_count': len(content.splitlines()),
        'has_code': '```' in content,
        'has_urls': 'http://' in content or 'https://' in content,
        'language': detect_language(content),
        'reading_time': f"{len(content.split()) // 200} min"
    })
    
    # Extract headings
    headings = []
    for line in content.splitlines():
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            heading = line.lstrip('#').strip()
            headings.append({'level': level, 'text': heading})
    
    doc.metadata['custom_metadata']['headings'] = headings
    
    return doc
```

## Embeddings

### Adding Embeddings

```python
from contextframe.embed import embed_frames
import numpy as np

# Single document
doc = FrameRecord.create(title="ML Tutorial", content="...")
embedded_doc = embed_frames([doc], model="text-embedding-3-small")[0]

# Access embedding
print(f"Embedding shape: {embedded_doc.vector.shape}")
print(f"Embedding dimension: {embedded_doc.embed_dim}")

# Manual embedding
embedding = generate_embedding(doc.text_content)  # Your embedding function
doc.vector = np.array(embedding, dtype=np.float32)
doc.embed_dim = len(embedding)
```

### Working with Embeddings

```python
def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def find_similar_documents(target_doc, all_docs, threshold=0.8):
    """Find documents similar to target based on embeddings."""
    if target_doc.vector is None:
        return []
    
    similar = []
    for doc in all_docs:
        if doc.vector is not None and doc.uuid != target_doc.uuid:
            similarity = cosine_similarity(target_doc.vector, doc.vector)
            if similarity >= threshold:
                similar.append({
                    'document': doc,
                    'similarity': similarity
                })
    
    # Sort by similarity
    similar.sort(key=lambda x: x['similarity'], reverse=True)
    return similar
```

## Relationships

### Adding Relationships

```python
# Simple relationship
doc.add_relationship("target-uuid", "related")

# With metadata
doc.add_relationship(
    "target-uuid",
    relationship_type="reference",
    title="Source Document",
    description="Original research this work is based on"
)

# Multiple relationships
doc.add_relationship("parent-uuid", "child")
doc.add_relationship("collection-uuid", "member_of")
doc.add_relationship("ref1-uuid", "reference", title="Smith et al., 2023")
doc.add_relationship("ref2-uuid", "reference", title="Jones, 2022")

# External relationships
doc.add_relationship(
    uri="https://example.com/resource",
    relationship_type="reference",
    title="External Resource"
)

doc.add_relationship(
    path="/docs/related-guide.md",
    relationship_type="related",
    title="Related Guide"
)
```

### Relationship Types

```python
# 1. Parent/Child - Hierarchical structure
book = FrameRecord.create(title="Python Cookbook", record_type="collection_header")
chapter = FrameRecord.create(title="Chapter 1: Basics")
section = FrameRecord.create(title="1.1 Variables and Types")

chapter.add_relationship(book.uuid, "child")
section.add_relationship(chapter.uuid, "child")

# 2. Related - General associations
doc1 = FrameRecord.create(title="REST API Design")
doc2 = FrameRecord.create(title="GraphQL Best Practices")
doc1.add_relationship(doc2.uuid, "related", 
                     description="Alternative API approach")

# 3. Reference - Citations and sources
article = FrameRecord.create(title="Modern Web Architecture")
source = FrameRecord.create(title="Microservices Patterns")
article.add_relationship(source.uuid, "reference",
                        title="Fowler, 2018",
                        description="Chapter 3: Communication Patterns")

# 4. Member Of - Collection membership
tutorial = FrameRecord.create(title="Async Python Tutorial")
series = FrameRecord.create(
    title="Python Advanced Series",
    record_type="collection_header"
)
tutorial.add_relationship(series.uuid, "member_of")

# 5. Contains - Inverse of member_of (used by framesets)
frameset = FrameRecord(
    metadata={
        "title": "Analysis Summary",
        "record_type": "frameset"
    }
)
frameset.add_relationship(doc1.uuid, "contains",
                         description="Used section 2.3")
```

### Managing Relationships

```python
def get_relationships(doc, relationship_type=None):
    """Get relationships of specific type or all."""
    relationships = doc.metadata.get('relationships', [])
    
    if relationship_type:
        return [r for r in relationships if r['type'] == relationship_type]
    return relationships

def remove_relationship(doc, target_id=None, relationship_type=None):
    """Remove specific relationships."""
    if 'relationships' not in doc.metadata:
        return
    
    original_count = len(doc.metadata['relationships'])
    
    doc.metadata['relationships'] = [
        r for r in doc.metadata['relationships']
        if not (
            (target_id is None or r.get('id') == target_id) and
            (relationship_type is None or r['type'] == relationship_type)
        )
    ]
    
    removed = original_count - len(doc.metadata['relationships'])
    return removed

def update_relationship(doc, target_id, updates):
    """Update existing relationship metadata."""
    for rel in doc.metadata.get('relationships', []):
        if rel.get('id') == target_id:
            rel.update(updates)
            return True
    return False
```

## Record Types

### Document Type (Default)

```python
# Standard content document
doc = FrameRecord.create(
    title="User Guide",
    content="How to use the application...",
    record_type="document"  # Can be omitted as it's default
)
```

### Collection Header

```python
# Describes a collection of documents
collection_header = FrameRecord.create(
    title="API Documentation Suite",
    content="Complete API documentation including guides and references",
    record_type="collection_header",
    collection="api-docs",
    custom_metadata={
        "collection_type": "documentation",
        "version": "2.0",
        "total_documents": 45,
        "last_updated": "2024-01-20",
        "maintainers": ["api-team@company.com"]
    }
)

# Add documents to collection
api_guide = FrameRecord.create(
    title="API Getting Started",
    content="...",
    collection="api-docs",
    collection_position=1
)
api_guide.add_relationship(collection_header.uuid, "member_of")
```

### Dataset Header

```python
# Self-describing dataset metadata
dataset_header = FrameRecord.create(
    title="Customer Support Knowledge Base",
    content="Contains all support articles, FAQs, and troubleshooting guides",
    record_type="dataset_header",
    custom_metadata={
        "dataset_version": "3.0.0",
        "schema_version": "2.0",
        "created_date": "2023-01-01",
        "last_full_update": "2024-01-15",
        "update_frequency": "daily",
        "primary_language": "en",
        "supported_languages": ["en", "es", "fr", "de"],
        "total_documents": 5234,
        "data_sources": ["zendesk", "confluence", "github-wiki"],
        "contact": "support-team@company.com"
    }
)
```

### FrameSet

```python
# AI-generated synthesis (usually created by dataset.create_frameset())
frameset = FrameRecord(
    text_content="Based on the analyzed documents, here are the key findings...",
    metadata={
        "uuid": str(uuid.uuid4()),
        "title": "Quarterly Performance Analysis",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "record_type": "frameset",
        "query": "Analyze Q4 2023 performance metrics",
        "model": "gpt-4",
        "source_count": 15,
        "relationships": [
            {"type": "contains", "id": "doc1-uuid", "title": "Q4 Sales Report"},
            {"type": "contains", "id": "doc2-uuid", "title": "Q4 Marketing Data"},
            # ... more source documents
        ]
    }
)
```

## Serialization

### To/From Dictionary

```python
# Convert to dictionary
doc_dict = doc.to_dict()
print(json.dumps(doc_dict, indent=2))

# Create from dictionary
doc_data = {
    "text_content": "Document content...",
    "metadata": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "title": "My Document",
        "created_at": "2024-01-20T10:00:00Z",
        "updated_at": "2024-01-20T10:00:00Z",
        "tags": ["important"]
    }
}
doc = FrameRecord.from_dict(doc_data)
```

### To/From Arrow

```python
import pyarrow as pa

# Convert to Arrow
arrow_dict = doc.to_arrow()
# Creates a dictionary compatible with Arrow schema

# Create from Arrow row
table = dataset.scanner().to_table()
for row in table.to_pylist():
    doc = FrameRecord.from_arrow(row)
    print(f"Loaded: {doc.metadata['title']}")
```

### JSON Serialization

```python
import json

def save_record_to_json(doc, filepath):
    """Save FrameRecord to JSON file."""
    doc_dict = doc.to_dict()
    
    # Convert numpy array to list for JSON
    if doc_dict.get('vector') is not None:
        doc_dict['vector'] = doc_dict['vector'].tolist()
    
    # Convert bytes to base64 for JSON
    if doc_dict.get('raw_data') is not None:
        import base64
        doc_dict['raw_data'] = base64.b64encode(
            doc_dict['raw_data']
        ).decode('utf-8')
    
    with open(filepath, 'w') as f:
        json.dump(doc_dict, f, indent=2)

def load_record_from_json(filepath):
    """Load FrameRecord from JSON file."""
    with open(filepath, 'r') as f:
        doc_dict = json.load(f)
    
    # Convert list back to numpy array
    if doc_dict.get('vector') is not None:
        doc_dict['vector'] = np.array(doc_dict['vector'], dtype=np.float32)
    
    # Convert base64 back to bytes
    if doc_dict.get('raw_data') is not None:
        import base64
        doc_dict['raw_data'] = base64.b64decode(doc_dict['raw_data'])
    
    return FrameRecord.from_dict(doc_dict)
```

## Validation

### Schema Validation

```python
from contextframe.schema import validate_metadata

# Automatic validation on creation
try:
    doc = FrameRecord.create(
        # Missing required 'title'
        content="Some content"
    )
except ValueError as e:
    print(f"Validation error: {e}")

# Manual validation
is_valid, errors = validate_metadata(doc.metadata)
if not is_valid:
    for error in errors:
        print(f"Schema error: {error}")

# Custom validation
def validate_custom_rules(doc):
    """Apply custom business rules."""
    errors = []
    
    # Title length
    if len(doc.metadata['title']) > 200:
        errors.append("Title too long (max 200 characters)")
    
    # Required custom fields
    custom = doc.metadata.get('custom_metadata', {})
    if not custom.get('department'):
        errors.append("Department is required")
    
    # Tag requirements
    tags = doc.metadata.get('tags', [])
    if len(tags) < 2:
        errors.append("At least 2 tags required")
    
    return len(errors) == 0, errors
```

## Best Practices

### 1. Consistent Metadata

```python
def create_document_template(doc_type):
    """Create consistent document templates."""
    templates = {
        'technical': {
            'tags': ['technical'],
            'custom_metadata': {
                'document_type': 'technical',
                'difficulty': 'intermediate',
                'requires_review': True
            }
        },
        'tutorial': {
            'tags': ['tutorial', 'educational'],
            'custom_metadata': {
                'document_type': 'tutorial',
                'difficulty': 'beginner',
                'includes_exercises': True
            }
        },
        'reference': {
            'tags': ['reference'],
            'status': 'published',
            'custom_metadata': {
                'document_type': 'reference',
                'version_controlled': True
            }
        }
    }
    
    return templates.get(doc_type, {})

# Usage
template = create_document_template('tutorial')
doc = FrameRecord.create(
    title="Python Basics Tutorial",
    content="...",
    **template
)
```

### 2. Metadata Enrichment

```python
def enrich_metadata(doc):
    """Add computed metadata to document."""
    content = doc.text_content
    
    # Text statistics
    doc.metadata['custom_metadata'].update({
        'statistics': {
            'word_count': len(content.split()),
            'char_count': len(content),
            'sentence_count': content.count('.') + content.count('!') + content.count('?'),
            'avg_word_length': sum(len(word) for word in content.split()) / len(content.split())
        }
    })
    
    # Content analysis
    doc.metadata['custom_metadata'].update({
        'content_features': {
            'has_code_blocks': '```' in content,
            'has_links': 'http' in content,
            'has_images': '![' in content,
            'has_tables': '|' in content and '---' in content,
            'has_lists': '- ' in content or '* ' in content or '1. ' in content
        }
    })
    
    # Update timestamp
    doc.metadata['updated_at'] = datetime.now().isoformat()
    
    return doc
```

### 3. Relationship Management

```python
class RelationshipManager:
    """Helper for managing document relationships."""
    
    @staticmethod
    def create_hierarchy(parent, children):
        """Create parent-child relationships."""
        for i, child in enumerate(children):
            child.add_relationship(
                parent.uuid,
                "child",
                title=f"Part of {parent.metadata['title']}"
            )
            # Add position if in collection
            if parent.metadata.get('collection'):
                child.metadata['collection'] = parent.metadata['collection']
                child.metadata['collection_position'] = i + 1
    
    @staticmethod
    def link_related(docs, bidirectional=True):
        """Link related documents."""
        for i, doc1 in enumerate(docs):
            for doc2 in docs[i+1:]:
                doc1.add_relationship(
                    doc2.uuid,
                    "related",
                    title=doc2.metadata['title']
                )
                if bidirectional:
                    doc2.add_relationship(
                        doc1.uuid,
                        "related",
                        title=doc1.metadata['title']
                    )
    
    @staticmethod
    def add_references(doc, references):
        """Add reference relationships."""
        for ref in references:
            doc.add_relationship(
                ref['uuid'],
                "reference",
                title=ref.get('citation', ref.get('title')),
                description=ref.get('description')
            )
```

### 4. Error Handling

```python
def safe_create_record(**kwargs):
    """Create record with comprehensive error handling."""
    try:
        # Validate required fields
        if 'title' not in kwargs:
            raise ValueError("Title is required")
        
        # Create record
        doc = FrameRecord.create(**kwargs)
        
        # Validate custom rules
        is_valid, errors = validate_custom_rules(doc)
        if not is_valid:
            raise ValueError(f"Custom validation failed: {errors}")
        
        return doc
        
    except ValueError as e:
        print(f"Validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error creating record: {e}")
        return None

def safe_update_metadata(doc, updates):
    """Safely update document metadata."""
    try:
        # Backup current metadata
        backup = doc.metadata.copy()
        
        # Apply updates
        doc.metadata.update(updates)
        
        # Validate
        is_valid, errors = validate_metadata(doc.metadata)
        if not is_valid:
            # Rollback
            doc.metadata = backup
            raise ValueError(f"Invalid metadata: {errors}")
        
        # Update timestamp
        doc.metadata['updated_at'] = datetime.now().isoformat()
        return True
        
    except Exception as e:
        print(f"Error updating metadata: {e}")
        return False
```

## Advanced Patterns

### Document Versioning

```python
class VersionedDocument:
    """Wrapper for document versioning."""
    
    def __init__(self, doc):
        self.current = doc
        self.versions = []
    
    def create_version(self, changes, version_note=""):
        """Create a new version of the document."""
        # Clone current document
        new_version = FrameRecord.create(
            title=self.current.metadata['title'],
            content=self.current.text_content,
            **{k: v for k, v in self.current.metadata.items() 
               if k not in ['uuid', 'created_at', 'updated_at']}
        )
        
        # Apply changes
        for key, value in changes.items():
            if key == 'content':
                new_version.text_content = value
            else:
                new_version.metadata[key] = value
        
        # Update version
        current_version = self.current.metadata.get('version', '1.0.0')
        major, minor, patch = map(int, current_version.split('.'))
        
        # Determine version increment
        if 'content' in changes:
            minor += 1
            patch = 0
        else:
            patch += 1
        
        new_version.metadata['version'] = f"{major}.{minor}.{patch}"
        new_version.metadata['version_note'] = version_note
        new_version.metadata['previous_version'] = self.current.uuid
        
        # Link versions
        new_version.add_relationship(
            self.current.uuid,
            "reference",
            title=f"Previous version ({current_version})"
        )
        
        # Archive current
        self.versions.append(self.current)
        self.current = new_version
        
        return new_version
```

### Document Templates

```python
class DocumentFactory:
    """Factory for creating consistent documents."""
    
    @staticmethod
    def create_api_doc(endpoint, method, description, parameters=None):
        """Create API documentation."""
        content = f"""# {method} {endpoint}

{description}

## Parameters
"""
        if parameters:
            for param in parameters:
                content += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
        
        return FrameRecord.create(
            title=f"API: {method} {endpoint}",
            content=content,
            tags=["api", "reference", method.lower()],
            custom_metadata={
                "api_endpoint": endpoint,
                "http_method": method,
                "parameters": parameters or [],
                "document_type": "api_reference"
            }
        )
    
    @staticmethod
    def create_meeting_notes(title, date, attendees, agenda, notes):
        """Create meeting notes document."""
        content = f"""# Meeting: {title}

**Date**: {date}
**Attendees**: {', '.join(attendees)}

## Agenda
{agenda}

## Notes
{notes}
"""
        
        return FrameRecord.create(
            title=f"Meeting Notes: {title} - {date}",
            content=content,
            author=attendees[0] if attendees else "Unknown",
            contributors=attendees[1:] if len(attendees) > 1 else [],
            tags=["meeting", "notes"],
            custom_metadata={
                "meeting_date": date,
                "attendees": attendees,
                "document_type": "meeting_notes"
            }
        )
```

## Next Steps

- Explore [Embeddings](embeddings.md) for semantic search
- Learn about [Enrichment](enrichment.md) techniques
- Understand [Search & Query](search-query.md) patterns
- See [Import/Export](import-export.md) for data migration
- Check the [API Reference](../api/frame-record.md) for all methods