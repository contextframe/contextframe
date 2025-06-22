"""
Document Extraction Pipeline using Chunkr and ContextFrame

This example demonstrates how to process complex documents using Chunkr's
intelligent chunking service with ContextFrame.

Chunkr specializes in:
- Structure-preserving chunking
- Multi-modal extraction (text, tables, images)
- Automatic OCR for scanned documents
- Intelligent segment identification

Requirements:
    pip install chunkr-ai contextframe[extract,embed]

Get API key: https://chunkr.ai
"""

import logging
import os
import time
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_with_chunkr(
    file_path: str,
    api_key: str,
    max_wait_time: int = 180,
    target_chunk_length: int | None = None,
    ocr_strategy: str = "auto",
) -> dict[str, Any]:
    """
    Extract and chunk content using Chunkr API.

    Args:
        file_path: Path to document
        api_key: Chunkr API key
        max_wait_time: Maximum time to wait for processing (seconds)
        target_chunk_length: Target chunk length (Chunkr handles this intelligently)
        ocr_strategy: OCR strategy - "auto", "force", or "off"

    Returns:
        Dictionary with chunks and metadata
    """
    try:
        from chunkr import Chunkr
    except ImportError:
        raise ImportError(
            "chunkr-ai package is required. Install with: pip install chunkr-ai"
        )

    # Initialize client
    client = Chunkr(api_key=api_key)

    logger.info(f"Uploading {file_path} to Chunkr...")

    # Upload and process
    with open(file_path, "rb") as f:
        task = client.upload(
            file=f,
            target_chunk_length=target_chunk_length,
            ocr_strategy=ocr_strategy,
        )

    # Poll for completion
    logger.info(f"Processing document (task ID: {task.task_id})...")
    start_time = time.time()

    while task.status in ["Pending", "Processing"]:
        if time.time() - start_time > max_wait_time:
            raise TimeoutError(f"Processing exceeded {max_wait_time} seconds")

        time.sleep(2)
        task = client.get_task(task.task_id)
        logger.info(f"Status: {task.status}")

    if task.status == "Failed":
        raise Exception(f"Chunkr processing failed: {task.error}")

    # Get results
    output = task.output

    # Extract segments and chunks
    segments = output.get("segments", [])
    chunks = output.get("chunks", [])

    # Build metadata
    metadata = {
        "source": "chunkr",
        "task_id": task.task_id,
        "num_segments": len(segments),
        "num_chunks": len(chunks),
        "ocr_strategy": ocr_strategy,
        "segment_types": {},
        "processing_time": time.time() - start_time,
    }

    # Count segment types
    for segment in segments:
        seg_type = segment.get("type", "unknown")
        metadata["segment_types"][seg_type] = (
            metadata["segment_types"].get(seg_type, 0) + 1
        )

    return {
        "chunks": chunks,
        "segments": segments,
        "metadata": metadata,
        "extracted_text": output.get("extracted_text", ""),
    }


