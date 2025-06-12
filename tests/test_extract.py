"""Tests for the extraction module."""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from contextframe.extract import (
    BatchExtractor,
    CSVExtractor,
    ExtractionResult,
    JSONExtractor,
    MarkdownExtractor,
    TextExtractor,
    TextFileExtractor,
    YAMLExtractor,
)
from contextframe.extract.base import ExtractorRegistry
from contextframe.extract.chunking import split_extraction_results


class TestExtractionResult:
    """Test the ExtractionResult dataclass."""
    
    def test_success_property(self):
        """Test the success property."""
        # Successful extraction
        result = ExtractionResult(content="test content")
        assert result.success is True
        
        # Failed extraction with error
        result = ExtractionResult(content="", error="Failed to extract")
        assert result.success is False
        
        # Empty content without error
        result = ExtractionResult(content="")
        assert result.success is False
    
    def test_to_frame_record_kwargs(self):
        """Test conversion to FrameRecord kwargs."""
        result = ExtractionResult(
            content="test content",
            metadata={"key": "value", "title": "Test Title"},
            source="/path/to/file.txt",
            format="text"
        )
        
        kwargs = result.to_frame_record_kwargs()
        
        assert kwargs["content"] == "test content"
        assert kwargs["title"] == "Test Title"
        assert kwargs.get("source_file") == "/path/to/file.txt"
        assert kwargs.get("source_type") == "text"
        # Custom field should be in custom_metadata
        assert kwargs.get("custom_metadata", {}).get("key") == "value"


class TestTextFileExtractor:
    """Test the TextFileExtractor."""
    
    def test_can_extract(self, tmp_path):
        """Test file type detection."""
        extractor = TextFileExtractor()
        
        # Should handle .txt files
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        assert extractor.can_extract(txt_file) is True
        
        # Should handle .log files
        log_file = tmp_path / "test.log"
        log_file.touch()
        assert extractor.can_extract(log_file) is True
        
        # Should not handle other files
        other_file = tmp_path / "test.pdf"
        other_file.touch()
        assert extractor.can_extract(other_file) is False
    
    def test_extract(self, tmp_path):
        """Test content extraction."""
        extractor = TextFileExtractor()
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "This is a test file.\nWith multiple lines."
        test_file.write_text(test_content)
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert result.content == test_content
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["size"] == len(test_content)
        assert result.metadata["encoding"] == "utf-8"
        assert result.format == "text"
    
    def test_extract_nonexistent_file(self):
        """Test extraction of non-existent file."""
        extractor = TextFileExtractor()
        
        result = extractor.extract("/nonexistent/file.txt")
        
        assert result.success is False
        assert "does not exist" in result.error


class TestMarkdownExtractor:
    """Test the MarkdownExtractor."""
    
    def test_can_extract(self, tmp_path):
        """Test file type detection."""
        extractor = MarkdownExtractor()
        
        # Should handle various markdown extensions
        for ext in [".md", ".markdown", ".mdown", ".mkd"]:
            md_file = tmp_path / f"test{ext}"
            md_file.touch()
            assert extractor.can_extract(md_file) is True
    
    def test_extract_without_frontmatter(self, tmp_path):
        """Test extraction of markdown without frontmatter."""
        extractor = MarkdownExtractor()
        
        test_file = tmp_path / "test.md"
        test_content = "# Title\n\nThis is markdown content."
        test_file.write_text(test_content)
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert result.content == test_content
        assert result.format == "markdown"
    
    def test_extract_with_frontmatter(self, tmp_path):
        """Test extraction of markdown with YAML frontmatter."""
        extractor = MarkdownExtractor()
        
        test_file = tmp_path / "test.md"
        frontmatter_content = """---
title: Test Document
author: Test Author
tags:
  - test
  - document
---

# Title

This is the markdown content."""
        test_file.write_text(frontmatter_content)
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert result.content.strip() == "# Title\n\nThis is the markdown content."
        assert result.metadata["title"] == "Test Document"
        assert result.metadata["author"] == "Test Author"
        assert result.metadata["tags"] == ["test", "document"]
    
    def test_extract_with_invalid_frontmatter(self, tmp_path):
        """Test extraction with invalid YAML frontmatter."""
        extractor = MarkdownExtractor()
        
        test_file = tmp_path / "test.md"
        content = """---
invalid: yaml: content
---

# Title"""
        test_file.write_text(content)
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert len(result.warnings) > 0
        assert "Failed to parse frontmatter" in result.warnings[0]
    
    def test_extract_from_string(self):
        """Test extraction from string content."""
        extractor = MarkdownExtractor()
        
        content = """---
title: String Test
---

Content from string"""
        
        result = extractor.extract_from_string(content)
        
        assert result.success is True
        assert result.content.strip() == "Content from string"
        assert result.metadata["title"] == "String Test"


