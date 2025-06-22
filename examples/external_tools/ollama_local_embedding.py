"""
Local Embedding Pipeline using Ollama and ContextFrame

This example demonstrates how to use locally-hosted embedding models
through Ollama with ContextFrame's LiteLLM integration.

Requirements:
    1. Install Ollama: https://ollama.ai
    2. Pull an embedding model: ollama pull nomic-embed-text
    3. Install dependencies: pip install contextframe[extract,embed]

Popular Ollama embedding models:
    - nomic-embed-text: High-quality 768-dim embeddings
    - mxbai-embed-large: 1024-dim embeddings
    - all-minilm: Sentence transformers model
"""

import logging
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames
from contextframe.extract import BatchExtractor
from pathlib import Path
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            embedding_models = [m for m in models if "embed" in m["name"]]
            if embedding_models:
                logger.info(
                    f"Found embedding models: {[m['name'] for m in embedding_models]}"
                )
                return True
            else:
                logger.warning(
                    "No embedding models found. Run: ollama pull nomic-embed-text"
                )
                return False
    except Exception as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        logger.info("Make sure Ollama is running: ollama serve")
        return False


def process_local_documents(
    folder_path: str,
    dataset_path: str = "local_docs.lance",
    model: str = "ollama/nomic-embed-text",
    chunk_size: int = 1000,
    batch_size: int = 50,
):
    """
    Process documents using local Ollama embeddings.

    Args:
        folder_path: Path to folder containing documents
        dataset_path: Path for ContextFrame dataset
        model: Ollama model name (prefix with ollama/)
        chunk_size: Size of text chunks
        batch_size: Number of documents to process at once
    """
    # Check Ollama connection
    if not test_ollama_connection():
        return

    # Initialize dataset
    dataset = FrameDataset(dataset_path)

    # Set up batch extractor
    extractor = BatchExtractor(
        patterns=["*.txt", "*.md", "*.json"],
        recursive=True,
        chunk_size=chunk_size,
        use_threads=True,
        max_workers=4,
    )

    # Extract documents
    logger.info(f"Extracting documents from {folder_path}...")
    results = extractor.extract_folder(folder_path)

    # Convert to FrameRecords
    frames = []
    for result in results:
        if result.success:
            if result.chunks:
                # Handle chunked content
                for i, chunk in enumerate(result.chunks):
                    frame = FrameRecord(
                        uri=f"{result.source}#chunk-{i}",
                        title=Path(result.source).stem,
                        content=chunk,
                        metadata={
                            **result.metadata,
                            "chunk_index": i,
                            "total_chunks": len(result.chunks),
                        },
                        record_type="document",
                    )
                    frames.append(frame)
            else:
                # Single document
                frame = FrameRecord(
                    uri=result.source,
                    title=Path(result.source).stem,
                    content=result.content,
                    metadata=result.metadata,
                    record_type="document",
                )
                frames.append(frame)

    logger.info(f"Created {len(frames)} frames from {len(results)} documents")

    # Embed frames in batches
    total_embedded = 0
    for i in range(0, len(frames), batch_size):
        batch = frames[i : i + batch_size]
        logger.info(f"Embedding batch {i // batch_size + 1} ({len(batch)} frames)...")

        try:
            embedded_batch = embed_frames(
                batch,
                model=model,
                show_progress=True,
            )
            dataset.add(embedded_batch)
            total_embedded += len(embedded_batch)
        except Exception as e:
            logger.error(f"Failed to embed batch: {e}")

    logger.info(f"Successfully embedded {total_embedded} frames")
    return dataset


def compare_embedding_models(
    test_text: str = "Machine learning is a subset of artificial intelligence.",
):
    """
    Compare different local embedding models.

    Args:
        test_text: Text to embed with different models
    """
    models = [
        "ollama/nomic-embed-text",
        "ollama/mxbai-embed-large",
        "ollama/all-minilm",
    ]

    for model in models:
        try:
            frame = FrameRecord(
                uri="test",
                content=test_text,
                record_type="document",
            )

            embedded = embed_frames([frame], model=model)
            embedding = embedded[0].embedding

            print(f"\n{model}:")
            print(f"  Dimensions: {len(embedding)}")
            print(f"  First 5 values: {embedding[:5]}")

        except Exception as e:
            print(f"\n{model}: Failed - {e}")


def semantic_search_example(dataset_path: str = "local_docs.lance"):
    """
    Example of semantic search using local embeddings.

    Args:
        dataset_path: Path to existing dataset
    """
    dataset = FrameDataset(dataset_path)

    queries = [
        "How to install Python packages",
        "Machine learning algorithms",
        "Database optimization techniques",
    ]

    for query in queries:
        print(f"\n\nSearching for: '{query}'")
        print("-" * 50)

        results = dataset.search(
            query=query,
            limit=3,
            search_type="vector",  # Pure vector search
        )

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title or result.uri}")
            print(f"   Score: {result.score:.3f}")
            print(f"   Preview: {result.content[:150]}...")


def process_with_custom_chunking(
    file_path: str,
    model: str = "ollama/nomic-embed-text",
):
    """
    Example using semantic text splitting with token counting.

    Args:
        file_path: Path to document
        model: Embedding model
    """
    from contextframe.extract import TextFileExtractor
    from contextframe.extract.chunking import ChunkingMixin

    # Extract with semantic chunking
    extractor = TextFileExtractor()

    # Mix in chunking capability
    class ChunkingTextExtractor(TextFileExtractor, ChunkingMixin):
        pass

    chunking_extractor = ChunkingTextExtractor()

    # Extract with token-based chunking
    result = chunking_extractor.extract_with_chunking(
        file_path,
        chunk_size=256,  # tokens
        tokenizer_model="gpt-3.5-turbo",  # Use tiktoken for counting
        splitter_type="markdown" if file_path.endswith(".md") else "text",
    )

    if result.success and result.chunks:
        frames = []
        for i, chunk in enumerate(result.chunks):
            frame = FrameRecord(
                uri=f"{file_path}#chunk-{i}",
                title=Path(file_path).stem,
                content=chunk,
                metadata={
                    "chunk_index": i,
                    "total_chunks": len(result.chunks),
                    "tokenizer": "gpt-3.5-turbo",
                },
                record_type="document",
            )
            frames.append(frame)

        # Embed with local model
        embedded = embed_frames(frames, model=model)

        print(f"Created {len(embedded)} embedded chunks")
        print(f"First chunk preview: {embedded[0].content[:100]}...")

        return embedded


if __name__ == "__main__":
    # Example 1: Test Ollama connection
    print("Testing Ollama connection...")
    test_ollama_connection()

    # Example 2: Compare embedding models (commented out)
    # compare_embedding_models()

    # Example 3: Process a folder of documents (commented out)
    # dataset = process_local_documents(
    #     folder_path="./documents",
    #     model="ollama/nomic-embed-text",
    #     chunk_size=1000,
    # )

    # Example 4: Search embedded documents (commented out)
    # semantic_search_example("local_docs.lance")

    # Example 5: Custom chunking with token counting (commented out)
    # process_with_custom_chunking(
    #     "README.md",
    #     model="ollama/nomic-embed-text",
    # )
