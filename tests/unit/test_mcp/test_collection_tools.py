"""Tests for MCP collection management tools."""

import asyncio
import pytest
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.collections import CollectionTools
from contextframe.mcp.collections.templates import TemplateRegistry
from contextframe.mcp.core.transport import Progress, TransportAdapter
from typing import Any, Dict, List
from uuid import UUID, uuid4


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


@pytest.fixture
async def test_dataset(tmp_path):
    """Create a test dataset with sample documents."""
    dataset_path = tmp_path / "test_collections.lance"
    dataset = FrameDataset.create(str(dataset_path))

    # Add test documents
    docs = []
    for i in range(15):
        record = FrameRecord(
            text_content=f"Test document {i}: Content about {'project' if i < 5 else 'research' if i < 10 else 'general'} topic",
            metadata={
                "title": f"Document {i}",
                "tags": [f"tag{i % 3}", f"category{i % 2}"],
                "created_at": f"2024-01-{(i % 30) + 1:02d}",
            },
        )
        dataset.add(record)
        docs.append(record)

    yield dataset, docs


@pytest.fixture
async def collection_tools(test_dataset):
    """Create collection tools with test dataset and transport."""
    dataset, _ = test_dataset
    transport = MockTransportAdapter()
    await transport.initialize()

    template_registry = TemplateRegistry()
    collection_tools = CollectionTools(dataset, transport, template_registry)

    yield collection_tools

    await transport.shutdown()


class TestCollectionCreation:
    """Test collection creation functionality."""

    @pytest.mark.asyncio
    async def test_create_basic_collection(self, collection_tools):
        """Test creating a basic collection."""
        params = {
            "name": "Test Collection",
            "description": "A test collection for unit tests",
            "metadata": {"x_purpose": "testing", "x_version": "1.0"},
        }

        result = await collection_tools.create_collection(params)

        assert result["name"] == "Test Collection"
        assert result["member_count"] == 0
        assert result["metadata"]["x_purpose"] == "testing"
        assert "collection_id" in result
        assert "header_id" in result
        assert "created_at" in result

    @pytest.mark.asyncio
    async def test_create_collection_with_members(self, collection_tools, test_dataset):
        """Test creating a collection with initial members."""
        dataset, docs = test_dataset

        # Get some document IDs
        doc_ids = [str(doc.uuid) for doc in docs[:3]]

        params = {
            "name": "Project Docs",
            "description": "Project documentation collection",
            "initial_members": doc_ids,
        }

        result = await collection_tools.create_collection(params)

        assert result["member_count"] == 3

    @pytest.mark.asyncio
    async def test_create_collection_with_template(self, collection_tools):
        """Test creating a collection with a template."""
        params = {
            "name": "My Project",
            "template": "project",
            "metadata": {"x_team": "engineering"},
        }

        result = await collection_tools.create_collection(params)

        assert result["name"] == "My Project"
        assert "collection_id" in result

    @pytest.mark.asyncio
    async def test_create_hierarchical_collection(self, collection_tools):
        """Test creating a collection hierarchy."""
        # Create parent collection
        parent_params = {"name": "Parent Collection", "description": "The parent"}
        parent_result = await collection_tools.create_collection(parent_params)

        # Create child collection
        child_params = {
            "name": "Child Collection",
            "description": "The child",
            "parent_collection": parent_result["collection_id"],
        }
        child_result = await collection_tools.create_collection(child_params)

        assert child_result["name"] == "Child Collection"
        # The relationships should be established


class TestCollectionUpdate:
    """Test collection update functionality."""

    @pytest.mark.asyncio
    async def test_update_collection_metadata(self, collection_tools):
        """Test updating collection metadata."""
        # Create collection
        create_params = {"name": "Original Name", "description": "Original description"}
        create_result = await collection_tools.create_collection(create_params)

        # Update collection
        update_params = {
            "collection_id": create_result["collection_id"],
            "name": "Updated Name",
            "description": "Updated description",
            "metadata_updates": {"x_status": "active"},
        }
        update_result = await collection_tools.update_collection(update_params)

        assert update_result["updated"] is True

    @pytest.mark.asyncio
    async def test_add_remove_members(self, collection_tools, test_dataset):
        """Test adding and removing collection members."""
        dataset, docs = test_dataset

        # Create collection
        create_result = await collection_tools.create_collection({"name": "Test"})
        collection_id = create_result["collection_id"]

        # Add members
        add_params = {
            "collection_id": collection_id,
            "add_members": [str(docs[0].uuid), str(docs[1].uuid), str(docs[2].uuid)],
        }
        add_result = await collection_tools.update_collection(add_params)

        assert add_result["members_added"] == 3
        assert add_result["total_members"] == 3

        # Remove members
        remove_params = {
            "collection_id": collection_id,
            "remove_members": [str(docs[0].uuid)],
        }
        remove_result = await collection_tools.update_collection(remove_params)

        assert remove_result["members_removed"] == 1
        assert remove_result["total_members"] == 2


