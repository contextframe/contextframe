"""
TEI (Text Embeddings Inference) Integration Example

This example demonstrates how to use ContextFrame with Hugging Face's
Text Embeddings Inference (TEI) server for high-performance embeddings.

Requirements:
1. Docker installed (for running TEI server)
2. ContextFrame with TEI dependencies: pip install contextframe[embed]
3. Optional: GPU with CUDA support for best performance
"""

import os
import time
import numpy as np
from contextframe import FrameRecord, FrameDataset
from contextframe.embed import TEIProvider, create_embedder
from contextframe.extract import DirectoryExtractor


def start_tei_server_instructions():
    """Print instructions for starting TEI server."""
    print("=" * 70)
    print("TEI Server Setup Instructions")
    print("=" * 70)
    print("\nOption 1 - GPU deployment (recommended):")
    print("""
docker run --gpus all -p 8080:80 -v $PWD/data:/data \\
  ghcr.io/huggingface/text-embeddings-inference:1.7 \\
  --model-id BAAI/bge-base-en-v1.5
    """)
    
    print("\nOption 2 - CPU deployment:")
    print("""
docker run -p 8080:80 -v $PWD/data:/data \\
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.7 \\
  --model-id BAAI/bge-base-en-v1.5
    """)
    
    print("\nOption 3 - Docker Compose (save as docker-compose.yml):")
    print("""
version: '3.8'
services:
  tei:
    image: ghcr.io/huggingface/text-embeddings-inference:1.7
    ports:
      - "8080:80"
    volumes:
      - ./models:/data
    command: --model-id BAAI/bge-base-en-v1.5
    """)
    print("\nThen run: docker-compose up")
    print("=" * 70)


def check_tei_server(api_base: str = "http://localhost:8080") -> bool:
    """Check if TEI server is running."""
    try:
        provider = TEIProvider(model="test", api_base=api_base)
        health = provider.health_check()
        return health["status"] == "healthy"
    except Exception as e:
        print(f"TEI server not available: {e}")
        return False


def basic_embedding_example():
    """Basic example of using TEI for embeddings."""
    print("\n" + "=" * 70)
    print("Basic TEI Embedding Example")
    print("=" * 70)
    
    # Create TEI provider
    provider = TEIProvider(
        model="BAAI/bge-base-en-v1.5",  # Model running on TEI server
        api_base="http://localhost:8080"
    )
    
    # Single text embedding
    text = "ContextFrame provides efficient document management for LLMs"
    result = provider.embed(text)
    
    print(f"\nEmbedded text: '{text}'")
    print(f"Embedding dimension: {result.dimension}")
    print(f"First 5 values: {result.embeddings[0][:5]}")
    
    # Batch embedding
    texts = [
        "Machine learning is transforming software development",
        "Large language models enable new applications",
        "Vector embeddings capture semantic meaning"
    ]
    
    batch_result = provider.embed(texts)
    print(f"\nBatch embedded {len(texts)} texts")
    print(f"All embeddings shape: ({len(batch_result.embeddings)}, {batch_result.dimension})")


def document_pipeline_example():
    """Example of processing documents with TEI embeddings."""
    print("\n" + "=" * 70)
    print("Document Pipeline with TEI")
    print("=" * 70)
    
    # Create sample documents
    documents = [
        {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "category": "AI/ML"
        },
        {
            "title": "Understanding Neural Networks",
            "content": "Neural networks are computing systems inspired by biological neural networks that constitute animal brains. They form the foundation of deep learning.",
            "category": "AI/ML"
        },
        {
            "title": "Natural Language Processing",
            "content": "NLP is a branch of AI that helps computers understand, interpret and manipulate human language. It bridges the gap between human communication and computer understanding.",
            "category": "NLP"
        }
    ]
    
    # Create embedder using factory function
    embedder = create_embedder(
        model="BAAI/bge-base-en-v1.5",
        provider_type="tei",
        api_base="http://localhost:8080",
        batch_size=100
    )
    
    # Process documents
    print("\nProcessing documents...")
    start_time = time.time()
    
    # Extract content for embedding
    texts = [doc["content"] for doc in documents]
    
    # Generate embeddings
    embedding_result = embedder.embed_batch(texts)
    
    # Create FrameRecords with embeddings
    frames = []
    for i, (doc, embedding) in enumerate(zip(documents, embedding_result.embeddings)):
        frame = FrameRecord.create(
            title=doc["title"],
            content=doc["content"],
            vector=np.array(embedding, dtype=np.float32),
            metadata={
                "category": doc["category"],
                "embedding_model": embedding_result.model,
                "embedding_dimension": embedding_result.dimension
            }
        )
        frames.append(frame)
    
    end_time = time.time()
    print(f"Processed {len(frames)} documents in {end_time - start_time:.2f} seconds")
    
    # Store in dataset
    dataset = FrameDataset.create("tei_demo.lance", embed_dim=embedding_result.dimension)
    dataset.add_many(frames)
    
    print(f"\nStored {len(frames)} documents in dataset")
    return dataset


