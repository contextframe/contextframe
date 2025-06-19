# Collection Metadata and Lance Filtering Analysis

## Problem Statement

The current implementation of collection management tools attempts to filter on `x_collection_metadata.parent_collection` using Lance SQL queries, but this fails because:

1. `x_collection_metadata` is stored in the FrameRecord's metadata dictionary, not as a Lance column
2. Lance can only filter on actual columns defined in the Arrow schema
3. The x_ prefix pattern allows fields at the metadata root, but they're not persisted to Lance

## Current Schema Analysis

### Available Lance Columns (from Arrow schema)

```python
# From contextframe_schema.py
- uuid (string, not null)
- text_content (string)
- vector (list<float32>)
- title (string, not null)
- version (string)
- context (string)
- uri (string)
- local_path (string)
- cid (string)
- collection (string)              # ← Available for filtering
- collection_id (string)           # ← Available for filtering
- collection_id_type (string)      # ← Available for filtering
- position (int32)
- author (string)
- contributors (list<string>)
- created_at (string)
- updated_at (string)
- tags (list<string>)
- status (string)
- source_file (string)
- source_type (string)
- source_url (string)
- relationships (list<struct>)     # ← Available for complex queries
- custom_metadata (list<struct>)   # ← Key-value pairs (string only)
- record_type (string)             # ← Available for filtering
- raw_data_type (string)
- raw_data (large_binary)
```

### Current Collection Implementation

Collections are implemented as special documents with:
- `record_type: "collection_header"`
- `x_collection_metadata` containing:
  - `parent_collection` (UUID of parent)
  - `member_count`
  - `created_at`
  - `template`
  - `shared_metadata`

## Options for Lance-Friendly Collection Storage

### Option 1: Use Existing Schema Fields (Recommended)

**Approach:**
- Use `collection_id` to store parent collection UUID
- Use `relationships` for hierarchical structure
- Store collection metadata in `custom_metadata`

**Implementation:**
```python
# Collection header document
{
    "record_type": "collection_header",
    "title": "My Collection",
    "collection_id": "parent-collection-uuid",  # Parent collection
    "collection_id_type": "uuid",
    "custom_metadata": [
        {"key": "member_count", "value": "42"},
        {"key": "template", "value": "project"},
        {"key": "created_at", "value": "2024-01-19"}
    ],
    "relationships": [
        {
            "type": "parent",
            "id": "parent-collection-uuid",
            "title": "Parent Collection Name"
        }
    ]
}

# Member document
{
    "title": "Document in collection",
    "collection": "My Collection",        # Collection name
    "collection_id": "collection-uuid",    # Collection UUID
    "collection_id_type": "uuid",
    "relationships": [
        {
            "type": "reference",
            "id": "collection-uuid",
            "title": "Member of My Collection"
        }
    ]
}
```

**Pros:**
- ✅ Uses existing schema - no changes needed
- ✅ Enables Lance native filtering: `collection_id = 'parent-uuid'`
- ✅ Relationships provide rich linking
- ✅ Backward compatible

**Cons:**
- ❌ `custom_metadata` only supports string values
- ❌ Slight semantic overload of `collection_id` field

### Option 2: Add Dedicated Collection Fields to Schema

**Approach:**
Add new fields to Arrow schema:
```python
pa.field("parent_collection_id", pa.string()),
pa.field("collection_metadata", pa.struct([
    pa.field("member_count", pa.int32()),
    pa.field("template", pa.string()),
    pa.field("shared_metadata", pa.map_(pa.string(), pa.string()))
]))
```

**Pros:**
- ✅ Clean, semantic field names
- ✅ Native Lance filtering on all fields
- ✅ Supports proper data types

**Cons:**
- ❌ Requires schema migration
- ❌ Breaking change for existing datasets
- ❌ Adds fields only used by collection headers

### Option 3: Hybrid Approach

**Approach:**
- Use relationships for hierarchy (Lance filterable)
- Keep x_collection_metadata for rich metadata (Python filtered)
- Add helper methods for common queries

**Implementation:**
```python
def find_subcollections(self, parent_id: str):
    # Use relationships for efficient filtering
    results = self.dataset.scanner(
        filter=f"record_type = 'collection_header' AND relationships.id = '{parent_id}' AND relationships.type = 'child'"
    ).to_table()
    
    # Then access x_collection_metadata for additional data
    return [self._enrich_with_metadata(r) for r in results]
```

## Recommendation: Option 1 with Enhancements

Use existing schema fields with these patterns:

1. **For Parent-Child Hierarchy:**
   - Store parent UUID in `collection_id`
   - Use bidirectional relationships (parent/child)

2. **For Collection Membership:**
   - Documents use `collection_id` for their collection
   - Add "reference" relationship to collection header

3. **For Collection Metadata:**
   - Critical fields (member_count) tracked separately
   - Less critical metadata in custom_metadata
   - Consider caching computed values

4. **Query Patterns:**
   ```python
   # Find subcollections (Lance native)
   f"record_type = 'collection_header' AND collection_id = '{parent_id}'"
   
   # Find collection members (Lance native)
   f"collection_id = '{collection_id}' AND record_type = 'document'"
   
   # Find by relationship (Lance native)
   f"relationships.id = '{target_id}' AND relationships.type = 'child'"
   ```

## Migration Strategy

1. **Phase 1: Update Collection Tools**
   - Modify create_collection to use collection_id for parent
   - Update queries to use Lance-native filters
   - Add relationships for richer navigation

2. **Phase 2: Migration Utilities**
   - Script to migrate existing x_collection_metadata
   - Backward compatibility layer

3. **Phase 3: Documentation**
   - Update collection patterns
   - Query examples
   - Best practices

## Performance Implications

**Current Approach (Python filtering):**
- O(n) scan of all collection headers
- Memory load of all records
- ~1-10ms for small datasets, >100ms for large

**Proposed Approach (Lance filtering):**
- Index-assisted filtering
- Lazy loading of results
- <1ms for most queries

## Decision Criteria

Choose Option 1 because:
1. No schema changes required
2. Immediate performance benefits
3. Maintains backward compatibility
4. Leverages existing, tested fields
5. Relationships provide future flexibility

## Next Steps

1. Update collection tools to use collection_id for parent storage
2. Implement bidirectional relationships
3. Update queries to use Lance native filters
4. Add migration utility for existing collections
5. Update tests to reflect new patterns