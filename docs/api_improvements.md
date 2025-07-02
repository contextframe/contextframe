# ContextFrame API Improvements Analysis

Based on the test findings and codebase analysis, here are the identified API improvements for ContextFrame:

## 1. Custom Metadata Constraints

### Current Pain Point
- All values in `custom_metadata` must be strings (lines 151-152 in contextframe_schema.py)
- Complex data like lists, numbers, or nested objects must be serialized as strings
- Example from tests: `custom_metadata["source_excerpts"] = str(source_records)` 

### Better API Design
```python
# Allow native Python types in custom_metadata
custom_metadata = {
    "score": 0.95,  # float
    "tags": ["ai", "ml"],  # list
    "metadata": {"version": 2, "reviewed": True}  # nested dict
}
```

### Implementation Complexity
- **Medium**: Need to update Arrow schema to use a more flexible structure
- Could use JSON serialization internally or support typed structs

### Breaking Change?
- **Yes**: Would require migration of existing datasets
- Alternative: Add a new field `extended_metadata` with flexible types

## 2. Relationship Types

### Current Pain Point
- Only 6 types allowed: parent, child, related, reference, contains, member_of
- JSON schema has 6 types but metadata_utils.py validates only 5 (missing "contains")
- Collections use "member_of" but it's not in the original 5 types

### Better API Design
```python
# Allow custom relationship types with validation
CORE_RELATIONSHIP_TYPES = {...}  # Keep existing
CUSTOM_RELATIONSHIP_PREFIX = "custom:"

# Usage
record.add_relationship(other, relationship_type="custom:derived_from")
```

### Implementation Complexity
- **Low**: Just need to update validation logic
- Keep core types for compatibility, allow prefixed custom types

### Breaking Change?
- **No**: Backward compatible extension

## 3. Status Field Access

### Current Pain Point
- Sometimes accessed as `metadata['status']`, sometimes as `record.status`
- Inconsistent validation - custom statuses are allowed but unclear

### Better API Design
```python
# Define standard statuses but allow custom ones
class Status:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        # Allow any string, but provide constants for common ones
        return isinstance(status, str)
```

### Implementation Complexity
- **Low**: Just documentation and convenience constants

### Breaking Change?
- **No**: Pure addition

## 4. UUID Handling

### Current Pain Point
- UUID is auto-generated and read-only after creation
- Makes testing harder when you need specific UUIDs
- Can't create records with predetermined UUIDs for migration

### Better API Design
```python
# Allow UUID override at creation time
record = FrameRecord.create(
    title="Test",
    content="...",
    uuid="550e8400-e29b-41d4-a716-446655440000"  # Optional
)
```

### Implementation Complexity
- **Low**: Just modify the create() method to accept uuid parameter

### Breaking Change?
- **No**: Backward compatible (uuid remains optional)

## 5. Error Messages

### Current Pain Point
- Validation errors can be unclear: "Invalid metadata: {errors}"
- No indication of which field failed or why

### Better API Design
```python
class ValidationError(Exception):
    def __init__(self, field: str, value: Any, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        super().__init__(f"Field '{field}' with value {value!r} violates {constraint}")
```

### Implementation Complexity
- **Medium**: Need to enhance validation functions throughout

### Breaking Change?
- **No**: Just better error messages

## 6. Search API

### Current Pain Point
- Vector search has bugs (returns empty results on small datasets)
- Full-text search requires manual index creation
- No unified search interface

### Better API Design
```python
# Unified search interface
results = dataset.search(
    query="machine learning",  # Text query
    vector=embedding,          # Vector query (optional)
    filter="status = 'published'",
    mode="hybrid",  # "text", "vector", or "hybrid"
    k=10
)

# Auto-create indexes as needed
dataset.enable_search(text=True, vector=True)  # One-time setup
```

### Implementation Complexity
- **High**: Need to handle index creation, query routing, result merging

### Breaking Change?
- **No**: New API, keep existing methods

## 7. Collection API

### Current Pain Point
- Complex relationship management for collection members
- Mixing of `collection` field and `member_of` relationships
- Header identification through custom_metadata is fragile

### Better API Design
```python
# First-class collection support
collection = dataset.create_collection(
    name="my_collection",
    title="My Document Collection",
    metadata={...}
)

# Simple member management
collection.add_member(record)
collection.remove_member(record)
members = collection.list_members(include_positions=True)

# Direct queries
records = dataset.find_in_collection("my_collection")
```

### Implementation Complexity
- **High**: Need new abstraction layer over existing structure

### Breaking Change?
- **No**: Can be built on top of existing schema

## 8. Additional Improvements

### Batch Operations Enhancement
```python
# Better batch API with progress and error handling
results = dataset.add_many(
    records,
    on_error="continue",  # or "stop"
    progress_callback=lambda i, total: print(f"{i}/{total}")
)
# Returns: {"added": [...], "errors": [...]}
```

### Metadata Shortcuts
```python
# Common metadata as properties
record.tags.add("new-tag")
record.contributors.append("Jane Doe")
record.custom["key"] = "value"  # Shortcut for custom_metadata
```

### Query Builder
```python
# Fluent query interface
results = (dataset.query()
    .filter(status="published")
    .has_tag("important")
    .in_collection("docs")
    .order_by("updated_at", desc=True)
    .limit(10)
    .execute())
```

## Implementation Priority

1. **High Priority** (Quick wins):
   - UUID override support
   - Better error messages
   - Fix relationship type validation

2. **Medium Priority** (Valuable but more work):
   - Flexible custom_metadata types
   - Unified search API
   - Collection management API

3. **Low Priority** (Nice to have):
   - Query builder
   - Metadata shortcuts
   - Advanced batch operations

## Migration Strategy

1. **Phase 1**: Add backward-compatible improvements
   - New optional parameters
   - Additional helper methods
   - Better error messages

2. **Phase 2**: Introduce new APIs alongside old ones
   - Mark old methods as deprecated
   - Provide migration guides

3. **Phase 3**: Major version bump with breaking changes
   - New custom_metadata format
   - Unified APIs
   - Remove deprecated methods