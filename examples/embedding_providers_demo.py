"""
Embedding Providers Demonstration

This example showcases various embedding providers and strategies
available through ContextFrame's LiteLLM integration.

Requirements:
    pip install contextframe[embed,extract]

    # For specific providers:
    export OPENAI_API_KEY="your-key"
    export COHERE_API_KEY="your-key"
    export VOYAGE_API_KEY="your-key"

    # For local embeddings:
    # Install Ollama: https://ollama.ai
    # Pull model: ollama pull nomic-embed-text
"""

import logging
import os
import time
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import LiteLLMProvider, embed_frames
from contextframe.extract import DirectoryExtractor
from contextframe.extract.chunking import semantic_splitter
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compare_embedding_providers():
    """Compare different embedding providers on the same content."""

    # Sample documents
    test_frames = [
        FrameRecord(
            uri="doc1.txt",
            content="Artificial intelligence is transforming how we work and live.",
            metadata={"type": "statement"},
        ),
        FrameRecord(
            uri="doc2.txt",
            content="Machine learning models require large amounts of data for training.",
            metadata={"type": "technical"},
        ),
        FrameRecord(
            uri="doc3.py",
            content="""def calculate_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))""",
            metadata={"type": "code"},
        ),
    ]

    providers = [
        {
            "name": "OpenAI Small",
            "model": "openai/text-embedding-3-small",
            "dimensions": 1536,
            "cost_per_million": 0.02,
        },
        {
            "name": "OpenAI Large",
            "model": "openai/text-embedding-3-large",
            "dimensions": 3072,
            "cost_per_million": 0.13,
        },
        {
            "name": "Cohere English",
            "model": "cohere/embed-english-v3.0",
            "dimensions": 1024,
            "cost_per_million": 0.10,
            "requires_api_key": "COHERE_API_KEY",
        },
        {
            "name": "Ollama Local",
            "model": "ollama/nomic-embed-text",
            "dimensions": 768,
            "cost_per_million": 0,
            "api_base": "http://localhost:11434",
        },
    ]

    results = []

    for provider_info in providers:
        # Skip if required API key not available
        if "requires_api_key" in provider_info:
            if not os.getenv(provider_info["requires_api_key"]):
                logger.warning(f"Skipping {provider_info['name']}: No API key")
                continue

        try:
            logger.info(f"\nTesting {provider_info['name']}...")
            start_time = time.time()

            # Create provider
            kwargs = {}
            if "api_base" in provider_info:
                kwargs["api_base"] = provider_info["api_base"]

            provider = LiteLLMProvider(model=provider_info["model"], **kwargs)

            # Embed frames
            embedded_frames = embed_frames(
                test_frames, model=provider_info["model"], **kwargs
            )

            elapsed = time.time() - start_time

            # Verify embeddings
            for frame in embedded_frames:
                if frame.embedding is None:
                    raise ValueError(f"No embedding for {frame.uri}")

            result = {
                "provider": provider_info["name"],
                "model": provider_info["model"],
                "success": True,
                "time": elapsed,
                "dimensions": len(embedded_frames[0].embedding),
                "cost_estimate": provider_info["cost_per_million"]
                * 0.001,  # Rough estimate
            }
            results.append(result)

            logger.info(f"✓ Success: {elapsed:.2f}s, {result['dimensions']} dimensions")

        except Exception as e:
            logger.error(f"✗ Failed: {e}")
            results.append(
                {
                    "provider": provider_info["name"],
                    "model": provider_info["model"],
                    "success": False,
                    "error": str(e),
                }
            )

    # Print comparison
    print("\n" + "=" * 60)
    print("EMBEDDING PROVIDER COMPARISON")
    print("=" * 60)

    for result in results:
        if result["success"]:
            print(f"\n{result['provider']}:")
            print(f"  Model: {result['model']}")
            print(f"  Dimensions: {result['dimensions']}")
            print(f"  Time: {result['time']:.2f}s")
            print(f"  Est. Cost: ${result['cost_estimate']:.4f}")
        else:
            print(f"\n{result['provider']}: FAILED - {result['error']}")


