"""Resource system for MCP server."""

import json
from typing import Any, Dict, List

from contextframe.frame import FrameDataset
from contextframe.mcp.errors import InvalidParams
from contextframe.mcp.schemas import Resource


class ResourceRegistry:
    """Manages MCP resources for dataset exploration."""

    def __init__(self, dataset: FrameDataset):
        self.dataset = dataset
        self._base_uri = "contextframe://"

    def list_resources(self) -> List[Resource]:
        """List all available resources."""
        resources = [
            Resource(
                uri=f"{self._base_uri}dataset/info",
                name="Dataset Information",
                description="Dataset metadata, statistics, and configuration",
                mimeType="application/json"
            ),
            Resource(
                uri=f"{self._base_uri}dataset/schema",
                name="Dataset Schema",
                description="Arrow schema information for the dataset",
                mimeType="application/json"
            ),
            Resource(
                uri=f"{self._base_uri}dataset/stats",
                name="Dataset Statistics",
                description="Statistical information about the dataset",
                mimeType="application/json"
            ),
            Resource(
                uri=f"{self._base_uri}collections",
                name="Document Collections",
                description="List of document collections in the dataset",
                mimeType="application/json"
            ),
            Resource(
                uri=f"{self._base_uri}relationships",
                name="Document Relationships",
                description="Overview of document relationships in the dataset",
                mimeType="application/json"
            )
        ]
        
        return resources

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read resource content by URI."""
        if not uri.startswith(self._base_uri):
            raise InvalidParams(f"Invalid resource URI: {uri}")
        
        resource_path = uri[len(self._base_uri):]
        
        if resource_path == "dataset/info":
            return await self._get_dataset_info()
        elif resource_path == "dataset/schema":
            return await self._get_dataset_schema()
        elif resource_path == "dataset/stats":
            return await self._get_dataset_stats()
        elif resource_path == "collections":
            return await self._get_collections()
        elif resource_path == "relationships":
            return await self._get_relationships()
        else:
            raise InvalidParams(f"Unknown resource: {uri}")

    async def _get_dataset_info(self) -> Dict[str, Any]:
        """Get general dataset information."""
        # Get dataset metadata
        try:
            # Get basic info from the dataset
            total_docs = self.dataset._dataset.count_rows()  # Get total document count
            
            info = {
                "uri": f"{self._base_uri}dataset/info",
                "name": "Dataset Information",
                "mimeType": "application/json",
                "text": json.dumps({
                    "dataset_path": str(self.dataset._dataset.uri),  # Lance dataset URI
                    "total_documents": total_docs,
                    "version": getattr(self.dataset._dataset, "version", "unknown"),
                    "storage_format": "lance",
                    "features": {
                        "vector_search": True,
                        "full_text_search": True,
                        "sql_filtering": True,
                        "relationships": True,
                        "collections": True
                    }
                }, indent=2)
            }
            
            return info
            
        except Exception as e:
            return {
                "uri": f"{self._base_uri}dataset/info",
                "name": "Dataset Information",
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}, indent=2)
            }

    async def _get_dataset_schema(self) -> Dict[str, Any]:
        """Get dataset schema information."""
        try:
            # Get Arrow schema from the dataset
            schema = self.dataset._dataset.schema
            
            # Convert schema to dict representation
            schema_dict = {
                "fields": []
            }
            
            for field in schema:
                field_info = {
                    "name": field.name,
                    "type": str(field.type),
                    "nullable": field.nullable
                }
                schema_dict["fields"].append(field_info)
            
            return {
                "uri": f"{self._base_uri}dataset/schema",
                "name": "Dataset Schema",
                "mimeType": "application/json",
                "text": json.dumps(schema_dict, indent=2)
            }
            
        except Exception as e:
            return {
                "uri": f"{self._base_uri}dataset/schema",
                "name": "Dataset Schema",
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}, indent=2)
            }

    async def _get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        try:
            # Gather statistics
            stats = {
                "document_count": 0,
                "collections": {},
                "record_types": {},
                "has_embeddings": 0,
                "avg_content_length": 0
            }
            
            # Sample documents for statistics
            sample = self.dataset.query("1=1", limit=1000)
            stats["document_count"] = len(sample)
            
            total_length = 0
            for record in sample:
                # Count by collection
                collection = record.metadata.get("collection", "uncategorized")
                stats["collections"][collection] = stats["collections"].get(collection, 0) + 1
                
                # Count by record type
                record_type = record.metadata.get("record_type", "document")
                stats["record_types"][record_type] = stats["record_types"].get(record_type, 0) + 1
                
                # Check embeddings
                if record.embeddings is not None:
                    stats["has_embeddings"] += 1
                
                # Content length
                if record.content:
                    total_length += len(record.content)
            
            if stats["document_count"] > 0:
                stats["avg_content_length"] = total_length / stats["document_count"]
                stats["embedding_coverage"] = f"{(stats['has_embeddings'] / stats['document_count']) * 100:.1f}%"
            
            return {
                "uri": f"{self._base_uri}dataset/stats",
                "name": "Dataset Statistics",
                "mimeType": "application/json",
                "text": json.dumps(stats, indent=2)
            }
            
        except Exception as e:
            return {
                "uri": f"{self._base_uri}dataset/stats",
                "name": "Dataset Statistics",
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}, indent=2)
            }

    async def _get_collections(self) -> Dict[str, Any]:
        """Get information about document collections."""
        try:
            # Find all unique collections
            collections = {}
            
            # Sample documents to find collections
            sample = self.dataset.query("1=1", limit=10000)
            
            for record in sample:
                collection = record.metadata.get("collection")
                if collection:
                    if collection not in collections:
                        collections[collection] = {
                            "name": collection,
                            "document_count": 0,
                            "has_header": False
                        }
                    collections[collection]["document_count"] += 1
                    
                    # Check if it's a collection header
                    if record.metadata.get("record_type") == "collection_header":
                        collections[collection]["has_header"] = True
                        collections[collection]["description"] = record.content[:200] + "..." if len(record.content) > 200 else record.content
            
            return {
                "uri": f"{self._base_uri}collections",
                "name": "Document Collections",
                "mimeType": "application/json",
                "text": json.dumps({
                    "total_collections": len(collections),
                    "collections": list(collections.values())
                }, indent=2)
            }
            
        except Exception as e:
            return {
                "uri": f"{self._base_uri}collections",
                "name": "Document Collections",
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}, indent=2)
            }

    async def _get_relationships(self) -> Dict[str, Any]:
        """Get information about document relationships."""
        try:
            # Find relationships in metadata
            relationships = {
                "parent_child": 0,
                "related": 0,
                "references": 0,
                "member_of": 0,
                "total": 0
            }
            
            # Sample documents to find relationships
            sample = self.dataset.query("1=1", limit=10000)
            
            for record in sample:
                if "relationships" in record.metadata:
                    for rel in record.metadata["relationships"]:
                        rel_type = rel.get("relationship_type", "related")
                        if rel_type in relationships:
                            relationships[rel_type] += 1
                        relationships["total"] += 1
            
            return {
                "uri": f"{self._base_uri}relationships",
                "name": "Document Relationships",
                "mimeType": "application/json",
                "text": json.dumps({
                    "relationship_counts": relationships,
                    "has_relationships": relationships["total"] > 0
                }, indent=2)
            }
            
        except Exception as e:
            return {
                "uri": f"{self._base_uri}relationships",
                "name": "Document Relationships",
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}, indent=2)
            }