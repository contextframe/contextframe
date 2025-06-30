# External Extraction Tools Guide

This guide helps you choose and integrate external document extraction services with ContextFrame.

## Overview

While ContextFrame provides native extractors for simple formats, complex documents (PDFs, scanned images, etc.) often require specialized extraction services. This guide covers popular extraction tools and their integration patterns.

## Comparison Matrix

| Service | Strengths | Best For | Pricing Model | Key Features |
|---------|-----------|----------|---------------|--------------|
| **Docling** | Advanced PDF understanding | Research papers, technical docs | Open source (self-hosted) | Table extraction, formula recognition, layout analysis |
| **Unstructured.io** | Wide format support | Enterprise documents | API & open source | 25+ formats, multiple strategies, element classification |
| **Chunkr** | Intelligent chunking | RAG applications | API (pay-per-use) | Structure-preserving chunks, confidence scores |
| **Reducto** | Scientific documents | Academic papers, reports | API (subscription) | Equation parsing, figure extraction, multi-language |

## Integration Examples

### 1. Docling (Self-Hosted)

**Best for**: Organizations wanting full control, no external dependencies

```python
from docling import DocumentConverter
from contextframe import FrameRecord

# Extract with Docling
converter = DocumentConverter()
result = converter.convert("research_paper.pdf")

# Convert to ContextFrame
frame = FrameRecord(
    uri="research_paper.pdf",
    content=result.document.export_to_markdown(),
    metadata={
        "source": "docling",
        "tables": len(result.document.tables),
        "pages": len(result.document.pages)
    }
)
```

**Pros**:
- No API costs
- Complete data privacy
- Excellent PDF handling
- Active open-source development

**Cons**:
- Heavy dependencies (PyTorch)
- Requires local compute resources
- Setup complexity

### 2. Unstructured.io

**Best for**: Organizations needing broad format support

```python
from unstructured_client import UnstructuredClient
from contextframe import FrameRecord

# API approach
client = UnstructuredClient(api_key_auth="YOUR_KEY")
with open("document.pdf", "rb") as f:
    resp = client.general.partition(
        files={"content": f.read(), "file_name": "document.pdf"},
        strategy="hi_res"
    )

# Process elements
content = "\n\n".join(e["text"] for e in resp.elements)
frame = FrameRecord(uri="document.pdf", content=content)
```

**Pros**:
- 25+ file formats supported
- Both API and open-source options
- Good element classification
- Fast processing option

**Cons**:
- API costs for cloud version
- Open-source version has many dependencies
- Limited customization options

### 3. Chunkr

**Best for**: RAG applications requiring intelligent chunking

```python
from chunkr import Chunkr
from contextframe import FrameRecord

# Process with Chunkr
client = Chunkr(api_key="YOUR_KEY")
with open("document.pdf", "rb") as f:
    task = client.upload(file=f, target_chunk_length=1000)

# Wait for processing
while task.status in ["Pending", "Processing"]:
    time.sleep(2)
    task = client.get_task(task.task_id)

# Create frames from chunks
frames = []
for i, chunk in enumerate(task.output["chunks"]):
    frame = FrameRecord(
        uri=f"document.pdf#chunk-{i}",
        content=chunk["content"],
        metadata={"chunk_id": chunk["chunk_id"]}
    )
    frames.append(frame)
```

**Pros**:
- Intelligent, structure-aware chunking
- Preserves document relationships
- Confidence scores
- Multimodal support

**Cons**:
- API-only (no self-hosted option)
- Costs can add up for large volumes
- Processing can be slow

### 4. Reducto

**Best for**: Scientific and technical documents

```python
import requests
from contextframe import FrameRecord

# Submit to Reducto
headers = {"Authorization": f"Bearer YOUR_KEY"}
with open("paper.pdf", "rb") as f:
    response = requests.post(
        "https://api.reducto.ai/v1/documents",
        files={"file": f},
        headers=headers
    )

doc_id = response.json()["document_id"]

# Get results
content = requests.get(
    f"https://api.reducto.ai/v1/documents/{doc_id}/content",
    headers=headers
).json()

# Create frames including equations
frames = [
    FrameRecord(
        uri="paper.pdf",
        content=content["content"],
        metadata={"equations": len(content.get("equations", []))}
    )
]
```

