# Phase 3.2: Batch Operations Implementation

## Overview
Implement 8 batch operation tools that work seamlessly with both stdio and HTTP transports, leveraging the transport abstraction layer from Phase 3.1.

## Timeline
**Week 2 of Phase 3 Implementation (5 days)**

## Batch Tools to Implement

### 1. batch_search
Execute multiple searches in one call with different parameters.

**Schema:**
```json
{
  "name": "batch_search",
  "description": "Execute multiple document searches in parallel",
  "inputSchema": {
    "type": "object",
    "properties": {
      "queries": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "search_type": {"enum": ["vector", "text", "hybrid"]},
            "limit": {"type": "integer", "default": 10},
            "filter": {"type": "string"}
          },
          "required": ["query"]
        }
      },
      "max_parallel": {
        "type": "integer",
        "default": 5,
        "description": "Maximum concurrent searches"
      }
    },
    "required": ["queries"]
  }
}
```

### 2. batch_add
Add multiple documents with shared settings.

**Schema:**
```json
{
  "name": "batch_add",
  "description": "Add multiple documents efficiently",
  "inputSchema": {
    "type": "object",
    "properties": {
      "documents": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "content": {"type": "string"},
            "metadata": {"type": "object"}
          },
          "required": ["content"]
        }
      },
      "shared_settings": {
        "type": "object",
        "properties": {
          "generate_embeddings": {"type": "boolean", "default": true},
          "collection": {"type": "string"},
          "chunk_size": {"type": "integer"},
          "chunk_overlap": {"type": "integer"}
        }
      },
      "atomic": {
        "type": "boolean",
        "default": true,
        "description": "Rollback all on any failure"
      }
    },
    "required": ["documents"]
  }
}
```

### 3. batch_update
Update many documents by filter or IDs.

**Schema:**
```json
{
  "name": "batch_update",
  "description": "Update multiple documents matching criteria",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {
        "type": "string",
        "description": "SQL filter for documents to update"
      },
      "document_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Specific UUIDs to update"
      },
      "updates": {
        "type": "object",
        "properties": {
          "metadata_updates": {"type": "object"},
          "content_template": {"type": "string"},
          "regenerate_embeddings": {"type": "boolean"}
        }
      },
      "max_documents": {
        "type": "integer",
        "default": 1000,
        "description": "Safety limit"
      }
    },
    "oneOf": [
      {"required": ["filter", "updates"]},
      {"required": ["document_ids", "updates"]}
    ]
  }
}
```

### 4. batch_delete
Delete documents matching criteria with safety checks.

**Schema:**
```json
{
  "name": "batch_delete",
  "description": "Delete multiple documents with confirmation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {"type": "string"},
      "document_ids": {"type": "array", "items": {"type": "string"}},
      "dry_run": {
        "type": "boolean",
        "default": true,
        "description": "Preview what would be deleted"
      },
      "confirm_count": {
        "type": "integer",
        "description": "Expected number of deletions"
      }
    },
    "oneOf": [
      {"required": ["filter"]},
      {"required": ["document_ids"]}
    ]
  }
}
```

### 5. batch_enhance
Enhance multiple documents together for efficiency.

**Schema:**
```json
{
  "name": "batch_enhance",
  "description": "Enhance multiple documents with LLM",
  "inputSchema": {
    "type": "object",
    "properties": {
      "document_ids": {"type": "array", "items": {"type": "string"}},
      "filter": {"type": "string"},
      "enhancements": {
        "type": "array",
        "items": {
          "enum": ["context", "tags", "title", "metadata"]
        }
      },
      "purpose": {"type": "string"},
      "batch_size": {
        "type": "integer",
        "default": 10,
        "description": "Documents per LLM call"
      }
    }
  }
}
```

### 6. batch_extract
Extract from multiple sources with progress tracking.

**Schema:**
```json
{
  "name": "batch_extract",
  "description": "Extract from multiple files/URLs",
  "inputSchema": {
    "type": "object",
    "properties": {
      "sources": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "path": {"type": "string"},
            "url": {"type": "string"},
            "type": {"enum": ["file", "url"]}
          }
        }
      },
      "add_to_dataset": {"type": "boolean", "default": true},
      "shared_metadata": {"type": "object"},
      "collection": {"type": "string"},
      "continue_on_error": {"type": "boolean", "default": true}
    },
    "required": ["sources"]
  }
}
```

### 7. batch_export
Export multiple documents in various formats.

