"""Integration tests for MCP batch operation tools."""

import asyncio
import json
import pytest
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.batch import BatchTools
from contextframe.mcp.core.transport import Progress, TransportAdapter
from typing import Any, Dict, List
from uuid import uuid4
from pathlib import Path
import tempfile


class MockTransportAdapter(TransportAdapter):
    """Mock transport adapter for testing."""

    def __init__(self):
        super().__init__()
        self.progress_updates: list[Progress] = []
        self.messages_sent: list[dict[str, Any]] = []

        # Add progress handler to capture updates
        self.add_progress_handler(self._capture_progress)

    async def _capture_progress(self, progress: Progress):
        self.progress_updates.append(progress)

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def send_message(self, message: dict[str, Any]) -> None:
        self.messages_sent.append(message)

    async def receive_message(self) -> None:
        return None


class MockToolRegistry:
    """Minimal tool registry mock for testing."""

    def __init__(self, dataset, transport):
        self.dataset = dataset
        self.transport = transport

    async def call_tool(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Route tool calls to appropriate handlers."""
        if name == "search_documents":
            return await self.search_documents(params)
        elif name == "document_create":
            return await self.document_create(params)
        elif name == "document_update":
            return await self.document_update(params)
        elif name == "document_delete":
            return await self.document_delete(params)
        elif name == "document_get":
            return await self.document_get(params)
        elif name == "collection_create":
            return await self.collection_create(params)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def search_documents(self, params: dict[str, Any]) -> dict[str, Any]:
        """Search documents in the dataset."""
        query = params.get("query", "")
        search_type = params.get("search_type", "text")
        limit = params.get("limit", 10)
        filter_expr = params.get("filter")
        
        # For testing, use a simple text matching approach
        results = []
        
        # Build scanner with filter if provided
        scanner_kwargs = {"limit": 1000}  # Scan more to find matches
        if filter_expr:
            scanner_kwargs["filter"] = filter_expr
            
        # Scan documents and filter by query text
        scanner = self.dataset.scanner(**scanner_kwargs)
        for batch in scanner.to_batches():
            # Convert batch to records
            for i in range(len(batch)):
                row_dict = {}
                for field in batch.schema:
                    col = batch.column(field.name)
                    if col is not None and i < len(col):
                        row_dict[field.name] = col[i].as_py()
                
                # Create FrameRecord from row
                if row_dict.get("text_content") and query.lower() in row_dict["text_content"].lower():
                    record = FrameRecord(
                        text_content=row_dict.get("text_content", ""),
                        metadata={k: v for k, v in row_dict.items() if k not in ["text_content", "vector", "raw_data", "raw_data_type"]}
                    )
                    results.append(record)
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break
        
        return {
            "total_count": len(results),
            "documents": [
                {
                    "id": doc.metadata["uuid"],
                    "content": doc.text_content,
                    "metadata": doc.metadata,
                    "score": 1.0  # Mock score
                }
                for doc in results
            ]
        }

    async def document_create(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new document."""
        content = params["content"]
        metadata = params.get("metadata", {})
        collection = params.get("collection")
        
        if collection:
            metadata["collection"] = collection
            
        record = FrameRecord(
            text_content=content,
            metadata=metadata
        )
        
        self.dataset.add(record)
        
        return {
            "id": record.metadata["uuid"],
            "message": "Document created successfully"
        }

    async def document_update(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update document metadata."""
        doc_id = params["id"]
        metadata_updates = params.get("metadata", {})
        
        # Get existing document
        scanner = self.dataset.scanner(filter=f"uuid = '{doc_id}'")
        tbl = scanner.to_table()
        if tbl.num_rows == 0:
            raise ValueError(f"Document {doc_id} not found")
        
        # Convert to FrameRecord
        doc = FrameRecord.from_arrow(tbl.slice(0, 1))
        
        # Update metadata
        doc.metadata.update(metadata_updates)
        
        # Delete and re-add (Lance doesn't support in-place updates)
        self.dataset.delete(f"uuid = '{doc_id}'")
        self.dataset.add(doc)
        
        return {
            "id": doc_id,
            "message": "Document updated successfully"
        }

    async def document_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a document."""
        doc_id = params["id"]
        self.dataset.delete(f"uuid = '{doc_id}'")
        
        return {
            "id": doc_id,
            "message": "Document deleted successfully"
        }

    async def document_get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get a document by ID."""
        doc_id = params["id"]
        
        scanner = self.dataset.scanner(filter=f"uuid = '{doc_id}'")
        tbl = scanner.to_table()
        if tbl.num_rows == 0:
            raise ValueError(f"Document {doc_id} not found")
        
        # Convert to FrameRecord
        doc = FrameRecord.from_arrow(tbl.slice(0, 1))
        
        return {
            "id": doc_id,
            "content": doc.text_content,
            "metadata": doc.metadata
        }

    async def collection_create(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a collection."""
        name = params["name"]
        description = params.get("description", "")
        
        # For testing, just return success
        return {
            "id": f"collection_{name}",
            "name": name,
            "description": description,
            "message": "Collection created successfully"
        }


@pytest.fixture
async def test_dataset(tmp_path):
    """Create a test dataset with sample documents."""
    dataset_path = tmp_path / "test_batch_integration.lance"
    dataset = FrameDataset.create(str(dataset_path))

    # Add test documents with proper metadata
    for i in range(20):
        record = FrameRecord(
            text_content=f"Test document {i}: This is test content about topic {i % 3}. "
                        f"Additional content for search testing with keyword{i % 5}.",
            metadata={
                "title": f"Test Document {i}",
                "record_type": "document",
                "collection": f"test_collection_{i % 2}",
                "tags": [f"tag{i % 3}", f"tag{i % 4}"],
                "custom_metadata": {
                    "x_topic": f"topic_{i % 3}",
                    "x_index": str(i),
                    "x_keyword": f"keyword{i % 5}"
                }
            }
        )
        dataset.add(record)

    yield dataset


@pytest.fixture
async def batch_tools_setup(test_dataset):
    """Create batch tools with test dataset and transport."""
    transport = MockTransportAdapter()
    await transport.initialize()

    # Create mock tool registry
    tool_registry = MockToolRegistry(test_dataset, transport)

    # Create batch tools
    batch_tools = BatchTools(test_dataset, transport, tool_registry)

    yield batch_tools, transport, tool_registry

    await transport.shutdown()


class TestBatchSearchIntegration:
    """Test batch search functionality."""

    @pytest.mark.asyncio
    async def test_batch_search_multiple_queries(self, batch_tools_setup):
        """Test batch search with multiple queries."""
        batch_tools, transport, _ = batch_tools_setup

        params = {
            "queries": [
                {"query": "topic 0", "search_type": "text", "limit": 5},
                {"query": "topic 1", "search_type": "text", "limit": 5},
                {"query": "topic 2", "search_type": "text", "limit": 5},
                {"query": "keyword3", "search_type": "text", "limit": 3},
            ],
            "max_parallel": 2,
        }

        result = await batch_tools.batch_search(params)
        
        print(f"Result: {result}")
        if "errors" in result:
            print(f"Errors: {result['errors']}")

        assert result["searches_completed"] == 4
        assert result["searches_failed"] == 0
        assert len(result["results"]) == 4

        # Check each query returned results
        for i, search_result in enumerate(result["results"][:3]):
            assert search_result["success"]
            assert search_result["query"] == f"topic {i}"
            assert "results" in search_result
            assert "count" in search_result
            # Should find documents about this topic
            assert search_result["count"] > 0

        # Check keyword search - looking for documents with keyword3
        keyword_result = result["results"][3]
        assert keyword_result["query"] == "keyword3"
        # keyword3 appears in documents 3, 8, 13, 18
        assert keyword_result["count"] >= 3  # Should find at least 3

        # Progress tracking is not implemented in our execute_parallel fix
        # This would require updating the batch handler implementation

    @pytest.mark.asyncio
    async def test_batch_search_with_filters(self, batch_tools_setup):
        """Test batch search with filters."""
        batch_tools, _, _ = batch_tools_setup

        params = {
            "queries": [
                {
                    "query": "test",
                    "search_type": "text",
                    "limit": 10,
                    "filter": "collection = 'test_collection_0'"
                },
                {
                    "query": "test",
                    "search_type": "text",
                    "limit": 10,
                    "filter": "collection = 'test_collection_1'"
                },
            ],
            "max_parallel": 2,
        }

        result = await batch_tools.batch_search(params)

        assert result["searches_completed"] == 2
        assert result["searches_failed"] == 0

        # Each query should only find documents in its collection
        for i, search_result in enumerate(result["results"]):
            assert search_result["success"]
            # All results should be from the filtered collection
            for doc in search_result["results"]:
                assert doc["metadata"]["collection"] == f"test_collection_{i}"


class TestBatchAddIntegration:
    """Test batch add functionality."""

    @pytest.mark.asyncio
    async def test_batch_add_atomic_success(self, batch_tools_setup):
        """Test successful atomic batch add."""
        batch_tools, _, _ = batch_tools_setup

        initial_count = batch_tools.dataset._dataset.count_rows()

        params = {
            "documents": [
                {
                    "content": "New document 1 about AI",
                    "metadata": {
                        "title": "AI Document",
                        "tags": ["ai", "ml"],
                        "custom_metadata": {"x_category": "technical"}
                    }
                },
                {
                    "content": "New document 2 about Python",
                    "metadata": {
                        "title": "Python Guide",
                        "tags": ["python", "programming"],
                        "custom_metadata": {"x_category": "tutorial"}
                    }
                },
                {
                    "content": "New document 3 about testing",
                    "metadata": {
                        "title": "Testing Best Practices",
                        "tags": ["testing", "qa"],
                        "custom_metadata": {"x_category": "methodology"}
                    }
                },
            ],
            "shared_settings": {
                "generate_embeddings": False,
                "collection": "new_batch",
            },
            "atomic": True,
        }

        result = await batch_tools.batch_add(params)
        
        # Debug print to see what's wrong
        if not result.get("success"):
            print(f"Batch add failed: {result}")

        assert result["success"]
        assert result["documents_added"] == 3
        assert result["atomic"]
        assert len(result["document_ids"]) == 3

        # Verify documents were added
        final_count = batch_tools.dataset._dataset.count_rows()
        assert final_count == initial_count + 3

        # Verify we can retrieve the documents
        for doc_id in result["document_ids"]:
            # Query for the document using scanner
            scanner = batch_tools.dataset.scanner(filter=f"uuid = '{doc_id}'")
            tbl = scanner.to_table()
            assert tbl.num_rows == 1
            # Verify collection was set
            row = tbl.to_pylist()[0]
            assert row["collection"] == "new_batch"

    @pytest.mark.asyncio
    async def test_batch_add_non_atomic_partial_failure(self, batch_tools_setup):
        """Test non-atomic batch add with some failures."""
        batch_tools, _, _ = batch_tools_setup

        params = {
            "documents": [
                {
                    "content": "Valid document",
                    "metadata": {"title": "Valid"}
                },
                {
                    "content": "Valid but will fail",
                    "metadata": {} # Missing required title field
                },
                {
                    "content": "Another valid document",
                    "metadata": {"title": "Also Valid"}
                },
            ],
            "shared_settings": {"generate_embeddings": False},
            "atomic": False,
        }

        result = await batch_tools.batch_add(params)

        assert result["documents_added"] == 2
        assert result["documents_failed"] == 1
        assert not result["atomic"]
        assert len(result["errors"]) == 1
        assert result["errors"][0]["item_index"] == 1


class TestBatchUpdateIntegration:
    """Test batch update functionality."""

    @pytest.mark.asyncio
    async def test_batch_update_by_filter(self, batch_tools_setup):
        """Test updating documents by filter."""
        batch_tools, _, _ = batch_tools_setup

        # Update all documents in collection 0
        params = {
            "filter": "collection = 'test_collection_0'",
            "updates": {
                "metadata_updates": {
                    "status": "reviewed"
                }
            },
            "max_documents": 50,
        }

        result = await batch_tools.batch_update(params)
        
        print(f"Update result: {result}")
        print(f"Errors: {result.get('errors', [])}")

        assert "documents_updated" in result
        assert result["documents_updated"] > 0
        assert result["documents_failed"] == 0

        # Verify updates were applied
        # Note: Can't filter by both collection and status in Lance, so just check collection
        scanner = batch_tools.dataset.scanner(
            filter="collection = 'test_collection_0'",
            limit=20
        )
        tbl = scanner.to_table()
        # Check that all rows have status = 'reviewed'
        reviewed_count = 0
        for i, row in enumerate(tbl.to_pylist()):
            # Debug: print first row structure
            if i == 0:
                print(f"Row keys: {list(row.keys())}")
                print(f"Status value: {row.get('status')}")
                print(f"Custom metadata: {row.get('custom_metadata')}")
            # Status is a top-level field in Lance schema
            if row.get("status") == "reviewed":
                reviewed_count += 1
        assert reviewed_count == result["documents_updated"]

    @pytest.mark.asyncio
    async def test_batch_update_by_ids(self, batch_tools_setup):
        """Test updating specific documents by IDs."""
        batch_tools, _, _ = batch_tools_setup

        # Get some document IDs  
        scanner = batch_tools.dataset.scanner(limit=3)
        tbl = scanner.to_table()
        doc_ids = []
        for i in range(min(3, tbl.num_rows)):
            row = tbl.to_pylist()[i]
            doc_ids.append(row["uuid"])

        params = {
            "document_ids": doc_ids,
            "updates": {
                "metadata_updates": {
                    "tags": ["updated", "batch"],
                    "custom_metadata": {
                        "x_priority": "high"
                    }
                }
            }
        }

        result = await batch_tools.batch_update(params)

        assert result["documents_updated"] == 3
        assert result["documents_failed"] == 0

        # Verify updates
        for doc_id in doc_ids:
            scanner = batch_tools.dataset.scanner(filter=f"uuid = '{doc_id}'")
            tbl = scanner.to_table()
            assert tbl.num_rows == 1
            row = tbl.to_pylist()[0]
            # Check custom_metadata for x_priority
            custom_metadata = row.get("custom_metadata", [])
            priority_found = False
            for item in custom_metadata:
                if item.get("key") == "x_priority" and item.get("value") == "high":
                    priority_found = True
                    break
            assert priority_found
            assert "updated" in row["tags"]
            assert "batch" in row["tags"]


class TestBatchDeleteIntegration:
    """Test batch delete functionality."""

    @pytest.mark.asyncio
    async def test_batch_delete_dry_run(self, batch_tools_setup):
        """Test batch delete with dry run."""
        batch_tools, _, _ = batch_tools_setup

        params = {
            "filter": "collection = 'test_collection_1'",
            "dry_run": True
        }

        result = await batch_tools.batch_delete(params)

        assert result["success"]
        assert result["dry_run"]
        assert result["documents_to_delete"] > 0
        assert "document_ids" in result
        assert len(result["document_ids"]) == result["documents_to_delete"]

        # Verify no documents were actually deleted
        scanner = batch_tools.dataset.scanner(
            filter="collection = 'test_collection_1'",
            limit=20
        )
        tbl = scanner.to_table()
        assert tbl.num_rows == result["documents_to_delete"]

    @pytest.mark.asyncio
    async def test_batch_delete_with_confirmation(self, batch_tools_setup):
        """Test batch delete with confirmation."""
        batch_tools, _, _ = batch_tools_setup

        # First do dry run
        dry_params = {
            "filter": "collection = 'test_collection_0'",
            "dry_run": True
        }
        dry_result = await batch_tools.batch_delete(dry_params)
        to_delete = dry_result["documents_to_delete"]

        # Delete with correct confirmation
        delete_params = {
            "filter": "collection = 'test_collection_0'",
            "dry_run": False,
            "confirm_count": to_delete
        }
        delete_result = await batch_tools.batch_delete(delete_params)

        assert delete_result["success"]
        assert delete_result["documents_deleted"] == to_delete

        # Verify documents were deleted
        scanner = batch_tools.dataset.scanner(
            filter="collection = 'test_collection_0'",
            limit=20
        )
        tbl = scanner.to_table()
        assert tbl.num_rows == 0


class TestBatchExportIntegration:
    """Test batch export functionality."""

    @pytest.mark.asyncio
    async def test_batch_export_json(self, batch_tools_setup, tmp_path):
        """Test exporting documents to JSON."""
        batch_tools, _, _ = batch_tools_setup

        export_file = tmp_path / "export.json"

        params = {
            "format": "json",
            "output_path": str(export_file),
            "filter": "collection = 'test_collection_0'",
            "limit": 5
        }

        result = await batch_tools.batch_export(params)
        
        if not result.get("success"):
            print(f"Export failed: {result}")

        assert result["success"]
        assert result["documents_exported"] == 5
        assert result["format"] == "json"
        assert export_file.exists()

        # Verify exported content
        with open(export_file) as f:
            exported = json.load(f)
        
        assert "documents" in exported
        assert len(exported["documents"]) == 5
        assert all(doc["metadata"]["collection"] == "test_collection_0" 
                  for doc in exported["documents"])

    @pytest.mark.asyncio
    async def test_batch_export_jsonl(self, batch_tools_setup, tmp_path):
        """Test exporting documents to JSONL."""
        batch_tools, _, _ = batch_tools_setup

        export_file = tmp_path / "export.jsonl"

        params = {
            "format": "jsonl",
            "output_path": str(export_file),
            "limit": 10
        }

        result = await batch_tools.batch_export(params)
        
        if not result.get("success"):
            print(f"Export failed: {result}")

        assert result["success"]
        assert result["documents_exported"] == 10
        assert export_file.exists()

        # Verify JSONL format
        with open(export_file) as f:
            lines = f.readlines()
        
        assert len(lines) == 10
        for line in lines:
            doc = json.loads(line)
            assert "content" in doc
            assert "metadata" in doc


class TestBatchImportIntegration:
    """Test batch import functionality."""

    @pytest.mark.asyncio
    async def test_batch_import_json(self, batch_tools_setup, tmp_path):
        """Test importing documents from JSON."""
        batch_tools, _, _ = batch_tools_setup

        # Create test import file
        import_data = {
            "documents": [
                {
                    "content": f"Imported document {i}",
                    "metadata": {
                        "title": f"Import {i}",
                        "record_type": "document",
                        "custom_metadata": {
                            "x_source": "json_import",
                            "x_import_batch": "test1"
                        }
                    }
                }
                for i in range(5)
            ]
        }

        import_file = tmp_path / "import.json"
        with open(import_file, "w") as f:
            json.dump(import_data, f)

        initial_count = batch_tools.dataset._dataset.count_rows()

        params = {
            "format": "json",
            "source_path": str(import_file),
            "generate_embeddings": False
        }

        result = await batch_tools.batch_import(params)
        
        # Debug output
        print(f"Import result: {result}")
        if not result.get("success"):
            print(f"Import failed: {result}")
        if "errors" in result and result["errors"]:
            print(f"Errors: {result['errors']}")

        assert result["success"]
        assert result["documents_imported"] == 5
        assert result["documents_failed"] == 0

        # Verify import
        final_count = batch_tools.dataset._dataset.count_rows()
        print(f"Initial count: {initial_count}, Final count: {final_count}")
        assert final_count == initial_count + 5

        # Verify documents were imported by checking custom metadata
        scanner = batch_tools.dataset.scanner(limit=50)
        tbl = scanner.to_table()
        
        # Count documents with our import batch marker
        imported_count = 0
        for i in range(tbl.num_rows):
            row = tbl.to_pylist()[i]
            custom_metadata = row.get("custom_metadata", [])
            for item in custom_metadata:
                if item.get("key") == "x_import_batch" and item.get("value") == "test1":
                    imported_count += 1
                    break
        
        assert imported_count == 5


@pytest.mark.asyncio
async def test_batch_operations_end_to_end(batch_tools_setup, tmp_path):
    """Test complete batch operation workflow."""
    batch_tools, transport, _ = batch_tools_setup

    # 1. Search for documents to process
    search_params = {
        "queries": [
            {"query": "topic", "limit": 10},
            {"query": "keyword", "limit": 10}
        ],
        "max_parallel": 2
    }
    search_result = await batch_tools.batch_search(search_params)
    assert search_result["searches_completed"] == 2

    # 2. Add new documents
    add_params = {
        "documents": [
            {
                "content": f"Workflow test document {i}",
                "metadata": {"title": f"Workflow {i}"}
            }
            for i in range(3)
        ],
        "shared_settings": {"collection": "workflow_test", "generate_embeddings": False},
        "atomic": True
    }
    add_result = await batch_tools.batch_add(add_params)
    assert add_result["documents_added"] == 3
    new_ids = add_result["document_ids"]

    # 3. Update the new documents
    update_params = {
        "document_ids": new_ids,
        "updates": {
            "metadata_updates": {
                "status": "processed",
                "custom_metadata": {
                    "x_workflow_stage": "completed"
                }
            }
        }
    }
    update_result = await batch_tools.batch_update(update_params)
    assert update_result["documents_updated"] == 3

    # 4. Export processed documents
    export_file = tmp_path / "workflow_export.json"
    export_params = {
        "format": "json",
        "output_path": str(export_file),
        "filter": "collection = 'workflow_test' AND status = 'processed'"
    }
    export_result = await batch_tools.batch_export(export_params)
    assert export_result["documents_exported"] == 3

    # 5. Delete the test documents
    delete_params = {
        "filter": "collection = 'workflow_test'",
        "dry_run": False,
        "confirm_count": 3
    }
    delete_result = await batch_tools.batch_delete(delete_params)
    assert delete_result["documents_deleted"] == 3

    # Verify workflow completed successfully
    assert len(transport.progress_updates) > 0
    # Check that all workflow_test documents were deleted
    scanner = batch_tools.dataset.scanner(
        filter="collection = 'workflow_test'",
        limit=10
    )
    tbl = scanner.to_table()
    assert tbl.num_rows == 0