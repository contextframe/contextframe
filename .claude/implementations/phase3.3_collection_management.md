# Phase 3.3: Collection Management Tools

## Overview

Phase 3.3 implements comprehensive collection management capabilities for the MCP server, enabling users to organize documents into logical groups with metadata, hierarchies, and templates. Collections provide a powerful way to manage related documents, track relationships, and apply consistent metadata across document sets.

## Core Concepts

### What is a Collection?

A collection in ContextFrame is a logical grouping of documents with:
- A header document (record_type: collection_header) containing metadata
- Member documents that belong to the collection
- Optional hierarchy (collections can contain sub-collections)
- Shared metadata that can be applied to all members
- Statistics and analytics about the collection contents

### Collection Use Cases

1. **Project Documentation**: Group all docs for a project (README, API docs, guides)
2. **Research Papers**: Organize papers by topic, author, or conference
3. **Knowledge Base**: Hierarchical organization of support articles
4. **Training Data**: Curated sets of documents for ML/AI training
5. **Version Control**: Group documents by release or version

## Implementation Timeline

**Duration**: 1 week (Part of Phase 3, Week 3)

1. **Day 1-2**: Schema design and core data structures
2. **Day 3-4**: CRUD operations implementation
3. **Day 5**: Statistics and analytics
4. **Day 6**: Template system
5. **Day 7**: Testing and documentation

## Tool Specifications

### 1. create_collection

Creates a new collection with header and initial configuration.

**Schema**:
```python
class CreateCollectionParams(BaseModel):
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Collection metadata")
    parent_collection: Optional[str] = Field(None, description="Parent collection ID for hierarchies")
    template: Optional[str] = Field(None, description="Template name to apply")
    initial_members: Optional[List[str]] = Field(default_factory=list, description="Document IDs to add")
```

**Response**:
```python
{
    "collection_id": "uuid",
    "header_id": "uuid",
    "name": "Project Alpha Docs",
    "created_at": "2024-01-15T10:00:00Z",
    "member_count": 0,
    "metadata": {...}
}
```

### 2. update_collection

Updates collection properties and metadata.

**Schema**:
```python
class UpdateCollectionParams(BaseModel):
    collection_id: str = Field(..., description="Collection ID to update")
    name: Optional[str] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    metadata_updates: Optional[Dict[str, Any]] = Field(None, description="Metadata to update")
    add_members: Optional[List[str]] = Field(default_factory=list, description="Document IDs to add")
    remove_members: Optional[List[str]] = Field(default_factory=list, description="Document IDs to remove")
```

### 3. delete_collection

Deletes a collection and optionally its members.

**Schema**:
```python
class DeleteCollectionParams(BaseModel):
    collection_id: str = Field(..., description="Collection ID to delete")
    delete_members: bool = Field(False, description="Also delete member documents")
    recursive: bool = Field(False, description="Delete sub-collections recursively")
```

### 4. list_collections

Lists all collections with filtering and statistics.

**Schema**:
```python
class ListCollectionsParams(BaseModel):
    parent_id: Optional[str] = Field(None, description="Filter by parent collection")
    include_stats: bool = Field(True, description="Include member statistics")
    include_empty: bool = Field(True, description="Include collections with no members")
    sort_by: Literal["name", "created_at", "member_count"] = Field("name")
    limit: int = Field(100, description="Maximum collections to return")
```

### 5. move_documents

Moves documents between collections.

**Schema**:
```python
class MoveDocumentsParams(BaseModel):
    document_ids: List[str] = Field(..., description="Documents to move")
    source_collection: Optional[str] = Field(None, description="Source collection (None for uncollected)")
    target_collection: Optional[str] = Field(None, description="Target collection (None to remove from collection)")
    update_metadata: bool = Field(True, description="Apply target collection metadata")
```

### 6. get_collection_stats

Gets detailed analytics for a collection.

**Schema**:
```python
class GetCollectionStatsParams(BaseModel):
    collection_id: str = Field(..., description="Collection ID")
    include_member_details: bool = Field(False, description="Include per-member statistics")
    include_subcollections: bool = Field(True, description="Include sub-collection stats")
```