class TestJSONExtractor:
    """Test the JSONExtractor."""
    
    def test_extract_json(self, tmp_path):
        """Test extraction of regular JSON file."""
        extractor = JSONExtractor()
        
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "nested": {"field": "content"}}
        test_file.write_text(json.dumps(test_data, indent=2))
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert json.loads(result.content) == test_data
        assert result.metadata["json_data"] == test_data
        assert result.format == "json"
    
    def test_extract_jsonl(self, tmp_path):
        """Test extraction of JSON Lines file."""
        extractor = JSONExtractor()
        
        test_file = tmp_path / "test.jsonl"
        lines = [
            {"id": 1, "text": "First line"},
            {"id": 2, "text": "Second line"},
        ]
        test_file.write_text("\n".join(json.dumps(line) for line in lines))
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert result.metadata["json_data"] == lines
    
    def test_extract_text_fields(self, tmp_path):
        """Test extraction of specific text fields."""
        extractor = JSONExtractor()
        
        test_file = tmp_path / "test.json"
        test_data = {
            "title": "Test Title",
            "description": "Test Description",
            "metadata": {"author": "Test Author"},
            "content": "Main content here"
        }
        test_file.write_text(json.dumps(test_data))
        
        result = extractor.extract(test_file, extract_text_fields=["title", "content"])
        
        assert result.success is True
        assert "Test Title" in result.content
        assert "Main content here" in result.content
        assert "Test Description" not in result.content
    
    def test_extract_invalid_json(self, tmp_path):
        """Test extraction of invalid JSON."""
        extractor = JSONExtractor()
        
        test_file = tmp_path / "test.json"
        test_file.write_text("{invalid json}")
        
        result = extractor.extract(test_file)
        
        assert result.success is False
        assert "Invalid JSON" in result.error


class TestYAMLExtractor:
    """Test the YAMLExtractor."""
    
    def test_extract_yaml(self, tmp_path):
        """Test extraction of YAML file."""
        extractor = YAMLExtractor()
        
        test_file = tmp_path / "test.yaml"
        test_data = {
            "key": "value",
            "list": ["item1", "item2"],
            "nested": {"field": "content"}
        }
        test_file.write_text(yaml.dump(test_data))
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert result.metadata["yaml_data"] == test_data
        assert result.format == "yaml"


