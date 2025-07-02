#!/usr/bin/env python3
"""
Integration tests for contextframe package - Collection Functionality
Tests document collections and collection headers.
"""

import os
import shutil
import tempfile
import numpy as np
import pytest

from contextframe import FrameRecord, FrameDataset
from contextframe.schema import RecordType


class TestCollections:
    """Test collection management functionality."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.temp_dir, "collections_test.lance")
        self.embed_dim = 1536
        
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_create_collection_header(self):
        """Test creating a collection header document."""
        header = FrameRecord.create(
            title="API Documentation Collection",
            content="This collection contains all API documentation for our project",
            record_type=RecordType.COLLECTION_HEADER,
            collection="api_docs",
            tags=["documentation", "api", "collection"],
            custom_metadata={
                "version": "1.0",
                "last_updated": "2024-01-01"
            }
        )
        
        assert header.metadata.get("record_type") == RecordType.COLLECTION_HEADER
        assert header.metadata["collection"] == "api_docs"
        assert "documentation" in header.tags
        assert header.metadata["custom_metadata"]["version"] == "1.0"
        
    def test_create_collection_with_members(self):
        """Test creating a collection with member documents."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create collection header
        header = FrameRecord.create(
            title="Python Tutorial Collection",
            content="A comprehensive Python tutorial series",
            record_type=RecordType.COLLECTION_HEADER,
            collection="python_tutorial",
            tags=["tutorial", "python"]
        )
        
        # Create member documents with positions
        members = []
        topics = [
            ("Introduction to Python", "Basic syntax and setup"),
            ("Variables and Data Types", "Understanding Python data types"),
            ("Control Flow", "If statements and loops"),
            ("Functions", "Defining and using functions"),
            ("Classes and Objects", "Object-oriented programming")
        ]
        
        for i, (title, content) in enumerate(topics):
            member = FrameRecord.create(
                title=title,
                content=content,
                collection="python_tutorial",
                position=i,
                tags=["tutorial", "python", f"chapter_{i+1}"]
            )
            member.add_relationship(header, relationship_type="member_of")
            members.append(member)
            
        # Add all to dataset
        dataset.add(header)
        dataset.add_many(members)
        
        # Retrieve collection header
        retrieved_header = dataset.get_collection_header("python_tutorial")
        assert retrieved_header is not None
        assert retrieved_header.title == "Python Tutorial Collection"
        
        # Get collection members
        collection_members = dataset.get_collection_members("python_tutorial")
        assert len(collection_members) == 5  # All tutorial chapters
        
        # Verify members are ordered by position
        positions = [m.metadata.get("position", -1) for m in collection_members]
        assert positions == [0, 1, 2, 3, 4]
        
    def test_multiple_collections(self):
        """Test managing multiple collections in same dataset."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create multiple collections
        collections = [
            ("frontend_docs", "Frontend Documentation", ["react", "vue", "angular"]),
            ("backend_docs", "Backend Documentation", ["django", "flask", "fastapi"]),
            ("devops_docs", "DevOps Documentation", ["docker", "kubernetes", "ci/cd"])
        ]
        
        for coll_name, coll_title, topics in collections:
            # Create header
            header = FrameRecord.create(
                title=coll_title,
                content=f"Documentation for {coll_title}",
                record_type=RecordType.COLLECTION_HEADER,
                collection=coll_name
            )
            dataset.add(header)
            
            # Create members
            for i, topic in enumerate(topics):
                member = FrameRecord.create(
                    title=f"{topic.title()} Guide",
                    content=f"Guide for {topic}",
                    collection=coll_name,
                    position=i,
                    tags=[topic, coll_name]
                )
                dataset.add(member)
                
        # Verify we can retrieve each collection separately
        frontend_members = dataset.get_collection_members("frontend_docs")
        assert len(frontend_members) == 3
        assert all("frontend_docs" in m.tags for m in frontend_members)
        
        backend_members = dataset.get_collection_members("backend_docs")
        assert len(backend_members) == 3
        assert all("backend_docs" in m.tags for m in backend_members)
        
        devops_members = dataset.get_collection_members("devops_docs")
        assert len(devops_members) == 3
        assert all("devops_docs" in m.tags for m in devops_members)
        
    def test_collection_with_subcollections(self):
        """Test nested collection structure."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create main collection
        main_header = FrameRecord.create(
            title="Complete Documentation",
            content="All project documentation",
            record_type=RecordType.COLLECTION_HEADER,
            collection="main_docs"
        )
        
        # Create sub-collections
        api_header = FrameRecord.create(
            title="API Documentation",
            content="API reference and guides",
            record_type=RecordType.COLLECTION_HEADER,
            collection="api_docs",
            custom_metadata={"parent_collection": "main_docs"}
        )
        api_header.add_relationship(main_header, relationship_type="member_of")
        
        user_header = FrameRecord.create(
            title="User Guide",
            content="End user documentation",
            record_type=RecordType.COLLECTION_HEADER,
            collection="user_docs",
            custom_metadata={"parent_collection": "main_docs"}
        )
        user_header.add_relationship(main_header, relationship_type="member_of")
        
        # Add some documents to sub-collections
        api_endpoint = FrameRecord.create(
            title="REST API Endpoints",
            content="List of all API endpoints",
            collection="api_docs"
        )
        
        user_tutorial = FrameRecord.create(
            title="Getting Started",
            content="How to get started with our app",
            collection="user_docs"
        )
        
        dataset.add_many([main_header, api_header, user_header, api_endpoint, user_tutorial])
        
        # Find sub-collections of main collection
        # Since custom_metadata is a list of key-value structs, we can't use dot notation
        # Instead, we'll use a different approach
        all_headers = dataset.scanner(
            filter=f"record_type = '{RecordType.COLLECTION_HEADER}'"
        ).to_table().to_pandas()
        
        # Filter in Python for headers with parent_collection = 'main_docs'
        sub_collections = []
        for _, row in all_headers.iterrows():
            custom_md = row.get('custom_metadata', [])
            if hasattr(custom_md, '__len__') and len(custom_md) > 0:
                for item in custom_md:
                    if item.get('key') == 'parent_collection' and item.get('value') == 'main_docs':
                        sub_collections.append(row)
                        break
        
        assert len(sub_collections) == 2
        
    def test_collection_search(self):
        """Test searching within a specific collection."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create a technical docs collection
        tech_header = FrameRecord.create(
            title="Technical Documentation",
            content="All technical docs",
            record_type=RecordType.COLLECTION_HEADER,
            collection="tech_docs"
        )
        
        # Create documents with embeddings
        base_vector = np.random.rand(self.embed_dim).astype(np.float32)
        
        tech_docs = []
        for i in range(5):
            doc = FrameRecord.create(
                title=f"Technical Document {i}",
                content=f"Technical content about component {i}",
                collection="tech_docs",
                position=i,
                vector=base_vector + np.random.randn(self.embed_dim).astype(np.float32) * 0.1
            )
            tech_docs.append(doc)
            
        # Create some non-collection documents
        other_docs = []
        for i in range(3):
            doc = FrameRecord.create(
                title=f"Other Document {i}",
                content=f"Non-technical content {i}",
                vector=np.random.rand(self.embed_dim).astype(np.float32)
            )
            other_docs.append(doc)
            
        dataset.add(tech_header)
        dataset.add_many(tech_docs + other_docs)
        
        # Search only within the tech_docs collection (excluding headers)
        query_vector = base_vector + np.random.randn(self.embed_dim).astype(np.float32) * 0.05
        # First, let's try just the collection filter
        results = dataset.knn_search(
            query_vector,
            k=10,
            filter="collection = 'tech_docs'"
        )
        
        # Should get tech docs and the header (6 total)
        assert len(results) == 6
        for result in results:
            assert result.metadata.get("collection") == "tech_docs"
            
    def test_collection_metadata_aggregation(self):
        """Test aggregating metadata across collection members."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create a research papers collection
        papers_header = FrameRecord.create(
            title="Research Papers 2024",
            content="Collection of research papers",
            record_type=RecordType.COLLECTION_HEADER,
            collection="research_2024"
        )
        
        # Create papers with metadata
        papers = []
        authors = ["Smith et al.", "Jones et al.", "Brown et al."]
        topics = ["machine learning", "natural language processing", "computer vision"]
        
        for i, (author, topic) in enumerate(zip(authors, topics)):
            paper = FrameRecord.create(
                title=f"Paper: {topic.title()}",
                content=f"Research on {topic}",
                collection="research_2024",
                position=i,
                author=author,
                tags=["research", topic.replace(" ", "_")],
                custom_metadata={
                    "citations": str(10 + i * 5),
                    "year": "2024",
                    "conference": "ICML" if i == 0 else "NeurIPS"
                }
            )
            papers.append(paper)
            
        dataset.add(papers_header)
        dataset.add_many(papers)
        
        # Get all papers in collection
        collection_papers = dataset.get_collection_members("research_2024")
        
        # Aggregate statistics
        total_citations = sum(
            int(p.metadata.get("custom_metadata", {}).get("citations", "0"))
            for p in collection_papers
        )
        assert total_citations == 10 + 15 + 20  # 45
        
        # Get unique authors
        authors_set = set(p.author for p in collection_papers if p.author)
        assert len(authors_set) == 3
        
        # Get all topics
        all_topics = set()
        for paper in collection_papers:
            all_topics.update(paper.tags)
        assert "machine_learning" in all_topics
        assert "natural_language_processing" in all_topics
        
    def test_collection_versioning(self):
        """Test versioning documents within collections."""
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        # Create a versioned documentation collection
        docs_header = FrameRecord.create(
            title="API Docs v2.0",
            content="Version 2.0 of our API documentation",
            record_type=RecordType.COLLECTION_HEADER,
            collection="api_v2",
            custom_metadata={"version": "2.0", "release_date": "2024-01-15"}
        )
        
        # Create versioned documents
        endpoints = ["users", "products", "orders"]
        
        for endpoint in endpoints:
            # Current version
            current = FrameRecord.create(
                title=f"/{endpoint} Endpoint",
                content=f"Documentation for {endpoint} API",
                collection="api_v2",
                tags=[endpoint, "v2.0", "current"],
                custom_metadata={"endpoint": endpoint, "version": "2.0"}
            )
            
            # Previous version reference
            previous = FrameRecord.create(
                title=f"/{endpoint} Endpoint (v1.0)",
                content=f"Legacy documentation for {endpoint} API",
                collection="api_v1_archive",
                tags=[endpoint, "v1.0", "deprecated"],
                custom_metadata={"endpoint": endpoint, "version": "1.0"}
            )
            
            # Link versions
            current.add_relationship(previous, relationship_type="reference")
            
            dataset.add_many([current, previous])
            
        dataset.add(docs_header)
        
        # Get current version docs
        current_docs = dataset.scanner(
            filter="collection = 'api_v2' AND array_has_any(tags, ['current'])"
        ).to_table().to_pandas()
        
        assert len(current_docs) == 3
        
        # Get deprecated docs
        deprecated_docs = dataset.scanner(
            filter="array_has_any(tags, ['deprecated'])"
        ).to_table().to_pandas()
        
        assert len(deprecated_docs) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])