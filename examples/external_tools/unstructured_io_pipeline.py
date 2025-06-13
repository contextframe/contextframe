"""
Document Extraction Pipeline using Unstructured.io and ContextFrame

This example demonstrates how to process various document types using
Unstructured.io's API or open-source library with ContextFrame.

Unstructured.io Options:
1. API (paid): https://unstructured-io.github.io/unstructured/api.html
2. Open Source: pip install "unstructured[all-docs]"

Requirements:
    # For API usage:
    pip install unstructured-client contextframe[extract,embed]
    
    # For local usage (heavy dependencies):
    pip install "unstructured[all-docs]" contextframe[extract,embed]
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import os

from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from contextframe.extract.chunking import ChunkingMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_with_unstructured_api(
    file_path: str,
    api_key: str,
    strategy: str = "hi_res",
    languages: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Extract content using Unstructured.io API.
    
    Args:
        file_path: Path to document
        api_key: Unstructured API key
        strategy: Processing strategy - "hi_res", "fast", or "auto"
        languages: List of languages for OCR (e.g., ["eng", "spa"])
        
    Returns:
        Dictionary with extracted content and metadata
    """
    try:
        from unstructured_client import UnstructuredClient
        from unstructured_client.models import shared
        from unstructured_client.models.errors import SDKError
    except ImportError:
        raise ImportError(
            "unstructured-client is required for API usage. "
            "Install with: pip install unstructured-client"
        )
    
    # Initialize client
    client = UnstructuredClient(
        api_key_auth=api_key,
        server_url="https://api.unstructured.io",
    )
    
    # Prepare file
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # Set up parameters
    req = shared.PartitionParameters(
        files=shared.Files(
            content=file_content,
            file_name=Path(file_path).name,
        ),
        strategy=strategy,
        languages=languages,
    )
    
    try:
        # Process document
        logger.info(f"Processing {file_path} with Unstructured API...")
        resp = client.general.partition(req)
        
        # Extract elements
        elements = resp.elements
        
        # Group elements by type
        content_parts = []
        metadata = {
            "source": "unstructured.io",
            "strategy": strategy,
            "num_elements": len(elements),
            "element_types": {},
        }
        
        # Process elements
        for element in elements:
            element_type = element.get("type", "unknown")
            metadata["element_types"][element_type] = metadata["element_types"].get(element_type, 0) + 1
            
            # Format based on type
            text = element.get("text", "")
            if element_type == "Title":
                content_parts.append(f"# {text}")
            elif element_type == "Header":
                content_parts.append(f"## {text}")
            elif element_type == "Table":
                # Tables come as HTML in metadata
                table_html = element.get("metadata", {}).get("text_as_html", text)
                content_parts.append(f"\n{table_html}\n")
            else:
                content_parts.append(text)
        
        return {
            "content": "\n\n".join(content_parts),
            "metadata": metadata,
            "elements": elements,  # Keep raw elements for advanced processing
        }
        
    except SDKError as e:
        logger.error(f"API error: {e}")
        raise


def extract_with_unstructured_local(
    file_path: str,
    strategy: str = "hi_res",
    **kwargs
) -> Dict[str, Any]:
    """
    Extract content using local Unstructured library.
    
    Args:
        file_path: Path to document
        strategy: Processing strategy
        **kwargs: Additional arguments for partition
        
    Returns:
        Dictionary with extracted content and metadata
    """
    try:
        from unstructured.partition.auto import partition
    except ImportError:
        raise ImportError(
            "unstructured package is required for local processing. "
            "Install with: pip install 'unstructured[all-docs]'"
        )
    
    logger.info(f"Processing {file_path} with local Unstructured...")
    
    # Partition document
    elements = partition(
        filename=file_path,
        strategy=strategy,
        **kwargs
    )
    
    # Group elements
    content_parts = []
    metadata = {
        "source": "unstructured_local",
        "strategy": strategy,
        "num_elements": len(elements),
        "element_types": {},
    }
    
    # Process elements
    for element in elements:
        element_type = element.category
        metadata["element_types"][element_type] = metadata["element_types"].get(element_type, 0) + 1
        
        # Format based on type
        if hasattr(element, "text"):
            text = element.text
            if element_type == "Title":
                content_parts.append(f"# {text}")
            elif element_type == "Header":
                content_parts.append(f"## {text}")
            elif element_type == "Table":
                # Get table as HTML if available
                if hasattr(element, "metadata") and hasattr(element.metadata, "text_as_html"):
                    content_parts.append(f"\n{element.metadata.text_as_html}\n")
                else:
                    content_parts.append(text)
            else:
                content_parts.append(text)
    
    return {
        "content": "\n\n".join(content_parts),
        "metadata": metadata,
        "elements": elements,
    }