class TestCSVExtractor:
    """Test the CSVExtractor."""
    
    def test_extract_csv(self, tmp_path):
        """Test extraction of CSV file."""
        extractor = CSVExtractor()
        
        test_file = tmp_path / "test.csv"
        rows = [
            ["Name", "Age", "City"],
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
        ]
        
        with open(test_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        result = extractor.extract(test_file)
        
        assert result.success is True
        assert "Alice, 30, New York" in result.content
        assert "Bob, 25, London" in result.content
        assert result.metadata["headers"] == ["Name", "Age", "City"]
        assert result.metadata["row_count"] == 3
        assert result.metadata["csv_data"] == rows
    
    def test_extract_specific_columns(self, tmp_path):
        """Test extraction of specific columns."""
        extractor = CSVExtractor()
        
        test_file = tmp_path / "test.csv"
        rows = [
            ["Name", "Age", "City", "Email"],
            ["Alice", "30", "New York", "alice@example.com"],
            ["Bob", "25", "London", "bob@example.com"],
        ]
        
        with open(test_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        # Extract by column names
        result = extractor.extract(test_file, text_columns=["Name", "City"])
        
        assert result.success is True
        assert "Alice, New York" in result.content
        assert "30" not in result.content
        assert "alice@example.com" not in result.content
        
        # Extract by column indices
        result = extractor.extract(test_file, text_columns=[0, 2])
        
        assert result.success is True
        assert "Alice, New York" in result.content


class TestExtractorRegistry:
    """Test the ExtractorRegistry."""
    
    def test_registry_operations(self):
        """Test registry registration and lookup."""
        registry = ExtractorRegistry()
        
        # Create a mock extractor
        mock_extractor = Mock(spec=TextExtractor)
        mock_extractor.can_extract.return_value = True
        mock_extractor.format_name = "test"
        mock_extractor.supported_extensions = [".test"]
        
        # Register extractor
        registry.register(mock_extractor)
        
        # Find extractor
        found = registry.find_extractor("test.test")
        assert found == mock_extractor
        
        # Get supported formats
        formats = registry.get_supported_formats()
        assert "test" in formats
        assert formats["test"] == [".test"]


class TestBatchExtractor:
    """Test the BatchExtractor."""
    
    def test_extract_files(self, tmp_path):
        """Test batch extraction of multiple files."""
        # Create test files
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.txt"
            file.write_text(f"Content {i}")
            files.append(file)
        
        batch = BatchExtractor()
        results = batch.extract_files(files)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.success is True
            assert result.content == f"Content {i}"
    
    def test_extract_directory(self, tmp_path):
        """Test extraction of all files in directory."""
        # Create test files
        (tmp_path / "file1.txt").write_text("Text 1")
        (tmp_path / "file2.md").write_text("# Markdown")
        (tmp_path / "data.json").write_text('{"key": "value"}')
        
        batch = BatchExtractor()
        results = batch.extract_directory(tmp_path)
        
        assert len(results) == 3
        
        # Check that different extractors were used
        formats = {r.format for r in results if r.success}
        assert "text" in formats
        assert "markdown" in formats
        assert "json" in formats
    
    def test_progress_callback(self, tmp_path):
        """Test progress callback functionality."""
        # Create test files
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.txt"
            file.write_text(f"Content {i}")
            files.append(file)
        
        # Track progress
        progress_calls = []
        
        def progress_callback(current, total, file_path):
            progress_calls.append((current, total, file_path))
        
        batch = BatchExtractor(progress_callback=progress_callback)
        batch.extract_files(files)
        
        assert len(progress_calls) == 3
        assert all(call[1] == 3 for call in progress_calls)  # Total is 3
        assert progress_calls[-1][0] == 3  # Last call shows 3/3
    
    @pytest.mark.asyncio
    async def test_extract_files_async(self, tmp_path):
        """Test async batch extraction."""
        # Create test files
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.txt"
            file.write_text(f"Content {i}")
            files.append(file)
        
        batch = BatchExtractor()
        results = await batch.extract_files_async(files)
        
        assert len(results) == 3
        for result in results:
            assert result.success is True


class TestChunking:
    """Test chunking functionality."""
    
    @patch("contextframe.extract.chunking.llama_index_splitter")
    def test_split_extraction_results(self, mock_splitter):
        """Test splitting of extraction results."""
        # Mock the splitter to return predictable chunks
        mock_splitter.return_value = [
            (0, "Chunk 1 from doc 1"),
            (0, "Chunk 2 from doc 1"),
            (1, "Chunk 1 from doc 2"),
        ]
        
        # Create test results
        results = [
            ExtractionResult(
                content="Long content 1",
                metadata={"doc": 1},
                source="file1.txt"
            ),
            ExtractionResult(
                content="Long content 2",
                metadata={"doc": 2},
                source="file2.txt"
            ),
        ]
        
        chunked = split_extraction_results(results, chunk_size=100)
        
        # Should have 3 chunks total
        assert len(chunked) == 3
        
        # Check metadata preservation and chunk info
        chunk1 = chunked[0]
        assert chunk1.metadata["doc"] == 1
        assert chunk1.metadata["chunk_index"] == 0
        assert chunk1.metadata["chunk_count"] == 2
        assert chunk1.content == "Chunk 1 from doc 1"
        
        chunk3 = chunked[2]
        assert chunk3.metadata["doc"] == 2
        assert chunk3.metadata["chunk_index"] == 0
        assert chunk3.metadata["chunk_count"] == 1