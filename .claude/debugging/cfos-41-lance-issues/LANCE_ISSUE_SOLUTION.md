# Lance Filtering Issue - Root Cause and Solution

## Summary

We've identified and solved the Lance filtering panic issue that was blocking CFOS-41 and CFOS-20.

## Root Cause

The issue was **NOT** caused by the `custom_metadata` field's `list<struct>` type as initially suspected. Instead, it was caused by a combination of:

1. The `raw_data` field being `pa.large_binary()` with `lance-encoding:blob` metadata
2. Having null values in this blob-encoded field
3. Using any filter operation on the dataset

This appears to be a bug in Lance where filtering operations cause a panic when blob-encoded fields contain null values.

## Solution

We need to make two changes to fix the issue:

### 1. Remove blob encoding from raw_data field

Change from:
```python
pa.field("raw_data", pa.large_binary(), metadata={"lance-encoding:blob": "true"})
```

To:
```python
pa.field("raw_data", pa.large_binary())
```

### 2. Change custom_metadata to JSON string (optional but recommended)

While the `list<struct>` approach works, using a JSON string is simpler and more flexible:

Change from:
```python
pa.field("custom_metadata", pa.list_(pa.struct([
    pa.field("key", pa.string()),
    pa.field("value", pa.string())
])))
```

To:
```python
pa.field("custom_metadata", pa.string())  # Store as JSON string
```

## Data Conversion

For the custom_metadata field, use these helper functions:

```python
import json

# When writing to Lance
def dict_to_lance(metadata_dict):
    return json.dumps(metadata_dict) if metadata_dict else None

# When reading from Lance
def lance_to_dict(metadata_json):
    return json.loads(metadata_json) if metadata_json else {}
```

## Testing Results

With these changes:
- ✅ All write operations work
- ✅ All read operations work
- ✅ All filter operations work (uuid, IS NOT NULL, compound filters, etc.)
- ✅ No Lance panics occur

## Next Steps

1. Update `contextframe_schema.py` to implement these changes
2. Update `frame.py` to handle JSON conversion for custom_metadata
3. Run all tests to ensure compatibility
4. Consider filing a bug report with Lance about the blob+null+filter issue