def demonstrate_multilingual_embedding():
    """Show multilingual embedding capabilities."""

    multilingual_frames = [
        FrameRecord(
            uri="en.txt", content="Hello, how are you?", metadata={"lang": "en"}
        ),
        FrameRecord(
            uri="es.txt", content="Hola, ¿cómo estás?", metadata={"lang": "es"}
        ),
        FrameRecord(
            uri="fr.txt",
            content="Bonjour, comment allez-vous?",
            metadata={"lang": "fr"},
        ),
        FrameRecord(
            uri="de.txt", content="Hallo, wie geht es dir?", metadata={"lang": "de"}
        ),
        FrameRecord(uri="zh.txt", content="你好，你好吗？", metadata={"lang": "zh"}),
        FrameRecord(
            uri="ja.txt", content="こんにちは、元気ですか？", metadata={"lang": "ja"}
        ),
    ]

    # Use multilingual model
    if os.getenv("COHERE_API_KEY"):
        logger.info("Using Cohere multilingual embeddings...")
        embedded = embed_frames(
            multilingual_frames,
            model="cohere/embed-multilingual-v3.0",
            input_type="search_document",
        )

        # Calculate cross-language similarities
        import numpy as np

        print("\nCross-language similarity (all asking 'Hello, how are you?'):")
        en_embedding = embedded[0].embedding

        for frame in embedded[1:]:
            similarity = np.dot(en_embedding, frame.embedding) / (
                np.linalg.norm(en_embedding) * np.linalg.norm(frame.embedding)
            )
            print(f"  English vs {frame.metadata['lang']}: {similarity:.3f}")
    else:
        logger.info("Cohere API key not found, using OpenAI...")
        embedded = embed_frames(
            multilingual_frames, model="openai/text-embedding-3-small"
        )


