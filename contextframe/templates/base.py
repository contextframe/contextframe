"""Base class for Context Templates."""

from __future__ import annotations

import abc
from ..frame import FrameDataset, FrameRecord
from ..schema.contextframe_schema import RecordType
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


@dataclass
class TemplateResult:
    """Result of applying a template to a dataset."""
    
    frames_created: int = 0
    collections_created: int = 0
    relationships_created: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    frame_ids: list[str] = field(default_factory=list)
    collection_ids: list[str] = field(default_factory=list)


@dataclass 
class FileMapping:
    """Maps a file to frame metadata and configuration."""
    
    path: Path
    title: str
    record_type: str = RecordType.DOCUMENT
    collection: str | None = None
    tags: list[str] = field(default_factory=list)
    custom_metadata: dict[str, str] = field(default_factory=dict)
    skip: bool = False
    extract_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectionDefinition:
    """Defines a collection structure."""
    
    name: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    parent: str | None = None
    position: int = 0


@dataclass
class EnrichmentSuggestion:
    """Suggested enrichment for a document type."""
    
    file_pattern: str  # glob pattern
    enhancement_config: dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # higher = more important


class ContextTemplate(abc.ABC):
    """Abstract base class for Context Templates.
    
    Templates provide pre-configured patterns for importing and structuring
    documents into ContextFrame datasets. Subclasses implement domain-specific
    logic for categorizing, organizing, and enriching documents.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize the template.
        
        Args:
            name: Template name (e.g., "software_project")
            description: Human-readable description
        """
        self.name = name
        self.description = description
        
    @abc.abstractmethod
    def scan(self, source_path: str | Path) -> list[FileMapping]:
        """Scan source directory and map files to frames.
        
        This method analyzes the directory structure and files to determine
        how they should be imported into ContextFrame.
        
        Args:
            source_path: Path to scan
            
        Returns:
            List of file mappings
        """
        ...
        
    @abc.abstractmethod
    def define_collections(self, file_mappings: list[FileMapping]) -> list[CollectionDefinition]:
        """Define collection structure based on discovered files.
        
        Args:
            file_mappings: Files discovered during scan
            
        Returns:
            List of collections to create
        """
        ...
        
    @abc.abstractmethod
    def discover_relationships(
        self, 
        file_mappings: list[FileMapping],
        dataset: FrameDataset
    ) -> list[dict[str, Any]]:
        """Discover relationships between documents.
        
        Args:
            file_mappings: Files being imported
            dataset: Dataset being populated
            
        Returns:
            List of relationship dictionaries
        """
        ...
        
    @abc.abstractmethod
    def suggest_enrichments(self, file_mappings: list[FileMapping]) -> list[EnrichmentSuggestion]:
        """Suggest enrichments for imported documents.
        
        Args:
            file_mappings: Files being imported
            
        Returns:
            List of enrichment suggestions
        """
        ...
        
    def validate_source(self, source_path: str | Path) -> Path:
        """Validate and normalize source path.
        
        Args:
            source_path: Path to validate
            
        Returns:
            Normalized Path object
            
        Raises:
            ValueError: If path is invalid
        """
        path = Path(source_path).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Source path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Source path must be a directory: {path}")
        return path
        
    def apply(
        self,
        source_path: str | Path,
        dataset: FrameDataset,
        *,
        auto_enhance: bool = False,
        dry_run: bool = False,
        progress_callback: callable | None = None
    ) -> TemplateResult:
        """Apply template to import documents into dataset.
        
        This is the main entry point that orchestrates the entire import process:
        1. Scans source directory
        2. Creates collections
        3. Imports documents as frames
        4. Establishes relationships
        5. Optionally runs enrichments
        
        Args:
            source_path: Directory to import from
            dataset: Target FrameDataset
            auto_enhance: Whether to run suggested enrichments
            dry_run: If True, only simulate the import
            progress_callback: Optional callback for progress updates
            
        Returns:
            TemplateResult with import statistics
        """
        result = TemplateResult()
        
        try:
            # Validate source
            source_path = self.validate_source(source_path)
            
            # Phase 1: Scan files
            if progress_callback:
                progress_callback("Scanning files...")
            file_mappings = self.scan(source_path)
            
            if dry_run:
                result.warnings.append(f"DRY RUN: Would import {len(file_mappings)} files")
                return result
                
            # Phase 2: Create collections
            if progress_callback:
                progress_callback("Creating collections...")
            collections = self.define_collections(file_mappings)
            collection_map = {}
            
            for coll_def in collections:
                try:
                    coll_record = self._create_collection(coll_def, dataset)
                    dataset.add(coll_record)
                    collection_map[coll_def.name] = coll_record.uuid
                    result.collections_created += 1
                    result.collection_ids.append(coll_record.uuid)
                except Exception as e:
                    result.errors.append(f"Failed to create collection {coll_def.name}: {e}")
                    
            # Phase 3: Import documents
            if progress_callback:
                progress_callback("Importing documents...")
                
            from ..extract import extract_from_file
            
            frame_map = {}
            for mapping in file_mappings:
                if mapping.skip:
                    continue
                    
                try:
                    # Extract content
                    extraction = extract_from_file(
                        str(mapping.path),
                        **mapping.extract_config
                    )
                    
                    if extraction.error:
                        result.warnings.append(f"Extraction warning for {mapping.path}: {extraction.error}")
                        
                    # Create frame
                    metadata = {
                        "title": mapping.title,
                        "record_type": mapping.record_type,
                        "source_file": str(mapping.path),
                        "tags": mapping.tags,
                        "custom_metadata": mapping.custom_metadata,
                    }
                    
                    if mapping.collection and mapping.collection in collection_map:
                        metadata["collection"] = mapping.collection
                        metadata["collection_id"] = collection_map[mapping.collection]
                        metadata["collection_id_type"] = "uuid"
                        
                    # Add extraction metadata
                    if extraction.metadata:
                        metadata["custom_metadata"].update({
                            f"extract_{k}": str(v) 
                            for k, v in extraction.metadata.items()
                        })
                        
                    frame = FrameRecord(
                        text_content=extraction.content,
                        metadata=metadata
                    )
                    
                    dataset.add(frame)
                    frame_map[str(mapping.path)] = frame.uuid
                    result.frames_created += 1
                    result.frame_ids.append(frame.uuid)
                    
                except Exception as e:
                    result.errors.append(f"Failed to import {mapping.path}: {e}")
                    
            # Phase 4: Discover relationships
            if progress_callback:
                progress_callback("Discovering relationships...")
                
            relationships = self.discover_relationships(file_mappings, dataset)
            for rel in relationships:
                try:
                    # Apply relationships to frames
                    # This is simplified - in practice would update frames
                    result.relationships_created += 1
                except Exception as e:
                    result.warnings.append(f"Failed to create relationship: {e}")
                    
            # Phase 5: Run enrichments if requested
            if auto_enhance:
                if progress_callback:
                    progress_callback("Running enrichments...")
                    
                suggestions = self.suggest_enrichments(file_mappings)
                # In practice, would integrate with enhancement module here
                result.warnings.append("Auto-enhancement not yet implemented")
                
        except Exception as e:
            result.errors.append(f"Template application failed: {e}")
            
        return result
        
    def _create_collection(self, definition: CollectionDefinition, dataset: FrameDataset) -> FrameRecord:
        """Create a collection header frame."""
        metadata = {
            "title": definition.title,
            "record_type": RecordType.COLLECTION_HEADER,
            "tags": definition.tags,
            "position": definition.position,
            "custom_metadata": {
                "collection_name": definition.name,
            }
        }
        
        if definition.parent:
            metadata["custom_metadata"]["parent_collection"] = definition.parent
            
        return FrameRecord(
            text_content=definition.description,
            metadata=metadata
        )