# Schema Discrepancy Report

This report compares the schema documentation (`docs/reference/schema.md`) against the actual implementation in `contextframe_schema.py` and `contextframe_schema.json`.

## 1. Fields Missing from schema.md Documentation

### Fields in Python Schema but NOT in Documentation:
- **`uuid`** - In Python as required field, named `id` in docs
- **`text_content`** - In Python, named `content` in docs  
- **`vector`** - In Python, named `embedding` in docs
- **`latest_version`** - In JSON schema but not mentioned in docs
- **`local_path`** - In both Python and JSON but not in docs
- **`cid`** - In both Python and JSON but not in docs
- **`collection_id_type`** - In both Python and JSON but not in docs
- **`author`** - In both Python and JSON but not in docs (marked as optional)
- **`contributors`** - In both Python and JSON but not in docs
- **`status`** - In both Python and JSON but not in docs
- **`source_file`** - In both Python and JSON but not in docs
- **`source_type`** - In both Python and JSON but not in docs
- **`source_url`** - In both Python and JSON but not in docs
- **`raw_data_type`** - In both Python and JSON but not in docs
- **`raw_data`** - In both Python and JSON but not in docs

### Fields in JSON Schema but NOT in Documentation:
- **`version_history`** - Complex array structure for tracking versions
- **`branch_name`** - For version branching
- **`branched_from`** - Object describing branch origin
- **`merge_history`** - Array tracking merge operations

## 2. Field Name Mismatches

| Documentation | Python Schema | JSON Schema | Notes |
|--------------|---------------|-------------|-------|
| `id` | `uuid` | `uuid` | Docs uses generic "id", implementation uses specific "uuid" |
| `content` | `text_content` | N/A | Text content field name differs |
| `embedding` | `vector` | N/A | Embedding/vector field name differs |
| `collection` | `collection` | `collection` | Consistent but docs doesn't mention it as optional |

## 3. Type Mismatches

### Date Fields:
- **Documentation**: States ISO 8601 timestamp format (e.g., "2024-01-15T10:30:00Z")
- **JSON Schema**: Pattern enforces date-only format (YYYY-MM-DD)
- **Python Schema**: Stores as string

### Embedding/Vector:
- **Documentation**: `array[float]`
- **Python Schema**: `pa.list_(pa.float32(), list_size=embed_dim)` - Fixed size, float32
- **JSON Schema**: Not defined (missing)

### Custom Metadata:
- **Documentation**: `object`
- **Python Schema**: List of key-value pairs: `pa.list_(pa.struct([key, value]))`
- **JSON Schema**: `object` with string values only

### Relationships:
- **Documentation**: Shows `relationships[].metadata` field
- **Python/JSON**: No metadata field in relationship structure
- **JSON Schema**: Has additional relationship type "contains" not in docs

## 4. Required Fields Discrepancies

### Documentation says Required:
- id, record_type, title, uri, content, content_type, language, created_at, modified_at, version

### Python Schema Required Fields:
- uuid, title (only these are marked nullable=False)

### JSON Schema Required Fields:
- title (only)

## 5. Missing from All Implementation:
These fields are documented but don't exist in either Python or JSON schemas:
- **`content_type`** - MIME type of original content
- **`language`** - ISO 639-1 language code
- **`description`** - Brief description (mentioned in optional fields)
- **`embedding_model`** - Model used for embedding
- **`embedding_dimensions`** - Dimensions of embedding
- **`parent_id`** - For hierarchical structures

## 6. Validation Rules Discrepancies

### Documentation Claims:
- UUID4 format validation
- ISO 8601 timestamp validation
- Language code validation
- MIME type validation
- Relationship target validation

### Actual JSON Schema:
- UUID pattern validation ✓
- Date pattern (YYYY-MM-DD only) ✓
- No language validation
- No MIME type validation
- No relationship target validation

## 7. Record Type Values

### Documentation:
- document, collection_header, dataset_header

### Python Schema:
- document, collection_header, dataset_header, **frameset** (extra)

### JSON Schema:
- document, collection_header, dataset_header, **frameset** (extra)

## 8. Additional Schema Features Not Documented

### JSON Schema allows custom fields:
- Pattern property `^x_` for custom fields
- `additionalProperties: false` prevents other additions

### Python Schema has metadata for Lance:
- `"lance-encoding:blob": "true"` on raw_data field

## Summary of Critical Issues

1. **Field Naming**: Core fields have different names between docs and implementation (id→uuid, content→text_content, embedding→vector)

2. **Missing Documentation**: ~15 fields exist in implementation but aren't documented

3. **Required Fields**: Documentation claims 10 required fields, but only 1-2 are actually required

4. **Type Inconsistencies**: Date formats, embedding types, and custom metadata structures differ

5. **Missing Implementation**: Several documented fields don't exist (content_type, language, description, embedding_model, embedding_dimensions, parent_id)

6. **Record Types**: "frameset" type exists but isn't documented

7. **Validation**: Most documented validation rules aren't implemented

The documentation appears to describe an idealized or planned schema that differs significantly from the actual implementation.