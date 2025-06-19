# Collection Metadata Storage Fix

## Problem
The collection management tools are storing metadata in `x_collection_metadata` which is not persisted to Lance because:
1. It's not a column in the Arrow schema
2. It's stored in the in-memory metadata dict but lost when reloading from Lance

## Solution
Use the existing `custom_metadata` field which is properly persisted to Lance. Since `custom_metadata` only supports string key-value pairs, we need to:

1. Prefix collection-specific metadata with `collection_`
2. Prefix shared metadata with `shared_`
3. Convert all values to strings
4. Parse values back when reading

## Implementation Changes

### Storage Pattern
```python
# Instead of:
"x_collection_metadata": {
    "created_at": "2024-01-19",
    "member_count": 5,
    "shared_metadata": {"key": "value"}
}

# Use:
"custom_metadata": {
    "collection_created_at": "2024-01-19",
    "collection_member_count": "5",
    "shared_key": "value"
}
```

### Helper Methods
```python
def _get_collection_metadata(self, record: FrameRecord) -> dict:
    """Extract collection metadata from custom_metadata."""
    custom = record.metadata.get("custom_metadata", {})
    return {
        "created_at": custom.get("collection_created_at", ""),
        "updated_at": custom.get("collection_updated_at", ""),
        "member_count": int(custom.get("collection_member_count", "0")),
        "total_size": int(custom.get("collection_total_size", "0")),
        "template": custom.get("collection_template", ""),
        "shared_metadata": {
            k[7:]: v for k, v in custom.items() 
            if k.startswith("shared_")
        }
    }

def _set_collection_metadata(self, record: FrameRecord, coll_meta: dict):
    """Store collection metadata in custom_metadata."""
    if "custom_metadata" not in record.metadata:
        record.metadata["custom_metadata"] = {}
    
    custom = record.metadata["custom_metadata"]
    custom["collection_created_at"] = coll_meta.get("created_at", "")
    custom["collection_updated_at"] = coll_meta.get("updated_at", "")
    custom["collection_member_count"] = str(coll_meta.get("member_count", 0))
    custom["collection_total_size"] = str(coll_meta.get("total_size", 0))
    custom["collection_template"] = coll_meta.get("template", "")
    
    # Store shared metadata
    for key, value in coll_meta.get("shared_metadata", {}).items():
        custom[f"shared_{key}"] = str(value)
```

## Benefits
1. Uses existing schema - no changes needed
2. Data persists correctly to Lance
3. Backward compatible with queries
4. Can still use Lance filtering on record_type and collection_id