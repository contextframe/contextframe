"""
Document Extraction Pipeline using Reducto and ContextFrame

This example demonstrates how to process documents using Reducto's
advanced document understanding API with ContextFrame.

Reducto specializes in:
- High-fidelity document parsing
- Complex layout understanding
- Table and figure extraction
- Mathematical formula parsing
- Multi-language support

Requirements:
    pip install requests contextframe[extract,embed]
    
Get API key: https://reducto.ai
API Docs: https://docs.reducto.ai
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import json
import requests
import time

from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from contextframe.extract.chunking import ChunkingMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_with_reducto(
    file_path: str,
    api_key: str,
    options: Optional[Dict[str, Any]] = None,
    wait_for_completion: bool = True,
    max_wait_time: int = 300,
) -> Dict[str, Any]:
    """
    Extract content using Reducto API.
    
    Args:
        file_path: Path to document
        api_key: Reducto API key
        options: Processing options (see Reducto docs)
        wait_for_completion: Whether to wait for async processing
        max_wait_time: Maximum time to wait (seconds)
        
    Returns:
        Dictionary with extracted content and metadata
    """
    # Default options
    if options is None:
        options = {
            "parse_tables": True,
            "parse_figures": True,
            "parse_equations": True,
            "output_format": "markdown",
            "chunk_size": None,  # Let Reducto handle chunking
        }
    
    # Upload file
    logger.info(f"Uploading {file_path} to Reducto...")
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.post(
            "https://api.reducto.ai/v1/documents",
            files=files,
            headers=headers,
            data={"options": json.dumps(options)},
        )
    
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    result = response.json()
    document_id = result["document_id"]
    
    logger.info(f"Document ID: {document_id}")
    
    # Wait for processing if requested
    if wait_for_completion:
        logger.info("Waiting for processing to complete...")
        start_time = time.time()
        
        while True:
            # Check status
            status_response = requests.get(
                f"https://api.reducto.ai/v1/documents/{document_id}/status",
                headers=headers,
            )
            
            if status_response.status_code != 200:
                raise Exception(f"Status check failed: {status_response.text}")
            
            status = status_response.json()
            
            if status["status"] == "completed":
                break
            elif status["status"] == "failed":
                raise Exception(f"Processing failed: {status.get('error')}")
            
            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"Processing exceeded {max_wait_time} seconds")
            
            time.sleep(2)
    
    # Get results
    logger.info("Retrieving extraction results...")
    
    results_response = requests.get(
        f"https://api.reducto.ai/v1/documents/{document_id}/content",
        headers=headers,
    )
    
    if results_response.status_code != 200:
        raise Exception(f"Failed to get results: {results_response.text}")
    
    content_data = results_response.json()
    
    # Build response
    metadata = {
        "source": "reducto",
        "document_id": document_id,
        "num_pages": content_data.get("num_pages", 0),
        "language": content_data.get("language"),
        "confidence": content_data.get("confidence"),
    }
    
    # Count extracted elements
    if "elements" in content_data:
        element_types = {}
        for element in content_data["elements"]:
            elem_type = element.get("type", "unknown")
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        metadata["element_types"] = element_types
    
    return {
        "content": content_data.get("content", ""),
        "metadata": metadata,
        "elements": content_data.get("elements", []),
        "chunks": content_data.get("chunks", []),
        "tables": content_data.get("tables", []),
        "figures": content_data.get("figures", []),
        "equations": content_data.get("equations", []),
    }


def create_frames_from_reducto(
    file_path: str,
    api_key: str,
    chunk_size: Optional[int] = None,
    include_specialized_frames: bool = False,
    **reducto_options
) -> List[FrameRecord]:
    """
    Create FrameRecords from Reducto extraction.
    
    Args:
        file_path: Path to document
        api_key: Reducto API key
        chunk_size: Optional chunk size for additional splitting
        include_specialized_frames: Create separate frames for tables/figures
        **reducto_options: Additional Reducto options
        
    Returns:
        List of FrameRecord objects
    """
    # Extract with Reducto
    result = extract_with_reducto(file_path, api_key, options=reducto_options)
    
    frames = []
    base_uri = file_path
    
    # Main content frame(s)
    main_content = result["content"]
    base_metadata = result["metadata"].copy()
    
    if chunk_size and len(main_content) > chunk_size:
        # Additional chunking if needed
        chunks = ChunkingMixin.chunk_text(
            main_content,
            chunk_size=chunk_size,
            chunk_overlap=50,
            splitter_type="markdown",  # Reducto usually outputs markdown
        )
        
        for i, chunk in enumerate(chunks):
            frame_metadata = base_metadata.copy()
            frame_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            
            frame = FrameRecord(
                uri=f"{base_uri}#chunk-{i}",
                title=Path(file_path).stem,
                content=chunk,
                metadata=frame_metadata,
                record_type="document",
            )
            frames.append(frame)
    else:
        # Single frame for main content
        frame = FrameRecord(
            uri=base_uri,
            title=Path(file_path).stem,
            content=main_content,
            metadata=base_metadata,
            record_type="document",
        )
        frames.append(frame)
    
    # Specialized frames for tables, figures, equations
    if include_specialized_frames:
        # Table frames
        for i, table in enumerate(result.get("tables", [])):
            table_metadata = {
                "source": "reducto",
                "type": "table",
                "table_index": i,
                "page": table.get("page"),
                "confidence": table.get("confidence"),
            }
            
            # Format table content
            table_content = table.get("markdown", "")
            if not table_content and "data" in table:
                # Convert structured data to markdown table
                table_content = _format_table_as_markdown(table["data"])
            
            frame = FrameRecord(
                uri=f"{base_uri}#table-{i}",
                title=f"Table {i+1} - {Path(file_path).stem}",
                content=table_content,
                metadata=table_metadata,
                record_type="document",
                parent_uri=base_uri,
            )
            frames.append(frame)
        
        # Figure frames
        for i, figure in enumerate(result.get("figures", [])):
            figure_metadata = {
                "source": "reducto",
                "type": "figure",
                "figure_index": i,
                "page": figure.get("page"),
                "caption": figure.get("caption"),
                "figure_type": figure.get("figure_type"),
            }
            
            frame = FrameRecord(
                uri=f"{base_uri}#figure-{i}",
                title=f"Figure {i+1} - {Path(file_path).stem}",
                content=figure.get("caption", f"Figure {i+1}"),
                metadata=figure_metadata,
                record_type="document",
                parent_uri=base_uri,
            )
            frames.append(frame)
        
        # Equation frames
        for i, equation in enumerate(result.get("equations", [])):
            equation_metadata = {
                "source": "reducto",
                "type": "equation",
                "equation_index": i,
                "page": equation.get("page"),
                "latex": equation.get("latex"),
            }
            
            frame = FrameRecord(
                uri=f"{base_uri}#equation-{i}",
                title=f"Equation {i+1} - {Path(file_path).stem}",
                content=equation.get("latex", equation.get("text", f"Equation {i+1}")),
                metadata=equation_metadata,
                record_type="document",
                parent_uri=base_uri,
            )
            frames.append(frame)
    
    return frames


def _format_table_as_markdown(table_data: List[List[str]]) -> str:
    """Convert table data to markdown format."""
    if not table_data or not table_data[0]:
        return ""
    
    # Header
    markdown = "| " + " | ".join(str(cell) for cell in table_data[0]) + " |\n"
    markdown += "|" + "|".join(["---"] * len(table_data[0])) + "|\n"
    
    # Rows
    for row in table_data[1:]:
        markdown += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return markdown


def process_scientific_documents(
    folder_path: str,
    dataset_path: str,
    api_key: str,
    embed_model: str = "openai/text-embedding-3-small",
):
    """
    Process scientific documents with equations and figures.
    
    Args:
        folder_path: Folder containing documents
        dataset_path: ContextFrame dataset path
        api_key: Reducto API key
        embed_model: Embedding model
    """
    # Find scientific documents
    folder = Path(folder_path)
    pdf_files = list(folder.glob("**/*.pdf"))
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Initialize dataset
    dataset = FrameDataset(dataset_path)
    
    # Process with specialized handling
    for pdf_path in pdf_files:
        try:
            logger.info(f"Processing scientific document: {pdf_path}")
            
            # Extract with equation and figure parsing
            frames = create_frames_from_reducto(
                str(pdf_path),
                api_key=api_key,
                include_specialized_frames=True,
                parse_tables=True,
                parse_figures=True,
                parse_equations=True,
                output_format="markdown",
            )
            
            # Separate frames by type for different embedding strategies
            text_frames = [f for f in frames if f.metadata.get("type") != "equation"]
            equation_frames = [f for f in frames if f.metadata.get("type") == "equation"]
            
            # Embed text content normally
            if text_frames:
                embedded_text = embed_frames(text_frames, model=embed_model)
                dataset.add(embedded_text)
            
            # Equations might need special handling
            if equation_frames:
                # Could use a different model or preprocessing
                embedded_equations = embed_frames(equation_frames, model=embed_model)
                dataset.add(embedded_equations)
            
            logger.info(f"Added {len(frames)} frames from {pdf_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
    
    return dataset


def compare_with_native_extraction():
    """
    Compare Reducto extraction with native extraction.
    """
    from contextframe.extract import TextFileExtractor
    
    # Simple text file
    text_file = "sample.txt"
    
    # Native extraction
    print("Native extraction:")
    extractor = TextFileExtractor()
    native_result = extractor.extract(text_file)
    print(f"Content length: {len(native_result.content)}")
    print(f"Metadata: {native_result.metadata}")
    
    # Reducto extraction (would handle PDFs, complex layouts, etc.)
    api_key = os.getenv("REDUCTO_API_KEY")
    if api_key:
        print("\nReducto extraction:")
        try:
            reducto_result = extract_with_reducto(text_file, api_key)
            print(f"Content length: {len(reducto_result['content'])}")
            print(f"Metadata: {reducto_result['metadata']}")
            print(f"Additional elements: {list(reducto_result.keys())}")
        except Exception as e:
            print(f"Reducto extraction failed: {e}")
    
    print("\nKey differences:")
    print("- Reducto handles complex formats (PDF, DOCX, etc.)")
    print("- Reducto extracts tables, figures, equations separately")
    print("- Reducto provides confidence scores and language detection")
    print("- Native extraction is faster for simple text files")


def async_batch_processing(
    file_paths: List[str],
    api_key: str,
    dataset_path: str,
):
    """
    Process multiple documents asynchronously with Reducto.
    
    Args:
        file_paths: List of document paths
        api_key: Reducto API key
        dataset_path: ContextFrame dataset path
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Submit all documents
    document_ids = []
    for file_path in file_paths:
        logger.info(f"Submitting {file_path}...")
        
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            response = requests.post(
                "https://api.reducto.ai/v1/documents",
                files=files,
                headers=headers,
                data={"options": json.dumps({"output_format": "markdown"})},
            )
        
        if response.status_code == 200:
            doc_id = response.json()["document_id"]
            document_ids.append((file_path, doc_id))
        else:
            logger.error(f"Failed to submit {file_path}: {response.text}")
    
    # Wait for all to complete
    logger.info(f"Waiting for {len(document_ids)} documents to process...")
    
    completed = []
    while document_ids:
        remaining = []
        for file_path, doc_id in document_ids:
            status_response = requests.get(
                f"https://api.reducto.ai/v1/documents/{doc_id}/status",
                headers=headers,
            )
            
            if status_response.status_code == 200:
                status = status_response.json()
                if status["status"] == "completed":
                    completed.append((file_path, doc_id))
                elif status["status"] != "failed":
                    remaining.append((file_path, doc_id))
            else:
                logger.error(f"Status check failed for {file_path}")
        
        document_ids = remaining
        if document_ids:
            time.sleep(2)
    
    # Process completed documents
    dataset = FrameDataset(dataset_path)
    for file_path, doc_id in completed:
        logger.info(f"Processing results for {file_path}...")
        # Retrieve and process results
        # ... (similar to create_frames_from_reducto)
    
    return dataset


if __name__ == "__main__":
    # Example 1: Process a single document
    api_key = os.getenv("REDUCTO_API_KEY")
    if api_key:
        frames = create_frames_from_reducto(
            "research_paper.pdf",
            api_key=api_key,
            chunk_size=1000,
            parse_equations=True,
            parse_figures=True,
        )
        print(f"Created {len(frames)} frames with Reducto")
    else:
        print("Set REDUCTO_API_KEY environment variable")
    
    # Example 2: Process scientific documents (commented out)
    # if api_key:
    #     dataset = process_scientific_documents(
    #         folder_path="./scientific_papers",
    #         dataset_path="./scientific_docs.lance",
    #         api_key=api_key,
    #     )
    
    # Example 3: Compare with native extraction (commented out)
    # compare_with_native_extraction()
    
    # Example 4: Async batch processing (commented out)
    # if api_key:
    #     files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    #     dataset = async_batch_processing(
    #         files,
    #         api_key=api_key,
    #         dataset_path="./batch_docs.lance",
    #     )