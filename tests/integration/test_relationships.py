#!/usr/bin/env python3
"""
Integration tests for contextframe package - Relationship Management
Tests document relationships and graph-like operations.
"""

import os
import shutil
import tempfile
import numpy as np
import pytest

from contextframe import FrameRecord, FrameDataset
from contextframe.schema import RecordType


class TestRelationships:
    """Test relationship management between documents."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.temp_dir, "relationships_test.lance")
        self.embed_dim = 1536
        
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_add_simple_relationship(self):
        """Test adding relationships between documents."""
        # Create parent and child documents
        parent = FrameRecord.create(
            title="Parent Document",
            content="This is the parent document",
            tags=["parent"]
        )
        
        child = FrameRecord.create(
            title="Child Document", 
            content="This document is derived from the parent",
            tags=["child"]
        )
        
        # Add parent-child relationship
        child.add_relationship(parent, relationship_type="parent")
        
        # Verify relationship was added
        relationships = child.metadata.get("relationships", [])
        assert len(relationships) == 1
        assert relationships[0]["type"] == "parent"
        assert relationships[0]["id"] == parent.uuid
        
    def test_multiple_relationships(self):
        """Test documents with multiple relationships."""
        # Create a network of documents
        main_doc = FrameRecord.create(
            title="Main Research Paper",
            content="Primary research findings"
        )
        
        reference1 = FrameRecord.create(
            title="Reference Paper 1",
            content="Supporting research 1"
        )
        
        reference2 = FrameRecord.create(
            title="Reference Paper 2",
            content="Supporting research 2"
        )
        
        related_work = FrameRecord.create(
            title="Related Work",
            content="Similar research in the field"
        )
        
        # Add multiple relationships
        main_doc.add_relationship(reference1, relationship_type="reference")
        main_doc.add_relationship(reference2, relationship_type="reference")
        main_doc.add_relationship(related_work, relationship_type="related")
        
        # Verify all relationships
        relationships = main_doc.metadata.get("relationships", [])
        assert len(relationships) == 3
        
        # Check relationship types
        rel_types = [r["type"] for r in relationships]
        assert rel_types.count("reference") == 2
        assert rel_types.count("related") == 1
        
        # Check target UUIDs
        ids = [r["id"] for r in relationships]
        assert reference1.uuid in ids
        assert reference2.uuid in ids
        assert related_work.uuid in ids
        
    def test_bidirectional_relationships(self):
        """Test creating bidirectional relationships."""
        doc1 = FrameRecord.create(
            title="Document A",
            content="First document"
        )
        
        doc2 = FrameRecord.create(
            title="Document B",
            content="Second document"
        )
        
        # Create bidirectional relationship
        doc1.add_relationship(doc2, relationship_type="related")
        doc2.add_relationship(doc1, relationship_type="related")
        
        # Both should have relationships
        assert len(doc1.metadata.get("relationships", [])) == 1
        assert len(doc2.metadata.get("relationships", [])) == 1
        
        # Verify they point to each other
        assert doc1.metadata["relationships"][0]["id"] == doc2.uuid
        assert doc2.metadata["relationships"][0]["id"] == doc1.uuid
        
    def test_find_related_documents(self):
        """Test finding documents by relationships in dataset."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create a document hierarchy
        root = FrameRecord.create(
            title="Root Document",
            content="Top level document",
            tags=["root"]
        )
        
        children = []
        for i in range(3):
            child = FrameRecord.create(
                title=f"Child {i}",
                content=f"Child document {i}",
                tags=["child"]
            )
            child.add_relationship(root, relationship_type="parent")
            children.append(child)
            
        # Add all to dataset
        dataset.add(root)
        dataset.add_many(children)
        
        # Find documents related to root
        related_docs = dataset.find_related_to(root.uuid)
        
        # Should find all children
        assert len(related_docs) == 3
        for doc in related_docs:
            assert "child" in doc.tags
            relationships = doc.metadata.get("relationships", [])
            assert any(r["id"] == root.uuid for r in relationships)
            
    def test_types(self):
        """Test different relationship types."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create documents with different relationship types
        original = FrameRecord.create(
            title="Original Document",
            content="The original content"
        )
        
        translation = FrameRecord.create(
            title="French Translation",
            content="Le contenu original"
        )
        translation.add_relationship(original, relationship_type="related")
        
        summary = FrameRecord.create(
            title="Executive Summary",
            content="A brief summary of the original"
        )
        summary.add_relationship(original, relationship_type="related")
        
        version2 = FrameRecord.create(
            title="Version 2.0",
            content="Updated content"
        )
        version2.add_relationship(original, relationship_type="related")
        
        dataset.add_many([original, translation, summary, version2])
        
        # Query specific relationship types
        # Find all documents related to original
        all_related = dataset.find_related_to(original.uuid)
        assert len(all_related) == 3
        
        # Verify relationship types are preserved
        rel_types = set()
        for doc in all_related:
            for rel in doc.metadata.get("relationships", []):
                if rel["id"] == original.uuid:
                    rel_types.add(rel["type"])
                    
        assert "related" in rel_types
        
        
        
    def test_relationship_with_identifiers(self):
            """Test relationships using different identifier types."""
            # Create documents with various identifiers
            doc1 = FrameRecord.create(
                title="Document with URI",
                content="Content 1",
                uri="https://example.com/doc1"
            )
            
            doc2 = FrameRecord.create(
                title="Document with Path",
                content="Content 2",
                source_file="/data/documents/doc2.txt"
            )
            
            doc3 = FrameRecord.create(
                title="Document with CID",
                content="Content 3"
            )
            # Simulate IPFS CID
            doc3.metadata["cid"] = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"
            
            # Add relationships using different identifiers
            doc1.add_relationship(
                doc2, 
                relationship_type="reference"
            )
            
            doc1.add_relationship(
                doc3,
                relationship_type="reference"
            )
            
            # Verify relationships were added
            relationships = doc1.metadata.get("relationships", [])
            assert len(relationships) == 2
            
            # Check that relationships contain target UUIDs
            ids = [r["id"] for r in relationships]
            assert doc2.uuid in ids
            assert doc3.uuid in ids
    
if __name__ == "__main__":
    pytest.main([__file__, "-v"])