# Collections & Relationships

ContextFrame provides powerful mechanisms for organizing documents into collections and establishing relationships between them. This enables you to model complex document hierarchies, cross-references, and semantic connections.

## Collections Overview

Collections are logical groupings of related documents. They help organize large datasets and provide context for document relationships.

### Collection Patterns

There are two primary patterns for implementing collections:

#### 1. Simple Collections (Tag-Based)

The simplest approach uses the `collection` field:

```python
# Create documents in a collection
doc1 = FrameRecord.create(
    title="Chapter 1: Introduction",
    content="...",
    collection="python-tutorial"
)

doc2 = FrameRecord.create(
    title="Chapter 2: Basic Syntax", 
    content="...",
    collection="python-tutorial"
)

dataset.add_many([doc1, doc2])

# Query collection members
members = dataset.scanner(
    filter="collection = 'python-tutorial'"
).to_table()
```

#### 2. Header-Based Collections

For richer collection metadata, use collection headers:

```python
# Create collection header
header = FrameRecord.create(
    title="Python Tutorial Series",
    content="""
    A comprehensive Python tutorial covering basics to advanced topics.
    Target audience: Beginners to intermediate developers.
    """,
    record_type="collection_header",
    collection="python-tutorial",
    custom_metadata={
        "collection_type": "tutorial_series",
        "difficulty": "beginner",
        "total_chapters": 12,
        "author": "Tutorial Team",
        "version": "3.0"
    }
)
dataset.add(header)

# Add documents with relationships
chapter = FrameRecord.create(
    title="Chapter 1: Introduction",
    content="...",
    collection="python-tutorial",
    collection_position=1
)
chapter.add_relationship(
    header.uuid,
    relationship_type="member_of",
    title="Part of Python Tutorial Series"
)
dataset.add(chapter)
```

### Collection Operations

#### Retrieving Collection Members

```python
# Get all members of a collection
def get_collection_members(dataset, collection_name):
    members = dataset.scanner(
        filter=f"collection = '{collection_name}'",
        columns=["uuid", "title", "collection_position"]
    ).to_table().to_pylist()
    
    # Sort by position if available
    return sorted(members, key=lambda x: x.get('collection_position', 0))

# Get collection with header
def get_collection_with_header(dataset, collection_name):
    # Find header
    headers = dataset.scanner(
        filter=f"collection = '{collection_name}' AND record_type = 'collection_header'"
    ).to_table().to_pylist()
    
    header = headers[0] if headers else None
    
    # Get members
    members = dataset.scanner(
        filter=f"collection = '{collection_name}' AND record_type != 'collection_header'"
    ).to_table().to_pylist()
    
    return {
        'header': header,
        'members': sorted(members, key=lambda x: x.get('collection_position', 0))
    }
```

#### Collection Statistics

```python
def get_collection_stats(dataset):
    """Get statistics about all collections."""
    stats = {}
    
    # Count documents per collection
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            collection = row.get('collection')
            if collection:
                if collection not in stats:
                    stats[collection] = {
                        'count': 0,
                        'has_header': False,
                        'types': set()
                    }
                stats[collection]['count'] += 1
                stats[collection]['types'].add(row.get('record_type', 'document'))
                if row.get('record_type') == 'collection_header':
                    stats[collection]['has_header'] = True
    
    return stats
```

### Collection Best Practices

1. **Use Consistent Naming**
```python
# Good - consistent, descriptive
collection_names = [
    "api-v2-docs",
    "user-guides-2024",
    "internal-kb-engineering"
]

# Avoid - inconsistent
collection_names = [
    "API Docs",
    "user_guides",
    "Internal KB"
]
```

2. **Include Collection Headers**
```python
def create_collection(name, description, metadata=None):
    """Create a collection with header."""
    header = FrameRecord.create(
        title=name,
        content=description,
        record_type="collection_header",
        collection=name.lower().replace(' ', '-'),
        custom_metadata=metadata or {}
    )
    return header
```

