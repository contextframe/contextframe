# Record Types

ContextFrame uses record types to categorize documents based on their purpose and role within a dataset. This type system enables semantic organization and specialized handling of different document categories.

## Overview

The `record_type` field in document metadata identifies the document's purpose:

```python
from contextframe import FrameRecord

# Explicitly set record type
doc = FrameRecord.create(
    title="My Document",
    content="...",
    record_type="document"  # Default if not specified
)
```

## Standard Record Types

ContextFrame defines four standard record types:

### 1. Document (Default)

The most common type for regular content documents.

**Purpose**: Store individual pieces of content like articles, notes, files, or any discrete information unit.

**Characteristics**:
- Default type when `record_type` is not specified
- Represents standalone content
- Can belong to collections
- Can have relationships to other documents

```python
# Examples of document records
article = FrameRecord.create(
    title="Understanding Neural Networks",
    content="Neural networks are computing systems...",
    record_type="document",  # Optional, as it's default
    tags=["ai", "machine-learning", "tutorial"],
    author="Dr. Smith"
)

code_file = FrameRecord.create(
    title="utils.py",
    content="def process_data(input):\n    ...",
    source_file="/src/utils.py",
    tags=["python", "utilities"]
)

meeting_notes = FrameRecord.create(
    title="Team Standup - 2024-01-20",
    content="Discussed progress on Q1 goals...",
    custom_metadata={
        "attendees": ["Alice", "Bob", "Charlie"],
        "duration_minutes": 30
    }
)
```

### 2. Collection Header

Metadata documents that describe and organize collections.

**Purpose**: Provide context, metadata, and organization for groups of related documents.

**Characteristics**:
- Contains information about the collection
- Other documents reference it via relationships
- Can store collection-level metadata
- Helps with discovery and navigation

```python
# Tutorial series header
tutorial_header = FrameRecord.create(
    title="Complete Python Web Development",
    content="""
    A comprehensive tutorial series covering Python web development
    from basics to deployment. Includes 12 chapters with hands-on
    exercises and real-world projects.
    """,
    record_type="collection_header",
    collection="python-web-dev",
    tags=["tutorial", "python", "web-development"],
    custom_metadata={
        "difficulty": "beginner-to-intermediate",
        "estimated_hours": 40,
        "prerequisites": ["basic-python", "html-css"],
        "target_audience": "web developers",
        "chapters": 12,
        "exercises": 48,
        "projects": 3
    }
)

# Research papers collection
research_collection = FrameRecord.create(
    title="Machine Learning Papers 2024",
    content="Curated collection of influential ML papers from 2024",
    record_type="collection_header",
    collection="ml-papers-2024",
    custom_metadata={
        "curator": "AI Research Team",
        "selection_criteria": "Impact factor > 5.0",
        "topics": ["deep-learning", "nlp", "computer-vision"],
        "total_papers": 127
    }
)

# Project documentation header
project_docs = FrameRecord.create(
    title="Project Atlas Documentation",
    content="Complete documentation for Project Atlas v2.0",
    record_type="collection_header",
    collection="atlas-docs-v2",
    version="2.0.0",
    custom_metadata={
        "project_name": "Atlas",
        "documentation_version": "2.0.0",
        "last_updated": "2024-01-15",
        "maintainers": ["docs-team@company.com"]
    }
)
```

### 3. Dataset Header

Self-describing metadata for entire datasets.

**Purpose**: Document the dataset itself, providing context about its purpose, creation, and contents.

**Characteristics**:
- Usually one per dataset
- Contains dataset-level metadata
- Helps with dataset discovery and understanding
- Can track schema versions and changes

