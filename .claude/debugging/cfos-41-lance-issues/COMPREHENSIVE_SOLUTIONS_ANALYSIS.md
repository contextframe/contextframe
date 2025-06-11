# Comprehensive Solutions Analysis for Lance Schema Issues

## Executive Summary

This document analyzes two critical Lance compatibility issues discovered in ContextFrame:

1. **raw_data blob field issue**: Lance panics when filtering datasets if the `raw_data` field (marked with `lance-encoding:blob`) contains null values
2. **custom_metadata storage**: Need for an optimal approach to store flexible key-value metadata given Lance's lack of Map type support

## Issue 1: Raw Data Blob Field

### Problem Description

The `raw_data` field is defined as:
```python
pa.field(
    "raw_data",
    pa.large_binary(),
    metadata={"lance-encoding:blob": "true"},
)
```

When this field contains null values (which is common since raw_data is optional), Lance panics during filter operations with a Rust-level error.

### Solution Options

#### 1.1 Remove Blob Encoding Metadata

**Implementation**:
```python
pa.field("raw_data", pa.large_binary())  # No metadata
```

**Pros**:
- Simplest fix
- Maintains schema compatibility
- No API changes needed

**Cons**:
- Loses lazy loading optimization for large binary data
- All binary data loaded into memory on read
- Performance impact for large files

**Performance Impact**: High for large files (images, audio, video)

#### 1.2 Use Lance Blob Dataset Feature

**Implementation**:
```python
# Store binary data in separate blob dataset
class FrameDataset:
    def __init__(self, path):
        self.main_dataset = lance.dataset(path)
        self.blob_dataset = lance.blob_dataset(f"{path}_blobs")
    
    def add_record(self, record):
        if record.raw_data:
            blob_id = self.blob_dataset.put(record.raw_data)
            record.metadata["raw_data_blob_id"] = blob_id
```

**Pros**:
- Proper use of Lance blob storage
- Excellent performance for large files
- True lazy loading
- Separates metadata from binary data

**Cons**:
- Requires managing two datasets
- More complex implementation
- Migration needed for existing data

**Performance Impact**: Optimal for large binary data

#### 1.3 External Object Storage

**Implementation**:
```python
# Store binary data in S3/GCS/Azure
pa.field("raw_data_uri", pa.string())  # Store URI instead of data
```

**Pros**:
- Unlimited scalability
- Industry standard approach
- Works with existing CDN/caching infrastructure
- No Lance-specific issues

**Cons**:
- Requires external storage setup
- Network latency for data access
- Additional dependency and complexity

**Performance Impact**: Depends on network and caching strategy

#### 1.4 Conditional Schema Based on Data

**Implementation**:
```python
def build_schema(include_blob_encoding=False):
    if include_blob_encoding:
        raw_data_field = pa.field(
            "raw_data",
            pa.large_binary(),
            metadata={"lance-encoding:blob": "true"},
        )
    else:
        raw_data_field = pa.field("raw_data", pa.large_binary())
```

**Pros**:
- Flexibility to optimize based on use case
- Can detect and handle null patterns

**Cons**:
- Schema inconsistency across datasets
- Complex version management
- Confusing for users

**Performance Impact**: Variable

#### 1.5 Store Binary Data as Base64 String

**Implementation**:
```python
pa.field("raw_data_base64", pa.string())  # or pa.large_string()
```

**Pros**:
- No Lance-specific issues
- Simple implementation
- Works with all Arrow/Lance versions

**Cons**:
- 33% storage overhead
- Encoding/decoding CPU cost
- Not suitable for large files

**Performance Impact**: Poor for large files

### Recommended Solution for Raw Data

**Short-term (immediate fix)**: Remove blob encoding metadata (Option 1.1)
**Long-term (proper solution)**: Use Lance Blob Dataset feature (Option 1.2)

## Issue 2: Custom Metadata Storage

### Problem Description

Lance doesn't support PyArrow's Map type, requiring alternative approaches for storing flexible key-value metadata.

### Solution Options

#### 2.1 List of Structs (Current Approach)

**Implementation**:
```python
pa.field("custom_metadata", pa.list_(pa.struct([
    pa.field("key", pa.string()),
    pa.field("value", pa.string())
])))
```

**Pros**:
- Maintains columnar structure
- Supports querying by keys (theoretically)
- Type-safe at schema level

**Cons**:
- Currently causes Lance filter panic
- Complex conversion logic
- Variable-length lists impact performance

**Performance Impact**: Good if Lance bug is fixed

#### 2.2 JSON String

**Implementation**:
```python
pa.field("custom_metadata", pa.string())  # Store as JSON
```

**Pros**:
- Simple and reliable
- No Lance compatibility issues
- Flexible schema evolution
- Easy debugging

**Cons**:
- Loses columnar query benefits
- Requires JSON parsing
- No type safety at storage level

**Performance Impact**: Moderate (JSON parsing overhead)

#### 2.3 Parallel Arrays

