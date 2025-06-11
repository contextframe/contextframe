# Long-Term Implementation Plan for ContextFrame Schema

## Executive Summary

Based on our testing, here's the long-term plan:

1. **Custom Metadata**: Continue using `list<struct>` approach (it works fine)
   - Lance Map type is still not supported
   - Our current approach is actually good and maintains columnar benefits
   
2. **Raw Data**: Use Lance Blob API properly
   - The blob encoding itself works well
   - The panic issue appears to be a Lance bug with specific filter combinations
   - We can work around it by being careful with our queries

## Confirmed Findings

### Map Type Support
- **Lance does NOT support Map type** (confirmed with test)
- Error: `Unsupported data type: Map`
- Must continue with alternative approaches

### Blob API Findings
- **Lance Blob API works well** for lazy loading large binary data
- `take_blobs()` method provides file-like access without loading into memory
- The panic issue occurs with certain filter patterns, not the blob encoding itself

### The Real Issue
The Lance panic occurs when:
1. Using certain types of filters (like `id > 2`) 
2. On datasets with blob columns containing mixed null/non-null values
3. But other filters work fine (IS NULL, IS NOT NULL, equality filters)

## Recommended Long-Term Architecture

### 1. Schema Design

```python
def build_contextframe_schema():
    """Build the optimized long-term schema."""
    return pa.schema([
        # Core fields
        pa.field("uuid", pa.string(), nullable=False),
        pa.field("title", pa.string(), nullable=False),
        pa.field("text_content", pa.string()),
        
        # Vector embedding
        pa.field("vector", pa.fixed_size_list(pa.float32(), embed_dim)),
        
        # Custom metadata - keep list<struct> approach
        pa.field("custom_metadata", pa.list_(pa.struct([
            pa.field("key", pa.string()),
            pa.field("value", pa.string())
        ]))),
        
        # Blob data with proper encoding
        pa.field("raw_data", pa.large_binary(), 
                 metadata={"lance-encoding:blob": "true"}),
        pa.field("raw_data_type", pa.string()),  # MIME type
        
        # Other fields...
    ])
```

### 2. Data Access Layer

```python
class ContextFrameDataset:
    """Wrapper around Lance dataset with blob support."""
    
    def __init__(self, path: str):
        self.path = path
        self.dataset = lance.dataset(path)
    
    def add_record(self, record: FrameRecord) -> None:
        """Add a record with proper blob handling."""
        # Convert record to table format
        table = record.to_table()
        
        # Append to dataset
        self.dataset = lance.write_dataset(
            table, 
            self.path,
            mode="append"
        )
    
    def get_by_uuid(self, uuid: str) -> Optional[FrameRecord]:
        """Get record by UUID with safe filtering."""
        # Use equality filter (safe)
        result = self.dataset.scanner(
            filter=f"uuid = '{uuid}'"
        ).to_table()
        
        if len(result) == 0:
            return None
            
        # Get blob data if needed
        if result['raw_data'][0].is_valid:
            blobs = self.dataset.take_blobs('raw_data', indices=[0])
            # Return with blob file reference
            return FrameRecord.from_arrow_with_blob(result[0], blobs[0])
        else:
            return FrameRecord.from_arrow(result[0])
    
    def query_metadata(self, **kwargs) -> List[FrameRecord]:
        """Query without loading blob data."""
        # Only select non-blob columns for efficiency
        columns = [col for col in self.dataset.schema.names 
                   if col != 'raw_data']
        
        scanner = self.dataset.scanner(columns=columns, **kwargs)
        return [FrameRecord.from_arrow(row) for row in scanner.to_table()]
    
    def get_blob(self, uuid: str) -> Optional[BlobFile]:
        """Get blob data for a specific record."""
        # First get the row index
        result = self.dataset.scanner(
            filter=f"uuid = '{uuid}'",
            columns=['uuid']
        ).to_table()
        
        if len(result) == 0:
            return None
            
        # Use take_blobs to get the blob file
        blobs = self.dataset.take_blobs('raw_data', indices=[0])
        return blobs[0] if blobs else None
```

### 3. Safe Query Patterns

```python
# SAFE FILTERS (work with blobs + nulls)
"uuid = 'specific-id'"              # Equality
"custom_metadata IS NOT NULL"       # NULL checks
"title LIKE 'prefix%'"              # String operations
"uuid IN ('id1', 'id2', 'id3')"   # IN clause

# UNSAFE FILTERS (cause panic with blobs + nulls)
"id > 2"                           # Numeric comparisons
"created_at < '2024-01-01'"        # Date comparisons

# WORKAROUND: Use post-filtering for unsafe operations
def query_with_unsafe_filter(dataset, unsafe_filter):
    # Get all data without filter
    all_data = dataset.scanner().to_table()
    
    # Apply filter in memory using PyArrow
    import pyarrow.compute as pc
    return all_data.filter(pc.field('id') > 2)
```

### 4. Migration Strategy

#### Phase 1: Update Schema (Week 1)
1. Keep `list<struct>` for custom_metadata (it works)
2. Keep blob encoding for raw_data (provides benefits)
3. Document safe query patterns
4. Add query wrapper methods to avoid unsafe filters

#### Phase 2: Implement Data Access Layer (Week 2)
1. Create `ContextFrameDataset` wrapper class
2. Implement safe query methods
3. Add blob streaming support
4. Test with large files

#### Phase 3: Optimize Performance (Week 3-4)
1. Add caching for frequently accessed blobs
2. Implement batch blob operations
3. Add progress tracking for large uploads
4. Benchmark against baseline

## Implementation Details

### Custom Metadata Handling

Keep the current approach but optimize the conversion:

```python
class FrameRecord:
    def _metadata_dict_to_list(self, metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """Convert dict to list of key-value structs."""
        if not metadata:
            return []
        return [{"key": k, "value": v} for k, v in metadata.items()]
    
    def _metadata_list_to_dict(self, metadata_list: List[Dict[str, str]]) -> Dict[str, str]:
        """Convert list of key-value structs to dict."""
        if not metadata_list:
            return {}
        return {item["key"]: item["value"] for item in metadata_list}
```

### Blob Handling Best Practices

```python
def process_large_file(blob_file: BlobFile):
    """Process large file in chunks."""
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    with blob_file as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            # Process chunk
            process_chunk(chunk)

def stream_image_response(blob_file: BlobFile):
    """Stream image data for web response."""
    def generate():
        with blob_file as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                yield data
    
    return Response(generate(), mimetype='image/jpeg')
```

## Future Considerations

1. **Monitor Lance Updates**
   - Track Map type support
   - Watch for blob + filter bug fixes
   - Consider contributing fix upstream

2. **Performance Optimization**
   - Consider separate blob storage for > 100MB files
   - Implement smart caching based on access patterns
   - Use Lance's future async APIs when available

3. **Schema Evolution**
   - Plan for adding new metadata fields
   - Consider versioned schemas
   - Maintain backward compatibility

## Conclusion

The long-term plan is to:
1. Keep `list<struct>` for custom_metadata (works well, maintains columnar benefits)
2. Use Lance Blob API for raw_data (provides lazy loading)
3. Implement safe query patterns to avoid Lance bugs
4. Build a robust data access layer that handles edge cases

This approach gives us the best of both worlds: columnar performance for metadata and efficient blob handling for large files.