```python
# Knowledge base dataset header
kb_header = FrameRecord.create(
    title="Customer Support Knowledge Base",
    content="""
    This dataset contains all customer support articles, FAQs,
    troubleshooting guides, and internal support documentation.
    Updated daily from multiple sources.
    """,
    record_type="dataset_header",
    custom_metadata={
        "dataset_version": "3.1.0",
        "schema_version": "2.0",
        "created_date": "2023-01-01",
        "last_full_sync": "2024-01-20",
        "sources": ["zendesk", "confluence", "github-wiki"],
        "languages": ["en", "es", "fr", "de"],
        "total_documents": 15234,
        "update_frequency": "daily",
        "contact": "support-team@company.com"
    }
)

# Research dataset header
research_dataset = FrameRecord.create(
    title="COVID-19 Research Papers Dataset",
    content="""
    Comprehensive collection of COVID-19 research papers from
    2020-2024, including preprints and peer-reviewed articles.
    """,
    record_type="dataset_header",
    custom_metadata={
        "time_period": "2020-01-01 to 2024-12-31",
        "sources": ["pubmed", "arxiv", "biorxiv", "medrxiv"],
        "inclusion_criteria": "COVID-19 related research",
        "total_papers": 285000,
        "with_embeddings": True,
        "embedding_model": "text-embedding-3-small",
        "license": "CC-BY-4.0"
    }
)

# Training data header
training_data = FrameRecord.create(
    title="Product Reviews Training Dataset",
    content="Labeled product reviews for sentiment analysis training",
    record_type="dataset_header",
    custom_metadata={
        "task": "sentiment-analysis",
        "labels": ["positive", "negative", "neutral"],
        "total_samples": 50000,
        "train_split": 40000,
        "val_split": 5000,
        "test_split": 5000,
        "annotation_guidelines": "url://internal/guidelines",
        "inter_annotator_agreement": 0.92
    }
)
```

### 4. FrameSet

AI-generated synthesis documents created from queries.

**Purpose**: Store the results of AI analysis, summaries, or synthesis operations performed on other documents.

**Characteristics**:
- Created by `dataset.create_frameset()` method
- Contains AI-generated content
- Links to source documents via relationships
- Preserves the original query/prompt
- Includes excerpts from source materials

```python
# Question-answering frameset
qa_frameset = dataset.create_frameset(
    title="Q&A: Best practices for API security",
    content="""
    Based on the analyzed documents, here are the key best practices
    for API security:
    
    1. Use OAuth 2.0 or JWT for authentication
    2. Implement rate limiting and throttling
    3. Always use HTTPS/TLS encryption
    4. Validate and sanitize all inputs
    5. Use API versioning for backward compatibility
    
    These recommendations are based on industry standards and
    security frameworks analyzed from the source documents.
    """,
    query="What are the best practices for API security?",
    source_records=[
        ("uuid-1", "OAuth 2.0 provides secure delegated access..."),
        ("uuid-2", "Rate limiting prevents abuse and ensures..."),
        ("uuid-3", "TLS encryption is mandatory for API traffic...")
    ],
    tags=["security", "api", "best-practices", "generated"]
)

# Analysis frameset
analysis_frameset = dataset.create_frameset(
    title="Sentiment Analysis: Q4 Customer Feedback",
    content="""
    Analysis of Q4 customer feedback reveals:
    - Overall sentiment: 72% positive (up from 68% in Q3)
    - Main pain points: shipping delays, mobile app bugs
    - Positive themes: product quality, customer service
    - Recommendation: Focus on logistics improvements
    """,
    query="Analyze sentiment trends in Q4 customer feedback",
    source_records=[
        ("feedback-1", "5 stars - Great product quality..."),
        ("feedback-2", "2 stars - Shipping took too long..."),
        # ... more source excerpts
    ],
    custom_metadata={
        "analysis_type": "sentiment",
        "time_period": "Q4-2023",
        "total_reviews_analyzed": 5234,
        "confidence_score": 0.89
    }
)

# Summary frameset
summary_frameset = dataset.create_frameset(
    title="Executive Summary: 2023 Annual Report",
    content="""
    Key highlights from the 2023 annual report:
    - Revenue: $45.2M (23% YoY growth)
    - New customers: 1,250 enterprise clients
    - Product launches: 3 major features
    - Market expansion: Entered APAC region
    """,
    query="Summarize key points from 2023 annual report",
    source_records=[
        ("report-uuid", "Total revenue for 2023 reached $45.2M..."),
    ],
    tags=["summary", "annual-report", "2023", "executive"]
)
```

## Working with Record Types

### Querying by Record Type

```python
# Find all collection headers
headers = dataset.scanner(
    filter="record_type = 'collection_header'"
).to_table()

# Get all framesets
framesets = dataset.scanner(
    filter="record_type = 'frameset'"
).to_table()

# Count documents by type
def count_by_type(dataset):
    counts = {}
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            record_type = row.get('record_type', 'document')
            counts[record_type] = counts.get(record_type, 0) + 1
    return counts
```

### Type-Specific Operations

