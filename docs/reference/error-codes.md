---
title: "Error Codes Reference"
---

# Error Codes Reference

This document lists all error codes that may be encountered when using ContextFrame.

## Error Code Format

ContextFrame error codes follow the format: `CF-XXXX`

Where:
- `CF` - ContextFrame prefix
- `XXXX` - Four-digit error code

## Error Categories

### Schema Validation Errors (CF-1xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-1001 | MISSING_REQUIRED_FIELD | Required field is missing from frame | Add the missing required field |
| CF-1002 | INVALID_FIELD_TYPE | Field type doesn't match schema | Ensure field has correct type |
| CF-1003 | INVALID_RECORD_TYPE | Invalid record_type value | Use: document, collection_header, or dataset_header |
| CF-1004 | INVALID_UUID_FORMAT | ID field is not valid UUID4 | Generate proper UUID4 identifier |
| CF-1005 | INVALID_TIMESTAMP | Timestamp not in ISO 8601 format | Use ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ) |
| CF-1006 | INVALID_LANGUAGE_CODE | Invalid ISO 639-1 language code | Use valid two-letter language code |
| CF-1007 | INVALID_MIME_TYPE | Invalid content_type MIME type | Use standard MIME type format |
| CF-1008 | INVALID_EMBEDDING | Embedding validation failed | Check dimensions and data types |
| CF-1009 | SCHEMA_VERSION_MISMATCH | Schema version not supported | Update to compatible schema version |

### Data Operation Errors (CF-2xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-2001 | FRAME_NOT_FOUND | Frame with specified ID not found | Verify frame ID exists |
| CF-2002 | DUPLICATE_FRAME_ID | Frame ID already exists | Use unique ID or update existing |
| CF-2003 | DATASET_NOT_FOUND | Dataset path not found | Check dataset path exists |
| CF-2004 | DATASET_CORRUPTED | Dataset files are corrupted | Restore from backup or recreate |
| CF-2005 | WRITE_PERMISSION_DENIED | No write access to dataset | Check file permissions |
| CF-2006 | READ_PERMISSION_DENIED | No read access to dataset | Check file permissions |
| CF-2007 | DATASET_LOCKED | Dataset is locked by another process | Wait and retry or check locks |
| CF-2008 | STORAGE_FULL | Insufficient storage space | Free up disk space |
| CF-2009 | INVALID_QUERY | Query syntax is invalid | Check query syntax documentation |

### Relationship Errors (CF-3xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-3001 | INVALID_RELATIONSHIP_TYPE | Unknown relationship type | Use valid relationship type |
| CF-3002 | TARGET_FRAME_NOT_FOUND | Relationship target doesn't exist | Ensure target frame exists |
| CF-3003 | CIRCULAR_RELATIONSHIP | Circular parent-child detected | Remove circular reference |
| CF-3004 | ORPHANED_RELATIONSHIP | Relationship has no valid target | Update or remove relationship |
| CF-3005 | DUPLICATE_RELATIONSHIP | Relationship already exists | Avoid duplicate relationships |

### Embedding Errors (CF-4xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-4001 | EMBEDDING_PROVIDER_ERROR | Embedding service failed | Check provider configuration |
| CF-4002 | INVALID_EMBEDDING_MODEL | Unknown embedding model | Use supported model name |
| CF-4003 | EMBEDDING_DIMENSION_MISMATCH | Embedding size doesn't match | Ensure consistent dimensions |
| CF-4004 | EMBEDDING_RATE_LIMIT | Provider rate limit exceeded | Implement rate limiting |
| CF-4005 | EMBEDDING_API_KEY_INVALID | Invalid API key for provider | Check API key configuration |

### Connector Errors (CF-5xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-5001 | CONNECTOR_AUTH_FAILED | Authentication failed | Check credentials |
| CF-5002 | CONNECTOR_NOT_FOUND | Unknown connector type | Use valid connector name |
| CF-5003 | CONNECTOR_RATE_LIMIT | API rate limit exceeded | Implement backoff strategy |
| CF-5004 | CONNECTOR_TIMEOUT | Connection timeout | Check network, increase timeout |
| CF-5005 | CONNECTOR_PERMISSION_DENIED | Insufficient permissions | Check API permissions |
| CF-5006 | CONNECTOR_INVALID_CONFIG | Invalid configuration | Review connector settings |

### Import/Export Errors (CF-6xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-6001 | INVALID_EXPORT_FORMAT | Unsupported export format | Use supported format |
| CF-6002 | INVALID_IMPORT_FORMAT | Cannot parse import file | Check file format |
| CF-6003 | IMPORT_SCHEMA_MISMATCH | Import schema incompatible | Update schema or transform data |
| CF-6004 | EXPORT_PATH_INVALID | Cannot write to export path | Check path permissions |
| CF-6005 | IMPORT_SIZE_LIMIT | Import file too large | Split into smaller files |

### MCP Server Errors (CF-7xxx)

| Code | Error | Description | Resolution |
|------|-------|-------------|------------|
| CF-7001 | MCP_SERVER_START_FAILED | Cannot start MCP server | Check port availability |
| CF-7002 | MCP_TRANSPORT_ERROR | Transport communication failed | Check transport configuration |
| CF-7003 | MCP_TOOL_NOT_FOUND | Requested tool doesn't exist | Verify tool name |
| CF-7004 | MCP_INVALID_PARAMS | Invalid tool parameters | Check parameter requirements |
| CF-7005 | MCP_AUTH_FAILED | MCP authentication failed | Verify credentials |

## Error Response Format

```json
{
  "error": {
    "code": "CF-1001",
    "message": "Missing required field: 'title'",
    "details": {
      "field": "title",
      "frame_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Common Solutions

### Schema Validation Issues
1. Use the validation tools before writing
2. Ensure all required fields are present
3. Check field types match schema

### Performance Issues
1. Use batch operations for multiple frames
2. Implement proper indexing
3. Consider pagination for large queries

### Integration Issues
1. Check API credentials and permissions
2. Implement retry logic with backoff
3. Monitor rate limits

### Data Consistency
1. Use transactions when available
2. Implement proper error handling
3. Maintain backups

## Getting Help

If you encounter an error not listed here:

1. Check the [Troubleshooting Guide](../troubleshooting.md)
2. Search [GitHub Issues](https://github.com/contextframe/contextframe/issues)
3. Ask in [Community Discussions](https://github.com/contextframe/contextframe/discussions)
4. Report new errors as GitHub issues