#!/usr/bin/env python3
"""
Integration tests for contextframe package - Vector Search Functionality
Tests vector search operations with real embeddings, no mocking.
"""

import os
import shutil
import tempfile
import numpy as np
import pytest

from contextframe import FrameRecord, FrameDataset
from contextframe.schema import RecordType


class TestVectorSearch:
    """Test vector search functionality with real embeddings."""
    
    def setup_method(self):
        """Create a temporary directory and sample embeddings for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.temp_dir, "vector_test.lance")
        self.embed_dim = 1536
        
        # Create some sample embeddings with known similarities
        # Base vectors for different "topics"
        self.topic_tech = np.random.rand(self.embed_dim).astype(np.float32)
        self.topic_science = np.random.rand(self.embed_dim).astype(np.float32)
        self.topic_arts = np.random.rand(self.embed_dim).astype(np.float32)
        
        # Ensure topics are somewhat different
        self.topic_science = self.topic_science + 0.5
        self.topic_arts = self.topic_arts - 0.5
        
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_similar_vector(self, base_vector, noise_level=0.1):
        """Create a vector similar to the base vector with some noise."""
        noise = np.random.randn(self.embed_dim).astype(np.float32) * noise_level
        similar = base_vector + noise
        # Normalize to maintain magnitude
        similar = similar / np.linalg.norm(similar) * np.linalg.norm(base_vector)
        return similar
        
    @pytest.mark.skip(reason="Lance v0.30.0 has a bug with vector search on small datasets - returns empty results")
    def test_knn_search_basic(self):
        """Test basic k-nearest neighbor search."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create documents with embeddings
        tech_docs = []
        for i in range(3):
            record = FrameRecord.create(
                title=f"Tech Document {i}",
                content=f"Technology content {i}",
                tags=["technology"],
                vector=self._create_similar_vector(self.topic_tech, 0.1)
            )
            tech_docs.append(record)
            
        science_docs = []
        for i in range(3):
            record = FrameRecord.create(
                title=f"Science Document {i}",
                content=f"Science content {i}",
                tags=["science"],
                vector=self._create_similar_vector(self.topic_science, 0.1)
            )
            science_docs.append(record)
            
        # Add all documents
        dataset.add_many(tech_docs + science_docs)
        
        # Search for tech-similar documents
        query_vector = self._create_similar_vector(self.topic_tech, 0.05)
        results = dataset.knn_search(query_vector, k=3)
        
        # Verify results
        assert len(results) == 3
        # All top results should be tech documents
        for result in results:
            assert "technology" in result.tags
            assert "Tech Document" in result.title
            
    def test_knn_search_with_filter(self):
        """Test KNN search with SQL filters."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create mixed documents
        records = []
        for i in range(10):
            record = FrameRecord.create(
                title=f"Document {i}",
                content=f"Content {i}",
                status="published" if i < 5 else "draft",
                tags=["tech"] if i % 2 == 0 else ["science"],
                vector=self._create_similar_vector(
                    self.topic_tech if i % 2 == 0 else self.topic_science, 
                    0.1
                )
            )
            records.append(record)
            
        dataset.add_many(records)
        
        # Search only published tech documents
        query_vector = self._create_similar_vector(self.topic_tech, 0.05)
        results = dataset.knn_search(
            query_vector, 
            k=10,  # Request many but filter should limit
            filter="status = 'published' AND array_has_any(tags, ['tech'])"
        )
        
        # Should only get published tech documents (indices 0, 2, 4)
        assert len(results) <= 3
        for result in results:
            assert result.metadata.get("status") == "published"
            assert "tech" in result.tags
            
    def test_full_text_search(self):
        """Test full-text search functionality."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create documents with specific content
        docs = [
            FrameRecord.create(
                title="Introduction to Machine Learning",
                content="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            ),
            FrameRecord.create(
                title="Deep Learning Fundamentals",
                content="Deep learning uses neural networks with multiple layers to learn representations.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            ),
            FrameRecord.create(
                title="Natural Language Processing",
                content="NLP involves teaching machines to understand and generate human language.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            ),
            FrameRecord.create(
                title="Computer Vision Basics",
                content="Computer vision enables machines to interpret and understand visual information.",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            )
        ]
        
        dataset.add_many(docs)
        
        # Create full-text search index
        dataset.create_fts_index()
        
        # Search for "machine learning"
        results = dataset.full_text_search("machine learning", k=2)
        
        assert len(results) > 0
        # First result should contain "machine learning"
        first_result = results[0]
        assert "machine" in first_result.content.lower() or "machine" in first_result.title.lower()
        
    def test_vector_search_with_collections(self):
        """Test vector search within specific collections."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create documents in different collections
        project_a_docs = []
        project_b_docs = []
        
        for i in range(3):
            doc_a = FrameRecord.create(
                title=f"Project A - Doc {i}",
                content=f"Content for project A document {i}",
                collection="project_a",
                vector=self._create_similar_vector(self.topic_tech, 0.1)
            )
            project_a_docs.append(doc_a)
            
            doc_b = FrameRecord.create(
                title=f"Project B - Doc {i}",
                content=f"Content for project B document {i}",
                collection="project_b",
                vector=self._create_similar_vector(self.topic_science, 0.1)
            )
            project_b_docs.append(doc_b)
            
        dataset.add_many(project_a_docs + project_b_docs)
        
        # Search within project_a collection only
        query_vector = self._create_similar_vector(self.topic_tech, 0.05)
        results = dataset.knn_search(
            query_vector,
            k=10,
            filter="collection = 'project_a'"
        )
        
        assert len(results) == 3  # Only 3 docs in project_a
        for result in results:
            assert result.metadata.get("collection") == "project_a"
            assert "Project A" in result.title
            
    @pytest.mark.skip(reason="Lance v0.30.0 has a bug with vector search on small datasets - returns empty results")
    def test_search_result_scores(self):
        """Test that search results include similarity scores."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create a reference document
        reference_vector = np.random.rand(self.embed_dim).astype(np.float32)
        reference_doc = FrameRecord.create(
            title="Reference Document",
            content="This is the reference",
            vector=reference_vector
        )
        
        # Create similar and dissimilar documents
        very_similar = FrameRecord.create(
            title="Very Similar",
            content="Almost identical",
            vector=self._create_similar_vector(reference_vector, 0.01)
        )
        
        somewhat_similar = FrameRecord.create(
            title="Somewhat Similar",
            content="Partially related",
            vector=self._create_similar_vector(reference_vector, 0.3)
        )
        
        different = FrameRecord.create(
            title="Different Document",
            content="Completely different topic",
            vector=np.random.rand(self.embed_dim).astype(np.float32) * 10  # Very different
        )
        
        dataset.add_many([reference_doc, very_similar, somewhat_similar, different])
        
        # Search with the reference vector
        results = dataset.knn_search(reference_vector, k=4)
        
        assert len(results) == 4
        
        # Results should be ordered by similarity
        # First should be the reference itself (or very similar)
        assert results[0].title in ["Reference Document", "Very Similar"]
        
        # Scores should be present in metadata
        for result in results:
            assert "_distance" in result.metadata or "_score" in result.metadata
            
    @pytest.mark.skip(reason="Lance v0.30.0 has a bug with vector search on small datasets - returns empty results")
    def test_empty_vector_handling(self):
        """Test searching when some documents have no vectors."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create documents with and without vectors
        with_vector = FrameRecord.create(
            title="Has Vector",
            content="This document has an embedding",
            vector=np.random.rand(self.embed_dim).astype(np.float32)
        )
        
        without_vector = FrameRecord.create(
            title="No Vector",
            content="This document has no embedding"
            # No vector provided
        )
        
        dataset.add_many([with_vector, without_vector])
        
        # Vector search should only return documents with vectors
        query_vector = np.random.rand(self.embed_dim).astype(np.float32)
        results = dataset.knn_search(query_vector, k=10)
        
        # Should only get the document with vector
        assert len(results) == 1
        assert results[0].title == "Has Vector"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])