class TestCollectionDeletion:
    """Test collection deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_collection_only(self, collection_tools, test_dataset):
        """Test deleting collection without members."""
        dataset, docs = test_dataset

        # Create collection with members
        create_params = {
            "name": "To Delete",
            "initial_members": [str(docs[0].uuid), str(docs[1].uuid)],
        }
        create_result = await collection_tools.create_collection(create_params)

        # Delete collection only
        delete_params = {
            "collection_id": create_result["collection_id"],
            "delete_members": False,
        }
        delete_result = await collection_tools.delete_collection(delete_params)

        assert delete_result["total_collections_deleted"] == 1
        assert delete_result["total_members_deleted"] == 0

        # Members should still exist
        assert dataset.get_by_uuid(str(docs[0].uuid)) is not None
        assert dataset.get_by_uuid(str(docs[1].uuid)) is not None

    @pytest.mark.asyncio
    async def test_delete_collection_with_members(self, collection_tools, test_dataset):
        """Test deleting collection with its members."""
        dataset, docs = test_dataset

        # Create collection with members
        create_params = {
            "name": "To Delete With Members",
            "initial_members": [str(docs[0].uuid), str(docs[1].uuid)],
        }
        create_result = await collection_tools.create_collection(create_params)

        # Delete collection and members
        delete_params = {
            "collection_id": create_result["collection_id"],
            "delete_members": True,
        }
        delete_result = await collection_tools.delete_collection(delete_params)

        assert delete_result["total_collections_deleted"] == 1
        assert delete_result["total_members_deleted"] == 2

    @pytest.mark.asyncio
    async def test_recursive_deletion(self, collection_tools):
        """Test recursive deletion of collection hierarchy."""
        # Create parent
        parent = await collection_tools.create_collection({"name": "Parent"})

        # Create children
        child1 = await collection_tools.create_collection(
            {"name": "Child1", "parent_collection": parent["collection_id"]}
        )
        child2 = await collection_tools.create_collection(
            {"name": "Child2", "parent_collection": parent["collection_id"]}
        )

        # Delete recursively
        delete_params = {"collection_id": parent["collection_id"], "recursive": True}
        delete_result = await collection_tools.delete_collection(delete_params)

        assert delete_result["total_collections_deleted"] == 3  # Parent + 2 children


class TestCollectionListing:
    """Test collection listing functionality."""

    @pytest.mark.asyncio
    async def test_list_all_collections(self, collection_tools):
        """Test listing all collections."""
        # Create some collections
        for i in range(5):
            await collection_tools.create_collection(
                {"name": f"Collection {i}", "metadata": {"x_index": i}}
            )

        # List all
        list_params = {"limit": 10, "include_stats": False}
        list_result = await collection_tools.list_collections(list_params)

        assert list_result["total_count"] >= 5
        assert len(list_result["collections"]) >= 5

    @pytest.mark.asyncio
    async def test_list_with_filters(self, collection_tools):
        """Test listing collections with filters."""
        # Create parent
        parent = await collection_tools.create_collection({"name": "Parent"})

        # Create children
        for i in range(3):
            await collection_tools.create_collection(
                {"name": f"Child {i}", "parent_collection": parent["collection_id"]}
            )

        # List only children
        list_params = {"parent_id": parent["collection_id"], "include_stats": False}
        list_result = await collection_tools.list_collections(list_params)

        assert list_result["total_count"] == 3

    @pytest.mark.asyncio
    async def test_list_with_sorting(self, collection_tools):
        """Test listing collections with different sort orders."""
        # Create collections
        names = ["Zebra", "Alpha", "Beta"]
        for name in names:
            await collection_tools.create_collection({"name": name})

        # Sort by name
        list_params = {"sort_by": "name", "limit": 10}
        list_result = await collection_tools.list_collections(list_params)

        # Extract names from results
        # Debug: check the structure
        if list_result["collections"]:
            first_item = list_result["collections"][0]
            if isinstance(first_item, dict) and "collection" in first_item:
                # It's wrapped with stats
                collection_names = [
                    c["collection"]["name"] for c in list_result["collections"]
                ]
            else:
                # Direct collection dicts
                collection_names = [c["name"] for c in list_result["collections"]]
        else:
            collection_names = []

        # Check alphabetical order
        assert collection_names[:3] == ["Alpha", "Beta", "Zebra"]


class TestDocumentMovement:
    """Test moving documents between collections."""

    @pytest.mark.asyncio
    async def test_move_documents_between_collections(
        self, collection_tools, test_dataset
    ):
        """Test moving documents from one collection to another."""
        dataset, docs = test_dataset

        # Create two collections
        source = await collection_tools.create_collection(
            {
                "name": "Source",
                "initial_members": [
                    str(docs[0].uuid),
                    str(docs[1].uuid),
                    str(docs[2].uuid),
                ],
            }
        )
        target = await collection_tools.create_collection({"name": "Target"})

        # Move documents
        move_params = {
            "document_ids": [str(docs[0].uuid), str(docs[1].uuid)],
            "source_collection": source["collection_id"],
            "target_collection": target["collection_id"],
        }
        move_result = await collection_tools.move_documents(move_params)

        assert move_result["moved_count"] == 2
        assert move_result["failed_count"] == 0

    @pytest.mark.asyncio
    async def test_remove_from_collection(self, collection_tools, test_dataset):
        """Test removing documents from a collection."""
        dataset, docs = test_dataset

        # Create collection with members
        collection = await collection_tools.create_collection(
            {
                "name": "Collection",
                "initial_members": [str(docs[0].uuid), str(docs[1].uuid)],
            }
        )

        # Remove from collection (no target)
        move_params = {
            "document_ids": [str(docs[0].uuid)],
            "source_collection": collection["collection_id"],
            "target_collection": None,
        }
        move_result = await collection_tools.move_documents(move_params)

        assert move_result["moved_count"] == 1


class TestCollectionStatistics:
    """Test collection statistics functionality."""

    @pytest.mark.asyncio
    async def test_basic_statistics(self, collection_tools, test_dataset):
        """Test getting basic collection statistics."""
        dataset, docs = test_dataset

        # Create collection with members
        collection = await collection_tools.create_collection(
            {
                "name": "Stats Test",
                "initial_members": [str(doc.uuid) for doc in docs[:5]],
            }
        )

        # Get stats
        stats_params = {
            "collection_id": collection["collection_id"],
            "include_member_details": False,
        }
        stats_result = await collection_tools.get_collection_stats(stats_params)

        assert stats_result["name"] == "Stats Test"
        assert stats_result["statistics"]["direct_members"] == 5
        assert stats_result["statistics"]["total_members"] == 5
        assert len(stats_result["statistics"]["unique_tags"]) > 0

    @pytest.mark.asyncio
    async def test_hierarchical_statistics(self, collection_tools, test_dataset):
        """Test statistics for hierarchical collections."""
        dataset, docs = test_dataset

        # Create parent with members
        parent = await collection_tools.create_collection(
            {
                "name": "Parent",
                "initial_members": [str(docs[0].uuid), str(docs[1].uuid)],
            }
        )

        # Create child with members
        child = await collection_tools.create_collection(
            {
                "name": "Child",
                "parent_collection": parent["collection_id"],
                "initial_members": [
                    str(docs[2].uuid),
                    str(docs[3].uuid),
                    str(docs[4].uuid),
                ],
            }
        )

        # Get parent stats with subcollections
        stats_params = {
            "collection_id": parent["collection_id"],
            "include_subcollections": True,
        }
        stats_result = await collection_tools.get_collection_stats(stats_params)

        assert stats_result["statistics"]["direct_members"] == 2
        assert stats_result["statistics"]["subcollection_members"] == 3
        assert stats_result["statistics"]["total_members"] == 5


class TestCollectionTemplates:
    """Test collection template functionality."""

    @pytest.mark.asyncio
    async def test_create_from_project_template(self, collection_tools):
        """Test creating a collection from project template."""
        params = {
            "name": "My Software Project",
            "template": "project",
            "metadata": {"x_language": "python"},
        }

        result = await collection_tools.create_collection(params)

        assert result["name"] == "My Software Project"
        # Template metadata should be applied

    @pytest.mark.asyncio
    async def test_available_templates(self, collection_tools):
        """Test that built-in templates are available."""
        registry = collection_tools.template_registry
        templates = registry.list_templates()

        template_names = [t["name"] for t in templates]
        assert "project" in template_names
        assert "research" in template_names
        assert "knowledge_base" in template_names
        assert "dataset" in template_names