def demonstrate_code_embeddings():
    """Show code-optimized embeddings."""

    code_samples = [
        FrameRecord(
            uri="python_func.py",
            content="""def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
            metadata={"language": "python", "algorithm": "binary_search"},
        ),
        FrameRecord(
            uri="js_func.js",
            content="""function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}""",
            metadata={"language": "javascript", "algorithm": "binary_search"},
        ),
        FrameRecord(
            uri="bubble_sort.py",
            content="""def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr""",
            metadata={"language": "python", "algorithm": "bubble_sort"},
        ),
    ]

    # Use code-optimized model if available
    if os.getenv("VOYAGE_API_KEY"):
        logger.info("Using Voyage code embeddings...")
        model = "voyage/voyage-code-2"
    else:
        logger.info("Using OpenAI embeddings for code...")
        model = "openai/text-embedding-3-small"

    embedded_code = embed_frames(code_samples, model=model)

    # Find similar code across languages
    dataset = FrameDataset("code_embeddings.lance")
    dataset.add(embedded_code)

    # Search for similar algorithms
    query_frame = FrameRecord(uri="query", content="binary search implementation")
    query_embedded = embed_frames([query_frame], model=model)[0]

    results = dataset.search(query_embedding=query_embedded.embedding, limit=3)

    print("\nCode similarity search for 'binary search implementation':")
    for result in results:
        print(f"  {result.uri} (score: {result.score:.3f})")
        print(f"    Language: {result.metadata.get('language')}")
        print(f"    Algorithm: {result.metadata.get('algorithm')}")


def demonstrate_batch_processing():
    """Show efficient batch processing strategies."""

    # Generate many documents
    documents = []
    for i in range(500):
        documents.append(
            FrameRecord(
                uri=f"doc_{i}.txt",
                content=f"This is document number {i}. " * 20,  # ~100 tokens
                metadata={"index": i, "batch": i // 100},
            )
        )

    logger.info(f"Processing {len(documents)} documents in batches...")

    # Method 1: Automatic batching
    start = time.time()
    embedded_auto = embed_frames(
        documents,
        model="openai/text-embedding-3-small",
        batch_size=100,  # Process 100 at a time
        show_progress=True,
    )
    auto_time = time.time() - start

    logger.info(f"Automatic batching completed in {auto_time:.2f}s")

    # Method 2: Manual batching with different models
    start = time.time()
    all_embedded = []

    for batch_idx in range(5):
        batch_docs = [d for d in documents if d.metadata["batch"] == batch_idx]

        # Use different strategies for different batches
        if batch_idx == 0:
            # High priority - use best model
            embedded_batch = embed_frames(
                batch_docs, model="openai/text-embedding-3-large"
            )
        else:
            # Lower priority - use cheaper model
            embedded_batch = embed_frames(
                batch_docs, model="openai/text-embedding-3-small"
            )

        all_embedded.extend(embedded_batch)

    manual_time = time.time() - start
    logger.info(f"Manual batching completed in {manual_time:.2f}s")


def demonstrate_fallback_strategy():
    """Show robust embedding with fallbacks."""

    frames = [
        FrameRecord(uri="important.txt", content="Critical business document content")
    ]

    # Define fallback chain
    models = [
        ("openai/text-embedding-3-small", {"api_key": os.getenv("OPENAI_API_KEY")}),
        ("cohere/embed-english-v3.0", {"api_key": os.getenv("COHERE_API_KEY")}),
        ("ollama/nomic-embed-text", {"api_base": "http://localhost:11434"}),
    ]

    embedded = None
    for model, kwargs in models:
        try:
            logger.info(f"Trying {model}...")
            embedded = embed_frames(frames, model=model, **kwargs)
            logger.info(f"Success with {model}")
            break
        except Exception as e:
            logger.warning(f"Failed with {model}: {e}")
            continue

    if embedded:
        print("\nSuccessfully embedded with fallback strategy")
        print(f"Embedding dimensions: {len(embedded[0].embedding)}")
    else:
        print("\nAll embedding methods failed!")


def demonstrate_search_vs_document_embeddings():
    """Show the difference between search query and document embeddings."""

    if not os.getenv("COHERE_API_KEY"):
        logger.info("Cohere API key not found, skipping search vs document demo")
        return

    # Document content
    documents = [
        FrameRecord(
            uri="physics.txt",
            content="Quantum mechanics is the mathematical description of the motion and interaction of subatomic particles.",
            metadata={"subject": "physics"},
        ),
        FrameRecord(
            uri="biology.txt",
            content="DNA replication is the biological process of producing two identical replicas from one original DNA molecule.",
            metadata={"subject": "biology"},
        ),
    ]

    # Embed as documents
    doc_embedded = embed_frames(
        documents,
        model="cohere/embed-english-v3.0",
        input_type="search_document",  # Optimize for storage
    )

    # Create dataset
    dataset = FrameDataset("search_demo.lance")
    dataset.add(doc_embedded)

    # Search queries
    queries = [
        "what is quantum physics?",
        "how does DNA copying work?",
        "subatomic particle behavior",
    ]

    for query in queries:
        # Create query embedding
        query_frame = FrameRecord(uri="query", content=query)
        query_embedded = embed_frames(
            [query_frame],
            model="cohere/embed-english-v3.0",
            input_type="search_query",  # Optimize for search
        )[0]

        # Search
        results = dataset.search(query_embedding=query_embedded.embedding, limit=2)

        print(f"\nQuery: '{query}'")
        for result in results:
            print(f"  → {result.uri} (score: {result.score:.3f})")


def main():
    """Run all demonstrations."""

    print("🚀 ContextFrame Embedding Providers Demo\n")

    demos = [
        ("Provider Comparison", compare_embedding_providers),
        ("Multilingual Embeddings", demonstrate_multilingual_embedding),
        ("Code Embeddings", demonstrate_code_embeddings),
        ("Batch Processing", demonstrate_batch_processing),
        ("Fallback Strategy", demonstrate_fallback_strategy),
        ("Search vs Document", demonstrate_search_vs_document_embeddings),
    ]

    for name, demo_func in demos:
        print(f"\n{'=' * 60}")
        print(f"Demo: {name}")
        print(f"{'=' * 60}")

        try:
            demo_func()
        except Exception as e:
            logger.error(f"Demo failed: {e}")

        time.sleep(1)  # Brief pause between demos

    print("\n✅ All demos completed!")
    print("\nKey takeaways:")
    print("1. LiteLLM provides unified access to 100+ embedding providers")
    print("2. Choose models based on quality, cost, and latency requirements")
    print("3. Use specialized models for code or multilingual content")
    print("4. Implement fallback strategies for production reliability")
    print("5. Optimize batch sizes for your provider")


if __name__ == "__main__":
    main()
