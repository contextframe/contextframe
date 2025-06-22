"""
PDF Extraction Pipeline using Docling and ContextFrame

This example demonstrates how to process complex PDF documents using Docling
for extraction and ContextFrame for storage and retrieval.

Requirements:
    pip install docling contextframe[extract,embed]

Note: Docling has heavy dependencies including PyTorch. For production use,
consider running Docling in a separate service or container.
"""

import logging
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from pathlib import Path
from typing import Any, Dict, List, Optional

# Docling imports (only if needed)
try:
    from docling.datamodel.pipeline_options import (
        EasyOcrOptions,
        PipelineOptions,
        TableFormerMode,
    )
    from docling.document_converter import DocumentConverter

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("Docling not installed. Install with: pip install docling")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_pdf_with_docling(
    pdf_path: str,
    use_ocr: bool = False,
    extract_tables: bool = True,
    extract_images: bool = True,
    table_mode: str = "accurate",
) -> dict[str, Any]:
    """
    Extract content from PDF using Docling.

    Args:
        pdf_path: Path to PDF file
        use_ocr: Enable OCR for scanned documents
        extract_tables: Extract table structures
        extract_images: Extract and classify images
        table_mode: "fast" or "accurate" for table extraction

    Returns:
        Dictionary with extracted content and metadata
    """
    if not DOCLING_AVAILABLE:
        raise ImportError("Docling is required for PDF extraction")

    # Configure pipeline options
    pipeline_options = PipelineOptions()
    pipeline_options.do_ocr = use_ocr
    pipeline_options.do_table_structure = extract_tables

    if use_ocr:
        pipeline_options.ocr_options = EasyOcrOptions()

    if extract_tables:
        pipeline_options.table_structure_options.mode = (
            TableFormerMode.FAST if table_mode == "fast" else TableFormerMode.ACCURATE
        )

    # Create converter
    converter = DocumentConverter()

    # Convert document
    logger.info(f"Processing PDF: {pdf_path}")
    result = converter.convert(pdf_path)

    # Extract metadata
    metadata = {
        "source": "docling",
        "format": "pdf",
        "extraction_settings": {
            "ocr_enabled": use_ocr,
            "tables_extracted": extract_tables,
            "images_extracted": extract_images,
            "table_mode": table_mode if extract_tables else None,
        },
    }

    # Get the document
    doc = result.document

    # Export to markdown (includes tables, formulas, etc.)
    markdown_content = doc.export_to_markdown()

    # Count elements
    if hasattr(doc, 'tables'):
        metadata["num_tables"] = len(doc.tables)
    if hasattr(doc, 'pictures'):
        metadata["num_images"] = len(doc.pictures)
    if hasattr(doc, 'pages'):
        metadata["num_pages"] = len(doc.pages)

    # Extract title if available
    title = Path(pdf_path).stem
    if hasattr(doc, 'texts') and doc.texts:
        # First text element is often the title
        first_text = doc.texts[0]
        if hasattr(first_text, 'text') and len(first_text.text) < 200:
            title = first_text.text

    return {
        "content": markdown_content,
        "metadata": metadata,
        "title": title,
        "doc": doc,  # Keep original doc for advanced processing
    }


def create_frame_from_pdf(
    pdf_path: str,
    collection_uri: str | None = None,
    chunk_size: int | None = None,
    **docling_kwargs,
) -> list[FrameRecord]:
    """
    Create FrameRecord(s) from a PDF file.

    Args:
        pdf_path: Path to PDF file
        collection_uri: Optional collection to add document to
        chunk_size: If specified, chunk the content
        **docling_kwargs: Additional arguments for Docling

    Returns:
        List of FrameRecord objects
    """
    # Extract content
    extracted = extract_pdf_with_docling(pdf_path, **docling_kwargs)

    # Create base frame data
    base_frame = {
        "uri": pdf_path,
        "title": extracted["title"],
        "metadata": extracted["metadata"],
        "record_type": "document",
    }

    # Handle chunking if requested
    if chunk_size:
        # Use ContextFrame's chunking capabilities
        from contextframe.extract.chunking import ChunkingMixin

        # Detect if content is markdown
        splitter_type = "markdown" if extracted["content"].startswith("#") else "text"

        chunks = ChunkingMixin.chunk_text(
            extracted["content"],
            chunk_size=chunk_size,
            chunk_overlap=100,
            splitter_type=splitter_type,
        )

        frames = []
        for i, chunk in enumerate(chunks):
            frame_data = base_frame.copy()
            frame_data.update(
                {
                    "uri": f"{pdf_path}#chunk-{i}",
                    "content": chunk,
                    "metadata": {
                        **frame_data["metadata"],
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    },
                    "parent_uri": pdf_path if i > 0 else None,
                }
            )
            if collection_uri:
                frame_data["collection_uri"] = collection_uri
            frames.append(FrameRecord(**frame_data))

        return frames
    else:
        # Single document
        base_frame["content"] = extracted["content"]
        if collection_uri:
            base_frame["collection_uri"] = collection_uri
        return [FrameRecord(**base_frame)]