```python
class DatasetOperations:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def get_dataset_header(self):
        """Get the dataset header if it exists."""
        headers = self.dataset.scanner(
            filter="record_type = 'dataset_header'",
            limit=1
        ).to_table().to_pylist()
        return headers[0] if headers else None
    
    def list_collections(self):
        """List all collections with their headers."""
        headers = self.dataset.scanner(
            filter="record_type = 'collection_header'",
            columns=['uuid', 'title', 'collection', 'custom_metadata']
        ).to_table().to_pylist()
        
        collections = []
        for header in headers:
            member_count = len(self.dataset.scanner(
                filter=f"collection = '{header['collection']}' AND record_type = 'document'"
            ).to_table())
            
            collections.append({
                'uuid': header['uuid'],
                'title': header['title'],
                'collection': header['collection'],
                'member_count': member_count,
                'metadata': header.get('custom_metadata', {})
            })
        
        return collections
    
    def get_frameset_sources(self, frameset_uuid):
        """Get source documents for a frameset."""
        frameset = self.dataset.get(frameset_uuid)
        
        if frameset.metadata.get('record_type') != 'frameset':
            raise ValueError("Not a frameset")
        
        sources = []
        for rel in frameset.metadata.get('relationships', []):
            if rel['type'] == 'contains':
                try:
                    source = self.dataset.get(rel['id'])
                    sources.append(source)
                except KeyError:
                    pass  # Source not found
        
        return sources
```

### Type Validation

```python
def validate_record_type(record):
    """Validate record type and required fields."""
    record_type = record.metadata.get('record_type', 'document')
    errors = []
    
    if record_type == 'collection_header':
        # Should have collection field
        if not record.metadata.get('collection'):
            errors.append("Collection headers must have 'collection' field")
            
    elif record_type == 'dataset_header':
        # Should have dataset metadata
        custom = record.metadata.get('custom_metadata', {})
        recommended = ['dataset_version', 'schema_version', 'created_date']
        missing = [f for f in recommended if f not in custom]
        if missing:
            errors.append(f"Dataset header missing recommended fields: {missing}")
            
    elif record_type == 'frameset':
        # Should have query and source relationships
        if not record.metadata.get('query'):
            errors.append("Framesets must have 'query' field")
        
        has_sources = any(
            rel['type'] == 'contains' 
            for rel in record.metadata.get('relationships', [])
        )
        if not has_sources:
            errors.append("Framesets should have 'contains' relationships to sources")
    
    return errors
```

## Custom Record Types

While ContextFrame provides four standard types, you can extend the system:

### Defining Custom Types

```python
# Extended record types for a specific domain
EXTENDED_RECORD_TYPES = [
    "document",
    "collection_header", 
    "dataset_header",
    "frameset",
    # Custom types
    "annotation",      # For labeled data
    "checkpoint",      # For model checkpoints
    "evaluation",      # For evaluation results
    "configuration"    # For config files
]

# Validation for custom types
def validate_custom_type(record):
    record_type = record.metadata.get('record_type')
    
    if record_type == 'annotation':
        # Must have annotation data
        if 'annotations' not in record.metadata.get('custom_metadata', {}):
            raise ValueError("Annotation records must have annotations")
            
    elif record_type == 'checkpoint':
        # Must have model metadata
        required = ['model_name', 'epoch', 'metrics']
        custom = record.metadata.get('custom_metadata', {})
        missing = [f for f in required if f not in custom]
        if missing:
            raise ValueError(f"Checkpoint missing fields: {missing}")
```

### Custom Type Examples

```python
# Annotation record
annotation = FrameRecord.create(
    title="Image annotation - IMG_001.jpg",
    content="Traffic scene with multiple vehicles",
    record_type="annotation",
    source_file="images/IMG_001.jpg",
    custom_metadata={
        "annotations": [
            {"bbox": [100, 100, 200, 200], "label": "car"},
            {"bbox": [300, 150, 400, 250], "label": "truck"}
        ],
        "annotator": "user@example.com",
        "annotation_tool": "labelbox",
        "confidence": 0.95
    }
)

# Configuration record
config = FrameRecord.create(
    title="Production API Configuration",
    content=json.dumps(config_data, indent=2),
    record_type="configuration",
    version="2.1.0",
    custom_metadata={
        "environment": "production",
        "service": "api-gateway",
        "last_modified_by": "ops-team",
        "validation_status": "passed"
    }
)

# Evaluation record
evaluation = FrameRecord.create(
    title="Model Evaluation - BERT-v2",
    content="Evaluation results for BERT-v2 on test set",
    record_type="evaluation",
    custom_metadata={
        "model_name": "BERT-v2",
        "dataset": "GLUE",
        "metrics": {
            "accuracy": 0.924,
            "f1_score": 0.918,
            "precision": 0.921,
            "recall": 0.915
        },
        "test_size": 10000,
        "timestamp": datetime.now().isoformat()
    }
)
```

