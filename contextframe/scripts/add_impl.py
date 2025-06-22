#!/usr/bin/env python3
"""Implementation of contextframe-add command."""

import argparse
import mimetypes
import sys
import uuid
from contextframe.embed import LiteLLMProvider, create_frame_records_with_embeddings
from contextframe.frame import FrameDataset, FrameRecord
from pathlib import Path
from typing import List, Optional


def read_file_content(file_path: Path) -> tuple[str, bytes | None, str | None]:
    """Read file content and determine if it's text or binary."""
    # Guess MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))

    # Common text file extensions
    text_extensions = {
        '.txt',
        '.md',
        '.py',
        '.js',
        '.html',
        '.css',
        '.json',
        '.xml',
        '.yaml',
        '.yml',
        '.toml',
        '.ini',
        '.cfg',
        '.conf',
        '.sh',
        '.bash',
        '.rst',
        '.tex',
        '.csv',
        '.tsv',
        '.sql',
    }

    # Check if it's a text file
    is_text = file_path.suffix.lower() in text_extensions or (
        mime_type and mime_type.startswith('text/')
    )

    if is_text:
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            return content, None, None
        except UnicodeDecodeError:
            # Fall back to binary
            pass

    # Read as binary
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    # For binary files, we'll store a placeholder text
    text_content = f"Binary file: {file_path.name} ({mime_type or 'unknown type'})"

    return text_content, raw_data, mime_type


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping chunks."""
    if chunk_size <= 0:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at a sentence or paragraph boundary
        if end < len(text):
            # Look for sentence end
            last_period = chunk.rfind('. ')
            last_newline = chunk.rfind('\n')

            # Use the latest boundary found
            boundary = max(last_period, last_newline)
            if boundary > chunk_size * 0.5:  # Only use if it's not too early
                chunk = text[start : start + boundary + 1]
                end = start + boundary + 1

        chunks.append(chunk.strip())
        start = end - chunk_overlap

    return [c for c in chunks if c]  # Filter out empty chunks


def create_record_metadata(
    file_path: Path,
    record_type: str,
    identifier: str | None,
    collection: str | None,
    chunk_info: dict | None = None,
) -> dict:
    """Create metadata for a record."""
    metadata = {
        "identifier": identifier or str(uuid.uuid4()),
        "record_type": record_type,
        "title": file_path.name,
        "source": {"type": "file", "path": str(file_path.absolute())},
        "relationships": [],
    }

    # Add collection relationship if specified
    if collection:
        metadata["relationships"].append(
            {
                "relationship_type": "member_of",
                "target_type": "collection",
                "target_identifier": collection,
            }
        )

    # Add chunk information if this is a chunked document
    if chunk_info:
        metadata["custom_metadata"] = {
            "chunk_index": chunk_info["index"],
            "chunk_total": chunk_info["total"],
            "parent_document": chunk_info["parent_id"],
        }

        # Add relationship to parent document
        metadata["relationships"].append(
            {
                "relationship_type": "child",
                "target_type": "document",
                "target_identifier": chunk_info["parent_id"],
            }
        )

    return metadata


def add_file(dataset: FrameDataset, file_path: Path, args) -> list[str]:
    """Add a single file to the dataset. Returns list of added record IDs."""
    print(f"Adding file: {file_path}")

    # Read file content
    text_content, raw_data, raw_data_type = read_file_content(file_path)

    # Handle chunking if requested
    if args.chunk_size and args.chunk_size > 0:
        chunks = chunk_text(text_content, args.chunk_size, args.chunk_overlap or 0)

        if len(chunks) > 1:
            print(f"Splitting into {len(chunks)} chunks")

            # Create parent document ID
            parent_id = args.identifier or str(uuid.uuid4())
            added_ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{parent_id}_chunk_{i}"
                chunk_info = {"index": i, "total": len(chunks), "parent_id": parent_id}

                metadata = create_record_metadata(
                    file_path, "document", chunk_id, args.collection, chunk_info
                )

                record = FrameRecord(
                    text_content=chunk,
                    metadata=metadata,
                    raw_data=raw_data
                    if i == 0
                    else None,  # Only store raw data with first chunk
                    raw_data_type=raw_data_type if i == 0 else None,
                )

                # Add to dataset
                dataset.add([record])
                added_ids.append(chunk_id)

            return added_ids

    # Single document (no chunking)
    metadata = create_record_metadata(
        file_path, args.type, args.identifier, args.collection
    )

    record = FrameRecord(
        text_content=text_content,
        metadata=metadata,
        raw_data=raw_data,
        raw_data_type=raw_data_type,
    )

    # Generate embeddings if requested
    if args.embeddings:
        print("Generating embeddings...")
        import os

        model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")

        try:
            # Use the contextframe embedding integration
            records_with_embeddings = create_frame_records_with_embeddings(
                documents=[{"content": text_content, "metadata": metadata}], model=model
            )
            record = records_with_embeddings[0]
        except Exception as e:
            print(f"Warning: Failed to generate embeddings: {e}", file=sys.stderr)
            print("Adding document without embeddings.", file=sys.stderr)

    # Add to dataset
    dataset.add([record])
    return [metadata["identifier"]]


def add_directory(dataset: FrameDataset, dir_path: Path, args) -> list[str]:
    """Add all files in a directory to the dataset."""
    added_ids = []

    # Get all files recursively
    files = list(dir_path.rglob('*'))
    files = [f for f in files if f.is_file()]

    print(f"Found {len(files)} files in {dir_path}")

    for file_path in files:
        try:
            ids = add_file(dataset, file_path, args)
            added_ids.extend(ids)
        except Exception as e:
            print(f"Error adding {file_path}: {e}", file=sys.stderr)

    return added_ids


def main():
    """Main entry point for add command."""
    parser = argparse.ArgumentParser(
        description='Add documents to a ContextFrame dataset'
    )
    parser.add_argument('dataset', help='Path to the dataset')
    parser.add_argument('input_path', help='File or directory to add')
    parser.add_argument(
        '--type',
        default='document',
        choices=['document', 'collection_header', 'dataset_header'],
        help='Record type',
    )
    parser.add_argument('--collection', help='Add to collection with this name')
    parser.add_argument('--identifier', help='Custom identifier')
    parser.add_argument(
        '--embeddings', action='store_true', help='Generate embeddings for documents'
    )
    parser.add_argument('--chunk-size', type=int, help='Split documents into chunks')
    parser.add_argument(
        '--chunk-overlap', type=int, default=0, help='Overlap between chunks'
    )

    args = parser.parse_args()

    # Open the dataset
    try:
        dataset = FrameDataset.open(args.dataset)
    except Exception as e:
        print(f"Error opening dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert input path to Path object
    input_path = Path(args.input_path)

    # Add file(s)
    try:
        if input_path.is_file():
            added_ids = add_file(dataset, input_path, args)
        elif input_path.is_dir():
            added_ids = add_directory(dataset, input_path, args)
        else:
            print(
                f"Error: {input_path} is neither a file nor a directory",
                file=sys.stderr,
            )
            sys.exit(1)
    except Exception as e:
        print(f"Error adding documents: {e}", file=sys.stderr)
        sys.exit(1)

    # Report results
    print(f"\nSuccessfully added {len(added_ids)} record(s) to {args.dataset}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
