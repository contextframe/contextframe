"""Extractor implementations for various text-based formats."""

import csv
import io
import json
import re
import yaml
from .base import ExtractionResult, TextExtractor, registry
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class TextFileExtractor(TextExtractor):
    """Extractor for plain text files."""
    
    def __init__(self):
        """Initialize the text file extractor."""
        super().__init__()
        self.supported_extensions = [".txt", ".text", ".log"]
        self.format_name = "text"
    
    def can_extract(self, source: str | Path) -> bool:
        """Check if this is a plain text file."""
        try:
            path = Path(source)
            return path.suffix.lower() in self.supported_extensions
        except Exception:
            return False
    
    def extract(
        self, 
        source: str | Path, 
        encoding: str = "utf-8",
        **kwargs
    ) -> ExtractionResult:
        """Extract content from a plain text file."""
        try:
            path = self.validate_source(source)
            
            with open(path, encoding=encoding) as f:
                content = f.read()
            
            metadata = {
                "filename": path.name,
                "size": path.stat().st_size,
                "encoding": encoding,
            }
            
            return ExtractionResult(
                content=content,
                metadata=metadata,
                source=path,
                format=self.format_name
            )
            
        except Exception as e:
            return ExtractionResult(
                content="",
                error=f"Failed to extract text file: {str(e)}",
                source=source,
                format=self.format_name
            )


class MarkdownExtractor(TextExtractor):
    """Extractor for Markdown files with frontmatter support."""
    
    def __init__(self):
        """Initialize the markdown extractor."""
        super().__init__()
        self.supported_extensions = [".md", ".markdown", ".mdown", ".mkd"]
        self.format_name = "markdown"
        # Pattern to match YAML frontmatter
        self.frontmatter_pattern = re.compile(
            r"^---\s*\n(.*?)\n---\s*\n",
            re.DOTALL | re.MULTILINE
        )
    
    def can_extract(self, source: str | Path) -> bool:
        """Check if this is a markdown file."""
        try:
            path = Path(source)
            return path.suffix.lower() in self.supported_extensions
        except Exception:
            return False
    
    def extract(
        self, 
        source: str | Path, 
        encoding: str = "utf-8",
        extract_frontmatter: bool = True,
        **kwargs
    ) -> ExtractionResult:
        """Extract content and frontmatter from a markdown file."""
        try:
            path = self.validate_source(source)
            
            with open(path, encoding=encoding) as f:
                raw_content = f.read()
            
            metadata = {
                "filename": path.name,
                "size": path.stat().st_size,
                "encoding": encoding,
            }
            
            content = raw_content
            
            # Extract frontmatter if present and requested
            if extract_frontmatter:
                match = self.frontmatter_pattern.match(raw_content)
                if match:
                    frontmatter_text = match.group(1)
                    try:
                        frontmatter_data = yaml.safe_load(frontmatter_text) or {}
                        metadata.update(frontmatter_data)
                        # Remove frontmatter from content
                        content = raw_content[match.end():]
                    except yaml.YAMLError as e:
                        # Add warning but continue
                        warnings = [f"Failed to parse frontmatter: {str(e)}"]
                        return ExtractionResult(
                            content=content,
                            metadata=metadata,
                            source=path,
                            format=self.format_name,
                            warnings=warnings
                        )
            
            return ExtractionResult(
                content=content.strip(),
                metadata=metadata,
                source=path,
                format=self.format_name
            )
            
        except Exception as e:
            return ExtractionResult(
                content="",
                error=f"Failed to extract markdown file: {str(e)}",
                source=source,
                format=self.format_name
            )
    
    def extract_from_string(
        self, 
        content: str,
        source: str | Path | None = None,
        extract_frontmatter: bool = True,
        **kwargs
    ) -> ExtractionResult:
        """Extract from markdown string content."""
        metadata = {}
        warnings = []
        
        # Extract frontmatter if requested
        if extract_frontmatter:
            match = self.frontmatter_pattern.match(content)
            if match:
                frontmatter_text = match.group(1)
                try:
                    frontmatter_data = yaml.safe_load(frontmatter_text) or {}
                    metadata.update(frontmatter_data)
                    # Remove frontmatter from content
                    content = content[match.end():]
                except yaml.YAMLError as e:
                    warnings.append(f"Failed to parse frontmatter: {str(e)}")
        
        return ExtractionResult(
            content=content.strip(),
            metadata=metadata,
            source=source,
            format=self.format_name,
            warnings=warnings
        )