def create_frames_from_chunkr(
    file_path: str,
    api_key: str,
    collection_uri: str | None = None,
    include_segment_frames: bool = False,
    **chunkr_kwargs,
) -> list[FrameRecord]:
    """
    Create FrameRecords from Chunkr output.

    Args:
        file_path: Path to document
        api_key: Chunkr API key
        collection_uri: Optional collection URI
        include_segment_frames: Whether to create frames for segments too
        **chunkr_kwargs: Additional Chunkr arguments

    Returns:
        List of FrameRecord objects
    """
    # Extract with Chunkr
    result = extract_with_chunkr(file_path, api_key, **chunkr_kwargs)

    frames = []
    base_uri = file_path

    # Create frames from chunks (primary output)
    for i, chunk in enumerate(result["chunks"]):
        # Chunkr chunks include rich metadata
        chunk_metadata = result["metadata"].copy()
        chunk_metadata.update(
            {
                "chunk_index": i,
                "total_chunks": len(result["chunks"]),
                "chunk_id": chunk.get("chunk_id"),
                "segment_ids": chunk.get("segment_ids", []),
                "confidence": chunk.get("confidence"),
            }
        )

        # Handle different content types
        content = chunk.get("content", "")
        if chunk.get("type") == "table":
            # Tables might have structured data
            if "table_data" in chunk:
                content = f"Table:\n{chunk['table_data']}"

        frame = FrameRecord(
            uri=f"{base_uri}#chunk-{i}",
            title=Path(file_path).stem,
            content=content,
            metadata=chunk_metadata,
            record_type="document",
            collection_uri=collection_uri,
        )
        frames.append(frame)

    # Optionally create frames for segments
    if include_segment_frames:
        for i, segment in enumerate(result["segments"]):
            seg_metadata = {
                "source": "chunkr",
                "segment_type": segment.get("type"),
                "segment_id": segment.get("segment_id"),
                "confidence": segment.get("confidence"),
                "bbox": segment.get("bbox"),  # Bounding box if available
                "page": segment.get("page"),
            }

            frame = FrameRecord(
                uri=f"{base_uri}#segment-{i}",
                title=f"{Path(file_path).stem} - {segment.get('type', 'segment')}",
                content=segment.get("content", ""),
                metadata=seg_metadata,
                record_type="document",
                parent_uri=base_uri,
            )
            frames.append(frame)

    return frames


def process_multimodal_document(
    file_path: str,
    api_key: str,
    dataset_path: str,
    embed_model: str = "openai/text-embedding-3-small",
):
    """
    Process a document with tables, images, and mixed content.

    Args:
        file_path: Path to document
        api_key: Chunkr API key
        dataset_path: ContextFrame dataset path
        embed_model: Embedding model
    """
    # Extract with Chunkr
    result = extract_with_chunkr(
        file_path,
        api_key,
        target_chunk_length=512,  # Smaller chunks for multimodal
        ocr_strategy="auto",
    )

    # Separate chunks by type
    text_chunks = []
    table_chunks = []
    image_chunks = []

    for chunk in result["chunks"]:
        chunk_type = chunk.get("type", "text")
        if chunk_type == "table":
            table_chunks.append(chunk)
        elif chunk_type == "image":
            image_chunks.append(chunk)
        else:
            text_chunks.append(chunk)

    logger.info(
        f"Found: {len(text_chunks)} text, {len(table_chunks)} tables, {len(image_chunks)} images"
    )

    # Create specialized frames
    frames = []

    # Text frames
    for i, chunk in enumerate(text_chunks):
        frame = FrameRecord(
            uri=f"{file_path}#text-{i}",
            content=chunk.get("content", ""),
            metadata={
                "type": "text",
                "chunk_index": i,
                "source": "chunkr",
            },
            record_type="document",
        )
        frames.append(frame)

    # Table frames (with special handling)
    for i, chunk in enumerate(table_chunks):
        # Tables might need different embedding strategy
        table_content = chunk.get("content", "")
        if "table_data" in chunk:
            # Convert structured table data to text
            table_content = f"Table {i + 1}:\n{chunk['table_data']}"

        frame = FrameRecord(
            uri=f"{file_path}#table-{i}",
            content=table_content,
            metadata={
                "type": "table",
                "table_index": i,
                "source": "chunkr",
                "headers": chunk.get("headers", []),
            },
            record_type="document",
        )
        frames.append(frame)

    # Image frames (descriptions or OCR text)
    for i, chunk in enumerate(image_chunks):
        frame = FrameRecord(
            uri=f"{file_path}#image-{i}",
            content=chunk.get("content", chunk.get("description", f"Image {i + 1}")),
            metadata={
                "type": "image",
                "image_index": i,
                "source": "chunkr",
                "ocr_text": chunk.get("ocr_text"),
            },
            record_type="document",
        )
        frames.append(frame)

    # Embed and store
    dataset = FrameDataset(dataset_path)
    embedded_frames = embed_frames(frames, model=embed_model)
    dataset.add(embedded_frames)

    return dataset