3. **Track Collection Position**
```python
def add_to_collection(dataset, doc, collection_name, position=None):
    """Add document to collection with position."""
    if position is None:
        # Auto-increment position
        members = get_collection_members(dataset, collection_name)
        position = len(members) + 1
    
    doc.metadata['collection'] = collection_name
    doc.metadata['collection_position'] = position
    
    # Find and link to header
    headers = dataset.scanner(
        filter=f"collection = '{collection_name}' AND record_type = 'collection_header'"
    ).to_table().to_pylist()
    
    if headers:
        doc.add_relationship(headers[0]['uuid'], 'member_of')
    
    return doc
```

## Relationships

Relationships create explicit connections between documents, enabling graph-like navigation and queries.

### Relationship Types

ContextFrame supports six standard relationship types:

#### 1. Parent/Child
Hierarchical relationships:
```python
# Book -> Chapter -> Section
book = FrameRecord.create(title="Python Mastery", record_type="collection_header")
chapter = FrameRecord.create(title="Chapter 1: Basics")
section = FrameRecord.create(title="1.1 Variables")

# Establish hierarchy
chapter.add_relationship(book.uuid, "child")
section.add_relationship(chapter.uuid, "child")

# Or reverse
book.add_relationship(chapter.uuid, "parent")
chapter.add_relationship(section.uuid, "parent")
```

#### 2. Related
General associations:
```python
# Cross-references between documents
doc1 = FrameRecord.create(title="API Authentication Guide")
doc2 = FrameRecord.create(title="Security Best Practices")

doc1.add_relationship(
    doc2.uuid,
    "related",
    title="See also: Security Best Practices",
    description="Related security considerations"
)
```

#### 3. Reference
Citations and dependencies:
```python
# Academic citations
paper = FrameRecord.create(title="Novel ML Approach")
citation = FrameRecord.create(title="Foundation Research")

paper.add_relationship(
    citation.uuid,
    "reference",
    title="Smith et al., 2023",
    description="Builds upon their classification method"
)
```

#### 4. Member Of
Collection membership:
```python
# Document belongs to collection
article.add_relationship(
    collection_header.uuid,
    "member_of",
    title="Part of User Guide"
)
```

#### 5. Contains
Inverse of member_of:
```python
# FrameSet contains source documents
frameset.add_relationship(
    source_doc.uuid,
    "contains",
    description="Used excerpt from section 2.3"
)
```

### Relationship Structure

Each relationship has this structure:
```python
relationship = {
    "type": "related",              # Required
    "id": "uuid-of-target",         # One of these
    "uri": "https://...",           # identifiers
    "path": "/docs/guide.md",       # is required
    "cid": "ipfs://...",           
    "title": "Human readable",      # Optional
    "description": "Details..."     # Optional
}
```

### Creating Relationships

#### Using add_relationship Method
```python
# Simple relationship
doc.add_relationship("target-uuid", "related")

# With metadata
doc.add_relationship(
    "target-uuid",
    "reference",
    title="Primary Source",
    description="Original research this work is based on"
)

# Multiple relationships
doc.add_relationship("uuid1", "related")
doc.add_relationship("uuid2", "reference") 
doc.add_relationship("uuid3", "child")
```

#### Direct Manipulation
```python
# Initialize relationships
doc.metadata['relationships'] = []

# Add relationship
doc.metadata['relationships'].append({
    "type": "related",
    "id": "target-uuid",
    "title": "Related Document"
})
```

### Querying Relationships

#### Finding Related Documents
```python
def find_related_documents(dataset, doc_uuid, relationship_type=None):
    """Find all documents related to a given document."""
    doc = dataset.get(doc_uuid)
    related = []
    
    for rel in doc.metadata.get('relationships', []):
        if relationship_type and rel['type'] != relationship_type:
            continue
            
        # Get related document by ID
        if 'id' in rel:
            try:
                related_doc = dataset.get(rel['id'])
                related.append({
                    'document': related_doc,
                    'relationship': rel
                })
            except KeyError:
                pass  # Document not found
    
    return related
```