def process_pdf_folder(
    folder_path: str,
    dataset_path: str,
    embed_model: str = "openai/text-embedding-3-small",
    chunk_size: int | None = 1000,
    batch_size: int = 50,
    **docling_kwargs,
):
    """
    Process all PDFs in a folder and store in ContextFrame.

    Args:
        folder_path: Path to folder containing PDFs
        dataset_path: Path for ContextFrame dataset
        embed_model: Model to use for embeddings
        chunk_size: Size of chunks (None for no chunking)
        batch_size: Number of frames to process at once
        **docling_kwargs: Arguments passed to Docling
    """
    # Initialize dataset
    dataset = FrameDataset(dataset_path)

    # Find all PDFs
    pdf_files = list(Path(folder_path).glob("**/*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")

    # Process PDFs in batches
    all_frames = []

    for pdf_path in pdf_files:
        try:
            logger.info(f"Processing: {pdf_path}")
            frames = create_frame_from_pdf(
                str(pdf_path),
                collection_uri=f"pdfs/{pdf_path.parent.name}",
                chunk_size=chunk_size,
                **docling_kwargs,
            )
            all_frames.extend(frames)
            logger.info(f"Created {len(frames)} frames from {pdf_path.name}")

            # Process batch if we've accumulated enough frames
            if len(all_frames) >= batch_size:
                logger.info(f"Embedding batch of {len(all_frames)} frames...")
                embedded_frames = embed_frames(all_frames, model=embed_model)
                dataset.add(embedded_frames)
                all_frames = []

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")

    # Process remaining frames
    if all_frames:
        logger.info(f"Embedding final batch of {len(all_frames)} frames...")
        embedded_frames = embed_frames(all_frames, model=embed_model)
        dataset.add(embedded_frames)

    # Print summary
    print("\nProcessing complete!")
    print(f"Total PDFs processed: {len(pdf_files)}")
    print(f"Dataset location: {dataset_path}")


def search_pdf_content(
    dataset_path: str,
    query: str,
    limit: int = 5,
):
    """
    Search PDF content in ContextFrame dataset.

    Args:
        dataset_path: Path to ContextFrame dataset
        query: Search query
        limit: Number of results to return
    """
    dataset = FrameDataset(dataset_path)

    # Search with embeddings
    results = dataset.search(
        query=query,
        limit=limit,
        search_type="hybrid",  # Combines vector and keyword search
    )

    print(f"\nSearch results for: '{query}'")
    print("-" * 50)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title or result.uri}")
        print(f"   Score: {result.score:.3f}")
        print(f"   Source: {result.uri}")
        if result.metadata.get("chunk_index") is not None:
            print(
                f"   Chunk: {result.metadata['chunk_index'] + 1}/{result.metadata['total_chunks']}"
            )
        print("\n   Content preview:")
        print(f"   {result.content[:200]}...")


def advanced_docling_example():
    """
    Example showing advanced Docling features with custom chunking.
    """
    if not DOCLING_AVAILABLE:
        print("This example requires Docling to be installed")
        return

    try:
        from docling.chunking import HybridChunker
    except ImportError:
        print("Advanced chunking requires newer Docling version")
        return

    # Convert document
    converter = DocumentConverter()
    result = converter.convert("https://arxiv.org/pdf/2408.09869")
    doc = result.document

    # Use Docling's hybrid chunker
    chunker = HybridChunker(
        tokenizer="sentence-transformers/all-MiniLM-L6-v2",
        max_tokens=512,
    )

    # Chunk the document
    chunks = list(chunker.chunk(doc))

    # Convert Docling chunks to FrameRecords
    frames = []
    for i, chunk in enumerate(chunks):
        frame = FrameRecord(
            uri=f"arxiv:2408.09869#chunk-{i}",
            title="Docling Technical Report",
            content=chunk["text"],
            metadata={
                "source": "docling",
                "chunk_meta": chunk.get("meta", {}),
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
            record_type="document",
        )
        frames.append(frame)

    return frames


if __name__ == "__main__":
    # Example 1: Process a single PDF
    if DOCLING_AVAILABLE:
        print("Example 1: Processing a single PDF")

        # Extract a research paper
        frames = create_frame_from_pdf(
            "research_paper.pdf",
            chunk_size=1000,
            use_ocr=False,
            extract_tables=True,
            table_mode="accurate",
        )
        print(f"Created {len(frames)} frames from PDF")

        # Store with embeddings
        embedded = embed_frames(frames, model="openai/text-embedding-3-small")
        dataset = FrameDataset("research_papers.lance")
        dataset.add(embedded)

    # Example 2: Process folder of PDFs (commented out)
    # process_pdf_folder(
    #     folder_path="./documents/pdfs",
    #     dataset_path="./pdf_knowledge_base.lance",
    #     embed_model="openai/text-embedding-3-small",
    #     chunk_size=1000,
    #     use_ocr=True,  # Enable for scanned documents
    #     extract_tables=True,
    #     table_mode="accurate",
    # )

    # Example 3: Search processed PDFs (commented out)
    # search_pdf_content(
    #     dataset_path="./pdf_knowledge_base.lance",
    #     query="machine learning optimization techniques",
    #     limit=5,
    # )

    # Example 4: Advanced Docling chunking (commented out)
    # frames = advanced_docling_example()
    # if frames:
    #     print(f"Created {len(frames)} frames using Docling's chunker")
