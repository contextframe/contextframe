# Docling Integration Analysis for ContextFrame

## Executive Summary

After investigating Docling, we recommend **NOT** integrating it directly into ContextFrame's core. Instead, we should document it as a recommended external tool for heavy document processing while maintaining our lightweight extraction approach.

## Key Findings

### Docling Strengths
1. **Advanced PDF Processing**: Exceptional PDF understanding with layout analysis, table extraction, formula recognition
2. **Vision Model Support**: Includes SmolDocling VLM for document understanding
3. **OCR Capabilities**: Multiple OCR engine support (EasyOCR, Tesseract, RapidOCR)
4. **Rich Integrations**: Pre-built connectors for LangChain, LlamaIndex, Haystack
5. **Enterprise Features**: Air-gapped execution, metadata extraction, complex document structures

### Docling Limitations for ContextFrame
1. **Heavy Dependencies**: 
   - Requires PyTorch (large download, ~2GB)
   - OCR engines need system dependencies
   - Significant installation footprint
   
2. **Complexity Overhead**:
   - Brings in features we don't need (chart understanding, molecular structures)
   - More complex than needed for simple text extraction
   
3. **Philosophy Mismatch**:
   - ContextFrame focuses on storage/retrieval, not document processing
   - We want users to choose their extraction tools
   - Lightweight core is a key design principle

## Recommended Approach

### 1. Keep Current Lightweight Extractors
Our existing extractors handle common formats well:
- Plain text, Markdown, JSON, YAML, CSV
- No heavy dependencies
- Fast and simple

### 2. Document Docling as External Tool
Create examples showing how to:
```python
# Use Docling for heavy processing
from docling import DocumentConverter
from contextframe import FrameDataset
from contextframe.embed import embed_frames

# Process complex PDFs with Docling
docling_conv = DocumentConverter()
docling_result = docling_conv.convert("complex.pdf")

# Convert to ContextFrame format
frame_data = {
    "uri": "complex.pdf",
    "content": docling_result.render_as_markdown(),
    "metadata": {
        "source": "docling",
        "tables_extracted": len(docling_result.tables),
        "formulas_extracted": len(docling_result.formulas)
    }
}

# Embed and store
frames = [FrameRecord(**frame_data)]
embedded_frames = embed_frames(frames, model="openai/text-embedding-3-small")
dataset = FrameDataset("documents.lance")
dataset.add(embedded_frames)
```

### 3. Integration Pattern Guide
Document best practices for:
- When to use Docling vs built-in extractors
- Converting Docling output to FrameRecords
- Handling Docling's rich metadata
- Chunking strategies for complex documents

## Implementation Plan

1. **Create `examples/external_tools/` directory**:
   - `docling_pdf_pipeline.py`
   - `unstructured_io_example.py`
   - `azure_document_intelligence.py`

2. **Update documentation**:
   - Add "External Extraction Tools" section
   - Comparison table of extraction options
   - Decision tree for choosing tools

3. **Keep ContextFrame lightweight**:
   - No Docling dependency in core
   - Optional `contextframe[docling]` if strong user demand
   - Focus on being the best storage layer

## Conclusion

Docling is an excellent tool for complex document processing, but integrating it would violate ContextFrame's core principle of being lightweight. Instead, we should position ContextFrame as the ideal storage layer that works with any extraction tool, using Docling as a prime example of best-in-class external processing.

This approach:
- Maintains our lightweight philosophy
- Gives users flexibility to choose tools
- Avoids heavy dependencies
- Focuses on our core strength: storage and retrieval