#### Finding Reverse Relationships
```python
def find_documents_referencing(dataset, target_uuid):
    """Find all documents that reference the target."""
    referencing = []
    
    # This requires scanning all documents
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            relationships = row.get('relationships', [])
            for rel in relationships:
                if rel.get('id') == target_uuid:
                    referencing.append({
                        'uuid': row['uuid'],
                        'title': row['title'],
                        'relationship_type': rel['type']
                    })
    
    return referencing
```

#### Building Relationship Graphs
```python
def build_relationship_graph(dataset, start_uuid, max_depth=3):
    """Build a graph of relationships starting from a document."""
    visited = set()
    graph = {'nodes': [], 'edges': []}
    
    def traverse(uuid, depth=0):
        if uuid in visited or depth > max_depth:
            return
            
        visited.add(uuid)
        
        try:
            doc = dataset.get(uuid)
            graph['nodes'].append({
                'id': uuid,
                'title': doc.metadata['title'],
                'type': doc.metadata.get('record_type', 'document')
            })
            
            for rel in doc.metadata.get('relationships', []):
                if 'id' in rel:
                    graph['edges'].append({
                        'source': uuid,
                        'target': rel['id'],
                        'type': rel['type']
                    })
                    traverse(rel['id'], depth + 1)
                    
        except KeyError:
            pass
    
    traverse(start_uuid)
    return graph
```

## Advanced Patterns

### Hierarchical Collections

Create multi-level collection structures:

```python
def create_hierarchical_collection(dataset, structure):
    """
    Create a hierarchical collection from a structure dict.
    
    Example structure:
    {
        'title': 'Documentation',
        'children': [
            {
                'title': 'User Guide',
                'children': [
                    {'title': 'Getting Started'},
                    {'title': 'Advanced Features'}
                ]
            },
            {
                'title': 'API Reference',
                'children': [...]
            }
        ]
    }
    """
    def create_node(node, parent_id=None, collection_name=None, position=1):
        # Create record
        record = FrameRecord.create(
            title=node['title'],
            content=node.get('content', ''),
            record_type='collection_header' if 'children' in node else 'document',
            collection=collection_name,
            collection_position=position
        )
        
        # Add parent relationship
        if parent_id:
            record.add_relationship(parent_id, 'child')
        
        # Add to dataset
        dataset.add(record)
        
        # Process children
        if 'children' in node:
            child_collection = f"{collection_name}-{record.uuid[:8]}"
            for i, child in enumerate(node['children'], 1):
                create_node(child, record.uuid, child_collection, i)
        
        return record
    
    root_collection = structure['title'].lower().replace(' ', '-')
    return create_node(structure, collection_name=root_collection)
```

### Bidirectional Relationships

Maintain relationships in both directions:

```python
def add_bidirectional_relationship(dataset, uuid1, uuid2, type1, type2):
    """Add relationships in both directions."""
    doc1 = dataset.get(uuid1)
    doc2 = dataset.get(uuid2)
    
    # Add forward relationship
    doc1.add_relationship(uuid2, type1)
    
    # Add reverse relationship
    doc2.add_relationship(uuid1, type2)
    
    # Update both documents
    dataset.update_record(uuid1, doc1)
    dataset.update_record(uuid2, doc2)
```

### Relationship Validation

Ensure relationship integrity:

```python
def validate_relationships(dataset):
    """Validate all relationships in dataset."""
    errors = []
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            doc_uuid = row['uuid']
            
            for rel in row.get('relationships', []):
                # Check required fields
                if 'type' not in rel:
                    errors.append(f"{doc_uuid}: Relationship missing type")
                    continue
                
                # Check identifier
                has_id = any(key in rel for key in ['id', 'uri', 'path', 'cid'])
                if not has_id:
                    errors.append(f"{doc_uuid}: Relationship missing identifier")
                
                # Validate UUID references
                if 'id' in rel:
                    try:
                        dataset.get(rel['id'])
                    except KeyError:
                        errors.append(f"{doc_uuid}: Invalid reference to {rel['id']}")
    
    return errors
```

### Collection Templates

Define reusable collection structures:

