"""Test FrameSet import/export functionality."""

import json
import numpy as np
import pytest
import tempfile
import yaml
from contextframe import FrameDataset, FrameRecord
from contextframe.io import ExportFormat, FrameSetExporter, FrameSetImporter
from contextframe.schema.contextframe_schema import RecordType
from pathlib import Path


@pytest.fixture
def temp_dataset_with_frameset():
    """Create a temporary dataset with a frameset and some frames."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = Path(tmpdir) / "test.lance"
        ds = FrameDataset.create(dataset_path)

        # Create some documents
        doc1 = FrameRecord.create(
            title="Document 1",
            content="This is the first document",
            author="Alice",
            tags=["test", "doc1"],
            context="Important context for doc1",
        )
        doc2 = FrameRecord.create(
            title="Document 2",
            content="This is the second document",
            author="Bob",
            tags=["test", "doc2"],
        )
        doc3 = FrameRecord.create(
            title="Document 3",
            content="This is the third document",
            tags=["test", "doc3"],
        )

        ds.add(doc1)
        ds.add(doc2)
        ds.add(doc3)

        # Create a frameset
        frameset = FrameRecord.create(
            title="Test FrameSet",
            content="This is a test frameset containing important documents",
            record_type=RecordType.FRAMESET,
            tags=["frameset", "test"],
            custom_metadata={"source_query": "tags contains 'test'"},
        )

        # Add relationships to frames
        frameset.add_relationship(
            doc1.uuid, relationship_type="contains", title=doc1.title
        )
        frameset.add_relationship(
            doc2.uuid, relationship_type="contains", title=doc2.title
        )

        ds.add(frameset)

        yield ds, frameset, [doc1, doc2, doc3]


def test_export_markdown_single_file(temp_dataset_with_frameset):
    """Test exporting a frameset to a single markdown file."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.md"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid,
            output_path,
            format=ExportFormat.MARKDOWN,
            include_frames=True,
            single_file=True,
        )

        assert exported_path.exists()
        assert exported_path.suffix == ".md"

        # Read and verify content
        content = exported_path.read_text()

        # Check frontmatter
        assert "---" in content
        assert f"uuid: {frameset.uuid}" in content
        assert "title: Test FrameSet" in content
        assert "record_type: frameset" in content
        # frame_count should be in custom_metadata
        assert "custom_metadata:" in content
        assert "frame_count: '2'" in content  # YAML will quote the string

        # Check content sections
        assert "# Test FrameSet" in content
        assert "## Summary" in content
        assert "This is a test frameset containing important documents" in content
        assert "## Source Query" in content
        assert "tags contains 'test'" in content

        # Check frames are included
        assert "## Frames (2)" in content
        assert "### 1. Document 1" in content
        assert "This is the first document" in content
        assert "### 2. Document 2" in content
        assert "This is the second document" in content

        # Check frame metadata
        assert f"**UUID**: `{docs[0].uuid}`" in content
        assert "**Author**: Alice" in content
        assert "**Tags**: test, doc1" in content
        assert "#### Context" in content
        assert "Important context for doc1" in content


def test_export_markdown_multi_file(temp_dataset_with_frameset):
    """Test exporting a frameset to multiple markdown files."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.md"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid,
            output_path,
            format=ExportFormat.MARKDOWN,
            include_frames=True,
            single_file=False,
        )

        # Should create a directory with index.md
        expected_dir = Path(tmpdir) / "frameset"
        assert expected_dir.exists()
        assert expected_dir.is_dir()

        index_path = expected_dir / "index.md"
        assert index_path.exists()
        assert exported_path == index_path

        # Check frame files exist
        frame1_path = expected_dir / "frame_001.md"
        frame2_path = expected_dir / "frame_002.md"
        assert frame1_path.exists()
        assert frame2_path.exists()

        # Verify index content
        index_content = index_path.read_text()
        assert "1. [Document 1](frame_001.md)" in index_content
        assert "2. [Document 2](frame_002.md)" in index_content

        # Verify frame file content
        frame1_content = frame1_path.read_text()
        assert "### 1. Document 1" in frame1_content
        assert "This is the first document" in frame1_content


def test_export_text_format(temp_dataset_with_frameset):
    """Test exporting to plain text format."""
    ds, frameset, _ = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.txt"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid, output_path, format=ExportFormat.TEXT, include_frames=True
        )

        assert exported_path.exists()
        assert exported_path.suffix == ".txt"

        content = exported_path.read_text()
        assert "FRAMESET: Test FrameSet" in content
        assert "SUMMARY:" in content
        assert "FRAMES (2):" in content
        assert "1. Document 1" in content
        assert "2. Document 2" in content


def test_export_json_format(temp_dataset_with_frameset):
    """Test exporting to JSON format."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.json"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid, output_path, format=ExportFormat.JSON, include_frames=True
        )

        assert exported_path.exists()
        assert exported_path.suffix == ".json"

        data = json.loads(exported_path.read_text())

        assert "frameset" in data
        assert data["frameset"]["uuid"] == frameset.uuid
        assert data["frameset"]["title"] == "Test FrameSet"

        assert "frames" in data
        assert len(data["frames"]) == 2
        assert data["frames"][0]["metadata"]["title"] == "Document 1"