def semantic_search_example(dataset: FrameDataset):
    """Example of semantic search using TEI embeddings."""
    print("\n" + "=" * 70)
    print("Semantic Search with TEI")
    print("=" * 70)
    
    # Create embedder for query
    embedder = create_embedder(
        model="BAAI/bge-base-en-v1.5",
        provider_type="tei",
        api_base="http://localhost:8080"
    )
    
    # Search queries
    queries = [
        "How do computers learn from data?",
        "What are artificial neurons?",
        "Language understanding in AI"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        
        # Embed query
        query_result = embedder.provider.embed(query)
        query_vector = np.array(query_result.embeddings[0], dtype=np.float32)
        
        # Search
        results = dataset.knn_search(query_vector, k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"  Title: {result.title}")
            print(f"  Score: {result.distance:.3f}")
            print(f"  Category: {result.metadata.get('category')}")
            print(f"  Preview: {result.content[:100]}...")


def performance_comparison():
    """Compare TEI performance with other providers."""
    print("\n" + "=" * 70)
    print("Performance Comparison")
    print("=" * 70)
    
    # Test data
    test_texts = [
        "The quick brown fox jumps over the lazy dog" * 10,  # ~100 tokens
        "Machine learning enables computers to learn from data" * 20,  # ~200 tokens
    ] * 50  # 100 total texts
    
    # TEI provider
    tei_provider = TEIProvider(
        model="BAAI/bge-base-en-v1.5",
        api_base="http://localhost:8080"
    )
    
    # Measure TEI performance
    print("\nTesting TEI performance...")
    start_time = time.time()
    tei_result = tei_provider.embed(test_texts)
    tei_time = time.time() - start_time
    
    print(f"TEI Results:")
    print(f"  Time: {tei_time:.2f} seconds")
    print(f"  Texts/second: {len(test_texts) / tei_time:.1f}")
    print(f"  Dimension: {tei_result.dimension}")
    
    # Compare with LiteLLM/OpenAI if available
    try:
        from contextframe.embed import LiteLLMProvider
        
        if os.getenv("OPENAI_API_KEY"):
            print("\nTesting OpenAI performance...")
            openai_provider = LiteLLMProvider(model="openai/text-embedding-3-small")
            
            start_time = time.time()
            openai_result = openai_provider.embed(test_texts[:10])  # Test smaller batch
            openai_time = time.time() - start_time
            
            print(f"\nOpenAI Results (10 texts):")
            print(f"  Time: {openai_time:.2f} seconds")
            print(f"  Texts/second: {10 / openai_time:.1f}")
            print(f"  Dimension: {openai_result.dimension}")
    except Exception as e:
        print(f"\nOpenAI comparison skipped: {e}")


def advanced_configuration_example():
    """Example of advanced TEI configuration."""
    print("\n" + "=" * 70)
    print("Advanced TEI Configuration")
    print("=" * 70)
    
    # Custom configuration
    provider = TEIProvider(
        model="BAAI/bge-base-en-v1.5",
        api_base=os.getenv("TEI_API_BASE", "http://localhost:8080"),
        api_key=os.getenv("TEI_API_KEY"),  # For secured instances
        timeout=60.0,  # Longer timeout for large batches
        max_retries=5,  # More retries for production
        truncate=True,  # Handle long inputs
        normalize=True  # L2 normalize for cosine similarity
    )
    
    # Get model information
    info = provider.get_model_info()
    print("\nTEI Server Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test with long text
    long_text = " ".join(["This is a long document."] * 200)
    print(f"\nTesting with long text ({len(long_text)} characters)...")
    
    result = provider.embed(long_text)
    print(f"Successfully embedded long text")
    print(f"Embedding dimension: {result.dimension}")


def main():
    """Run all TEI examples."""
    print("\n" + "=" * 70)
    print("ContextFrame TEI Integration Examples")
    print("=" * 70)
    
    # Check if TEI server is running
    if not check_tei_server():
        print("\n⚠️  TEI server is not running!")
        start_tei_server_instructions()
        print("\nPlease start the TEI server and run this example again.")
        return
    
    print("\n✅ TEI server is running!")
    
    # Run examples
    basic_embedding_example()
    dataset = document_pipeline_example()
    semantic_search_example(dataset)
    performance_comparison()
    advanced_configuration_example()
    
    print("\n" + "=" * 70)
    print("TEI integration examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()