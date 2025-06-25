"""Obsidian connector for importing vault content into ContextFrame."""

import json
import re
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ObsidianConnector(SourceConnector):
    """Connector for importing Obsidian vault content."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Obsidian connector.

        Args:
            config: Connector configuration with Obsidian-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.vault_path = Path(config.sync_config.get("vault_path", ""))
        self.include_attachments = config.sync_config.get("include_attachments", True)
        self.include_daily_notes = config.sync_config.get("include_daily_notes", True)
        self.include_templates = config.sync_config.get("include_templates", False)
        self.folders_to_include = config.sync_config.get("folders_to_include", [])
        self.folders_to_exclude = config.sync_config.get("folders_to_exclude", [".obsidian", ".trash"])
        self.extract_frontmatter = config.sync_config.get("extract_frontmatter", True)
        self.extract_tags = config.sync_config.get("extract_tags", True)
        self.extract_backlinks = config.sync_config.get("extract_backlinks", True)
        
        # Validate vault path
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault path does not exist: {self.vault_path}")
        if not self.vault_path.is_dir():
            raise ValueError(f"Obsidian vault path is not a directory: {self.vault_path}")

        # Look for .obsidian folder to confirm it's a vault
        obsidian_config = self.vault_path / ".obsidian"
        if not obsidian_config.exists():
            self.logger.warning(f"No .obsidian folder found in {self.vault_path}. Are you sure this is an Obsidian vault?")

    def validate_connection(self) -> bool:
        """Validate Obsidian vault access."""
        try:
            # Check if we can read the vault
            if not self.vault_path.exists():
                return False
            
            # Try to list files
            list(self.vault_path.glob("*.md"))
            self.logger.info(f"Connected to Obsidian vault: {self.vault_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate Obsidian vault access: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover Obsidian vault structure."""
        discovery = {
            "vault_path": str(self.vault_path),
            "vault_name": self.vault_path.name,
            "folders": [],
            "file_stats": {
                "total_notes": 0,
                "total_attachments": 0,
                "total_size": 0,
                "file_types": {},
            },
            "metadata": {
                "tags_found": set(),
                "backlinks_count": 0,
                "has_frontmatter": 0,
            }
        }

        try:
            # Walk through vault
            for file_path in self.vault_path.rglob("*"):
                if file_path.is_file():
                    # Skip excluded folders
                    if any(excluded in file_path.parts for excluded in self.folders_to_exclude):
                        continue
                    
                    file_size = file_path.stat().st_size
                    discovery["file_stats"]["total_size"] += file_size
                    
                    # Track file types
                    ext = file_path.suffix.lower()
                    discovery["file_stats"]["file_types"][ext] = \
                        discovery["file_stats"]["file_types"].get(ext, 0) + 1
                    
                    if ext == ".md":
                        discovery["file_stats"]["total_notes"] += 1
                        
                        # Analyze note content
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            
                            # Check for frontmatter
                            if content.startswith("---"):
                                discovery["metadata"]["has_frontmatter"] += 1
                            
                            # Extract tags
                            tags = re.findall(r'#[\w\-\/]+', content)
                            discovery["metadata"]["tags_found"].update(tags)
                            
                            # Count backlinks
                            backlinks = re.findall(r'\[\[([^\]]+)\]\]', content)
                            discovery["metadata"]["backlinks_count"] += len(backlinks)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to analyze {file_path}: {e}")
                    
                    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.mp4', '.webm']:
                        discovery["file_stats"]["total_attachments"] += 1
                
                elif file_path.is_dir():
                    # Skip excluded folders
                    if file_path.name not in self.folders_to_exclude:
                        rel_path = file_path.relative_to(self.vault_path)
                        discovery["folders"].append(str(rel_path))

            # Convert set to list for JSON serialization
            discovery["metadata"]["tags_found"] = list(discovery["metadata"]["tags_found"])

        except Exception as e:
            self.logger.error(f"Failed to discover Obsidian content: {e}")
            discovery["error"] = str(e)

        return discovery

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Obsidian vault to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create main collection
        collection_id = self.create_collection(
            f"Obsidian: {self.vault_path.name}",
            f"Notes and attachments from Obsidian vault: {self.vault_path}"
        )

        # Track processed files and relationships
        processed_files: set[str] = set()
        note_relationships: dict[str, list[str]] = {}  # note_path -> [linked_notes]

        # Process markdown files
        self._sync_notes(
            collection_id,
            result,
            last_sync_state,
            processed_files,
            note_relationships
        )

        # Process attachments if enabled
        if self.include_attachments:
            self._sync_attachments(
                collection_id,
                result,
                last_sync_state,
                processed_files
            )

        # Create backlink relationships after all notes are processed
        self._create_backlink_relationships(note_relationships, result)

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "vault_path": str(self.vault_path),
                "processed_files": list(processed_files),
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _sync_notes(
        self,
        collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_files: set[str],
        note_relationships: dict[str, list[str]]
    ):
        """Sync Obsidian notes (.md files)."""
        try:
            # Find all markdown files
            for note_path in self.vault_path.rglob("*.md"):
                # Skip excluded folders
                if any(excluded in note_path.parts for excluded in self.folders_to_exclude):
                    continue

                # Skip templates unless included
                if not self.include_templates and "template" in note_path.name.lower():
                    continue

                # Check folder filters
                rel_path = note_path.relative_to(self.vault_path)
                if self.folders_to_include:
                    if not any(str(rel_path).startswith(folder) for folder in self.folders_to_include):
                        continue

                # Check if needs update
                if incremental and last_sync_state:
                    last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                    modified = datetime.fromtimestamp(note_path.stat().st_mtime)
                    if modified <= last_sync:
                        continue

                # Process note
                frame = self._map_note_to_frame(note_path, collection_id, note_relationships)
                if frame:
                    try:
                        # Use relative path as unique identifier
                        file_id = str(rel_path)
                        
                        existing = self.dataset.search(
                            f"source_file:'{file_id}'",
                            limit=1
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                        processed_files.add(file_id)

                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(f"Failed to sync note {rel_path}: {e}")

        except Exception as e:
            result.add_error(f"Failed to sync notes: {e}")
            result.success = False

    def _sync_attachments(
        self,
        collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_files: set[str]
    ):
        """Sync Obsidian attachments (images, PDFs, etc.)."""
        try:
            attachment_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.mp4', '.webm', '.mov', '.mp3', '.wav'}
            
            for file_path in self.vault_path.rglob("*"):
                if not file_path.is_file():
                    continue
                    
                if file_path.suffix.lower() not in attachment_extensions:
                    continue

                # Skip excluded folders
                if any(excluded in file_path.parts for excluded in self.folders_to_exclude):
                    continue

                # Check if needs update
                if incremental and last_sync_state:
                    last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if modified <= last_sync:
                        continue

                # Process attachment
                frame = self._map_attachment_to_frame(file_path, collection_id)
                if frame:
                    try:
                        rel_path = file_path.relative_to(self.vault_path)
                        file_id = str(rel_path)
                        
                        existing = self.dataset.search(
                            f"source_file:'{file_id}'",
                            limit=1
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                        processed_files.add(file_id)

                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(f"Failed to sync attachment {rel_path}: {e}")

        except Exception as e:
            result.add_warning(f"Failed to sync attachments: {e}")

    def _create_backlink_relationships(
        self,
        note_relationships: dict[str, list[str]],
        result: SyncResult
    ):
        """Create backlink relationships between notes."""
        if not self.extract_backlinks:
            return

        try:
            for source_path, linked_notes in note_relationships.items():
                # Find the source frame
                source_results = self.dataset.search(
                    f"source_file:'{source_path}'",
                    limit=1
                )
                
                if not source_results:
                    continue
                    
                source_frame = source_results[0]
                
                for linked_note in linked_notes:
                    # Find the target frame
                    target_results = self.dataset.search(
                        f"source_file:'{linked_note}'",
                        limit=1
                    )
                    
                    if target_results:
                        target_frame = target_results[0]
                        # Add relationship
                        source_frame.add_relationship(
                            "links_to",
                            id=target_frame.metadata["uuid"]
                        )
                        
                        # Update the source frame
                        self.dataset.update(source_frame.metadata["uuid"], source_frame)

        except Exception as e:
            result.add_warning(f"Failed to create backlink relationships: {e}")

    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Map Obsidian data to FrameRecord."""
        file_path = Path(source_data.get("file_path", ""))
        if file_path.suffix == ".md":
            return self._map_note_to_frame(file_path, "", {})
        else:
            return self._map_attachment_to_frame(file_path, "")

    def _map_note_to_frame(
        self,
        note_path: Path,
        collection_id: str,
        note_relationships: dict[str, list[str]]
    ) -> FrameRecord | None:
        """Map Obsidian note to FrameRecord."""
        try:
            # Read note content
            content = note_path.read_text(encoding='utf-8', errors='replace')
            
            # Extract frontmatter
            frontmatter = {}
            main_content = content
            
            if self.extract_frontmatter and content.startswith("---"):
                try:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter_text = parts[1].strip()
                        main_content = parts[2].strip()
                        
                        # Parse YAML frontmatter
                        try:
                            import yaml
                            frontmatter = yaml.safe_load(frontmatter_text) or {}
                        except ImportError:
                            # Parse simple key-value pairs if PyYAML not available
                            for line in frontmatter_text.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    frontmatter[key.strip()] = value.strip()
                        except Exception as e:
                            self.logger.warning(f"Failed to parse frontmatter in {note_path}: {e}")
                            
                except Exception as e:
                    self.logger.warning(f"Failed to extract frontmatter from {note_path}: {e}")

            # Extract title (from frontmatter or filename)
            title = frontmatter.get("title", note_path.stem)
            
            # Get file stats
            stat = note_path.stat()
            rel_path = note_path.relative_to(self.vault_path)
            
            # Build metadata
            metadata = {
                "title": title,
                "record_type": RecordType.DOCUMENT,
                "source_type": "obsidian_note",
                "source_file": str(rel_path),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "collection": collection_id,
                "collection_id": collection_id,
                "custom_metadata": {
                    "x_obsidian_vault": self.vault_path.name,
                    "x_obsidian_folder": str(rel_path.parent) if rel_path.parent != Path(".") else "",
                    "x_obsidian_basename": note_path.stem,
                }
            }

            # Add frontmatter to metadata
            if frontmatter:
                metadata["custom_metadata"]["x_obsidian_frontmatter"] = frontmatter
                
                # Extract common frontmatter fields
                if "tags" in frontmatter:
                    metadata["tags"] = frontmatter["tags"] if isinstance(frontmatter["tags"], list) else [frontmatter["tags"]]
                if "author" in frontmatter:
                    metadata["author"] = frontmatter["author"]
                if "created" in frontmatter:
                    metadata["created_at"] = frontmatter["created"]
                if "modified" in frontmatter:
                    metadata["updated_at"] = frontmatter["modified"]

            # Extract tags from content
            if self.extract_tags:
                content_tags = re.findall(r'#[\w\-\/]+', main_content)
                if content_tags:
                    existing_tags = metadata.get("tags", [])
                    all_tags = list(set(existing_tags + content_tags))
                    metadata["tags"] = all_tags

            # Extract and store backlinks
            linked_notes = []
            if self.extract_backlinks:
                # Find [[Note Name]] style links
                backlinks = re.findall(r'\[\[([^\]]+)\]\]', main_content)
                for link in backlinks:
                    # Handle alias syntax [[Note Name|Display Text]]
                    if '|' in link:
                        link = link.split('|')[0]
                    
                    # Convert to potential file path
                    linked_file = f"{link}.md"
                    
                    # Try to find the actual file (case-insensitive)
                    for potential_path in self.vault_path.rglob("*.md"):
                        if potential_path.name.lower() == linked_file.lower():
                            linked_rel_path = str(potential_path.relative_to(self.vault_path))
                            linked_notes.append(linked_rel_path)
                            break
                
                # Store for relationship creation later
                note_relationships[str(rel_path)] = linked_notes
                
                # Replace wiki-links with markdown links for better readability
                main_content = re.sub(r'\[\[([^\]]+)\]\]', r'[\1]', main_content)

            # Build full content
            full_content = f"# {title}\n\n"
            if frontmatter:
                full_content += "## Metadata\n\n"
                for key, value in frontmatter.items():
                    full_content += f"**{key}**: {value}\n"
                full_content += "\n"
            
            full_content += main_content

            return FrameRecord(
                text_content=full_content,
                metadata=metadata,
                context=main_content[:500],  # First 500 chars as context
            )

        except Exception as e:
            self.logger.error(f"Failed to map note {note_path}: {e}")
            return None

    def _map_attachment_to_frame(
        self,
        file_path: Path,
        collection_id: str
    ) -> FrameRecord | None:
        """Map Obsidian attachment to FrameRecord."""
        try:
            stat = file_path.stat()
            rel_path = file_path.relative_to(self.vault_path)
            
            metadata = {
                "title": file_path.name,
                "record_type": RecordType.DOCUMENT,
                "source_type": "obsidian_attachment",
                "source_file": str(rel_path),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "collection": collection_id,
                "collection_id": collection_id,
                "custom_metadata": {
                    "x_obsidian_vault": self.vault_path.name,
                    "x_obsidian_folder": str(rel_path.parent) if rel_path.parent != Path(".") else "",
                    "x_obsidian_file_size": stat.st_size,
                    "x_obsidian_file_type": file_path.suffix,
                }
            }

            # Determine content based on file type
            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                text_content = f"# {file_path.name}\n\nImage attachment from Obsidian vault.\n\n**File**: {rel_path}\n**Size**: {stat.st_size} bytes"
                
                # Could read image data here if needed
                # raw_data = file_path.read_bytes()
                # raw_data_type = f"image/{file_path.suffix[1:]}"
                
            elif file_path.suffix.lower() == '.pdf':
                text_content = f"# {file_path.name}\n\nPDF document from Obsidian vault.\n\n**File**: {rel_path}\n**Size**: {stat.st_size} bytes"
                
            elif file_path.suffix.lower() in ['.mp4', '.webm', '.mov']:
                text_content = f"# {file_path.name}\n\nVideo file from Obsidian vault.\n\n**File**: {rel_path}\n**Size**: {stat.st_size} bytes"
                
            elif file_path.suffix.lower() in ['.mp3', '.wav']:
                text_content = f"# {file_path.name}\n\nAudio file from Obsidian vault.\n\n**File**: {rel_path}\n**Size**: {stat.st_size} bytes"
                
            else:
                text_content = f"# {file_path.name}\n\nAttachment from Obsidian vault.\n\n**File**: {rel_path}\n**Type**: {file_path.suffix}\n**Size**: {stat.st_size} bytes"

            return FrameRecord(
                text_content=text_content,
                metadata=metadata,
                # raw_data and raw_data_type could be added here for binary files
            )

        except Exception as e:
            self.logger.error(f"Failed to map attachment {file_path}: {e}")
            return None