def test_import_markdown_single_file(temp_dataset_with_frameset):
    """Test importing a frameset from a markdown file."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        # First export
        export_path = Path(tmpdir) / "export.md"
        exporter = FrameSetExporter(ds)
        exporter.export_frameset(
            frameset.uuid,
            export_path,
            format=ExportFormat.MARKDOWN,
            include_frames=True,
            single_file=True,
        )

        # Create new dataset for import
        import_dataset_path = Path(tmpdir) / "import.lance"
        import_ds = FrameDataset.create(import_dataset_path)

        # Import
        importer = FrameSetImporter(import_ds)
        imported_frameset = importer.import_frameset(
            export_path, conflict_strategy="new_uuid", import_frames=True
        )

        # Verify imported frameset
        assert imported_frameset.title == "Test FrameSet"
        assert imported_frameset.content == frameset.content
        assert imported_frameset.metadata["record_type"] == "frameset"
        assert imported_frameset.metadata["tags"] == ["frameset", "test"]

        # Verify frames were imported
        imported_frames = import_ds.get_frameset_frames(imported_frameset.uuid)
        assert len(imported_frames) == 2

        # Check frame content
        frame_titles = [f.title for f in imported_frames]
        assert "Document 1" in frame_titles
        assert "Document 2" in frame_titles


def test_import_conflict_strategies(temp_dataset_with_frameset):
    """Test different conflict resolution strategies."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        # Export frameset
        export_path = Path(tmpdir) / "export.md"
        exporter = FrameSetExporter(ds)
        exporter.export_frameset(
            frameset.uuid,
            export_path,
            format=ExportFormat.MARKDOWN,
            include_frames=True,
        )

        # Test "skip" strategy
        importer = FrameSetImporter(ds)
        result = importer.import_frameset(export_path, conflict_strategy="skip")
        assert result.uuid == frameset.uuid  # Should return existing

        # Test "replace" strategy
        original_content = frameset.content
        frameset.content = "Modified content"
        ds.update_record(frameset)

        result = importer.import_frameset(export_path, conflict_strategy="replace")

        # Should have original content from export
        reloaded = ds.get_by_uuid(frameset.uuid)
        assert reloaded.content == original_content

        # Test "new_uuid" strategy
        result = importer.import_frameset(export_path, conflict_strategy="new_uuid")
        assert result.uuid != frameset.uuid
        assert result.title == frameset.title


def test_export_without_frames(temp_dataset_with_frameset):
    """Test exporting frameset without including frames."""
    ds, frameset, _ = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.md"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid, output_path, include_frames=False
        )

        content = exported_path.read_text()

        # Should have frameset info but no frames
        assert "# Test FrameSet" in content
        assert "custom_metadata:" in content
        assert (
            "frame_count: '2'" in content
        )  # Count is still in custom_metadata as string
        assert "## Frames" not in content  # But frames section is not included
        assert "Document 1" not in content
        assert "Document 2" not in content


def test_roundtrip_preservation(temp_dataset_with_frameset):
    """Test that export/import preserves all data."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        # Export
        export_path = Path(tmpdir) / "export.md"
        exporter = FrameSetExporter(ds)
        exporter.export_frameset(frameset.uuid, export_path, include_frames=True)

        # Import to new dataset
        import_dataset_path = Path(tmpdir) / "import.lance"
        import_ds = FrameDataset.create(import_dataset_path)

        importer = FrameSetImporter(import_ds)
        imported = importer.import_frameset(export_path, conflict_strategy="new_uuid")

        # Compare metadata (excluding UUID which is different)
        original_meta = frameset.metadata.copy()
        imported_meta = imported.metadata.copy()

        original_meta.pop("uuid")
        imported_meta.pop("uuid")

        # Some fields might differ slightly due to parsing
        assert original_meta["title"] == imported_meta["title"]
        assert original_meta["record_type"] == imported_meta["record_type"]
        assert original_meta["tags"] == imported_meta["tags"]

        # Check relationships were preserved
        assert len(imported.metadata["relationships"]) == 2

        # Check custom metadata
        orig_custom = original_meta.get("custom_metadata", {})
        imp_custom = imported_meta.get("custom_metadata", {})
        assert orig_custom.get("source_query") == imp_custom.get("source_query")


def test_export_with_mermaid_diagram(temp_dataset_with_frameset):
    """Test that Mermaid relationship diagrams are included in export."""
    ds, frameset, docs = temp_dataset_with_frameset

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "frameset.md"

        exporter = FrameSetExporter(ds)
        exported_path = exporter.export_frameset(
            frameset.uuid,
            output_path,
            format=ExportFormat.MARKDOWN,
            include_frames=True,
            single_file=True,
        )

        content = exported_path.read_text()

        # Check that Mermaid diagram is included
        assert "## Relationship Visualization" in content
        assert "```mermaid" in content
        assert "graph TD" in content
        assert 'FS["Test FrameSet<br/>FrameSet"]' in content
        
        # Check that relationships are shown
        assert 'F1["Document 1"]' in content
        assert 'F2["Document 2"]' in content
        assert "FS -->|contains| F1" in content
        assert "FS -->|contains| F2" in content
        
        # Check legend
        assert "**Relationship Types:**" in content
        assert "- `contains`: Direct inclusion in the frameset" in content
