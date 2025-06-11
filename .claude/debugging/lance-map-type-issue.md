# Lance Map Type Compatibility Issue - Debugging Report

## ⚠️ UPDATE: ISSUE RESOLVED

**This issue has been fully resolved.** The root cause was not the Map type or list<struct> schema, but Lance's inability to scan blob-encoded columns. 

**For the complete solution and investigation, see:** `.claude/debugging/cfos-41-lance-issues/`

---

## Original Issue Summary

**Issue ID**: CFOS-41  
**Branch**: `jay/cfos-41-fix-lance-map-type-incompatibility-for-custom_metadata-field`  
**Status**: ~~In Progress~~ **RESOLVED**

### Problem Description

The Lance columnar data format does not support PyArrow's Map type (`pa.map_(pa.string(), pa.string())`), which was originally used for the `custom_metadata` field in our ContextFrame schema. This incompatibility prevents us from storing flexible key-value metadata pairs in the Lance dataset.

## Current Status

### What We've Done

1. **Identified the Core Issue**
   - Lance throws: `LanceError(Schema): Unsupported data type: Map`
   - This occurs when trying to write data with the Map type schema

2. **Attempted Solutions**

   **a. JSON String Approach (First Attempt)**
   - Changed schema from `pa.map_()` to `pa.string()`
   - Serialized dict to JSON in `to_table()` method
   - Deserialized JSON back to dict in `from_arrow()` method
   - Added `custom_metadata` to JSON schema validation
   - **Result**: Data writes successfully, but Lance panics when using filters

   **b. List of Structs Approach (Current)**
   - Changed schema to:
     ```python
     pa.field("custom_metadata", pa.list_(pa.struct([
         pa.field("key", pa.string()),
         pa.field("value", pa.string())
     ])))
     ```
   - Convert dict to list of key-value structs in `to_table()`
   - Convert back to dict in `from_arrow()`
   - **Result**: Data writes successfully, but Lance still panics when using filters

3. **Current Symptoms**
   - `test_create_frameset` passes (writes data successfully)
   - Reading data without filters works fine
   - Any query with filters causes Lance to panic with:
     ```
     thread 'lance_background_thread' panicked at /rustc/.../collections/vec_deque/mod.rs:1514:36:
     range end index 1 out of range for slice of length 0
     ```

## Technical Details

### Files Modified

1. **contextframe/schema/contextframe_schema.py**
   - Line 148-151: Changed custom_metadata from Map to list<struct>

2. **contextframe/frame.py**
   - Lines 183-189: Added conversion from dict to list of structs in `to_table()`
   - Lines 224-231: Added conversion from list of structs back to dict in `from_arrow()`

3. **contextframe/schema/contextframe_schema.json**
   - Added custom_metadata object definition for validation

### Test Results

Running `test_frameset.py`:
- `test_create_frameset`: ✅ PASSES
- `test_get_frameset`: ❌ FAILS (Lance panic on filter)
- `test_get_frameset_sources`: ❌ FAILS (Lance panic on filter)
- `test_update_frameset_content`: ❌ FAILS (Lance panic on filter)
- All other tests: ❌ FAIL (Lance panic on filter)

## Root Cause Analysis

The issue appears to be a bug in Lance's query engine when filtering datasets that contain list<struct> schemas. This is evidenced by:

1. Write operations work correctly
2. Read operations without filters work correctly
3. Only filter operations cause the panic
4. The panic occurs in Lance's Rust code, not in our Python code

## Next Steps

### Immediate Actions Needed

1. **Verify Lance Version Compatibility**
   - Check if this is a known issue in our version of Lance
   - Consider upgrading/downgrading Lance if needed

2. **Test Alternative Schema Designs**
   - Simple string field with JSON serialization
   - Binary field for JSON data
   - Parallel arrays approach (separate keys and values arrays)
   - Fixed-size struct with predefined fields

3. **Consider Production-Ready Alternatives**
   - Store custom_metadata in a separate Lance dataset/table
   - Use a different storage format for this specific field
   - Implement a hybrid approach with core fields in Lance and metadata elsewhere

### Long-term Considerations

1. **File a Bug Report with Lance**
   - Provide minimal reproducible example
   - Include stack traces and version information

2. **Design Implications**
   - The custom_metadata field is critical for extensibility
   - Must maintain backward compatibility
   - Solution must be performant for large datasets

## Dependencies

- PyArrow version: 20.0.0
- Lance version: Installed via `pylance>=0.29.0`
- Python version: 3.12.3

## Related Issues

- CFOS-20: Add FrameSet Record Type (blocked by this issue)
- CFOS-21: Documentation Updates (waiting on resolution)

## Conclusion

The current blocker is a Lance bug that prevents filtering on datasets containing list<struct> schemas. We need to find a schema design that:

1. Supports flexible key-value metadata storage
2. Works with Lance's current filtering capabilities
3. Maintains API compatibility for users
4. Is performant and production-ready

The next step is to systematically test alternative schema designs to find one that works with Lance's current implementation while meeting our requirements.