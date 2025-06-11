# Solution Summary for CFOS-41

## Problem
Lance was causing panics when filtering datasets that contained blob-encoded fields with null values. Initially thought to be a Map type incompatibility issue with custom_metadata.

## Root Cause Discovery
Through extensive testing and research:

1. **Lance doesn't support Map type** - Confirmed this is still the case
2. **The real issue**: Lance doesn't support scanning/filtering blob-encoded columns at all
3. **Lance documentation confirms**: You must exclude blob columns from scanner projections and use `take_blobs` API separately

## Solution Implemented

### 1. Schema Changes
- Changed `custom_metadata` from `pa.map_` to `pa.list_(pa.struct([...]))` for Lance compatibility
- Added `custom_metadata` to JSON validation schema

### 2. Frame.py Changes
- Added `_get_non_blob_columns()` helper to identify non-blob columns
- Modified `scanner()` to automatically exclude blob columns when filters are used
- Updated `get_by_uuid()` to use the filtered scanner
- Fixed `from_arrow()` to handle missing fields gracefully
- Fixed `delete_record()` to handle Lance's delete method returning None
- Added missing return statement in `find_related_to()`

### 3. Key Code Changes

```python
# Automatically exclude blob columns from filtered scans
def scanner(self, **scan_kwargs):
    if 'filter' in scan_kwargs and self._non_blob_columns is not None:
        if 'columns' not in scan_kwargs:
            scan_kwargs['columns'] = self._non_blob_columns
    return self._dataset.scanner(**scan_kwargs)
```

## Benefits
1. **No more panics** - Lance can't scan blob columns, so we don't let it try
2. **Transparent to users** - Filtering still works as expected
3. **Minimal changes** - No complex workarounds or post-filtering needed
4. **Future-proof** - When Lance adds blob scanning support, we can easily remove this

## Trade-offs
1. `raw_data` field will be None when records are retrieved via filtering
2. If blob data is needed, must use `take_blobs` API separately (not implemented yet)

## Testing
All frameset tests now pass, confirming the solution works correctly.