def create_frames_from_unstructured(
    file_path: str,
    api_key: Optional[str] = None,
    use_api: bool = True,
    chunk_size: Optional[int] = None,
    strategy: str = "hi_res",
    **extract_kwargs
) -> List[FrameRecord]:
    """
    Create FrameRecords from document using Unstructured.
    
    Args:
        file_path: Path to document
        api_key: API key (required if use_api=True)
        use_api: Whether to use API or local processing
        chunk_size: Optional chunk size for splitting
        strategy: Extraction strategy
        **extract_kwargs: Additional extraction arguments
        
    Returns:
        List of FrameRecord objects
    """
    # Extract content
    if use_api:
        if not api_key:
            api_key = os.getenv("UNSTRUCTURED_API_KEY")
            if not api_key:
                raise ValueError("API key required for Unstructured API")
        
        extracted = extract_with_unstructured_api(
            file_path,
            api_key=api_key,
            strategy=strategy,
            **extract_kwargs
        )
    else:
        extracted = extract_with_unstructured_local(
            file_path,
            strategy=strategy,
            **extract_kwargs
        )
    
    # Create base frame
    base_frame = {
        "uri": file_path,
        "title": Path(file_path).stem,
        "metadata": extracted["metadata"],
        "record_type": "document",
    }
    
    # Handle chunking if requested
    if chunk_size:
        # Detect content type for intelligent chunking
        splitter_type = "markdown" if extracted["content"].count("#") > 2 else "text"
        
        chunks = ChunkingMixin.chunk_text(
            extracted["content"],
            chunk_size=chunk_size,
            chunk_overlap=50,
            splitter_type=splitter_type,
        )
        
        frames = []
        for i, chunk in enumerate(chunks):
            frame_data = base_frame.copy()
            frame_data.update({
                "uri": f"{file_path}#chunk-{i}",
                "content": chunk,
                "metadata": {
                    **frame_data["metadata"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            })
            frames.append(FrameRecord(**frame_data))
        
        return frames
    else:
        base_frame["content"] = extracted["content"]
        return [FrameRecord(**base_frame)]


def process_folder_with_unstructured(
    folder_path: str,
    dataset_path: str,
    api_key: Optional[str] = None,
    use_api: bool = True,
    embed_model: str = "openai/text-embedding-3-small",
    chunk_size: Optional[int] = 1000,
    file_patterns: List[str] = None,
):
    """
    Process a folder of documents using Unstructured.
    
    Args:
        folder_path: Path to folder
        dataset_path: Path for ContextFrame dataset
        api_key: Unstructured API key
        use_api: Whether to use API or local processing
        embed_model: Embedding model
        chunk_size: Chunk size for splitting
        file_patterns: File patterns to process
    """
    if file_patterns is None:
        file_patterns = ["*.pdf", "*.docx", "*.pptx", "*.html", "*.md"]
    
    # Initialize dataset
    dataset = FrameDataset(dataset_path)
    
    # Find files
    all_files = []
    folder = Path(folder_path)
    for pattern in file_patterns:
        all_files.extend(folder.glob(f"**/{pattern}"))
    
    logger.info(f"Found {len(all_files)} files to process")
    
    # Process each file
    all_frames = []
    for file_path in all_files:
        try:
            logger.info(f"Processing: {file_path}")
            frames = create_frames_from_unstructured(
                str(file_path),
                api_key=api_key,
                use_api=use_api,
                chunk_size=chunk_size,
                strategy="hi_res",  # Best quality
            )
            all_frames.extend(frames)
            logger.info(f"Created {len(frames)} frames from {file_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
    
    # Embed frames
    if all_frames:
        logger.info(f"Embedding {len(all_frames)} frames...")
        embedded_frames = embed_frames(all_frames, model=embed_model)
        dataset.add(embedded_frames)
        logger.info(f"Stored {len(embedded_frames)} frames in {dataset_path}")
    
    return dataset


def advanced_element_processing():
    """
    Example of advanced processing using element types.
    """
    # This example shows how to process specific element types
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    
    extracted = extract_with_unstructured_api(
        "document.pdf",
        api_key=api_key,
        strategy="hi_res"
    )
    
    # Group elements by type for specialized processing
    elements_by_type = {}
    for element in extracted["elements"]:
        elem_type = element.get("type", "unknown")
        if elem_type not in elements_by_type:
            elements_by_type[elem_type] = []
        elements_by_type[elem_type].append(element)
    
    # Extract specific content
    tables = elements_by_type.get("Table", [])
    images = elements_by_type.get("Image", [])
    formulas = elements_by_type.get("Formula", [])
    
    print(f"Found {len(tables)} tables, {len(images)} images, {len(formulas)} formulas")
    
    # Create specialized frames
    frames = []
    
    # Table frames
    for i, table in enumerate(tables):
        frame = FrameRecord(
            uri=f"document.pdf#table-{i}",
            content=table.get("metadata", {}).get("text_as_html", table.get("text", "")),
            metadata={
                "type": "table",
                "source": "unstructured.io",
            },
            record_type="document",
        )
        frames.append(frame)
    
    return frames


if __name__ == "__main__":
    # Example 1: Process single file with API
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    if api_key:
        frames = create_frames_from_unstructured(
            "document.pdf",
            api_key=api_key,
            use_api=True,
            chunk_size=1000,
            strategy="hi_res",
        )
        print(f"Created {len(frames)} frames")
    
    # Example 2: Process with local library (commented out)
    # frames = create_frames_from_unstructured(
    #     "document.pdf",
    #     use_api=False,
    #     chunk_size=1000,
    #     strategy="fast",
    # )
    
    # Example 3: Process folder (commented out)
    # dataset = process_folder_with_unstructured(
    #     folder_path="./documents",
    #     dataset_path="./unstructured_docs.lance",
    #     api_key=api_key,
    #     use_api=True,
    #     chunk_size=1000,
    # )
    
    # Example 4: Advanced element processing (commented out)
    # if api_key:
    #     frames = advanced_element_processing()