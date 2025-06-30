---
title: "Schema Reference"
---

# Schema Reference

This document provides a comprehensive reference for the ContextFrame schema system. The schema is defined in both JSON Schema format (`contextframe_schema.json`) for validation and PyArrow format (`contextframe_schema.py`) for efficient storage.

## Core Schema Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable title of the document (only required field in JSON schema) |
| `uuid` | string | Unique identifier for the frame (UUID4 format) - required in PyArrow schema |

### Primary Content Fields

| Field | Type | Description |
|-------|------|-------------|
| `text_content` | string | The main textual content of the document (PyArrow) |
| `context` | string | Additional context about the document |
| `vector` | array[float32] | Vector embedding of the content (configurable dimensions) |

### Identification Fields

| Field | Type | Description |
|-------|------|-------------|
| `uri` | string | URI reference for the document |
| `local_path` | string | Local filesystem path relative to a defined root |
| `cid` | string | IPFS Content Identifier (CID) for content addressing |

### Versioning Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Semantic version (MAJOR.MINOR.PATCH) |
| `latest_version` | string | The latest semantic version of the document |
| `version_history` | array[object] | History of document versions |
| `branch_name` | string | Name of this branch (if document is branched) |
| `branched_from` | object | Information about the original document |
| `merge_history` | array[object] | History of merges into this document |

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `author` | string | The author of the document |
| `contributors` | array[string] | List of contributors |
| `created_at` | string | Creation date (YYYY-MM-DD format) |
| `updated_at` | string | Last update date (YYYY-MM-DD format) |
| `tags` | array[string] | User-defined tags for categorization |
| `status` | string | Document status (draft, published, archived, deprecated) |

### Collection Fields

| Field | Type | Description |
|-------|------|-------------|
| `collection` | string | Collection this document belongs to |
| `collection_id` | string | Unique identifier for the collection |
| `collection_id_type` | string | Type of identifier (uuid, uri, cid, string) |
| `position` | integer | Position in an ordered collection |

### Source Information

| Field | Type | Description |
|-------|------|-------------|
| `source_file` | string | Original file name if converted |
| `source_type` | string | Original file type if converted |
| `source_url` | string | URL of the original content |

### Relationship Fields

| Field | Type | Description |
|-------|------|-------------|
| `relationships` | array[object] | Array of relationship objects |

Each relationship object contains:

- `type` (required): Type of relationship (parent, child, related, reference, contains)
- One of: `id`, `uri`, `path`, or `cid` (at least one required)
- `title` (optional): Title of the related document
- `description` (optional): Description of the relationship

### Raw Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `raw_data_type` | string | MIME type of embedded raw data (e.g., image/jpeg) |
| `raw_data` | binary/string | Raw binary data (base64 encoded in JSON) |

### Extension Fields

| Field | Type | Description |
|-------|------|-------------|
| `custom_metadata` | object/array | User-defined metadata (object in JSON, key-value array in PyArrow) |
| `record_type` | string | Type of record (see Record Types below) |

## Record Types

### document

Standard document record containing content and metadata.

### collection_header

Header record for a collection of related documents.

### dataset_header

Header record describing the entire dataset.

### frameset

A set of related frames treated as a unit.

## Schema Differences

### JSON Schema vs PyArrow Schema

1. **Field Names**:
   - JSON uses `uuid`, PyArrow uses `uuid`
   - JSON has no content field defined, PyArrow uses `text_content`
   - JSON has no embedding field defined, PyArrow uses `vector`

2. **Required Fields**:
   - JSON Schema: Only `title` is required
   - PyArrow Schema: `uuid` and `title` are required

3. **Data Types**:
   - Dates: JSON enforces YYYY-MM-DD pattern, PyArrow stores as strings
   - Custom metadata: JSON uses object with string values, PyArrow uses array of key-value structs
   - Embeddings: PyArrow defines as fixed-size float32 array, not in JSON schema

## Validation Rules

### JSON Schema Validation

1. **Pattern Validation**:
   - `uuid`: Must match UUID4 format
   - `version`: Semantic version pattern (X.Y.Z)
   - `created_at`/`updated_at`: YYYY-MM-DD format
   - `cid`: Valid IPFS CID format

2. **Enum Validation**:
   - `collection_id_type`: Must be one of: uuid, uri, cid, string
   - `record_type`: Must be one of: document, collection_header, dataset_header, frameset
   - `relationships.type`: Must be one of: parent, child, related, reference, contains

3. **Additional Properties**:
   - Custom fields must be prefixed with `x_`
   - No additional properties allowed except those prefixed with `x_`

## Best Practices

1. **Always Provide Title**: It's the only universally required field
2. **Use UUIDs**: Generate proper UUID4 identifiers for `uuid` field
3. **Date Format**: Use YYYY-MM-DD format for date fields
4. **Semantic Versioning**: Follow MAJOR.MINOR.PATCH format
5. **Relationships**: Ensure at least one identifier field in each relationship
6. **MIME Types**: Use standard MIME types for `raw_data_type`

## Example: Complete Frame

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "title": "API Documentation",
  "text_content": "# API Reference\n\nThis document...",
  "context": "REST API reference guide for v2.0",
  "uri": "docs/api/reference.md",
  "version": "2.1.0",
  "author": "Tech Team",
  "created_at": "2024-01-15",
  "updated_at": "2024-01-20",
  "tags": ["api", "documentation", "reference"],
  "status": "published",
  "collection": "Technical Documentation",
  "collection_id": "tech-docs-2024",
  "collection_id_type": "string",
  "position": 3,
  "record_type": "document",
  "relationships": [
    {
      "type": "parent",
      "id": "parent-doc-uuid",
      "title": "Documentation Root",
      "description": "Main documentation index"
    }
  ],
  "custom_metadata": {
    "review_status": "approved",
    "department": "engineering"
  }
}
```

## Storage Considerations

- The PyArrow schema is optimized for Lance columnar storage
- Vector embeddings are stored as fixed-size float32 arrays
- Raw binary data is stored as Lance Blobs for efficient lazy loading
- Custom metadata in PyArrow is stored as key-value pairs for better query performance
