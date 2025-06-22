"""Dataset statistics and metrics collection using Lance native capabilities."""

import asyncio
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import time
from contextframe.frame import FrameDataset, FrameRecord
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class DatasetStats:
    """Container for comprehensive dataset statistics."""

    # Basic counts from Lance stats
    total_documents: int = 0
    total_collections: int = 0
    total_relationships: int = 0

    # Storage metrics from Lance
    num_fragments: int = 0
    num_deleted_rows: int = 0
    num_small_files: int = 0
    storage_size_bytes: int = 0

    # Version metrics
    current_version: int = 0
    latest_version: int = 0
    version_count: int = 0

    # Content metrics
    document_types: dict[str, int] = field(default_factory=dict)
    collection_sizes: dict[str, int] = field(default_factory=dict)
    metadata_fields: dict[str, int] = field(default_factory=dict)

    # Embedding metrics
    embedding_coverage: float = 0.0
    embedding_dimensions: set[int] = field(default_factory=set)

    # Relationship metrics
    relationship_types: dict[str, int] = field(default_factory=dict)
    avg_relationships_per_doc: float = 0.0
    orphaned_documents: int = 0

    # Index metrics
    indices: list[dict[str, Any]] = field(default_factory=list)
    indexed_fields: set[str] = field(default_factory=set)

    # Time-based metrics
    oldest_document: datetime | None = None
    newest_document: datetime | None = None

    # Performance metrics
    avg_document_size_kb: float = 0.0
    fragment_efficiency: float = 0.0  # ratio of active to total rows
    collection_time_seconds: float = 0.0
    
    # Collection statistics
    avg_collection_size: float = 0.0
    max_collection_size: int = 0
    min_collection_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary format."""
        return {
            "summary": {
                "total_documents": self.total_documents,
                "total_collections": self.total_collections,
                "total_relationships": self.total_relationships,
                "storage_size_mb": round(self.storage_size_bytes / (1024 * 1024), 2),
            },
            "storage": {
                "num_fragments": self.num_fragments,
                "num_deleted_rows": self.num_deleted_rows,
                "num_small_files": self.num_small_files,
                "avg_document_size_kb": round(self.avg_document_size_kb, 2),
                "fragment_efficiency": round(self.fragment_efficiency, 3),
            },
            "versions": {
                "current": self.current_version,
                "latest": self.latest_version,
                "total_versions": self.version_count,
            },
            "content": {
                "document_types": self.document_types,
                "collection_count": len(self.collection_sizes),
                "collection_sizes": self.collection_sizes,
                "metadata_fields": self.metadata_fields,
            },
            "embeddings": {
                "coverage": round(self.embedding_coverage, 3),
                "dimensions": sorted(list(self.embedding_dimensions)),
            },
            "relationships": {
                "types": self.relationship_types,
                "avg_per_document": round(self.avg_relationships_per_doc, 2),
                "orphaned_documents": self.orphaned_documents,
            },
            "indices": {
                "count": len(self.indices),
                "indexed_fields": sorted(list(self.indexed_fields)),
                "details": self.indices,
            },
            "time_range": {
                "oldest": self.oldest_document.isoformat()
                if self.oldest_document
                else None,
                "newest": self.newest_document.isoformat()
                if self.newest_document
                else None,
            },
        }


class StatsCollector:
    """Collects comprehensive statistics from a FrameDataset using Lance native features."""

    def __init__(self, dataset: FrameDataset):
        """Initialize stats collector.

        Args:
            dataset: The FrameDataset to analyze
        """
        self.dataset = dataset
        self._stats = DatasetStats()

    async def collect_stats(
        self,
        include_content: bool = True,
        include_fragments: bool = True,
        include_relationships: bool = True,
        sample_size: int | None = None,
    ) -> DatasetStats:
        """Collect all statistics using Lance native capabilities.

        Args:
            include_content: Include content analysis
            include_fragments: Include fragment-level analysis
            include_relationships: Include relationship analysis
            sample_size: If set, sample for expensive operations

        Returns:
            DatasetStats object with comprehensive metrics
        """
        start_time = time.time()

        # Get Lance native stats first
        await self._collect_lance_stats()

        # Collect basic counts
        await self._collect_basic_counts()

        # Run optional detailed analyses in parallel
        tasks = []

        if include_content:
            tasks.append(self._collect_content_stats(sample_size))

        if include_fragments:
            tasks.append(self._collect_fragment_analysis())

        if include_relationships:
            tasks.append(self._collect_relationship_stats(sample_size))

        if tasks:
            await asyncio.gather(*tasks)

        # Calculate derived metrics
        self._calculate_derived_metrics()

        collection_time = time.time() - start_time
        self._stats.collection_time_seconds = collection_time

        return self._stats

    async def _collect_lance_stats(self) -> None:
        """Collect statistics using Lance native methods."""
        # Get dataset stats from Lance
        lance_stats = self.dataset.get_dataset_stats()

        # Extract Lance dataset stats
        if 'dataset_stats' in lance_stats:
            ds_stats = lance_stats['dataset_stats']
            self._stats.num_fragments = ds_stats.get('num_fragments', 0)
            self._stats.num_deleted_rows = ds_stats.get('num_deleted_rows', 0)
            self._stats.num_small_files = ds_stats.get('num_small_files', 0)

        # Version info
        if 'version_info' in lance_stats:
            v_info = lance_stats['version_info']
            self._stats.current_version = v_info.get('current_version', 0)
            self._stats.latest_version = v_info.get('latest_version', 0)
            self._stats.version_count = self._stats.latest_version + 1

        # Storage info
        if 'storage' in lance_stats:
            self._stats.total_documents = lance_stats['storage'].get('num_rows', 0)

        # Index info
        if 'indices' in lance_stats:
            self._stats.indices = lance_stats['indices']
            for idx in self._stats.indices:
                self._stats.indexed_fields.update(idx.get('fields', []))

    async def _collect_basic_counts(self) -> None:
        """Collect basic document and collection counts."""
        # Count collections using filter
        collection_count = self.dataset.count_by_filter(
            "record_type = 'collection_header'"
        )
        self._stats.total_collections = collection_count

    async def _collect_fragment_analysis(self) -> None:
        """Analyze fragment-level statistics."""
        fragments = self.dataset.get_fragment_stats()

        if fragments:
            # Calculate storage size from fragments
            total_size = 0
            active_rows = 0
            physical_rows = 0

            for frag in fragments:
                active_rows += frag['num_rows']
                physical_rows += frag['physical_rows']
                # Estimate size based on rows (if file info not available)
                if self._stats.total_documents > 0:
                    avg_row_size = 1024  # Default estimate
                    total_size += frag['physical_rows'] * avg_row_size

            self._stats.storage_size_bytes = total_size

            # Calculate efficiency
            if physical_rows > 0:
                self._stats.fragment_efficiency = active_rows / physical_rows

            # Average document size
            if self._stats.total_documents > 0:
                self._stats.avg_document_size_kb = (
                    self._stats.storage_size_bytes / self._stats.total_documents / 1024
                )

    async def _collect_content_stats(self, sample_size: int | None = None) -> None:
        """Collect content-related statistics."""
        # Document type distribution
        doc_types: Dict[str, int] = {}
        collection_members: Dict[str, int] = {}
        metadata_fields: Dict[str, int] = {}
        oldest = None
        newest = None

        # Use scanner with projection for efficiency
        columns = ["id", "record_type", "context", "custom_metadata", "created_at"]

        # Sample if needed
        if sample_size and sample_size < self._stats.total_documents:
            # Use limit for sampling
            scanner = self.dataset.scanner(columns=columns, limit=sample_size)
        else:
            scanner = self.dataset.scanner(columns=columns)

        # Process batches
        for batch in scanner.to_batches():
            # Document types
            if "record_type" in batch.column_names:
                types = batch.column("record_type").to_pylist()
                for doc_type in types:
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

            # Collection membership
            if "context" in batch.column_names:
                contexts = batch.column("context").to_pylist()
                for context in contexts:
                    if (
                        context
                        and isinstance(context, dict)
                        and "collection_id" in context
                    ):
                        coll_id = context["collection_id"]
                        collection_members[coll_id] = (
                            collection_members.get(coll_id, 0) + 1
                        )

            # Metadata fields
            if "custom_metadata" in batch.column_names:
                metadatas = batch.column("custom_metadata").to_pylist()
                for metadata in metadatas:
                    if metadata and isinstance(metadata, dict):
                        for field in metadata.keys():
                            metadata_fields[field] = metadata_fields.get(field, 0) + 1

            # Time metrics
            if "created_at" in batch.column_names:
                timestamps = batch.column("created_at").to_pylist()
                for ts_str in timestamps:
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if oldest is None or ts < oldest:
                                oldest = ts
                            if newest is None or ts > newest:
                                newest = ts
                        except (ValueError, AttributeError):
                            continue

        # Update stats
        self._stats.document_types = doc_types
        self._stats.collection_sizes = collection_members
        self._stats.metadata_fields = metadata_fields
        self._stats.oldest_document = oldest
        self._stats.newest_document = newest

    async def _collect_relationship_stats(self, sample_size: int | None = None) -> None:
        """Collect relationship statistics."""
        relationship_types: Dict[str, int] = {}
        docs_with_relationships = 0
        total_relationships = 0

        # Use projection for efficiency
        columns = ["id", "relationships"]

        if sample_size and sample_size < self._stats.total_documents:
            scanner = self.dataset.scanner(columns=columns, limit=sample_size)
            scaling_factor = self._stats.total_documents / sample_size
        else:
            scanner = self.dataset.scanner(columns=columns)
            scaling_factor = 1.0

        # Process relationships
        for batch in scanner.to_batches():
            if "relationships" in batch.column_names:
                relationships_list = batch.column("relationships").to_pylist()

                for relationships in relationships_list:
                    if relationships and isinstance(relationships, list):
                        docs_with_relationships += 1
                        for rel in relationships:
                            if isinstance(rel, dict):
                                rel_type = rel.get("type", "unknown")
                                relationship_types[rel_type] = (
                                    relationship_types.get(rel_type, 0) + 1
                                )
                                total_relationships += 1

        # Scale if sampled
        if scaling_factor > 1:
            docs_with_relationships = int(docs_with_relationships * scaling_factor)
            total_relationships = int(total_relationships * scaling_factor)
            for rel_type in relationship_types:
                relationship_types[rel_type] = int(
                    relationship_types[rel_type] * scaling_factor
                )

        # Update stats
        self._stats.relationship_types = relationship_types
        self._stats.total_relationships = total_relationships

        if self._stats.total_documents > 0:
            self._stats.avg_relationships_per_doc = (
                total_relationships / self._stats.total_documents
            )
            self._stats.orphaned_documents = (
                self._stats.total_documents - docs_with_relationships
            )

    async def _collect_embedding_stats(self, sample_size: int | None = None) -> None:
        """Collect embedding statistics."""
        total_with_embeddings = 0
        embedding_dims = set()

        # Use projection
        columns = ["embedding"]

        if sample_size and sample_size < self._stats.total_documents:
            scanner = self.dataset.scanner(columns=columns, limit=sample_size)
            scaling_factor = self._stats.total_documents / sample_size
        else:
            scanner = self.dataset.scanner(columns=columns)
            scaling_factor = 1.0

        # Process embeddings
        for batch in scanner.to_batches():
            if "embedding" in batch.column_names:
                embeddings = batch.column("embedding").to_pylist()

                for emb in embeddings:
                    if emb is not None and len(emb) > 0:
                        total_with_embeddings += 1
                        embedding_dims.add(len(emb))

        # Scale and update
        if scaling_factor > 1:
            total_with_embeddings = int(total_with_embeddings * scaling_factor)

        if self._stats.total_documents > 0:
            self._stats.embedding_coverage = (
                total_with_embeddings / self._stats.total_documents
            )

        self._stats.embedding_dimensions = embedding_dims

    def _calculate_derived_metrics(self) -> None:
        """Calculate metrics derived from collected stats."""
        # Collection size statistics
        if self._stats.collection_sizes:
            sizes = list(self._stats.collection_sizes.values())
            self._stats.avg_collection_size = sum(sizes) / len(sizes)
            self._stats.max_collection_size = max(sizes)
            self._stats.min_collection_size = min(sizes)
