# Weaviate Export Methods and API Research

## Overview

Weaviate provides several methods to export vectors and objects from its vector database. This research covers the available export methods, API approaches, data formats, and best practices.

## 1. Export Methods

### 1.1 GraphQL Cursor API (Primary Method)
The recommended approach for exporting all data from Weaviate is using the GraphQL API with cursor-based pagination.

**Key Features:**
- Uses the `after` operator for cursor-based iteration
- Supports exporting all object properties, IDs, and vectors
- Handles large datasets efficiently
- Available in all client libraries

**Limitations:**
- Cannot combine `where` filters with `after` and `limit` parameters
- Maximum of 10,000 objects with offset/limit pagination
- For deeper pagination, must use cursor API

### 1.2 REST API
- Individual object retrieval by UUID
- Batch operations for multiple objects
- Limited batch export capabilities

### 1.3 Backup Module
- Full database backup to filesystem, S3, or GCS
- Preserves all data including vectors
- Can backup/restore specific classes
- Asynchronous operations
- Not suitable for selective data export

## 2. Data Export Approaches

### 2.1 Full Collection Export
```python
# Python Client v4
collection = client.collections.get("CollectionName")

for item in collection.iterator(include_vector=True):
    print(item.uuid, item.properties, item.vector)
```

### 2.2 Cursor-Based Pagination (Python Client v3)
```python
def get_batch_with_cursor(collection_name, batch_size, cursor=None):
    query = (
        client.query.get(
            collection_name,
            ["property1", "property2"]  # Specify properties
        )
        .with_additional(["id", "vector"])
        .with_limit(batch_size)
    )
    
    if cursor is not None:
        result = query.with_after(cursor).do()
    else:
        result = query.do()
    
    return result["data"]["Get"][collection_name]

# Iterate through all data
cursor = None
while True:
    next_batch = get_batch_with_cursor("CollectionName", 100, cursor)
    
    if len(next_batch) == 0:
        break
    
    # Process batch
    for obj in next_batch:
        print(obj)
    
    # Move cursor to last UUID
    cursor = next_batch[-1]["_additional"]["id"]
```

### 2.3 Including Vectors
Vectors can be included in the export by adding them to the `_additional` fields:

```python
# Python Client v4
collection.iterator(include_vector=True)

# Python Client v3
.with_additional(["id", "vector"])
```

## 3. Data Format

### 3.1 GraphQL Response Structure
```json
{
  "data": {
    "Get": {
      "CollectionName": [
        {
          "property1": "value1",
          "property2": "value2",
          "_additional": {
            "id": "uuid-here",
            "vector": [0.1, 0.2, 0.3, ...]
          }
        }
      ]
    }
  }
}
```

### 3.2 Object Properties
- Standard properties: As defined in schema
- Metadata: Available through `_additional`
  - `id`: Object UUID
  - `vector`: Embedding vector
  - `creationTimeUnix`: Creation timestamp
  - `lastUpdateTimeUnix`: Last update timestamp
  - `distance`: Distance to query (in search context)

## 4. Authentication Methods

### 4.1 API Key Authentication
```python
import weaviate

client = weaviate.Client(
    url="https://your-instance.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey(api_key="YOUR-API-KEY")
)
```

### 4.2 Custom Headers
```python
client = weaviate.Client(
    url="https://your-instance.weaviate.network",
    additional_headers={
        "X-API-Key": "YOUR-API-KEY"
    }
)
```

## 5. Batch Export Best Practices

### 5.1 Recommended Parameters
- **Batch size**: 100-500 objects per request
- **Timeout**: Adjust based on data size
- **Error handling**: Implement retry logic
- **Progress tracking**: Use cursor position for resume capability

### 5.2 Performance Considerations
- Start with smaller batch sizes and adjust up
- Monitor memory usage for large vector exports
- Consider parallel processing for multiple collections
- Use compression for network transfer

## 6. Limitations and Constraints

### 6.1 Query Limitations
- Cannot use `where` filters with cursor pagination
- Maximum 10,000 objects with offset/limit
- No built-in streaming export
- No native CSV/JSON export format

### 6.2 Vector Size Limits
- Maximum vector dimensions: 65,535
- Vectors stored as float32 arrays
- Memory considerations for large vectors

## 7. Multi-Tenancy Considerations

For multi-tenant collections, iterate through each tenant:

```python
# Get all tenants
tenants = collection.tenants.get()

# Iterate through tenants
for tenant_name in tenants.keys():
    for item in collection.with_tenant(tenant_name).iterator():
        print(f"{tenant_name}: {item.properties}")
```

## 8. Cross-References

Cross-references are exported as properties and can be retrieved with:

```python
# Include cross-references in query
response = collection.query.fetch_objects(
    return_references=wvc.query.QueryReference(
        link_on="hasCategory",
        return_properties=["title"]
    )
)
```

## 9. Alternative Export Methods

### 9.1 Backup and Restore
- Use for full database migration
- Supports filesystem, S3, GCS backends
- Preserves all metadata and vectors
- Not suitable for selective export

### 9.2 Direct Database Access
- Not recommended
- Would require direct access to underlying storage
- Breaks abstraction layer

## 10. Example: Complete Export Script

```python
import weaviate
import json
from datetime import datetime

def export_weaviate_collection(client, collection_name, output_file):
    """Export entire Weaviate collection to JSON file"""
    
    collection = client.collections.get(collection_name)
    
    exported_data = {
        "collection": collection_name,
        "export_date": datetime.now().isoformat(),
        "objects": []
    }
    
    # Export all objects with vectors
    for item in collection.iterator(include_vector=True):
        obj_data = {
            "uuid": item.uuid,
            "properties": item.properties,
            "vector": item.vector.get("default") if item.vector else None,
            "references": {}
        }
        
        # Add references if any
        if hasattr(item, 'references'):
            for ref_name, ref_data in item.references.items():
                obj_data["references"][ref_name] = [
                    {"uuid": r.uuid, "properties": r.properties} 
                    for r in ref_data.objects
                ]
        
        exported_data["objects"].append(obj_data)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(exported_data, f, indent=2)
    
    return len(exported_data["objects"])

# Usage
client = weaviate.connect_to_local()
count = export_weaviate_collection(client, "Articles", "articles_export.json")
print(f"Exported {count} objects")
```

## Key Takeaways

1. **Primary Export Method**: Use GraphQL cursor API with iterator pattern
2. **Include Vectors**: Explicitly request vectors in `_additional` fields
3. **Batch Processing**: Use reasonable batch sizes (100-500)
4. **Authentication**: Use API keys or custom headers
5. **Format**: Data returned as JSON, needs custom formatting for other formats
6. **Large Datasets**: Implement cursor-based pagination with resume capability
7. **Multi-tenancy**: Handle tenant iteration separately
8. **Cross-references**: Export as part of object properties