**Response**:
```python
{
    "collection_id": "uuid",
    "name": "Research Papers 2024",
    "statistics": {
        "total_members": 150,
        "direct_members": 120,
        "subcollection_members": 30,
        "total_size_bytes": 25000000,
        "avg_document_size": 166666,
        "unique_tags": ["ml", "nlp", "cv"],
        "date_range": {
            "earliest": "2024-01-01",
            "latest": "2024-01-15"
        },
        "member_types": {
            "document": 145,
            "collection_header": 5
        }
    },
    "subcollections": [...],
    "metadata": {...}
}
```

## Collection Templates

Templates provide pre-configured collection structures for common use cases.

### Built-in Templates

1. **project_template**:
   - README → overview
   - src/ → implementation
   - docs/ → documentation
   - tests/ → validation

2. **research_template**:
   - Papers by year
   - Papers by topic
   - Papers by author
   - Citations network

3. **knowledge_base_template**:
   - Categories → subcategories → articles
   - FAQ section
   - Troubleshooting guides

### Template Schema

```python
class CollectionTemplate(BaseModel):
    name: str
    description: str
    structure: Dict[str, Any]  # Hierarchical structure definition
    default_metadata: Dict[str, Any]
    naming_pattern: str  # e.g., "{year}-{topic}"
    auto_organize_rules: List[Dict[str, Any]]  # Rules for auto-organization
```

## Implementation Details

### File Structure

```
contextframe/mcp/collections/
├── __init__.py
├── tools.py          # Collection tool implementations
├── schemas.py        # Collection-specific schemas
├── templates.py      # Template definitions and loader
└── stats.py         # Statistics calculation utilities
```

### Core Classes

```python
# collections/tools.py
class CollectionTools:
    """Collection management tools for MCP server."""
    
    def __init__(self, dataset: FrameDataset, transport: TransportAdapter):
        self.dataset = dataset
        self.transport = transport
        self.templates = TemplateRegistry()
    
    async def create_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collection with header."""
        ...
    
    async def update_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update collection properties."""
        ...
    
    # ... other tool methods
```

### Collection Header Schema

Collections use a special header document with record_type="collection_header":

```python
{
    "record_type": "collection_header",
    "title": "Collection Name",
    "context": "Collection description and purpose",
    "metadata": {
        "collection_metadata": {
            "created_at": "2024-01-15T10:00:00Z",
            "template": "project_template",
            "parent_collection": "parent-uuid",
            "member_count": 42,
            "total_size": 1048576,
            "shared_metadata": {
                # Metadata applied to all members
            }
        }
    },
    "relationships": [
        {
            "type": "contains",
            "target": "member-doc-uuid",
            "title": "Member document"
        }
    ]
}
```

### Relationship Management

Collections use the existing relationship system:
- Header → Members: "contains" relationship
- Members → Header: "member_of" relationship
- Collection → Subcollection: "parent/child" relationships

## Testing Strategy

### Unit Tests

1. Test each collection tool independently
2. Mock FrameDataset operations
3. Verify schema validation
4. Test error handling

### Integration Tests

1. Full collection lifecycle (create, update, add members, stats, delete)
2. Hierarchical collections
3. Template application
4. Bulk operations with collections
5. Cross-transport compatibility

### Test Scenarios

```python
# test_collection_tools.py
class TestCollectionTools:
    async def test_create_project_collection(self):
        """Test creating a project collection with template."""
        
    async def test_move_documents_between_collections(self):
        """Test moving documents preserves relationships."""
        
    async def test_collection_statistics(self):
        """Test accurate statistics calculation."""
        
    async def test_hierarchical_collections(self):
        """Test parent/child collection relationships."""
```

## Security Considerations

1. **Access Control**: Collections can have access restrictions
2. **Metadata Validation**: Ensure metadata doesn't leak sensitive info
3. **Size Limits**: Prevent collections from growing too large
4. **Recursive Operations**: Limit depth to prevent DoS

## Performance Optimizations

1. **Lazy Loading**: Don't load all members unless requested
2. **Cached Statistics**: Cache collection stats with TTL
3. **Batch Operations**: Optimize bulk membership changes
4. **Index Usage**: Use collection indexes for fast queries

## Success Metrics

- Create collection in < 100ms
- List 1000 collections in < 500ms
- Move 100 documents in < 1s
- Calculate stats for 10k member collection in < 2s
- Template application in < 200ms

## Migration Path

For existing datasets without collections:
1. Auto-create "Uncategorized" collection
2. Provide migration tool to organize existing docs
3. Preserve all existing relationships
4. No breaking changes to document structure