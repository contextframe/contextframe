# ContextFrame API Improvements Proposal (v0.2.0)

Based on extensive testing and user feedback, this document proposes API improvements for ContextFrame v0.2.0.

## 1. Custom Metadata Type Support

### Current Issue
All custom metadata values must be strings, forcing awkward conversions:
```python
# Current (awkward)
custom_metadata = {
    "priority": "1",        # String conversion required
    "published": "true",    # Boolean as string
    "score": "0.95"        # Float as string
}
```

### Proposed Improvement
Support native Python types with automatic serialization:
```python
# Proposed
custom_metadata = {
    "priority": 1,          # Native int
    "published": True,      # Native bool
    "score": 0.95,         # Native float
    "tags": ["a", "b"],    # Lists allowed
    "meta": {"k": "v"}     # Nested dicts allowed
}
```

### Implementation
- Serialize to JSON strings internally for Lance compatibility
- Deserialize on read to restore original types
- Maintain backward compatibility with string values

## 2. Enhanced Relationship Management

### Current Issues
- Missing "member_of" relationship type (used by collections)
- No bulk relationship operations
- Complex bidirectional relationship setup

### Proposed Improvements

#### Add Missing Relationship Type
```python
# Add to valid types
RELATIONSHIP_TYPES = [
    "parent", "child", "related", "reference", 
    "contains", "member_of"  # Add member_of
]
```

#### Bulk Relationship Operations
```python
# Proposed API
record.add_relationships([
    (doc1, "reference"),
    (doc2, "related"),
    (doc3, "member_of")
])

# Query relationships
refs = record.get_relationships("reference")
all_rels = record.get_all_relationships()
```

## 3. Consistent Field Access

### Current Issue
Inconsistent access patterns for metadata fields:
```python
# Current (inconsistent)
title = record.title                    # Direct property
status = record.metadata.get('status')  # Via metadata
author = record.author                   # Direct property
```

### Proposed Improvement
Add property shortcuts for common metadata fields:
```python
# Proposed
@property
def status(self):
    return self.metadata.get('status', 'draft')

@status.setter
def status(self, value):
    self.metadata['status'] = value

# Usage
record.status = "published"  # Clean API
```

## 4. Flexible UUID Handling

### Current Issue
UUIDs are read-only, making testing difficult:
```python
# Current
record = FrameRecord.create(title="Test")
# Cannot set custom UUID for testing
```

### Proposed Improvement
Allow UUID override at creation:
```python
# Proposed
record = FrameRecord.create(
    title="Test",
    uuid="custom-test-uuid-123"  # Optional UUID override
)
```

## 5. Unified Search API

### Current Issues
- Full-text search requires manual index creation
- Vector search has compatibility bugs
- No unified search interface

### Proposed Improvement
```python
# Proposed unified search API
class SearchBuilder:
    def text(self, query: str):
        """Add text search criteria"""
        return self
    
    def vector(self, embedding: np.ndarray):
        """Add vector similarity criteria"""
        return self
    
    def filter(self, expression: str):
        """Add SQL filter"""
        return self
    
    def within_collection(self, collection: str):
        """Limit to collection"""
        return self
    
    def limit(self, k: int):
        """Set result limit"""
        return self
    
    def execute(self) -> list[FrameRecord]:
        """Run the search"""
        pass

# Usage
results = dataset.search() \
    .text("machine learning") \
    .vector(query_embedding) \
    .filter("status = 'published'") \
    .within_collection("docs") \
    .limit(10) \
    .execute()
```

## 6. Improved Collection API

### Current Issue
Collection management requires manual relationship handling:
```python
# Current (complex)
member.add_relationship(header, "member_of")
```

### Proposed Improvement
```python
# Proposed collection API
collection = dataset.create_collection(
    name="docs_v2",
    title="Documentation v2",
    description="Latest documentation"
)

# Add members
collection.add_member(doc1, position=0)
collection.add_members([doc2, doc3, doc4])

# Query collection
members = collection.get_members(ordered=True)
header = collection.header
```

## 7. Better Error Messages

### Current Issue
Generic validation errors without field context:
```python
# Current
ValidationError: "1 is not of type 'string'"
```

### Proposed Improvement
```python
# Proposed
ValidationError: "Field 'custom_metadata.priority': Expected string, got int (1). 
                 Convert to string or wait for v0.2.0 which supports native types."
```

## 8. Auto-indexing for Search

### Current Issue
Manual index creation required:
```python
# Current
dataset.create_fts_index()  # Must remember to do this
results = dataset.full_text_search("query")
```

### Proposed Improvement
```python
# Proposed
results = dataset.full_text_search("query", auto_index=True)
# Automatically creates index if missing
```

## Implementation Priority

### Phase 1 (v0.1.3) - Non-breaking improvements
1. Add "member_of" to relationship types ✓
2. Better error messages
3. UUID override at creation
4. Auto-indexing option

### Phase 2 (v0.2.0) - Enhanced APIs
1. Native type support in custom_metadata
2. Property shortcuts for metadata fields
3. Bulk relationship operations
4. Collection management API

### Phase 3 (v0.3.0) - Advanced features
1. Unified search API with query builder
2. Streaming/async operations
3. Advanced indexing strategies

## Migration Guide

### For v0.1.3 (non-breaking)
```python
# No changes required, just new features available
record = FrameRecord.create(title="Test", uuid="custom-id")
```

### For v0.2.0 (with deprecations)
```python
# Old way (still works but deprecated)
record.metadata['status'] = 'published'

# New way (recommended)
record.status = 'published'

# Custom metadata migration
# Old way
meta = {"count": "42", "active": "true"}

# New way
meta = {"count": 42, "active": True}
```

## Backward Compatibility

All improvements will maintain backward compatibility where possible:
- String values in custom_metadata continue to work
- Old metadata access patterns remain functional
- Existing relationship types unchanged
- Current search methods preserved

## Testing Strategy

1. Add comprehensive tests for each new feature
2. Ensure all existing tests pass
3. Add migration tests to verify compatibility
4. Performance benchmarks for new APIs

## Feedback Requested

Please provide feedback on:
1. Which improvements are most valuable to your use case
2. Any additional pain points not addressed
3. Concerns about breaking changes
4. Preferred migration timeline