**Pros**:
- Excellent equation/formula parsing
- Figure and table extraction
- Multi-language support
- High-fidelity output

**Cons**:
- API-only
- Higher cost than alternatives
- Focused on specific document types

## Decision Guide

### Choose Docling if:
- You need to process documents on-premises
- Data privacy is critical
- You have compute resources available
- You primarily work with PDFs

### Choose Unstructured.io if:
- You need to support many file formats
- You want flexibility (API or self-hosted)
- You need fast processing options
- Budget is a consideration

### Choose Chunkr if:
- You're building RAG applications
- Chunk quality is critical
- You need structure-aware splitting
- You don't mind API-only solution

### Choose Reducto if:
- You work with scientific documents
- Equation extraction is important
- You need high-fidelity parsing
- Budget is not a primary concern

## Complete Pipeline Example

Here's a complete example showing how to choose the right tool based on document type:

```python
from pathlib import Path
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from contextframe.extract import TextFileExtractor
import os

def smart_extraction_pipeline(file_path: str) -> List[FrameRecord]:
    """Choose the best extraction method based on file type and content."""
    
    file_ext = Path(file_path).suffix.lower()
    
    # Simple formats - use native extractors
    if file_ext in [".txt", ".md", ".json", ".yaml", ".csv"]:
        extractor = TextFileExtractor()
        result = extractor.extract(file_path)
        return [FrameRecord(
            uri=file_path,
            content=result.content,
            metadata=result.metadata
        )]
    
    # PDFs - check content type
    elif file_ext == ".pdf":
        # For scientific papers with equations
        if "equation" in file_path or "paper" in file_path:
            if os.getenv("REDUCTO_API_KEY"):
                return extract_with_reducto(file_path)
        
        # For general documents needing good chunking
        elif os.getenv("CHUNKR_API_KEY"):
            return extract_with_chunkr(file_path)
        
        # Fallback to Unstructured
        elif os.getenv("UNSTRUCTURED_API_KEY"):
            return extract_with_unstructured(file_path)
        
        # Local fallback with Docling
        else:
            return extract_with_docling(file_path)
    
    # Office documents
    elif file_ext in [".docx", ".pptx", ".xlsx"]:
        if os.getenv("UNSTRUCTURED_API_KEY"):
            return extract_with_unstructured(file_path)
        else:
            # Could use python-docx, python-pptx, etc.
            raise NotImplementedError(f"No extractor for {file_ext}")
    
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

# Usage
frames = smart_extraction_pipeline("research_paper.pdf")
embedded = embed_frames(frames, model="openai/text-embedding-3-small")
dataset = FrameDataset("documents.lance")
dataset.add(embedded)
```

## Cost Optimization Tips

1. **Use native extractors** for simple formats (text, markdown, JSON)
2. **Cache extraction results** to avoid reprocessing
3. **Batch API calls** when possible
4. **Choose the right strategy** (e.g., "fast" vs "hi_res" in Unstructured)
5. **Pre-filter documents** to only process what you need

## Performance Considerations

- **Docling**: Slowest (local processing), but no API limits
- **Unstructured "fast"**: Fastest option for quick extraction
- **Chunkr**: Medium speed, optimized for quality
- **Reducto**: Slower for complex documents, very accurate

## Security & Privacy

| Service | Self-Hosted | Data Retention | Compliance |
|---------|-------------|----------------|------------|
| Docling | ✅ Yes | N/A (local) | Full control |
| Unstructured | ✅ Optional | Varies | SOC2 (API) |
| Chunkr | ❌ No | 30 days | SOC2 pending |
| Reducto | ❌ No | 7 days | GDPR compliant |

## Conclusion

Choose your extraction tool based on:
1. **Document types** you process most
2. **Privacy requirements**
3. **Budget constraints**
4. **Quality requirements**
5. **Processing volume**

ContextFrame works seamlessly with all these tools, allowing you to use the best tool for each job while maintaining a consistent storage and retrieval interface.