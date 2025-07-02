#!/usr/bin/env python3
"""
Integration tests for API improvements in v0.1.3
Tests new non-breaking features added to improve the API.
"""

import os
import shutil
import tempfile
import numpy as np
import pytest

from contextframe import FrameRecord, FrameDataset


class TestAPIImprovements:
    """Test new API features and improvements."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.temp_dir, "api_test.lance")
        self.embed_dim = 1536
        
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_uuid_override_at_creation(self):
        """Test that UUID can be overridden at creation time."""
        # Create record with custom UUID
        custom_uuid = "test-uuid-12345"
        record = FrameRecord.create(
            title="Test Document",
            content="Test content",
            uuid=custom_uuid
        )
        
        # Verify UUID was set correctly
        assert record.uuid == custom_uuid
        
        # Test that it persists when saved to dataset
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        dataset.add(record)
        
        # Retrieve and verify
        retrieved = dataset.get_by_uuid(custom_uuid)
        assert retrieved is not None
        assert retrieved.uuid == custom_uuid
        
    def test_uuid_auto_generation_still_works(self):
        """Test that UUID is still auto-generated when not provided."""
        # Create record without UUID
        record = FrameRecord.create(
            title="Auto UUID Document",
            content="This should get an auto-generated UUID"
        )
        
        # Verify UUID was generated
        assert record.uuid is not None
        assert len(record.uuid) == 36  # Standard UUID length
        assert "-" in record.uuid  # UUID format check
        
    def test_auto_indexing_full_text_search(self):
        """Test auto-indexing option for full-text search."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Add documents
        docs = [
            FrameRecord.create(
                title="Python Programming",
                content="Python is a high-level programming language.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            ),
            FrameRecord.create(
                title="JavaScript Tutorial",
                content="JavaScript is the language of the web.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            ),
            FrameRecord.create(
                title="Data Science with Python",
                content="Python is widely used in data science and machine learning.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            )
        ]
        dataset.add_many(docs)
        
        # Search with auto_index=True (should create index automatically)
        results = dataset.full_text_search("Python", k=5, auto_index=True)
        
        # Should find documents containing "Python"
        assert len(results) >= 2
        python_titles = [r.title for r in results]
        assert any("Python" in title for title in python_titles)
        
    def test_auto_indexing_only_creates_once(self):
        """Test that auto-indexing doesn't recreate existing index."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Add a document
        doc = FrameRecord.create(
            title="Test Document",
            content="Content for testing auto-indexing"
        )
        dataset.add(doc)
        
        # First search with auto_index should create index
        results1 = dataset.full_text_search("testing", auto_index=True)
        
        # Second search with auto_index should reuse existing index
        # (no error should occur)
        results2 = dataset.full_text_search("content", auto_index=True)
        
        # Both searches should work
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        
    def test_member_of_relationship_type(self):
        """Test that member_of relationship type is supported."""
        # Create collection header and member
        header = FrameRecord.create(
            title="Collection Header",
            content="Header for the collection",
            record_type="collection_header"
        )
        
        member = FrameRecord.create(
            title="Collection Member",
            content="Member of the collection"
        )
        
        # Add member_of relationship (previously would fail)
        member.add_relationship(header, relationship_type="member_of")
        
        # Verify relationship was added
        relationships = member.metadata.get("relationships", [])
        assert len(relationships) == 1
        assert relationships[0]["relationship_type"] == "member_of"
        assert relationships[0]["target_uuid"] == header.uuid
        
    def test_improved_scalar_index_api(self):
        """Test enhanced scalar index creation with index types."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Add documents with various fields
        docs = [
            FrameRecord.create(
                title=f"Document {i}",
                content=f"Content {i}",
                status="published" if i % 2 == 0 else "draft",
                custom_metadata={"priority": str(i)}
            )
            for i in range(10)
        ]
        dataset.add_many(docs)
        
        # Create different types of indexes
        # BITMAP for status field
        dataset.create_scalar_index("status", index_type="BITMAP")
        
        # INVERTED for text search on title
        dataset.create_scalar_index("title", index_type="INVERTED")
        
        # Verify indexes work by using them in queries
        published = dataset.scanner(filter="status = 'published'").to_table()
        assert len(published) == 5  # Half should be published
        
        # Full-text search on title
        results = dataset.full_text_search("Document", columns=["title"], k=10)
        assert len(results) == 10  # All have "Document" in title
        

if __name__ == "__main__":
    pytest.main([__file__, "-v"])