class JSONExtractor(TextExtractor):
    """Extractor for JSON and JSONL files."""
    
    def __init__(self):
        """Initialize the JSON extractor."""
        super().__init__()
        self.supported_extensions = [".json", ".jsonl", ".ndjson"]
        self.format_name = "json"
    
    def can_extract(self, source: str | Path) -> bool:
        """Check if this is a JSON file."""
        try:
            path = Path(source)
            return path.suffix.lower() in self.supported_extensions
        except Exception:
            return False
    
    def extract(
        self, 
        source: str | Path, 
        encoding: str = "utf-8",
        extract_text_fields: list[str] | None = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content from JSON files.
        
        Args:
            source: File path
            encoding: Text encoding
            extract_text_fields: List of field names to extract text from.
                                If None, returns pretty-printed JSON.
        """
        try:
            path = self.validate_source(source)
            
            with open(path, encoding=encoding) as f:
                if path.suffix.lower() in [".jsonl", ".ndjson"]:
                    # Handle JSON Lines format
                    lines = []
                    data = []
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data.append(json.loads(line))
                            lines.append(line)
                        except json.JSONDecodeError as e:
                            return ExtractionResult(
                                content="",
                                error=f"Invalid JSON on line {line_num}: {str(e)}",
                                source=path,
                                format=self.format_name
                            )
                else:
                    # Regular JSON file
                    content = f.read()
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        return ExtractionResult(
                            content="",
                            error=f"Invalid JSON: {str(e)}",
                            source=path,
                            format=self.format_name
                        )
            
            metadata = {
                "filename": path.name,
                "size": path.stat().st_size,
                "encoding": encoding,
            }
            
            # Extract text content
            if extract_text_fields:
                extracted_texts = []
                
                def extract_fields(obj, fields):
                    """Recursively extract text from specified fields."""
                    if isinstance(obj, dict):
                        for field in fields:
                            if field in obj and isinstance(obj[field], str):
                                extracted_texts.append(obj[field])
                        for value in obj.values():
                            extract_fields(value, fields)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_fields(item, fields)
                
                extract_fields(data, extract_text_fields)
                content = "\n\n".join(extracted_texts)
            else:
                # Pretty-print the JSON as content
                content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Store the structured data in metadata
            metadata["json_data"] = data
            
            return ExtractionResult(
                content=content,
                metadata=metadata,
                source=path,
                format=self.format_name
            )
            
        except Exception as e:
            return ExtractionResult(
                content="",
                error=f"Failed to extract JSON file: {str(e)}",
                source=source,
                format=self.format_name
            )


class YAMLExtractor(TextExtractor):
    """Extractor for YAML files."""
    
    def __init__(self):
        """Initialize the YAML extractor."""
        super().__init__()
        self.supported_extensions = [".yaml", ".yml"]
        self.format_name = "yaml"
    
    def can_extract(self, source: str | Path) -> bool:
        """Check if this is a YAML file."""
        try:
            path = Path(source)
            return path.suffix.lower() in self.supported_extensions
        except Exception:
            return False
    
    def extract(
        self, 
        source: str | Path, 
        encoding: str = "utf-8",
        extract_text_fields: list[str] | None = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content from YAML files."""
        try:
            path = self.validate_source(source)
            
            with open(path, encoding=encoding) as f:
                content = f.read()
                try:
                    data = yaml.safe_load(content)
                except yaml.YAMLError as e:
                    return ExtractionResult(
                        content="",
                        error=f"Invalid YAML: {str(e)}",
                        source=path,
                        format=self.format_name
                    )
            
            metadata = {
                "filename": path.name,
                "size": path.stat().st_size,
                "encoding": encoding,
            }
            
            # Extract text content
            if extract_text_fields and isinstance(data, dict):
                extracted_texts = []
                
                def extract_fields(obj, fields):
                    """Recursively extract text from specified fields."""
                    if isinstance(obj, dict):
                        for field in fields:
                            if field in obj and isinstance(obj[field], str):
                                extracted_texts.append(obj[field])
                        for value in obj.values():
                            extract_fields(value, fields)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_fields(item, fields)
                
                extract_fields(data, extract_text_fields)
                content = "\n\n".join(extracted_texts)
            else:
                # Use original YAML content
                pass
            
            # Store the structured data in metadata
            metadata["yaml_data"] = data
            
            return ExtractionResult(
                content=content,
                metadata=metadata,
                source=path,
                format=self.format_name
            )
            
        except Exception as e:
            return ExtractionResult(
                content="",
                error=f"Failed to extract YAML file: {str(e)}",
                source=source,
                format=self.format_name
            )


class CSVExtractor(TextExtractor):
    """Extractor for CSV/TSV files."""
    
    def __init__(self):
        """Initialize the CSV extractor."""
        super().__init__()
        self.supported_extensions = [".csv", ".tsv"]
        self.format_name = "csv"
    
    def can_extract(self, source: str | Path) -> bool:
        """Check if this is a CSV/TSV file."""
        try:
            path = Path(source)
            return path.suffix.lower() in self.supported_extensions
        except Exception:
            return False
    
    def extract(
        self, 
        source: str | Path, 
        encoding: str = "utf-8",
        text_columns: list[str | int] | None = None,
        include_headers: bool = True,
        **kwargs
    ) -> ExtractionResult:
        """Extract content from CSV/TSV files.
        
        Args:
            source: File path
            encoding: Text encoding
            text_columns: Column names or indices to extract. If None, extracts all.
            include_headers: Whether to include column headers in output
        """
        try:
            path = self.validate_source(source)
            
            # Determine delimiter
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
            
            rows = []
            headers = []
            
            with open(path, encoding=encoding, newline="") as f:
                # Try to detect dialect
                sample = f.read(8192)
                f.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except csv.Error:
                    # Use default delimiter based on extension
                    pass
                
                reader = csv.reader(f, delimiter=delimiter)
                
                for i, row in enumerate(reader):
                    if i == 0 and csv.Sniffer().has_header(sample):
                        headers = row
                    rows.append(row)
            
            metadata = {
                "filename": path.name,
                "size": path.stat().st_size,
                "encoding": encoding,
                "delimiter": delimiter,
                "row_count": len(rows),
                "column_count": len(rows[0]) if rows else 0,
            }
            
            if headers:
                metadata["headers"] = headers
            
            # Extract text content
            extracted_rows = []
            
            if text_columns is not None:
                # Extract specific columns
                column_indices = []
                
                for col in text_columns:
                    if isinstance(col, int):
                        column_indices.append(col)
                    elif isinstance(col, str) and headers:
                        try:
                            idx = headers.index(col)
                            column_indices.append(idx)
                        except ValueError:
                            warnings = [f"Column '{col}' not found in headers"]
                            
                for i, row in enumerate(rows):
                    if i == 0 and headers and not include_headers:
                        continue
                    extracted_values = []
                    for idx in column_indices:
                        if idx < len(row):
                            extracted_values.append(row[idx])
                    if extracted_values:
                        extracted_rows.append(", ".join(extracted_values))
            else:
                # Extract all columns
                for i, row in enumerate(rows):
                    if i == 0 and headers and not include_headers:
                        continue
                    extracted_rows.append(", ".join(row))
            
            content = "\n".join(extracted_rows)
            
            # Store the structured data in metadata
            metadata["csv_data"] = rows
            
            return ExtractionResult(
                content=content,
                metadata=metadata,
                source=path,
                format=self.format_name
            )
            
        except Exception as e:
            return ExtractionResult(
                content="",
                error=f"Failed to extract CSV file: {str(e)}",
                source=source,
                format=self.format_name
            )


# Register all extractors
registry.register(TextFileExtractor())
registry.register(MarkdownExtractor())
registry.register(JSONExtractor())
registry.register(YAMLExtractor())
registry.register(CSVExtractor())