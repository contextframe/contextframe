"""Test FrameSet functionality."""

import numpy as np
import pytest
import tempfile
from contextframe import FrameDataset, FrameRecord
from contextframe.schema.contextframe_schema import RecordType
from pathlib import Path


@pytest.fixture
def temp_dataset():
    """Create a temporary dataset for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = Path(tmpdir) / "test.lance"
        ds = FrameDataset.create(dataset_path)

        # Add some sample documents
        doc1 = FrameRecord.create(
            title="Tesla Q4 Earnings Report",
            content="Tesla reported Q4 2023 earnings with COGS of $65 billion...",
            tags=["tesla", "earnings", "q4"],
            collection="financial_quant",
        )
        doc2 = FrameRecord.create(
            title="Tesla Cost Analysis",
            content="Deep dive into Tesla's cost structure and margins...",
            tags=["tesla", "analysis", "costs"],
            collection="financial_quant",
        )
        doc3 = FrameRecord.create(
            title="Q4 Industry Comparison",
            content="Comparing Q4 performance across automotive industry...",
            tags=["q4", "industry", "comparison"],
            collection="financial_quant",
        )

        ds.add(doc1)
        ds.add(doc2)
        ds.add(doc3)

        yield ds, [doc1, doc2, doc3]


def test_create_frameset(temp_dataset):
    """Test creating a frameset record."""
    ds, docs = temp_dataset

    # Create a frameset from LLM analysis
    frameset = ds.create_frameset(
        title="Q4 COGS Analysis for Tesla",
        content="""
        Based on the analysis of Tesla's Q4 reports:
        
        1. Tesla reported Q4 2023 COGS of $65 billion, representing 78% of revenue
        2. The cost structure shows improvement from previous quarters
        3. Key drivers include battery cost reductions and manufacturing efficiency
        
        Sources analyzed:
        - Tesla Q4 Earnings Report: "...COGS of $65 billion..."
        - Tesla Cost Analysis: "...cost structure and margins..."
        """,
        query="What was Tesla's Q4 cost of goods sold and analysis?",
        source_records=[
            (docs[0].uuid, "Tesla reported Q4 2023 earnings with COGS of $65 billion"),
            (docs[1].uuid, "Deep dive into Tesla's cost structure and margins"),
        ],
        tags=["analysis", "tesla", "q4", "cogs"],
        status="published",
    )

    assert frameset.metadata["record_type"] == "frameset"
    assert frameset.title == "Q4 COGS Analysis for Tesla"
    assert (
        frameset.metadata["custom_metadata"]["original_query"]
        == "What was Tesla's Q4 cost of goods sold and analysis?"
    )
    assert len(frameset.metadata["relationships"]) == 2
    assert frameset.metadata["tags"] == ["analysis", "tesla", "q4", "cogs"]


def test_get_frameset(temp_dataset):
    """Test retrieving a frameset by ID."""
    ds, docs = temp_dataset

    # Create a frameset
    frameset = ds.create_frameset(
        title="Test FrameSet",
        content="Test content",
        source_records=[(docs[0].uuid, "excerpt")],
    )

    # Retrieve it
    retrieved = ds.get_frameset(frameset.uuid)
    assert retrieved is not None
    assert retrieved.uuid == frameset.uuid
    assert retrieved.metadata["record_type"] == "frameset"

    # Try to retrieve a non-frameset
    non_frameset = ds.get_frameset(docs[0].uuid)
    assert non_frameset is None


def test_get_frameset_sources(temp_dataset):
    """Test retrieving source documents from a frameset."""
    ds, docs = temp_dataset

    # Create frameset with sources
    excerpts = [
        (docs[0].uuid, "COGS of $65 billion"),
        (docs[1].uuid, "cost structure and margins"),
    ]

    frameset = ds.create_frameset(
        title="Analysis", content="Combined analysis", source_records=excerpts
    )

    # Get sources
    sources = ds.get_frameset_sources(frameset.uuid)
    assert len(sources) == 2

    # Check first source
    source_doc, excerpt = sources[0]
    assert source_doc.uuid == docs[0].uuid
    assert excerpt == "COGS of $65 billion"

    # Check second source
    source_doc, excerpt = sources[1]
    assert source_doc.uuid == docs[1].uuid
    assert excerpt == "cost structure and margins"


def test_update_frameset_content(temp_dataset):
    """Test updating frameset content."""
    ds, docs = temp_dataset

    # Create initial frameset
    frameset = ds.create_frameset(
        title="Initial Analysis",
        content="Initial content",
        source_records=[(docs[0].uuid, "excerpt 1")],
    )

    # Update with new content
    updated = ds.update_frameset_content(
        frameset.uuid, new_content="Updated analysis with more details"
    )

    assert updated.content == "Updated analysis with more details"

    # Append content
    updated2 = ds.update_frameset_content(
        frameset.uuid, append_content="Additional insights from further analysis"
    )

    assert "Updated analysis with more details" in updated2.content
    assert "Additional insights from further analysis" in updated2.content

    # Add new sources
    updated3 = ds.update_frameset_content(
        frameset.uuid, new_sources=[(docs[1].uuid, "new excerpt")]
    )

    sources = ds.get_frameset_sources(updated3.uuid)
    assert len(sources) == 2  # Original + new


def test_find_framesets_by_query(temp_dataset):
    """Test finding framesets by query substring."""
    ds, docs = temp_dataset

    # Create framesets with different queries
    fs1 = ds.create_frameset(
        title="Tesla Analysis",
        content="Content 1",
        query="What is Tesla's Q4 COGS?",
        source_records=[(docs[0].uuid, "excerpt")],
    )

    fs2 = ds.create_frameset(
        title="Industry Analysis",
        content="Content 2",
        query="Compare automotive industry margins",
        source_records=[(docs[2].uuid, "excerpt")],
    )

    # Find by query
    tesla_framesets = ds.find_framesets_by_query("Tesla")
    assert len(tesla_framesets) == 1
    assert tesla_framesets[0].uuid == fs1.uuid

    industry_framesets = ds.find_framesets_by_query("industry")
    assert len(industry_framesets) == 1
    assert industry_framesets[0].uuid == fs2.uuid

    # Case insensitive
    cogs_framesets = ds.find_framesets_by_query("cogs")
    assert len(cogs_framesets) == 1


def test_find_framesets_referencing(temp_dataset):
    """Test finding framesets that reference a document."""
    ds, docs = temp_dataset

    # Create framesets referencing different documents
    fs1 = ds.create_frameset(
        title="Analysis 1",
        content="Content 1",
        source_records=[(docs[0].uuid, "excerpt"), (docs[1].uuid, "excerpt")],
    )

    fs2 = ds.create_frameset(
        title="Analysis 2",
        content="Content 2",
        source_records=[(docs[1].uuid, "excerpt")],
    )

    # Find framesets referencing doc[0]
    refs_doc0 = ds.find_framesets_referencing(docs[0].uuid)
    assert len(refs_doc0) == 1
    assert refs_doc0[0].uuid == fs1.uuid

    # Find framesets referencing doc[1]
    refs_doc1 = ds.find_framesets_referencing(docs[1].uuid)
    assert len(refs_doc1) == 2
    assert set(fs.uuid for fs in refs_doc1) == {fs1.uuid, fs2.uuid}

    # No framesets reference doc[2]
    refs_doc2 = ds.find_framesets_referencing(docs[2].uuid)
    assert len(refs_doc2) == 0


def test_list_framesets(temp_dataset):
    """Test listing all framesets."""
    ds, docs = temp_dataset

    # Initially no framesets
    framesets = ds.list_framesets()
    assert len(framesets) == 0

    # Create some framesets
    fs1 = ds.create_frameset(
        title="FrameSet 1",
        content="Content 1",
        source_records=[(docs[0].uuid, "excerpt")],
    )

    fs2 = ds.create_frameset(
        title="FrameSet 2",
        content="Content 2",
        source_records=[(docs[1].uuid, "excerpt")],
    )

    # List them
    framesets = ds.list_framesets()
    assert len(framesets) == 2
    assert all(fs.metadata["record_type"] == "frameset" for fs in framesets)
    assert set(fs.uuid for fs in framesets) == {fs1.uuid, fs2.uuid}


def test_frameset_with_embeddings(temp_dataset):
    """Test creating framesets with embeddings."""
    ds, docs = temp_dataset

    # Create embedding for frameset content
    embedding = np.random.rand(1536).astype(np.float32)

    frameset = ds.create_frameset(
        title="Embedded Analysis",
        content="Analysis with semantic search capabilities",
        vector=embedding,
        source_records=[(docs[0].uuid, "excerpt")],
    )

    assert frameset.vector is not None
    assert len(frameset.vector) == 1536

    # Search for framesets using vector similarity
    query_embedding = np.random.rand(1536).astype(np.float32)
    results = ds.knn_search(query_embedding, k=5, filter="record_type = 'frameset'")

    assert len(results) == 1
    assert results[0].uuid == frameset.uuid


def test_frameset_record_type_enum():
    """Test that RecordType enum includes FRAMESET."""
    assert hasattr(RecordType, 'FRAMESET')
    assert RecordType.FRAMESET == "frameset"
    assert "frameset" in RecordType.choices()


def test_get_frameset_headers(temp_dataset):
    """Test retrieving all frameset headers."""
    ds, docs = temp_dataset

    # Create multiple framesets
    frameset1 = ds.create_frameset(
        title="Analysis 1",
        content="First analysis",
        source_records=[(docs[0].uuid, "excerpt")],
    )

    frameset2 = ds.create_frameset(
        title="Analysis 2",
        content="Second analysis",
        source_records=[(docs[1].uuid, "excerpt")],
    )

    # Get all frameset headers
    headers = ds.get_frameset_headers()
    assert len(headers) == 2

    # Check that both framesets are included
    header_uuids = [h.uuid for h in headers]
    assert frameset1.uuid in header_uuids
    assert frameset2.uuid in header_uuids

    # Verify they are all framesets
    for header in headers:
        assert header.metadata.get("record_type") == "frameset"


def test_get_frameset_frames(temp_dataset):
    """Test retrieving frames referenced by a frameset."""
    ds, docs = temp_dataset

    # Create a frameset with relationships to frames
    frameset = FrameRecord.create(
        title="Test FrameSet with Frames",
        content="This frameset references specific frames",
        record_type=RecordType.FRAMESET,
        custom_metadata={"source_query": "test query"},
    )

    # Add relationships to the frames
    frameset.add_relationship(
        docs[0].uuid, relationship_type="contains", title=docs[0].title
    )
    frameset.add_relationship(
        docs[1].uuid, relationship_type="contains", title=docs[1].title
    )

    ds.add(frameset)

    # Get the frames referenced by this frameset
    frames = ds.get_frameset_frames(frameset.uuid)
    assert len(frames) == 2

    # Verify the correct frames were returned
    frame_uuids = [f.uuid for f in frames]
    assert docs[0].uuid in frame_uuids
    assert docs[1].uuid in frame_uuids

    # Test the frame count method
    count = ds.get_frameset_frame_count(frameset.uuid)
    assert count == 2

    # Test with empty frameset (no relationships)
    empty_frameset = FrameRecord.create(
        title="Empty FrameSet",
        content="No frames",
        record_type=RecordType.FRAMESET,
        custom_metadata={},
    )
    ds.add(empty_frameset)

    frames = ds.get_frameset_frames(empty_frameset.uuid)
    assert len(frames) == 0

    # Test frame count for empty frameset
    count = ds.get_frameset_frame_count(empty_frameset.uuid)
    assert count == 0

    # Test with non-existent frameset
    with pytest.raises(ValueError, match="FrameSet .* not found"):
        ds.get_frameset_frames("non-existent-uuid")

    # Test frame count with non-existent frameset
    with pytest.raises(ValueError, match="FrameSet .* not found"):
        ds.get_frameset_frame_count("non-existent-uuid")