## Best Practices

### 1. Use Appropriate Types

Choose the right type for your use case:

```python
# Good - clear type usage
header = FrameRecord.create(
    title="API Documentation",
    record_type="collection_header",  # Correct for collection metadata
    collection="api-docs"
)

# Avoid - misusing types
doc = FrameRecord.create(
    title="API Documentation",
    record_type="document",  # Wrong - this is organizing other docs
    collection="api-docs"
)
```

### 2. Include Type-Specific Metadata

```python
# Collection header with rich metadata
collection_header = FrameRecord.create(
    title="Machine Learning Course",
    record_type="collection_header",
    collection="ml-course",
    custom_metadata={
        # Type-specific metadata
        "course_level": "intermediate",
        "duration_hours": 40,
        "modules": 8,
        "exercises": 120,
        "prerequisites": ["python-basics", "linear-algebra"],
        "instructor": "Dr. Jane Smith",
        "last_updated": "2024-01-15"
    }
)
```

### 3. Validate Type Consistency

```python
def ensure_single_dataset_header(dataset):
    """Ensure only one dataset header exists."""
    headers = dataset.scanner(
        filter="record_type = 'dataset_header'"
    ).to_table()
    
    if len(headers) > 1:
        print(f"Warning: Found {len(headers)} dataset headers")
        # Keep the most recent
        headers_list = headers.to_pylist()
        headers_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Remove extra headers
        for header in headers_list[1:]:
            dataset.delete_record(header['uuid'])
```

### 4. Type-Aware Search

```python
class TypeAwareSearch:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def search_documents(self, query, exclude_generated=True):
        """Search only human-created documents."""
        filter_expr = "record_type = 'document'"
        if exclude_generated:
            filter_expr += " AND NOT tags.contains('generated')"
        
        return self.dataset.full_text_search(
            query,
            filter=filter_expr
        )
    
    def search_collections(self, query):
        """Search collection headers."""
        return self.dataset.full_text_search(
            query,
            filter="record_type = 'collection_header'"
        )
    
    def get_generated_content(self, topic):
        """Get AI-generated content on a topic."""
        return self.dataset.full_text_search(
            topic,
            filter="record_type = 'frameset'"
        )
```

## Type Patterns

### Documentation Projects

```python
def setup_documentation_project(dataset, project_name, version):
    """Set up a documentation project with proper types."""
    
    # Dataset header
    dataset_header = FrameRecord.create(
        title=f"{project_name} Documentation Dataset",
        content=f"Complete documentation for {project_name} v{version}",
        record_type="dataset_header",
        custom_metadata={
            "project": project_name,
            "version": version,
            "doc_version": "1.0",
            "created": datetime.now().isoformat()
        }
    )
    dataset.add(dataset_header)
    
    # Main sections as collection headers
    sections = [
        "Getting Started",
        "User Guide", 
        "API Reference",
        "Examples"
    ]
    
    for section in sections:
        header = FrameRecord.create(
            title=f"{project_name} - {section}",
            content=f"{section} documentation for {project_name}",
            record_type="collection_header",
            collection=f"{project_name.lower()}-{section.lower().replace(' ', '-')}"
        )
        header.add_relationship(dataset_header.uuid, "child")
        dataset.add(header)
```

### Research Datasets

```python
def create_research_dataset(dataset, study_name, papers):
    """Create a research dataset with proper structure."""
    
    # Dataset header with study metadata
    study_header = FrameRecord.create(
        title=f"{study_name} Research Dataset",
        record_type="dataset_header",
        custom_metadata={
            "study_name": study_name,
            "paper_count": len(papers),
            "date_range": "2020-2024",
            "inclusion_criteria": "Peer-reviewed only",
            "fields": ["machine-learning", "nlp"]
        }
    )
    dataset.add(study_header)
    
    # Add papers as documents
    for paper in papers:
        doc = FrameRecord.create(
            title=paper['title'],
            content=paper['abstract'],
            record_type="document",
            author=paper['authors'][0],
            custom_metadata={
                "doi": paper['doi'],
                "journal": paper['journal'],
                "year": paper['year'],
                "citations": paper['citation_count']
            }
        )
        dataset.add(doc)
```

## Next Steps

Now that you understand record types:

- Learn about [Module Guides](../modules/frame-dataset.md) for practical usage
- Explore [Search & Query](../modules/search-query.md) with type filters
- See [Integration Guides](../integration/overview.md) for importing typed content
- Browse [Cookbook Examples](../cookbook/index.md) using different types