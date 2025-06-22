"""FrameSet exporter implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ..frame import FrameDataset, FrameRecord
from .formats import ExportFormat


class FrameSetExporter:
    """Export FrameSets to various formats.

    This class handles exporting FrameSets and their associated frames
    to different file formats, with Markdown being the primary format
    for human readability and portability.
    """

    def __init__(self, dataset: FrameDataset):
        """Initialize the exporter with a dataset.

        Parameters
        ----------
        dataset : FrameDataset
            The dataset containing the framesets to export
        """
        self.dataset = dataset

    def export_frameset(
        self,
        frameset_uuid: str,
        output_path: Path | str,
        format: ExportFormat | str = ExportFormat.MARKDOWN,
        *,
        include_frames: bool = True,
        single_file: bool = True,
    ) -> Path:
        """Export a FrameSet to the specified format.

        Parameters
        ----------
        frameset_uuid : str
            UUID of the frameset to export
        output_path : Path | str
            Output file or directory path
        format : ExportFormat | str
            Export format (default: markdown)
        include_frames : bool
            Whether to include the frames referenced by the frameset
        single_file : bool
            For markdown: True creates one file, False creates index + frame files

        Returns
        -------
        Path
            Path to the exported file(s)

        Raises
        ------
        ValueError
            If frameset not found or format not supported
        """
        # Get the frameset
        frameset = self.dataset.get_frameset(frameset_uuid)
        if not frameset:
            raise ValueError(f"FrameSet {frameset_uuid} not found")

        # Convert format string to enum if needed
        if isinstance(format, str):
            try:
                format = ExportFormat(format)
            except ValueError:
                raise ValueError(f"Unsupported format: {format}")

        output_path = Path(output_path)

        # Route to appropriate export method
        if format == ExportFormat.MARKDOWN:
            return self._export_markdown(
                frameset, output_path, include_frames, single_file
            )
        elif format == ExportFormat.TEXT:
            return self._export_text(frameset, output_path, include_frames)
        elif format == ExportFormat.JSON:
            return self._export_json(frameset, output_path, include_frames)
        elif format == ExportFormat.PARQUET:
            return self._export_parquet(frameset, output_path, include_frames)
        elif format == ExportFormat.CSV:
            return self._export_csv(frameset, output_path, include_frames)
        else:
            raise ValueError(f"Export format {format} not implemented")

    def _export_markdown(
        self,
        frameset: FrameRecord,
        output_path: Path,
        include_frames: bool,
        single_file: bool,
    ) -> Path:
        """Export frameset as Markdown with YAML frontmatter.

        This is the primary export format, optimized for human readability
        and easy parsing by both humans and AI agents.
        """
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required for Markdown export. "
                "Install with: pip install 'contextframe[io]'"
            )
        # Ensure .md extension
        if output_path.suffix != ".md":
            output_path = output_path.with_suffix(".md")

        # Build the markdown content
        content = []

        # Add YAML frontmatter
        frontmatter = self._build_frontmatter(frameset)
        content.append("---")
        content.append(
            yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
        )
        content.append("---")
        content.append("")

        # Add title and content
        content.append(f"# {frameset.title}")
        content.append("")

        if frameset.content:
            content.append("## Summary")
            content.append("")
            content.append(frameset.content)
            content.append("")

        # Add metadata section
        custom_meta = frameset.metadata.get("custom_metadata", {})
        if source_query := custom_meta.get("source_query"):
            content.append("## Source Query")
            content.append("")
            content.append("```")
            content.append(source_query)
            content.append("```")
            content.append("")

        # Add frames if requested
        if include_frames:
            # Add relationship visualization
            relationships = frameset.metadata.get("relationships", [])
            if relationships:
                content.extend(
                    self._build_relationship_diagram(frameset, relationships)
                )
                content.append("")
            frames = self.dataset.get_frameset_frames(frameset.uuid)
            frame_count = len(frames)

            if frames:
                content.append(f"## Frames ({frame_count})")
                content.append("")

                if single_file:
                    # Include all frames in the same file
                    for i, frame in enumerate(frames, 1):
                        content.extend(self._format_frame_markdown(frame, i))
                        content.append("")
                else:
                    # Create separate files for frames
                    output_dir = output_path.parent / output_path.stem
                    output_dir.mkdir(exist_ok=True)

                    # Update main file to be index.md
                    output_path = output_dir / "index.md"

                    # Add links to frame files
                    for i, frame in enumerate(frames, 1):
                        frame_filename = f"frame_{i:03d}.md"
                        content.append(f"{i}. [{frame.title}]({frame_filename})")

                        # Write individual frame file
                        frame_content = self._format_frame_markdown(frame, i)
                        frame_path = output_dir / frame_filename
                        frame_path.write_text("\n".join(frame_content))

                    content.append("")

        # Add usage instructions
        content.extend(self._add_usage_instructions())

        # Write the main file
        output_path.write_text("\n".join(content))

        return output_path

    def _build_frontmatter(self, frameset: FrameRecord) -> dict[str, Any]:
        """Build YAML frontmatter for the frameset."""
        meta = frameset.metadata.copy()

        # Essential fields at the top
        frontmatter = {
            "uuid": meta.get("uuid"),
            "title": meta.get("title"),
            "record_type": meta.get("record_type"),
        }

        # Add other metadata fields
        for key in ["context", "author", "created_at", "updated_at", "tags", "status"]:
            if value := meta.get(key):
                frontmatter[key] = value

        # Add custom metadata (including frame_count as custom metadata)
        custom_meta = meta.get("custom_metadata", {}).copy()
        # Add frame count to custom metadata for reference
        frame_count = self.dataset.get_frameset_frame_count(frameset.uuid)
        custom_meta["frame_count"] = str(frame_count)

        if custom_meta:
            frontmatter["custom_metadata"] = dict(custom_meta)

        return frontmatter

    def _format_frame_markdown(self, frame: FrameRecord, index: int) -> list[str]:
        """Format a single frame as markdown sections."""
        lines = []

        lines.append(f"### {index}. {frame.title}")
        lines.append("")

        # Add metadata
        lines.append(f"**UUID**: `{frame.uuid}`")
        if author := frame.metadata.get("author"):
            lines.append(f"**Author**: {author}")
        if tags := frame.metadata.get("tags"):
            lines.append(f"**Tags**: {', '.join(tags)}")
        lines.append("")

        # Add content
        if frame.content:
            lines.append("#### Content")
            lines.append("")
            lines.append(frame.content)
            lines.append("")

        # Add context if present
        if context := frame.metadata.get("context"):
            lines.append("#### Context")
            lines.append("")
            lines.append(context)
            lines.append("")

        return lines

    def _build_relationship_diagram(
        self, frameset: FrameRecord, relationships: list[dict[str, Any]]
    ) -> list[str]:
        """Build a Mermaid diagram showing relationships."""
        lines = []

        lines.append("## Relationship Visualization")
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append(f'    FS["{frameset.title}<br/>FrameSet"]')
        lines.append("")

        # Group relationships by type
        rel_by_type = {}
        for rel in relationships:
            rel_type = rel.get("type", "related")
            if rel_type not in rel_by_type:
                rel_by_type[rel_type] = []
            rel_by_type[rel_type].append(rel)

        # Add nodes and connections
        node_count = 0
        for rel_type, rels in rel_by_type.items():
            for rel in rels:
                node_count += 1
                node_id = f"F{node_count}"
                title = rel.get("title", "Unknown")
                # Escape quotes in title for Mermaid
                title = title.replace('"', "'")

                lines.append(f'    {node_id}["{title}"]')

                # Define edge style based on relationship type
                if rel_type == "contains":
                    edge_style = "-->|contains|"
                elif rel_type == "references":
                    edge_style = "-.->|references|"
                elif rel_type == "member_of":
                    edge_style = "==>|member of|"
                elif rel_type == "related":
                    edge_style = "---|related|"
                else:
                    edge_style = f"---|{rel_type}|"

                lines.append(f"    FS {edge_style} {node_id}")

        lines.append("```")
        lines.append("")

        # Add legend
        lines.append("**Relationship Types:**")
        lines.append("- `contains`: Direct inclusion in the frameset")
        lines.append("- `references`: External reference or citation")
        lines.append("- `member_of`: Part of a collection or group")

        return lines

    def _add_usage_instructions(self) -> list[str]:
        """Add usage instructions for humans and agents."""
        return [
            "## Usage",
            "",
            "This FrameSet can be used in several ways:",
            "",
            "1. **For Humans**: Read through the summary and frames to understand the collected context",
            "2. **For AI Agents**: Parse the YAML frontmatter and frame content for structured information",
            "3. **For Import**: Use `FrameSetImporter` to recreate this FrameSet in another ContextFrame dataset",
            "",
            "### Import Example",
            "",
            "```python",
            "from contextframe.import_export import FrameSetImporter",
            "",
            "importer = FrameSetImporter(dataset)",
            'frameset = importer.import_frameset("path/to/this/file.md")',
            "```",
        ]

    def _export_text(
        self, frameset: FrameRecord, output_path: Path, include_frames: bool
    ) -> Path:
        """Export as plain text format."""
        if output_path.suffix != ".txt":
            output_path = output_path.with_suffix(".txt")

        lines = []
        lines.append(f"FRAMESET: {frameset.title}")
        lines.append("=" * len(lines[0]))
        lines.append("")

        if frameset.content:
            lines.append("SUMMARY:")
            lines.append(frameset.content)
            lines.append("")

        if include_frames:
            frames = self.dataset.get_frameset_frames(frameset.uuid)
            if frames:
                lines.append(f"FRAMES ({len(frames)}):")
                lines.append("-" * 20)
                lines.append("")

                for i, frame in enumerate(frames, 1):
                    lines.append(f"{i}. {frame.title}")
                    if frame.content:
                        lines.append(f"   {frame.content[:200]}...")
                    lines.append("")

        output_path.write_text("\n".join(lines))
        return output_path

    def _export_json(
        self, frameset: FrameRecord, output_path: Path, include_frames: bool
    ) -> Path:
        """Export as JSON format."""
        if output_path.suffix != ".json":
            output_path = output_path.with_suffix(".json")

        data = {
            "frameset": frameset.metadata,
            "content": frameset.content,
        }

        if include_frames:
            frames = self.dataset.get_frameset_frames(frameset.uuid)
            data["frames"] = [
                {
                    "metadata": frame.metadata,
                    "content": frame.content,
                }
                for frame in frames
            ]

        output_path.write_text(json.dumps(data, indent=2))
        return output_path

    def _export_parquet(
        self, frameset: FrameRecord, output_path: Path, include_frames: bool
    ) -> Path:
        """Export as Parquet format using PyArrow."""
        if output_path.suffix != ".parquet":
            output_path = output_path.with_suffix(".parquet")

        if include_frames:
            # Get all frames and convert to a table
            frames = self.dataset.get_frameset_frames(frameset.uuid)
            if frames:
                # Create a table from the frames
                import pyarrow as pa
                import pyarrow.parquet as pq

                # Combine frameset and frames into one table
                all_records = [frameset] + frames
                tables = [record.to_table() for record in all_records]
                combined_table = pa.concat_tables(tables)

                # Write to parquet
                pq.write_table(combined_table, output_path)
        else:
            # Just export the frameset record
            import pyarrow.parquet as pq

            table = frameset.to_table()
            pq.write_table(table, output_path)

        return output_path

    def _export_csv(
        self, frameset: FrameRecord, output_path: Path, include_frames: bool
    ) -> Path:
        """Export as CSV format."""
        if output_path.suffix != ".csv":
            output_path = output_path.with_suffix(".csv")

        # Convert to pandas for easy CSV export
        if include_frames:
            frames = self.dataset.get_frameset_frames(frameset.uuid)
            if frames:
                # Combine all records
                all_records = [frameset] + frames
                tables = [record.to_table() for record in all_records]

                import pyarrow as pa

                combined_table = pa.concat_tables(tables)
                df = combined_table.to_pandas()

                # Flatten nested structures for CSV
                # This is a simplified version - might need more sophisticated handling
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].apply(
                            lambda x: str(x) if x is not None else ''
                        )

                df.to_csv(output_path, index=False)
        else:
            # Just the frameset
            table = frameset.to_table()
            df = table.to_pandas()

            # Flatten for CSV
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x) if x is not None else '')

            df.to_csv(output_path, index=False)

        return output_path