**Implementation**:
```python
pa.field("metadata_keys", pa.list_(pa.string())),
pa.field("metadata_values", pa.list_(pa.string()))
```

**Pros**:
- Pure columnar storage
- Should work with Lance filters
- Can index keys array

**Cons**:
- Must maintain array alignment
- Complex API for users
- Two fields instead of one

**Performance Impact**: Good for columnar operations

#### 2.4 Fixed Schema with Extension Field

**Implementation**:
```python
# Predefined common fields
pa.field("meta_source", pa.string()),
pa.field("meta_author", pa.string()),
pa.field("meta_version", pa.string()),
pa.field("meta_extensions", pa.string())  # JSON for rare fields
```

**Pros**:
- Optimal performance for common fields
- Type safety for known fields
- Columnar benefits preserved

**Cons**:
- Requires schema changes for new fields
- Less flexible
- May have many null values

**Performance Impact**: Excellent for predefined fields

#### 2.5 Binary JSON

**Implementation**:
```python
pa.field("custom_metadata", pa.binary())  # Store as msgpack/BSON
```

**Pros**:
- More efficient than JSON strings
- Supports complex types
- No escaping issues

**Cons**:
- Requires binary parser
- Less human-readable
- Still loses columnar benefits

**Performance Impact**: Better than JSON string

#### 2.6 Separate Metadata Table

**Implementation**:
```python
# Main dataset: contextframe.lance
# Metadata dataset: contextframe_metadata.lance
# Link via uuid
```

**Pros**:
- Clean separation of concerns
- Can use optimal schema for metadata
- No impact on main query performance

**Cons**:
- Requires joins for full records
- More complex data management
- Two datasets to maintain

**Performance Impact**: Depends on join strategy

### Recommended Solution for Custom Metadata

**Short-term**: JSON string (Option 2.2) - reliable and simple
**Medium-term**: Parallel arrays (Option 2.3) - if performance critical
**Long-term**: Wait for Lance Map type support or use fixed schema

## Combined Recommendation Strategy

### Phase 1: Immediate Fix (1-2 days)
1. Remove blob encoding from raw_data field
2. Use JSON string for custom_metadata
3. Document the temporary nature of these changes

### Phase 2: Optimization (1-2 weeks)
1. Implement parallel arrays for custom_metadata if performance requires
2. Add benchmarks to measure impact
3. Consider fixed schema for common metadata fields

### Phase 3: Long-term Solution (1-3 months)
1. Migrate to Lance Blob Dataset for binary data
2. Monitor Lance roadmap for Map type support
3. Design migration tools for existing datasets

## Implementation Guidelines

### For Raw Data Field

```python
# Remove blob encoding
pa.field("raw_data", pa.large_binary())

# Future: Use blob dataset
class FrameDataset:
    def __init__(self, path):
        self.path = path
        self.dataset = lance.dataset(path)
        self.blob_store = self._init_blob_store()
    
    def _init_blob_store(self):
        # Implementation depends on Lance blob dataset API
        pass
```

### For Custom Metadata Field

```python
# Short-term: JSON string
def to_table(self):
    if self.metadata.get("custom_metadata"):
        custom_meta_json = json.dumps(self.metadata["custom_metadata"])
    else:
        custom_meta_json = None
    
def from_arrow(cls, record_batch):
    if custom_meta_json:
        metadata["custom_metadata"] = json.loads(custom_meta_json)
```

## Migration Considerations

1. **Backward Compatibility**: Provide tools to migrate existing datasets
2. **Version Detection**: Add schema version field for future migrations
3. **Gradual Rollout**: Support both old and new schemas during transition

## Performance Benchmarks Needed

1. Compare JSON vs parallel arrays for metadata queries
2. Measure impact of removing blob encoding
3. Test Lance Blob Dataset performance
4. Benchmark filter operations with different schemas

## Risk Assessment

### High Risk
- Continuing with current list<struct> approach (causes production failures)
- Using blob encoding with nullable fields

### Medium Risk
- JSON string approach (loses some query optimization)
- Schema changes requiring migration

### Low Risk
- Removing blob encoding (only impacts performance, not functionality)
- Parallel arrays approach (well-supported by Arrow/Lance)

## Conclusion

The Lance compatibility issues require immediate attention. The recommended approach balances:

1. **Immediate stability**: Remove problematic features
2. **Maintain functionality**: Use proven patterns (JSON)
3. **Future optimization**: Plan for proper blob storage and columnar metadata

The key is to implement solutions that work today while maintaining a clear path to optimal solutions as Lance evolves.

## Appendix: Test Results

From our testing, the following schemas work with Lance filtering:
- ✓ Simple types (string, int, float)
- ✓ List of strings
- ✓ Simple structs
- ✓ Parallel arrays
- ✓ JSON strings
- ✗ List of structs (causes panic)
- ✗ Large binary with blob encoding + nulls (causes panic)

This data informed our recommendations above.