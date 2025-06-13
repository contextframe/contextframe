"""Integration tests for extraction module with ContextFrame data model."""

import json
import tempfile
from pathlib import Path

import pytest

from contextframe import FrameDataset, FrameRecord
from contextframe.extract import (
    BatchExtractor,
    ExtractionResult,
    MarkdownExtractor,
    TextFileExtractor,
)
from contextframe.extract.chunking import split_extraction_results


class TestExtractionToFrameRecord:
    """Test conversion from ExtractionResult to FrameRecord."""
    
    def test_extraction_result_to_frame_record(self):
        """Test that ExtractionResult converts to valid FrameRecord."""
        # Create an extraction result
        result = ExtractionResult(
            content="Test content",
            metadata={
                "title": "Test Document",
                "author": "Test Author",
                "custom_field": "custom_value"
            },
            source="/path/to/file.txt",
            format="text"
        )
        
        # Convert to FrameRecord kwargs
        kwargs = result.to_frame_record_kwargs()
        
        # Create FrameRecord directly from kwargs
        frame = FrameRecord.create(
            record_type="document",
            **kwargs
        )
        
        assert frame.content == "Test content"
        assert frame.title == "Test Document"
        assert frame.metadata.get("author") == "Test Author"
        assert frame.metadata.get("source_type") == "text"
        assert frame.metadata.get("source_file") == "/path/to/file.txt"
        assert frame.metadata.get("custom_metadata", {}).get("custom_field") == "custom_value"
    
    def test_markdown_extraction_to_frame_record(self, tmp_path):
        """Test Markdown extraction creates valid FrameRecord with frontmatter."""
        # Create test markdown file
        md_file = tmp_path / "test.md"
        md_content = """---
title: Integration Test
tags:
  - test
  - integration
date: 2024-01-01
---

# Test Document

This is a test document for integration testing."""
        md_file.write_text(md_content)
        
        # Extract
        extractor = MarkdownExtractor()
        result = extractor.extract(md_file)
        
        # Convert to FrameRecord
        kwargs = result.to_frame_record_kwargs()
        frame = FrameRecord.create(
            record_type="document",
            **kwargs
        )
        
        # Verify
        assert frame.content.strip().startswith("# Test Document")
        assert frame.title == "Integration Test"
        # Tags is a standard field, so it stays at top level
        assert frame.metadata.get("tags") == ["test", "integration"]
        # Date is custom, so it goes to custom_metadata
        custom_meta = frame.metadata.get("custom_metadata", {})
        assert str(custom_meta.get("date")) == "2024-01-01"
        assert frame.metadata.get("source_type") == "markdown"
        assert frame.metadata.get("source_file") == str(md_file)


class TestExtractionToFrameDataset:
    """Test extraction workflow with FrameDataset."""
    
    def test_single_file_extraction_to_dataset(self, tmp_path):
        """Test extracting a single file and adding to dataset."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is test content for dataset integration.")
        
        # Create dataset
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(dataset_path)
        
        # Extract file
        extractor = TextFileExtractor()
        result = extractor.extract(test_file)
        
        # Convert and add to dataset
        kwargs = result.to_frame_record_kwargs()
        frame = FrameRecord.create(
            record_type="document",
            **kwargs
        )
        
        dataset.add(frame)
        
        # Verify the frame was added by checking dataset stats
        assert len(dataset._dataset) == 1
        
        # Verify we can query the dataset
        results = dataset.scanner().to_table()
        assert len(results) == 1
        
        # Check the content directly from the table
        assert results["text_content"][0].as_py() == "This is test content for dataset integration."
        assert results["source_type"][0].as_py() == "text"
    
    def test_batch_extraction_to_dataset(self, tmp_path):
        """Test batch extraction workflow."""
        # Create test files
        files = []
        for i in range(3):
            file = tmp_path / f"doc{i}.txt"
            file.write_text(f"Document {i} content")
            files.append(file)
        
        # Create markdown file
        md_file = tmp_path / "readme.md"
        md_file.write_text("""---
title: Readme
---

# Project Documentation

