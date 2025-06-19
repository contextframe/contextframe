"""Collection management tools for MCP server."""

import datetime
import logging
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.helpers.metadata_utils import (
    add_relationship_to_metadata,
    create_relationship,
)
from contextframe.mcp.core.transport import TransportAdapter
from contextframe.mcp.schemas import (
    CollectionInfo,
    CollectionResult,
    CollectionStats,
    CreateCollectionParams,
    DeleteCollectionParams,
    DocumentResult,
    GetCollectionStatsParams,
    ListCollectionsParams,
    MoveDocumentsParams,
    UpdateCollectionParams,
)
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class CollectionTools:
    """Collection management tools for MCP server.
    
    Provides comprehensive collection management including:
    - Collection CRUD operations
    - Document membership management
    - Hierarchical collections
    - Collection templates
    - Statistics and analytics
    """
    
    def __init__(
        self,
        dataset: FrameDataset,
        transport: TransportAdapter,
        template_registry: Any | None = None
    ):
        """Initialize collection tools.
        
        Args:
            dataset: The dataset to operate on
            transport: Transport adapter for progress
            template_registry: Optional template registry for collection templates
        """
        self.dataset = dataset
        self.transport = transport
        self.template_registry = template_registry
    
    def register_tools(self, tool_registry):
        """Register collection tools with the tool registry."""
        tools = [
            ("create_collection", self.create_collection, CreateCollectionParams),
            ("update_collection", self.update_collection, UpdateCollectionParams),
            ("delete_collection", self.delete_collection, DeleteCollectionParams),
            ("list_collections", self.list_collections, ListCollectionsParams),
            ("move_documents", self.move_documents, MoveDocumentsParams),
            ("get_collection_stats", self.get_collection_stats, GetCollectionStatsParams),
        ]
        
        for name, handler, schema in tools:
            tool_registry.register_tool(
                name=name,
                handler=handler,
                schema=schema,
                description=schema.__doc__ or f"Collection {name.split('_')[1]} operation"
            )
    
    async def create_collection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new collection with header and initial configuration."""
        validated = CreateCollectionParams(**params)
        
        # Create collection header document
        header_metadata = {
            "record_type": "collection_header",
            "title": validated.name
        }
        
        # Store parent in collection_id for Lance-native filtering
        if validated.parent_collection:
            header_metadata["collection_id"] = validated.parent_collection
            header_metadata["collection_id_type"] = "uuid"
        
        if validated.description:
            header_metadata["context"] = validated.description
        
        # Create header record
        header_record = FrameRecord(
            text_content=f"Collection: {validated.name}\n\n{validated.description or 'No description provided.'}",
            metadata=header_metadata
        )
        
        # Set collection metadata using helper
        coll_meta = {
            "created_at": datetime.date.today().isoformat(),
            "template": validated.template,
            "member_count": 0,
            "total_size": 0,
            "shared_metadata": validated.metadata
        }
        self._set_collection_metadata(header_record, coll_meta)
        
        # Apply template if specified
        if validated.template and self.template_registry:
            template = self.template_registry.get_template(validated.template)
            if template:
                # Apply template defaults to collection metadata
                for key, value in template.default_metadata.items():
                    if key not in coll_meta["shared_metadata"]:
                        coll_meta["shared_metadata"][key] = value
                # Update the record
                self._set_collection_metadata(header_record, coll_meta)
        
        # Add relationships if parent collection exists
        parent_header = None
        if validated.parent_collection:
            try:
                parent_header = self._get_collection_header(validated.parent_collection)
                if parent_header:
                    # Add parent relationship to this collection
                    add_relationship_to_metadata(
                        header_metadata,
                        create_relationship(
                            validated.parent_collection,
                            rel_type="parent",
                            title=f"Parent: {parent_header.metadata.get('title', 'Unknown')}"
                        )
                    )
            except Exception as e:
                logger.warning(f"Parent collection not found: {e}")
        
        # Save header to dataset
        self.dataset.add(header_record)
        # Use the UUID from metadata
        collection_id = header_record.metadata.get("uuid")
        
        # Update parent to add child relationship
        if validated.parent_collection and parent_header:
            try:
                add_relationship_to_metadata(
                    parent_header.metadata,
                    create_relationship(
                        collection_id,
                        rel_type="child",
                        title=f"Subcollection: {validated.name}"
                    )
                )
                self.dataset.update_record(parent_header)
            except Exception as e:
                logger.warning(f"Could not update parent: {e}")
        
        # Add initial members if specified
        added_members = 0
        if validated.initial_members:
            for doc_id in validated.initial_members:
                try:
                    self._add_document_to_collection(doc_id, collection_id, header_record.metadata.get("uuid"))
                    added_members += 1
                except Exception as e:
                    logger.warning(f"Failed to add document {doc_id} to collection: {e}")
        
        # Update member count if we added any
        if added_members > 0:
            coll_meta["member_count"] = added_members
            self._set_collection_metadata(header_record, coll_meta)
            self.dataset.update_record(header_record)
        
        return {
            "collection_id": collection_id,
            "header_id": collection_id,
            "name": validated.name,
            "created_at": coll_meta["created_at"],
            "member_count": added_members,
            "metadata": validated.metadata
        }
    
    async def update_collection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update collection properties and membership."""
        validated = UpdateCollectionParams(**params)
        
        # Get collection header
        header = self._get_collection_header(validated.collection_id)
        if not header:
            raise ValueError(f"Collection not found: {validated.collection_id}")
        
        # Update metadata
        updated = False
        
        if validated.name:
            header.metadata["title"] = validated.name
            updated = True
        
        if validated.description is not None:
            header.metadata["context"] = validated.description
            updated = True
        
        if validated.metadata_updates:
            # Get current collection metadata
            coll_meta = self._get_collection_metadata(header)
            # Update shared metadata
            coll_meta["shared_metadata"].update(validated.metadata_updates)
            # Save back
            self._set_collection_metadata(header, coll_meta)
            updated = True
        
        # Remove members
        removed_count = 0
        if validated.remove_members:
            for doc_id in validated.remove_members:
                try:
                    self._remove_document_from_collection(doc_id, validated.collection_id)
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove document {doc_id}: {e}")
        
        # Add members
        added_count = 0
        if validated.add_members:
            for doc_id in validated.add_members:
                try:
                    self._add_document_to_collection(doc_id, validated.collection_id, header.metadata.get("uuid"))
                    added_count += 1
                except Exception as e:
                    logger.warning(f"Failed to add document {doc_id}: {e}")
        
        # Update member count
        coll_meta = self._get_collection_metadata(header)
        current_count = coll_meta["member_count"]
        new_count = current_count - removed_count + added_count
        coll_meta["member_count"] = new_count
        coll_meta["updated_at"] = datetime.date.today().isoformat()
        self._set_collection_metadata(header, coll_meta)
        
        # Save updates
        if updated or removed_count > 0 or added_count > 0:
            self.dataset.update_record(header)
        
        return {
            "collection_id": validated.collection_id,
            "updated": updated,
            "members_added": added_count,
            "members_removed": removed_count,
            "total_members": new_count
        }
    
    async def delete_collection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a collection and optionally its members."""
        validated = DeleteCollectionParams(**params)
        
        # Get collection header
        header = self._get_collection_header(validated.collection_id)
        if not header:
            raise ValueError(f"Collection not found: {validated.collection_id}")
        
        deleted_collections = []
        deleted_members = []
        
        # Handle recursive deletion
        if validated.recursive:
            # Find all subcollections
            subcollections = self._find_subcollections(validated.collection_id)
            for subcoll in subcollections:
                # Recursively delete each subcollection
                sub_result = await self.delete_collection({
                    "collection_id": subcoll["collection_id"],
                    "delete_members": validated.delete_members,
                    "recursive": True
                })
                deleted_collections.extend(sub_result["deleted_collections"])
                deleted_members.extend(sub_result["deleted_members"])
        
        # Get all member documents
        members = self._get_collection_members(validated.collection_id)
        
        # Delete members if requested
        if validated.delete_members:
            for member in members:
                try:
                    self.dataset.delete_record(member["uuid"])
                    deleted_members.append(member["uuid"])
                except Exception as e:
                    logger.warning(f"Failed to delete member {member['uuid']}: {e}")
        else:
            # Just remove collection relationships
            for member in members:
                try:
                    self._remove_document_from_collection(member["uuid"], validated.collection_id)
                except Exception as e:
                    logger.warning(f"Failed to remove collection relationship: {e}")
        
        # Delete the collection header
        self.dataset.delete_record(header.metadata.get("uuid"))
        deleted_collections.append(validated.collection_id)
        
        return {
            "deleted_collections": deleted_collections,
            "deleted_members": deleted_members,
            "total_collections_deleted": len(deleted_collections),
            "total_members_deleted": len(deleted_members)
        }
    
    async def list_collections(self, params: dict[str, Any]) -> dict[str, Any]:
        """List collections with filtering and statistics."""
        validated = ListCollectionsParams(**params)
        
        # Build filter for collection headers
        filters = ["record_type = 'collection_header'"]
        
        if validated.parent_id:
            # Use collection_id field for Lance-native parent filtering
            filters.append(f"collection_id = '{validated.parent_id}'")
        
        filter_str = " AND ".join(filters)
        
        # Query collections
        # Exclude raw_data columns to avoid issues
        columns = [col for col in self.dataset._dataset.schema.names if col not in ["raw_data", "raw_data_type"]]
        scanner = self.dataset.scanner(filter=filter_str, columns=columns)
        collections = []
        
        for batch in scanner.to_batches():
            for i in range(len(batch)):
                row_table = batch.slice(i, 1)
                record = self._safe_load_record(row_table)
                
                # Build collection info using helper
                coll_meta = self._get_collection_metadata(record)
                member_count = coll_meta["member_count"]
                
                # Skip empty collections if requested
                if not validated.include_empty and member_count == 0:
                    continue
                
                coll_info = CollectionInfo(
                    collection_id=str(record.metadata.get("uuid")),
                    header_id=str(record.metadata.get("uuid")),
                    name=record.metadata.get("title", "Unnamed"),
                    description=record.metadata.get("context"),
                    parent_id=record.metadata.get("collection_id") if record.metadata.get("collection_id_type") == "uuid" else None,
                    created_at=coll_meta["created_at"] or record.metadata.get("created_at", ""),
                    updated_at=coll_meta["updated_at"] or record.metadata.get("updated_at", ""),
                    metadata=coll_meta["shared_metadata"],
                    member_count=member_count,
                    total_size_bytes=coll_meta["total_size"] if coll_meta["total_size"] > 0 else None
                )
                
                # Add statistics if requested
                if validated.include_stats:
                    stats = await self._calculate_collection_stats(str(record.metadata.get("uuid")), include_subcollections=False)
                    collections.append({
                        "collection": coll_info.model_dump(),
                        "statistics": stats
                    })
                else:
                    collections.append(coll_info.model_dump())
        
        # Sort collections
        if validated.sort_by == "name":
            collections.sort(key=lambda x: x.get("name", x.get("collection", {}).get("name", "")) if isinstance(x, dict) else x.name)
        elif validated.sort_by == "created_at":
            collections.sort(key=lambda x: x.get("created_at", x.get("collection", {}).get("created_at", "")) if isinstance(x, dict) else x.created_at, reverse=True)
        elif validated.sort_by == "member_count":
            collections.sort(key=lambda x: x.get("member_count", x.get("collection", {}).get("member_count", 0)) if isinstance(x, dict) else x.member_count, reverse=True)
        
        # Apply pagination
        total_count = len(collections)
        collections = collections[validated.offset:validated.offset + validated.limit]
        
        return {
            "collections": collections,
            "total_count": total_count,
            "offset": validated.offset,
            "limit": validated.limit
        }
    
    async def move_documents(self, params: dict[str, Any]) -> dict[str, Any]:
        """Move documents between collections."""
        validated = MoveDocumentsParams(**params)
        
        moved_count = 0
        failed_moves = []
        
        # Validate target collection exists if specified
        target_header = None
        if validated.target_collection:
            target_header = self._get_collection_header(validated.target_collection)
            if not target_header:
                raise ValueError(f"Target collection not found: {validated.target_collection}")
        
        for doc_id in validated.document_ids:
            try:
                # Remove from source collection if specified
                if validated.source_collection:
                    self._remove_document_from_collection(doc_id, validated.source_collection)
                
                # Add to target collection if specified
                if validated.target_collection:
                    self._add_document_to_collection(
                        doc_id, 
                        validated.target_collection,
                        target_header.metadata.get("uuid")
                    )
                    
                    # Apply shared metadata if requested
                    if validated.update_metadata and target_header:
                        doc = self.dataset.get_by_uuid(doc_id)
                        if doc:
                            # Apply shared metadata from collection
                            coll_meta = self._get_collection_metadata(target_header)
                            doc.metadata.update(coll_meta["shared_metadata"])
                            self.dataset.update_record(doc)
                
                moved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to move document {doc_id}: {e}")
                failed_moves.append({
                    "document_id": doc_id,
                    "error": str(e)
                })
        
        return {
            "moved_count": moved_count,
            "failed_count": len(failed_moves),
            "failed_moves": failed_moves,
            "source_collection": validated.source_collection,
            "target_collection": validated.target_collection
        }
    
    async def get_collection_stats(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get detailed statistics for a collection."""
        validated = GetCollectionStatsParams(**params)
        
        # Get collection header
        header = self._get_collection_header(validated.collection_id)
        if not header:
            raise ValueError(f"Collection not found: {validated.collection_id}")
        
        # Calculate statistics
        stats = await self._calculate_collection_stats(
            validated.collection_id,
            include_subcollections=validated.include_subcollections
        )
        
        # Build response
        result = {
            "collection_id": validated.collection_id,
            "name": header.metadata.get("title", "Unnamed"),
            "statistics": stats
        }
        
        # Add subcollection info if requested
        if validated.include_subcollections:
            subcollections = self._find_subcollections(validated.collection_id)
            result["subcollections"] = subcollections
        
        # Add member details if requested
        if validated.include_member_details:
            members = self._get_collection_members(validated.collection_id, include_content=False)
            result["members"] = members[:100]  # Limit to first 100
        
        return result
    
    # Helper methods
    
    def _safe_load_record(self, row_table) -> FrameRecord:
        """Safely load a FrameRecord from Arrow."""
        # Since we're excluding raw_data columns from scans, we can just load directly
        return FrameRecord.from_arrow(row_table)
    
    def _get_collection_metadata(self, record: FrameRecord) -> dict[str, Any]:
        """Extract collection metadata from custom_metadata."""
        custom = record.metadata.get("custom_metadata", {})
        return {
            "created_at": custom.get("collection_created_at", ""),
            "updated_at": custom.get("collection_updated_at", ""),
            "member_count": int(custom.get("collection_member_count", "0")),
            "total_size": int(custom.get("collection_total_size", "0")),
            "template": custom.get("collection_template", ""),
            "shared_metadata": {
                k[7:]: v for k, v in custom.items() 
                if k.startswith("shared_")
            }
        }
    
    def _set_collection_metadata(self, record: FrameRecord, coll_meta: dict[str, Any]) -> None:
        """Store collection metadata in custom_metadata."""
        if "custom_metadata" not in record.metadata:
            record.metadata["custom_metadata"] = {}
        
        custom = record.metadata["custom_metadata"]
        custom["collection_created_at"] = coll_meta.get("created_at", "")
        custom["collection_updated_at"] = coll_meta.get("updated_at", datetime.date.today().isoformat())
        custom["collection_member_count"] = str(coll_meta.get("member_count", 0))
        custom["collection_total_size"] = str(coll_meta.get("total_size", 0))
        custom["collection_template"] = str(coll_meta.get("template") or "")
        
        # Store shared metadata
        for key, value in coll_meta.get("shared_metadata", {}).items():
            custom[f"shared_{key}"] = str(value)
    
    def _get_collection_header(self, collection_id: str) -> FrameRecord | None:
        """Get collection header by ID."""
        try:
            # Try direct ID lookup first
            record = self.dataset.get_by_uuid(collection_id)
            if record and record.metadata.get("record_type") == "collection_header":
                return record
            
            # Search by collection_id using uuid field
            filter_str = f"record_type = 'collection_header' AND uuid = '{collection_id}'"
            columns = [col for col in self.dataset._dataset.schema.names if col not in ["raw_data", "raw_data_type"]]
            scanner = self.dataset.scanner(filter=filter_str, columns=columns)
            
            for batch in scanner.to_batches():
                if len(batch) > 0:
                    return self._safe_load_record(batch.slice(0, 1))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting collection header: {e}")
            return None
    
    def _add_document_to_collection(
        self, 
        doc_id: str, 
        collection_id: str,
        header_uuid: str
    ) -> None:
        """Add document to collection by updating relationships."""
        doc = self.dataset.get_by_uuid(doc_id)
        if not doc:
            raise ValueError(f"Document not found: {doc_id}")
        
        # Add reference relationship from document to collection header
        add_relationship_to_metadata(
            doc.metadata,
            create_relationship(
                header_uuid,
                rel_type="reference",
                title=f"Member of collection {collection_id}"
            )
        )
        
        # Update document
        self.dataset.update_record(doc)
    
    def _remove_document_from_collection(self, doc_id: str, collection_id: str) -> None:
        """Remove document from collection by removing relationships."""
        doc = self.dataset.get_by_uuid(doc_id)
        if not doc:
            raise ValueError(f"Document not found: {doc_id}")
        
        # Remove reference relationship
        relationships = doc.metadata.get("relationships", [])
        doc.metadata["relationships"] = [
            rel for rel in relationships 
            if not (rel.get("type") == "reference" and collection_id in str(rel.get("id", "")))
        ]
        
        # Update document
        self.dataset.update_record(doc)
    
    def _get_collection_members(
        self, 
        collection_id: str,
        include_content: bool = True
    ) -> list[dict[str, Any]]:
        """Get all members of a collection."""
        members = []
        
        # Find documents with member_of relationship to this collection
        # Exclude raw_data to avoid loading large binary data
        columns = [col for col in self.dataset._dataset.schema.names if col not in ["raw_data", "raw_data_type"]]
        scanner = self.dataset.scanner(columns=columns)
        
        for batch in scanner.to_batches():
            for i in range(len(batch)):
                row_table = batch.slice(i, 1)
                record = self._safe_load_record(row_table)
                
                # Check relationships
                relationships = record.metadata.get("relationships", [])
                for rel in relationships:
                    if (rel.get("type") == "reference" and 
                        collection_id in str(rel.get("id", ""))):
                        
                        member_info = {
                            "uuid": str(record.metadata.get("uuid")),
                            "title": record.metadata.get("title", ""),
                            "metadata": record.metadata
                        }
                        
                        if include_content:
                            member_info["content"] = record.text_content
                        
                        members.append(member_info)
                        break
        
        return members
    
    def _find_subcollections(self, parent_id: str) -> list[dict[str, Any]]:
        """Find all subcollections of a parent collection."""
        # Use Lance-native filtering on collection_id field
        filter_str = f"record_type = 'collection_header' AND collection_id = '{parent_id}'"
        columns = [col for col in self.dataset._dataset.schema.names if col not in ["raw_data", "raw_data_type"]]
        scanner = self.dataset.scanner(filter=filter_str, columns=columns)
        
        subcollections = []
        for batch in scanner.to_batches():
            for i in range(len(batch)):
                row_table = batch.slice(i, 1)
                record = self._safe_load_record(row_table)
                
                subcollections.append({
                    "collection_id": str(record.metadata.get("uuid")),
                    "name": record.metadata.get("title", "Unnamed"),
                    "member_count": self._get_collection_metadata(record)["member_count"]
                })
        
        return subcollections
    
    async def _calculate_collection_stats(
        self, 
        collection_id: str,
        include_subcollections: bool = True
    ) -> dict[str, Any]:
        """Calculate detailed statistics for a collection."""
        members = self._get_collection_members(collection_id)
        
        # Basic counts
        direct_members = len(members)
        subcollection_members = 0
        
        # Calculate subcollection members if requested
        if include_subcollections:
            subcollections = self._find_subcollections(collection_id)
            for subcoll in subcollections:
                sub_stats = await self._calculate_collection_stats(
                    subcoll["collection_id"], 
                    include_subcollections=True
                )
                subcollection_members += sub_stats["total_members"]
        
        # Calculate sizes and metadata
        total_size = 0
        unique_tags = set()
        dates = []
        member_types = {}
        
        for member in members:
            # Size (approximate)
            content_size = len(member.get("content", "").encode('utf-8'))
            total_size += content_size
            
            # Tags
            tags = member["metadata"].get("tags", [])
            unique_tags.update(tags)
            
            # Dates
            created_at = member["metadata"].get("created_at")
            if created_at:
                dates.append(created_at)
            
            # Types
            record_type = member["metadata"].get("record_type", "document")
            member_types[record_type] = member_types.get(record_type, 0) + 1
        
        # Calculate averages and ranges
        avg_size = total_size / direct_members if direct_members > 0 else 0
        
        date_range = {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None
        }
        
        return {
            "total_members": direct_members + subcollection_members,
            "direct_members": direct_members,
            "subcollection_members": subcollection_members,
            "total_size_bytes": total_size,
            "avg_document_size": avg_size,
            "unique_tags": sorted(list(unique_tags)),
            "date_range": date_range,
            "member_types": member_types
        }