```python
class CollectionTemplates:
    @staticmethod
    def create_project_documentation(dataset, project_name, version):
        """Create standard project documentation structure."""
        
        # Main collection header
        main_header = FrameRecord.create(
            title=f"{project_name} Documentation v{version}",
            record_type="collection_header",
            collection=f"{project_name.lower()}-docs-v{version}",
            custom_metadata={
                "project": project_name,
                "version": version,
                "created_date": datetime.now().isoformat()
            }
        )
        dataset.add(main_header)
        
        # Standard sections
        sections = [
            ("Getting Started", "Quick start guide and installation"),
            ("User Guide", "Comprehensive user documentation"),
            ("API Reference", "Complete API documentation"),
            ("Examples", "Code examples and tutorials"),
            ("FAQ", "Frequently asked questions")
        ]
        
        for i, (title, description) in enumerate(sections, 1):
            section = FrameRecord.create(
                title=title,
                content=description,
                record_type="collection_header",
                collection=f"{project_name.lower()}-{title.lower().replace(' ', '-')}",
                collection_position=i
            )
            section.add_relationship(main_header.uuid, "child")
            dataset.add(section)
        
        return main_header
```

## Performance Considerations

### Efficient Relationship Queries

```python
# Inefficient - scans all documents
def find_all_children_slow(dataset, parent_uuid):
    children = []
    for doc in dataset.to_table().to_pylist():
        for rel in doc.get('relationships', []):
            if rel.get('id') == parent_uuid and rel['type'] == 'child':
                children.append(doc)
    return children

# Better - use scanner with projection
def find_all_children_fast(dataset, parent_uuid):
    # First, get documents with relationships
    docs_with_rels = dataset.scanner(
        columns=['uuid', 'title', 'relationships'],
        filter="relationships IS NOT NULL"
    ).to_table().to_pylist()
    
    # Filter in memory (still more efficient)
    children = []
    for doc in docs_with_rels:
        for rel in doc.get('relationships', []):
            if rel.get('id') == parent_uuid and rel['type'] == 'child':
                children.append(doc['uuid'])
    
    # Batch retrieve
    return [dataset.get(uuid) for uuid in children]
```

### Caching Relationship Data

```python
class RelationshipCache:
    def __init__(self, dataset):
        self.dataset = dataset
        self._cache = {}
        self._reverse_cache = {}
        self.build_cache()
    
    def build_cache(self):
        """Build forward and reverse relationship caches."""
        for batch in self.dataset.to_batches():
            for row in batch.to_pylist():
                uuid = row['uuid']
                self._cache[uuid] = []
                
                for rel in row.get('relationships', []):
                    self._cache[uuid].append(rel)
                    
                    # Build reverse cache
                    target = rel.get('id')
                    if target:
                        if target not in self._reverse_cache:
                            self._reverse_cache[target] = []
                        self._reverse_cache[target].append({
                            'source': uuid,
                            'type': rel['type']
                        })
    
    def get_relationships(self, uuid):
        """Get all relationships for a document."""
        return self._cache.get(uuid, [])
    
    def get_reverse_relationships(self, uuid):
        """Get all documents pointing to this one."""
        return self._reverse_cache.get(uuid, [])
```

## Best Practices

1. **Use Collections for Logical Grouping**
   - Group related documents
   - Provide context via headers
   - Track position for ordering

2. **Use Relationships for Semantic Connections**
   - Link related concepts
   - Build navigable structures
   - Track dependencies

3. **Document Relationship Semantics**
   - Always include title/description
   - Use consistent relationship types
   - Validate relationships regularly

4. **Consider Performance**
   - Batch relationship operations
   - Cache for complex queries
   - Use appropriate indices

5. **Maintain Integrity**
   - Validate references exist
   - Clean up broken relationships
   - Consider bidirectional links

## Next Steps

- Explore [Record Types](record-types.md) in detail
- Learn about [Search & Query](../modules/search-query.md) operations
- See [Collections Example](../cookbook/research-papers.md) in the cookbook
- Understand [Performance Optimization](../mcp/guides/performance.md)