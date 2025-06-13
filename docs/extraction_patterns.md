# Extraction Patterns Guide

This guide provides best practices and patterns for extracting and processing documents with ContextFrame.

## Overview

ContextFrame's extraction module provides:
- Native extractors for common formats (text, markdown, JSON, YAML, CSV)
- Intelligent text chunking with semantic awareness
- Batch processing capabilities
- Integration patterns for external tools

## Basic Extraction

### Single File Extraction

```python
from contextframe.extract import TextFileExtractor

extractor = TextFileExtractor()
result = extractor.extract("document.txt")

if result.success:
    print(f"Content: {result.content}")
    print(f"Metadata: {result.metadata}")
```

### Format-Specific Extraction

```python
from contextframe.extract import (
    MarkdownExtractor,
    JSONExtractor,
    YAMLExtractor,
    CSVExtractor
)

# Markdown with frontmatter
md_extractor = MarkdownExtractor()
result = md_extractor.extract("post.md")
# Access frontmatter: result.metadata["frontmatter"]

# JSON with field extraction
json_extractor = JSONExtractor()
result = json_extractor.extract(
    "data.json",
    extract_text_fields=["title", "description", "content"]
)

# CSV with specific columns
csv_extractor = CSVExtractor()
result = csv_extractor.extract(
    "data.csv",
    text_columns=["name", "description"]
)
```

## Intelligent Chunking

ContextFrame uses semantic-text-splitter for intelligent chunking that preserves document structure.

### Character-Based Chunking

```python
from contextframe.extract.chunking import ChunkingMixin

# Simple character-based chunking
chunks = ChunkingMixin.chunk_text(
    text="Your long document text...",
    chunk_size=1000,  # characters
    chunk_overlap=100
)
```

### Token-Based Chunking (for LLMs)

```python
# OpenAI models (using tiktoken)
chunks = ChunkingMixin.chunk_text(
    text="Your document text...",
    chunk_size=256,  # tokens
    tokenizer_model="gpt-3.5-turbo"
)

# HuggingFace models
chunks = ChunkingMixin.chunk_text(
    text="Your document text...",
    chunk_size=384,  # tokens
    tokenizer_model="sentence-transformers/all-MiniLM-L6-v2"
)
```

### Structure-Aware Chunking

```python
# Markdown-aware chunking (preserves headers, lists, etc.)
chunks = ChunkingMixin.chunk_text(
    text="# Header\n\nParagraph...\n\n## Subheader\n\n- List item",
    chunk_size=500,
    splitter_type="markdown"
)

# Code-aware chunking (preserves functions, classes, etc.)
chunks = ChunkingMixin.chunk_text(
    text=python_code,
    chunk_size=500,
    splitter_type="code",
    tokenizer_model="gpt-3.5-turbo"  # Optional: token-based
)
```

### Chunking During Extraction

```python
from contextframe.extract import TextFileExtractor
from contextframe.extract.chunking import ChunkingMixin

class ChunkingTextExtractor(TextFileExtractor, ChunkingMixin):
    pass

extractor = ChunkingTextExtractor()
result = extractor.extract_with_chunking(
    "large_document.md",
    chunk_size=1000,
    splitter_type="markdown",
    tokenizer_model="gpt-3.5-turbo"  # Optional
)

# Access chunks
for i, chunk in enumerate(result.chunks):
    print(f"Chunk {i + 1}: {chunk[:100]}...")
```

## Batch Processing

### Directory Processing

```python
from contextframe.extract import BatchExtractor

batch = BatchExtractor(
    patterns=["*.txt", "*.md", "*.json"],
    recursive=True,
    chunk_size=1000,  # Optional: chunk large files
    use_threads=True,
    max_workers=4
)

results = batch.extract_folder("./documents")

# Process results
for result in results:
    if result.success:
        print(f"Extracted: {result.source}")
        if result.chunks:
            print(f"  Chunks: {len(result.chunks)}")
```

### Async Processing

```python
import asyncio

async def process_async():
    batch = BatchExtractor(patterns=["*.md"])
    results = await batch.extract_files_async(file_list)
    return results

results = asyncio.run(process_async())
```

## Integration with External Tools

### Pattern 1: Docling for Complex PDFs

```python
# Use Docling for extraction
from docling import DocumentConverter

converter = DocumentConverter()
docling_result = converter.convert("complex.pdf")

# Convert to ContextFrame format
from contextframe import FrameRecord

frame = FrameRecord(
    uri="complex.pdf",
    content=docling_result.document.export_to_markdown(),
    metadata={
        "source": "docling",
        "num_tables": len(docling_result.document.tables),
        "num_pages": len(docling_result.document.pages)
    },
    record_type="document"
)
```

