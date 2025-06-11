"""FrameSet importer implementation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ..frame import FrameDataset, FrameRecord
from ..schema.contextframe_schema import RecordType


class FrameSetImporter:
    """Import FrameSets from various formats.

    This class handles importing FrameSets that were previously exported,
    with support for recreating the full structure including frames and
    relationships.
    """

    def __init__(self, dataset: FrameDataset):
        """Initialize the importer with a target dataset.

        Parameters
        ----------
        dataset : FrameDataset
            The dataset to import framesets into
        """
        self.dataset = dataset

    def import_frameset(
        self,
        input_path: Path | str,
        *,
        conflict_strategy: str = "skip",
        import_frames: bool = True,
    ) -> FrameRecord:
        """Import a FrameSet from a file.

        Parameters
        ----------
        input_path : Path | str
            Path to the file to import (or directory for multi-file imports)
        conflict_strategy : str
            How to handle existing records with same UUID:
            - "skip": Skip importing conflicting records
            - "replace": Replace existing records
            - "new_uuid": Generate new UUIDs for imported records
        import_frames : bool
            Whether to import the frames referenced by the frameset

        Returns
        -------
        FrameRecord
            The imported frameset record

        Raises
        ------
        ValueError
            If file format not supported or parsing fails
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")

        # Determine format from extension
        if input_path.suffix == ".md":
            return self._import_markdown(input_path, conflict_strategy, import_frames)
        elif input_path.suffix == ".json":
            return self._import_json(input_path, conflict_strategy, import_frames)
        else:
            raise ValueError(f"Unsupported import format: {input_path.suffix}")

    def _import_markdown(
        self,
        input_path: Path,
        conflict_strategy: str,
        import_frames: bool,
    ) -> FrameRecord:
        """Import from Markdown format."""
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required for Markdown import. "
                "Install with: pip install 'contextframe[io]'"
            )
        content = input_path.read_text()

        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError("No YAML frontmatter found in Markdown file")

        frontmatter_text = frontmatter_match.group(1)
        frontmatter = yaml.safe_load(frontmatter_text)

        # Extract content after frontmatter
        body_start = frontmatter_match.end()
        body = content[body_start:].strip()

        # Parse the body to extract summary
        summary = ""
        summary_match = re.search(r'## Summary\n\n(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()

        # Create the frameset record
        frameset, is_existing = self._create_frameset_from_metadata(
            frontmatter, summary, conflict_strategy
        )

        # Import frames if requested and the input is a directory (multi-file)
        if import_frames:
            if (
                input_path.parent.name == input_path.stem
                and input_path.name == "index.md"
            ):
                # This is a multi-file export
                frames_imported = self._import_frame_files(
                    input_path.parent, frameset, conflict_strategy
                )
            else:
                # Single file - parse frames from the content
                frames_imported = self._parse_frames_from_markdown(
                    body, frameset, conflict_strategy
                )

        # Add the frameset to the dataset only if it's not an existing one
        if not is_existing:
            self.dataset.add(frameset)

        return frameset

    def _create_frameset_from_metadata(
        self,
        metadata: dict[str, Any],
        summary: str,
        conflict_strategy: str,
    ) -> tuple[FrameRecord, bool]:
        """Create a FrameSet record from parsed metadata.

        Returns
        -------
        tuple[FrameRecord, bool]
            The frameset and whether it's an existing record
        """
        # Handle conflict strategy for UUID
        uuid = metadata.get("uuid")
        if uuid and conflict_strategy != "new_uuid":
            # Check if UUID already exists
            existing = self.dataset.get_by_uuid(uuid)
            if existing:
                if conflict_strategy == "skip":
                    return existing, True
                elif conflict_strategy == "replace":
                    self.dataset.delete_record(uuid)
        elif conflict_strategy == "new_uuid" or not uuid:
            # Generate new UUID
            import uuid as uuid_lib

            uuid = str(uuid_lib.uuid4())
            metadata["uuid"] = uuid

        # Build the frameset record
        title = metadata.pop("title", "Imported FrameSet")
        record_type = metadata.pop("record_type", RecordType.FRAMESET)

        # Extract custom metadata
        custom_metadata = metadata.pop("custom_metadata", {})

        # Create the record
        frameset = FrameRecord.create(
            title=title,
            content=summary,
            record_type=record_type,
            custom_metadata=custom_metadata,
            **metadata,  # Pass remaining metadata fields
        )

        # Ensure UUID is set correctly
        frameset.metadata["uuid"] = uuid

        return frameset, False

    def _parse_frames_from_markdown(
        self,
        body: str,
        frameset: FrameRecord,
        conflict_strategy: str,
    ) -> int:
        """Parse frames from single-file markdown body."""
        frames_section_match = re.search(r'## Frames \(\d+\)\n\n(.*)', body, re.DOTALL)
        if not frames_section_match:
            return 0

        frames_content = frames_section_match.group(1)

        # Split into individual frame sections
        frame_pattern = r'### \d+\. (.*?)\n\n(.*?)(?=\n### \d+\.|$)'
        frame_matches = re.finditer(frame_pattern, frames_content, re.DOTALL)

        imported_count = 0
        for match in frame_matches:
            frame_title = match.group(1)
            frame_body = match.group(2)

            # Parse frame metadata
            uuid_match = re.search(r'\*\*UUID\*\*: `(.*?)`', frame_body)
            author_match = re.search(r'\*\*Author\*\*: (.*?)(?:\n|$)', frame_body)
            tags_match = re.search(r'\*\*Tags\*\*: (.*?)(?:\n|$)', frame_body)

            # Parse content
            content_match = re.search(
                r'#### Content\n\n(.*?)(?=\n####|\Z)', frame_body, re.DOTALL
            )
            context_match = re.search(
                r'#### Context\n\n(.*?)(?=\n####|\Z)', frame_body, re.DOTALL
            )

            # Create frame record
            frame_data = {
                "title": frame_title,
                "content": content_match.group(1).strip() if content_match else "",
            }

            if uuid_match:
                frame_data["uuid"] = uuid_match.group(1)
            if author_match:
                frame_data["author"] = author_match.group(1).strip()
            if tags_match:
                tags_str = tags_match.group(1).strip()
                frame_data["tags"] = [tag.strip() for tag in tags_str.split(",")]
            if context_match:
                frame_data["context"] = context_match.group(1).strip()

            # Handle conflicts
            if "uuid" in frame_data and conflict_strategy != "new_uuid":
                existing = self.dataset.get_by_uuid(frame_data["uuid"])
                if existing:
                    if conflict_strategy == "skip":
                        # Still add relationship to frameset
                        frameset.add_relationship(
                            frame_data["uuid"],
                            relationship_type="contains",
                            title=frame_title,
                        )
                        imported_count += 1
                        continue
                    elif conflict_strategy == "replace":
                        self.dataset.delete_record(frame_data["uuid"])

            # Create and add frame
            frame = FrameRecord.create(**frame_data)
            self.dataset.add(frame)

            # Add relationship to frameset
            frameset.add_relationship(
                frame.uuid, relationship_type="contains", title=frame_title
            )

            imported_count += 1

        return imported_count

    def _import_frame_files(
        self,
        directory: Path,
        frameset: FrameRecord,
        conflict_strategy: str,
    ) -> int:
        """Import frames from separate markdown files."""
        frame_files = sorted(directory.glob("frame_*.md"))
        imported_count = 0

        for frame_file in frame_files:
            content = frame_file.read_text()

            # Extract frontmatter if present
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                body = content[frontmatter_match.end() :].strip()
            else:
                # Parse from markdown structure
                lines = content.strip().split('\n')
                title_line = lines[0] if lines else ""
                title_match = re.match(r'### \d+\. (.+)', title_line)
                title = title_match.group(1) if title_match else "Imported Frame"

                # Simple parsing for frame without frontmatter
                frontmatter = {"title": title}
                body = '\n'.join(lines[1:]).strip()

            # Extract content sections
            if "content" not in frontmatter:
                content_match = re.search(
                    r'#### Content\n\n(.*?)(?=\n####|\Z)', body, re.DOTALL
                )
                if content_match:
                    frontmatter["content"] = content_match.group(1).strip()

            # Create frame
            frame = self._create_frame_from_metadata(frontmatter, conflict_strategy)
            self.dataset.add(frame)

            # Add relationship
            frameset.add_relationship(
                frame.uuid, relationship_type="contains", title=frame.title
            )

            imported_count += 1

        return imported_count

    def _create_frame_from_metadata(
        self,
        metadata: dict[str, Any],
        conflict_strategy: str,
    ) -> FrameRecord:
        """Create a frame record from metadata."""
        # Similar to frameset creation but for regular frames
        uuid = metadata.get("uuid")
        if uuid and conflict_strategy != "new_uuid":
            existing = self.dataset.get_by_uuid(uuid)
            if existing:
                if conflict_strategy == "skip":
                    return existing
                elif conflict_strategy == "replace":
                    self.dataset.delete_record(uuid)
        elif conflict_strategy == "new_uuid" or not uuid:
            import uuid as uuid_lib

            uuid = str(uuid_lib.uuid4())
            metadata["uuid"] = uuid

        title = metadata.pop("title", "Imported Frame")
        content = metadata.pop("content", "")

        frame = FrameRecord.create(title=title, content=content, **metadata)

        frame.metadata["uuid"] = uuid
        return frame

    def _import_json(
        self,
        input_path: Path,
        conflict_strategy: str,
        import_frames: bool,
    ) -> FrameRecord:
        """Import from JSON format."""
        data = json.loads(input_path.read_text())

        # Create frameset
        frameset_data = data.get("frameset", {})
        content = data.get("content", "")

        frameset, is_existing = self._create_frameset_from_metadata(
            frameset_data, content, conflict_strategy
        )

        # Import frames if present and requested
        if import_frames and "frames" in data:
            for frame_data in data["frames"]:
                frame_metadata = frame_data.get("metadata", {})
                frame_content = frame_data.get("content", "")
                frame_metadata["content"] = frame_content

                frame = self._create_frame_from_metadata(
                    frame_metadata, conflict_strategy
                )
                self.dataset.add(frame)

                # Add relationship
                frameset.add_relationship(
                    frame.uuid, relationship_type="contains", title=frame.title
                )

        # Add frameset to dataset only if it's not an existing one
        if not is_existing:
            self.dataset.add(frameset)

        return frameset