This is the readme file.""")
        files.append(md_file)
        
        # Create dataset
        dataset_path = tmp_path / "batch_test.lance"
        dataset = FrameDataset.create(dataset_path)
        
        # Batch extract
        batch_extractor = BatchExtractor()
        results = batch_extractor.extract_files(files)
        
        # Convert all to FrameRecords
        frames = []
        for result in results:
            if result.success:
                kwargs = result.to_frame_record_kwargs()
                frame = FrameRecord.create(
                    record_type="document",
                    **kwargs
                )
                frames.append(frame)
        
        # Add to dataset
        dataset.add_many(frames)
        
        # Verify
        assert len(dataset._dataset) == 4
        
        # Query and verify content types
        results = dataset.scanner().to_table()
        source_types = [st.as_py() for st in results["source_type"]]
        
        # Check text files
        text_count = sum(1 for st in source_types if st == "text")
        assert text_count == 3
        
        # Check markdown file
        md_count = sum(1 for st in source_types if st == "markdown")
        assert md_count == 1
        
        # Check title of markdown file
        titles = [t.as_py() for t in results["title"]]
        assert "Readme" in titles
    
    def test_extraction_with_chunking_to_dataset(self, tmp_path):
        """Test extraction with chunking creates valid dataset entries."""
        # Create a longer document
        long_file = tmp_path / "long_doc.txt"
        long_content = " ".join([f"Sentence {i}." for i in range(100)])
        long_file.write_text(long_content)
        
        # Create dataset
        dataset_path = tmp_path / "chunked_test.lance"
        dataset = FrameDataset.create(dataset_path)
        
        # Extract
        extractor = TextFileExtractor()
        result = extractor.extract(long_file)
        
        # Chunk the results (mocking since we don't have semantic-text-splitter installed)
        # In real usage, this would use semantic_splitter
        def mock_splitter(texts, chunk_size=100, chunk_overlap=20):
            chunks = []
            for idx, text in enumerate(texts):
                # Simple character-based chunking for testing
                overlap = chunk_overlap if chunk_overlap is not None else 20
                for i in range(0, len(text), chunk_size - overlap):
                    chunk = text[i:i + chunk_size]
                    if chunk:
                        chunks.append((idx, chunk))
            return chunks
        
        chunked_results = split_extraction_results(
            [result],
            chunk_size=100,
            splitter_fn=mock_splitter
        )
        
        # Convert chunks to FrameRecords
        frames = []
        for chunk_result in chunked_results:
            if chunk_result.success:
                kwargs = chunk_result.to_frame_record_kwargs()
                chunk_idx = kwargs.get('custom_metadata', {}).get('chunk_index', 0)
                # Override title with chunk info
                kwargs['title'] = f"Chunk {chunk_idx}"
                frame = FrameRecord.create(
                    record_type="document",
                    **kwargs
                )
                frames.append(frame)
        
        # Add to dataset
        dataset.add_many(frames)
        
        # Verify
        num_chunks = len(dataset._dataset)
        assert num_chunks > 1  # Should have multiple chunks
        
        # Check chunk metadata directly from table
        results = dataset.scanner().to_table()
        custom_metadata_col = results["custom_metadata"]
        
        # Verify chunk metadata
        for i in range(len(results)):
            custom_meta_list = custom_metadata_col[i].as_py()
            # Convert list of dicts to a single dict
            custom_meta = {item['key']: item['value'] for item in custom_meta_list}
            assert "chunk_index" in custom_meta
            assert "chunk_count" in custom_meta
            assert int(custom_meta["chunk_index"]) == i
            assert int(custom_meta["original_content_length"]) == len(long_content)


class TestExtractionMetadataSchema:
    """Test that extraction metadata follows ContextFrame schema."""
    
    def test_extraction_metadata_types(self, tmp_path):
        """Test that metadata types are compatible with Lance schema."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        # Extract
        extractor = TextFileExtractor()
        result = extractor.extract(test_file)
        
        # Check metadata types from extraction result
        assert isinstance(result.metadata["filename"], str)
        assert isinstance(result.metadata["size"], int)
        assert isinstance(result.metadata["encoding"], str)
        
        # Convert to FrameRecord to ensure compatibility
        kwargs = result.to_frame_record_kwargs()
        frame = FrameRecord.create(
            record_type="document",
            **kwargs
        )
        
        # Should not raise any schema validation errors
        assert frame.metadata is not None
    
    def test_custom_metadata_preserved(self, tmp_path):
        """Test that custom metadata is preserved through the pipeline."""
        # Create JSON file with custom fields
        json_file = tmp_path / "data.json"
        json_data = {
            "title": "Test Data",
            "custom_field": "custom_value",
            "nested": {
                "field": "value"
            },
            "tags": ["tag1", "tag2"]
        }
        json_file.write_text(json.dumps(json_data))
        
        # Extract
        from contextframe.extract import JSONExtractor
        extractor = JSONExtractor()
        result = extractor.extract(json_file)
        
        # The JSON data should be in metadata
        assert result.metadata["json_data"] == json_data
        
        # Create FrameRecord with additional custom metadata
        kwargs = result.to_frame_record_kwargs()
        # Add custom fields directly to kwargs (they'll be moved to custom_metadata)
        kwargs["processing_version"] = "1.0"
        kwargs["department"] = "Engineering"
        
        frame = FrameRecord.create(
            record_type="document",
            **kwargs
        )
        
        # Verify all metadata is preserved
        custom_meta = frame.metadata.get("custom_metadata", {})
        # json_data was converted to JSON string, so parse it back
        assert json.loads(custom_meta.get("json_data")) == json_data
        # Check if the extra fields were added at the top level or custom_metadata
        assert frame.metadata.get("processing_version") == "1.0" or custom_meta.get("processing_version") == "1.0"
        assert frame.metadata.get("department") == "Engineering" or custom_meta.get("department") == "Engineering"


class TestExtractionErrorHandling:
    """Test error handling in extraction to dataset pipeline."""
    
    def test_failed_extraction_handling(self, tmp_path):
        """Test handling of failed extractions in batch processing."""
        # Create mix of valid and invalid files
        valid_file = tmp_path / "valid.txt"
        valid_file.write_text("Valid content")
        
        # Non-existent file
        invalid_file = tmp_path / "nonexistent.txt"
        
        # Create dataset
        dataset_path = tmp_path / "error_test.lance"
        dataset = FrameDataset.create(dataset_path)
        
        # Batch extract with error handling
        batch_extractor = BatchExtractor()
        results = batch_extractor.extract_files(
            [valid_file, invalid_file],
            skip_errors=True
        )
        
        # Process results
        frames = []
        errors = []
        
        for result in results:
            if result.success:
                kwargs = result.to_frame_record_kwargs()
                frame = FrameRecord.create(
                    record_type="document",
                    **kwargs
                )
                frames.append(frame)
            else:
                errors.append(result)
        
        # Add successful extractions to dataset
        if frames:
            dataset.add_many(frames)
        
        # Verify
        assert len(dataset._dataset) == 1  # Only valid file
        assert len(errors) == 1  # One failed extraction
        assert "does not exist" in errors[0].error