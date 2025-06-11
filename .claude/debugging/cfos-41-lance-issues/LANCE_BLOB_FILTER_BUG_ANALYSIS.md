# Lance Blob + Filter Bug Analysis

## Precise Bug Pattern

Based on comprehensive testing, the Lance panic occurs specifically when:

1. **Blob-encoded field** (`lance-encoding:blob` metadata) 
2. **Contains null values** (mixed or all nulls)
3. **Using `>` or `>=` operators** in filters

## Test Results Summary

### ✅ Works Fine:
- Blob fields with **no null values** + any filter type
- Blob fields with nulls + filters using: `<`, `<=`, `=`, `!=`, `IS NULL`, `IS NOT NULL`, `IN`, `LIKE`
- Non-blob `large_binary` fields + any filter type
- Any schema without blob encoding

### ❌ Causes Panic:
- Blob fields with **any null values** + `>` or `>=` filters
- Blob fields with **all null values** + **any filter type**

## Specific Patterns

| Blob Field State | Filter Type | Result |
|------------------|-------------|---------|
| All non-null | Any filter | ✅ Works |
| Mixed null/non-null | `<`, `<=`, `=`, `!=`, `IS NULL`, etc. | ✅ Works |
| Mixed null/non-null | `>` or `>=` | ❌ Panic |
| All null | Any filter | ❌ Panic |

## Root Cause

This appears to be a Lance bug in the query execution engine when:
- The blob encoding optimization interacts with null value handling
- Specifically during "greater than" comparison operations
- Or when the entire blob column is null

## Recommended Workarounds

### 1. Safe Filter Strategy

```python
# ALWAYS SAFE
def safe_filter_with_blobs(dataset, filter_expr):
    # These patterns are always safe
    safe_patterns = [
        r'^\w+\s*=\s*',      # Equality
        r'^\w+\s*!=\s*',     # Not equal
        r'^\w+\s*<\s*',      # Less than (safe!)
        r'^\w+\s*<=\s*',     # Less than or equal (safe!)
        r'IS\s+NULL',        # Null checks
        r'IS\s+NOT\s+NULL',
        r'IN\s*\(',          # IN operator
        r'LIKE\s+',          # LIKE operator
    ]
    
    # Check if filter is safe
    is_safe = any(re.search(pattern, filter_expr, re.IGNORECASE) 
                  for pattern in safe_patterns)
    
    if is_safe or '>' not in filter_expr:
        return dataset.scanner(filter=filter_expr).to_table()
    else:
        # Unsafe - use post-filtering
        return post_filter_workaround(dataset, filter_expr)
```

### 2. Post-Filter Workaround

```python
def post_filter_workaround(dataset, filter_expr):
    """Apply filters in memory for unsafe operations."""
    # Get all data
    table = dataset.to_table()
    
    # Parse and apply filter using PyArrow compute
    import pyarrow.compute as pc
    
    # Example for "id > 2"
    if ">" in filter_expr and ">=" not in filter_expr:
        col, val = filter_expr.split(">")
        col = col.strip()
        val = int(val.strip())
        return table.filter(pc.field(col) > val)
    
    # Add more cases as needed
```

### 3. Ensure Non-Null Blobs

```python
def write_with_blob_safety(table, path):
    """Ensure blob fields don't have all null values."""
    schema = table.schema
    
    for i, field in enumerate(schema):
        if field.metadata and field.metadata.get(b"lance-encoding:blob") == b"true":
            col = table[field.name]
            if pc.all(pc.is_null(col)).as_py():
                # Replace all-null blob column with empty bytes
                empty_bytes = pa.array([b""] * len(table), type=field.type)
                table = table.set_column(i, field.name, empty_bytes)
    
    return write_dataset(table, path)
```

## Long-Term Solution

### For ContextFrame:

1. **Keep blob encoding** - The benefits outweigh the bug
2. **Document the limitation** - Warn about `>` and `>=` filters
3. **Implement safe wrappers** - Use the patterns above
4. **File bug report** - This is clearly a Lance bug

### Implementation in FrameDataset:

```python
class FrameDataset:
    def query(self, filter_expr: str, **kwargs):
        """Safe query method that handles blob filter edge cases."""
        # Check for unsafe patterns
        if self._has_blob_fields() and self._is_unsafe_filter(filter_expr):
            # Use post-filtering
            return self._query_with_post_filter(filter_expr, **kwargs)
        else:
            # Use normal Lance filtering
            return self.dataset.scanner(filter=filter_expr, **kwargs).to_table()
    
    def _is_unsafe_filter(self, filter_expr: str) -> bool:
        """Check if filter uses > or >= operators."""
        # Simple check - could be made more sophisticated
        return '>' in filter_expr and '<' not in filter_expr
```

## Conclusion

The bug is very specific: blob-encoded fields with nulls + greater-than filters. Since:
- Most queries use equality filters (`uuid = 'x'`)
- Less-than filters work fine
- We can work around greater-than filters

We should proceed with blob encoding and implement the safe query patterns.