**Schema:**
```json
{
  "name": "batch_export",
  "description": "Export documents in bulk",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {"type": "string"},
      "document_ids": {"type": "array", "items": {"type": "string"}},
      "format": {"enum": ["json", "jsonl", "csv", "parquet"]},
      "include_embeddings": {"type": "boolean", "default": false},
      "output_path": {"type": "string"},
      "chunk_size": {
        "type": "integer",
        "default": 1000,
        "description": "Documents per file for large exports"
      }
    }
  }
}
```

### 8. batch_import
Import documents from various sources.

**Schema:**
```json
{
  "name": "batch_import",
  "description": "Import documents from files",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source_path": {"type": "string"},
      "format": {"enum": ["json", "jsonl", "csv", "parquet"]},
      "mapping": {
        "type": "object",
        "description": "Field mapping configuration"
      },
      "validation": {
        "type": "object",
        "properties": {
          "require_schema_match": {"type": "boolean"},
          "max_errors": {"type": "integer", "default": 10}
        }
      },
      "generate_embeddings": {"type": "boolean", "default": true}
    },
    "required": ["source_path", "format"]
  }
}
```

## Implementation Architecture

### BatchOperationHandler
Base class for all batch operations:

```python
class BatchOperationHandler:
    def __init__(self, dataset: FrameDataset, transport: TransportAdapter):
        self.dataset = dataset
        self.transport = transport
        self.streaming = transport.get_streaming_adapter()
    
    async def execute_batch(self, operation: str, items: List[Any], processor: Callable):
        """Execute batch operation with progress tracking."""
        await self.streaming.start_stream(operation, len(items))
        
        results = []
        errors = []
        
        for i, item in enumerate(items):
            # Send progress
            await self.transport.send_progress(Progress(
                operation=operation,
                current=i + 1,
                total=len(items),
                status=f"Processing item {i + 1}"
            ))
            
            try:
                result = await processor(item)
                await self.streaming.send_item(result)
                results.append(result)
            except Exception as e:
                error = {"item": i, "error": str(e)}
                await self.streaming.send_error(json.dumps(error))
                errors.append(error)
        
        return await self.streaming.complete_stream({
            "total_processed": len(results),
            "total_errors": len(errors),
            "errors": errors
        })
```

### Transaction Support
For atomic operations:

```python
class BatchTransaction:
    def __init__(self, dataset: FrameDataset):
        self.dataset = dataset
        self.operations = []
        self.rollback_actions = []
    
    async def add_operation(self, op_type: str, data: Any):
        self.operations.append((op_type, data))
    
    async def commit(self):
        """Execute all operations atomically."""
        try:
            for op_type, data in self.operations:
                await self._execute_operation(op_type, data)
        except Exception as e:
            await self.rollback()
            raise
    
    async def rollback(self):
        """Undo all completed operations."""
        for action in reversed(self.rollback_actions):
            await action()
```

### Parallel Execution
For operations that can run concurrently:

```python
async def execute_parallel(tasks: List[Callable], max_parallel: int = 5):
    """Execute tasks with controlled parallelism."""
    semaphore = asyncio.Semaphore(max_parallel)
    
    async def run_with_semaphore(task):
        async with semaphore:
            return await task()
    
    return await asyncio.gather(*[
        run_with_semaphore(task) for task in tasks
    ])
```

## Transport-Specific Behavior

### Stdio Transport
- Progress updates collected in response
- All results returned at once
- Memory-efficient chunking for large operations

### HTTP Transport (Future)
- Real-time progress via SSE
- Streaming results as they complete
- Client can cancel mid-operation

## Testing Strategy

### Unit Tests
- Test each batch operation in isolation
- Mock transport and dataset interactions
- Verify progress reporting

### Integration Tests
- Test with real dataset
- Verify atomic transactions
- Test error handling and rollback

### Performance Tests
- Benchmark batch vs individual operations
- Memory usage for large batches
- Concurrent operation limits

## Success Criteria

- [ ] All 8 batch tools implemented
- [ ] Progress reporting works on stdio
- [ ] Atomic transactions with rollback
- [ ] Efficient parallel execution
- [ ] Comprehensive error handling
- [ ] Memory-efficient for large batches
- [ ] 90%+ test coverage
- [ ] Documentation with examples

## Next Steps

After batch operations are complete:
- Phase 3.3: Collection Management Tools
- Phase 3.4: Subscription System
- Phase 3.5: HTTP Transport Implementation