def batch_process_with_chunkr(
    folder_path: str,
    dataset_path: str,
    api_key: str,
    file_patterns: list[str] = None,
    embed_model: str = "openai/text-embedding-3-small",
):
    """
    Process multiple documents with Chunkr.

    Args:
        folder_path: Folder containing documents
        dataset_path: ContextFrame dataset path
        api_key: Chunkr API key
        file_patterns: File patterns to process
        embed_model: Embedding model
    """
    if file_patterns is None:
        file_patterns = ["*.pdf", "*.docx", "*.pptx"]

    # Find files
    all_files = []
    folder = Path(folder_path)
    for pattern in file_patterns:
        all_files.extend(folder.glob(f"**/{pattern}"))

    logger.info(f"Found {len(all_files)} files to process")

    # Initialize dataset
    dataset = FrameDataset(dataset_path)

    # Process each file
    for file_path in all_files:
        try:
            logger.info(f"Processing: {file_path}")

            # Create frames with Chunkr
            frames = create_frames_from_chunkr(
                str(file_path),
                api_key=api_key,
                collection_uri=f"documents/{file_path.parent.name}",
            )

            # Embed and store
            embedded_frames = embed_frames(frames, model=embed_model)
            dataset.add(embedded_frames)

            logger.info(f"Added {len(frames)} frames from {file_path.name}")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    return dataset


def compare_chunking_strategies():
    """
    Compare Chunkr's intelligent chunking with basic chunking.
    """
    api_key = os.getenv("CHUNKR_API_KEY")
    if not api_key:
        print("Set CHUNKR_API_KEY environment variable")
        return

    file_path = "complex_document.pdf"

    # 1. Chunkr's intelligent chunking
    print("Using Chunkr's intelligent chunking...")
    chunkr_frames = create_frames_from_chunkr(
        file_path,
        api_key=api_key,
        target_chunk_length=500,
    )

    print(f"\nChunkr created {len(chunkr_frames)} chunks")
    for i, frame in enumerate(chunkr_frames[:3]):
        print(f"\nChunk {i + 1}:")
        print(frame.content[:200] + "...")
        print(f"Metadata: {frame.metadata.get('segment_ids')}")

    # 2. Basic character splitting (for comparison)
    from contextframe.extract import TextFileExtractor
    from contextframe.extract.chunking import ChunkingMixin

    print("\n\nUsing basic character splitting...")
    # This would need to extract PDF first
    # Just showing the concept
    basic_chunks = ChunkingMixin.chunk_text(
        "Sample text that would come from PDF extraction...",
        chunk_size=500,
        splitter_type="text",
    )

    print(f"Basic splitting created {len(basic_chunks)} chunks")
    print("\nKey differences:")
    print("- Chunkr preserves document structure")
    print("- Chunkr handles tables and images intelligently")
    print("- Chunkr provides confidence scores and segment relationships")


if __name__ == "__main__":
    # Example 1: Process a single document
    api_key = os.getenv("CHUNKR_API_KEY")
    if api_key:
        frames = create_frames_from_chunkr(
            "document.pdf",
            api_key=api_key,
            target_chunk_length=1000,
        )
        print(f"Created {len(frames)} frames with Chunkr")
    else:
        print("Set CHUNKR_API_KEY environment variable")

    # Example 2: Process multimodal document (commented out)
    # if api_key:
    #     dataset = process_multimodal_document(
    #         "report_with_tables.pdf",
    #         api_key=api_key,
    #         dataset_path="./multimodal_docs.lance",
    #     )

    # Example 3: Batch processing (commented out)
    # if api_key:
    #     dataset = batch_process_with_chunkr(
    #         folder_path="./documents",
    #         dataset_path="./chunkr_docs.lance",
    #         api_key=api_key,
    #     )

    # Example 4: Compare strategies (commented out)
    # compare_chunking_strategies()