### Pattern 2: Unstructured.io API

```python
import requests
from contextframe import FrameRecord

# Call Unstructured API
response = requests.post(
    "https://api.unstructured.io/general/v0/general",
    headers={"unstructured-api-key": "YOUR_KEY"},
    files={"files": open("document.pdf", "rb")},
    data={"strategy": "hi_res"}
)

# Convert to FrameRecord
elements = response.json()
content = "\n\n".join(e["text"] for e in elements)

frame = FrameRecord(
    uri="document.pdf",
    content=content,
    metadata={"source": "unstructured.io"},
    record_type="document"
)
```

## Complete Pipeline Example

```python
from contextframe import FrameDataset, FrameRecord
from contextframe.extract import BatchExtractor
from contextframe.embed import embed_frames

def process_knowledge_base(folder_path: str):
    """Complete extraction and embedding pipeline."""
    
    # 1. Extract documents with chunking
    extractor = BatchExtractor(
        patterns=["*.txt", "*.md", "*.pdf"],
        recursive=True,
        chunk_size=1000,
        use_threads=True
    )
    
    results = extractor.extract_folder(folder_path)
    
    # 2. Convert to FrameRecords
    frames = []
    for result in results:
        if result.success:
            if result.chunks:
                # Handle chunked documents
                for i, chunk in enumerate(result.chunks):
                    frame = FrameRecord(
                        uri=f"{result.source}#chunk-{i}",
                        content=chunk,
                        metadata={
                            **result.metadata,
                            "chunk_index": i,
                            "total_chunks": len(result.chunks)
                        },
                        record_type="document"
                    )
                    frames.append(frame)
            else:
                # Single document
                frame = FrameRecord(
                    uri=result.source,
                    content=result.content,
                    metadata=result.metadata,
                    record_type="document"
                )
                frames.append(frame)
    
    # 3. Embed frames
    embedded_frames = embed_frames(
        frames,
        model="openai/text-embedding-3-small",
        batch_size=100
    )
    
    # 4. Store in dataset
    dataset = FrameDataset("knowledge_base.lance")
    dataset.add(embedded_frames)
    
    return dataset

# Use the pipeline
dataset = process_knowledge_base("./documents")
print(f"Processed {len(dataset)} documents")
```

## Best Practices

### 1. Choose the Right Chunking Strategy

- **Character-based**: Fast, good for general text
- **Token-based**: Essential for LLM applications
- **Markdown-aware**: Preserves document structure
- **Code-aware**: Maintains syntactic boundaries

### 2. Optimize Chunk Sizes

- **Small chunks (200-500)**: Better for precise retrieval
- **Medium chunks (500-1000)**: Balanced context and precision
- **Large chunks (1000-2000)**: More context, less precision

### 3. Handle Large Documents

```python
# For very large files, use streaming extraction
with open("huge_file.txt", "r") as f:
    chunk_buffer = []
    for line in f:
        chunk_buffer.append(line)
        if len("".join(chunk_buffer)) > 1000:
            # Process chunk
            chunk_text = "".join(chunk_buffer)
            # ... process chunk_text
            chunk_buffer = []
```

### 4. Metadata Best Practices

- Always preserve source file information
- Track chunk indices and relationships
- Include extraction settings (chunk size, overlap)
- Add format-specific metadata (frontmatter, CSV headers)

### 5. Error Handling

```python
results = extractor.extract_folder("./documents")

successful = [r for r in results if r.success]
failed = [r for r in results if not r.success]

if failed:
    for result in failed:
        print(f"Failed: {result.source} - {result.error}")

# Continue processing successful extractions
```

## Language Support for Code Chunking

ContextFrame includes support for these programming languages:

- Python (`py`)
- JavaScript (`js`)
- TypeScript (`ts`)
- Rust (`rs`)
- Go (`go`)
- C++ (`cpp`)
- C (`c`)
- Java (`java`)
- Ruby (`rb`)
- PHP (`php`)
- HTML (`html`)
- CSS (`css`)
- JSON (`json`)
- YAML (`yaml`, `yml`)
- TOML (`toml`)
- XML (`xml`)
- Bash (`sh`, `bash`)

Example:
```python
# Automatic language detection from file extension
result = extractor.extract_with_chunking(
    "script.py",
    chunk_size=500,
    splitter_type="code"  # Auto-detects Python
)
```