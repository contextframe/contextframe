# Embedding Providers Guide

This guide covers how to use various embedding providers with ContextFrame through our LiteLLM integration.

## Overview

ContextFrame provides unified embedding support through LiteLLM, enabling access to 100+ embedding providers with a single interface. This includes OpenAI, Anthropic, Cohere, local models via Ollama, and many more.

## Quick Start

```python
from contextframe import FrameRecord, FrameDataset
from contextframe.embed import embed_frames

# Create frames
frames = [
    FrameRecord(
        uri="doc1.txt",
        content="This is a sample document about machine learning.",
        metadata={"type": "tutorial"}
    ),
    FrameRecord(
        uri="doc2.txt",
        content="Deep learning is a subset of machine learning.",
        metadata={"type": "definition"}
    )
]

# Embed with OpenAI (default)
embedded_frames = embed_frames(frames, model="openai/text-embedding-3-small")

# Store in dataset
dataset = FrameDataset("my_docs.lance")
dataset.add(embedded_frames)
```

## LiteLLM Integration

### Why LiteLLM?

1. **Unified Interface**: Single API for all providers
2. **Provider Flexibility**: Switch providers without code changes
3. **Automatic Retries**: Built-in error handling
4. **Cost Tracking**: Monitor embedding costs
5. **Caching Support**: Reduce redundant API calls

### Basic Usage

```python
from contextframe.embed import LiteLLMProvider

# Initialize provider
provider = LiteLLMProvider(
    model="openai/text-embedding-3-small",
    api_key="your-api-key"  # Optional if set in environment
)

# Embed single text
embedding = provider.embed("Hello, world!")

# Embed multiple texts (batch)
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = provider.embed_batch(texts, batch_size=100)
```

## Provider-Specific Examples

### OpenAI

```python
# Latest models with different dimensions
models = [
    "openai/text-embedding-3-small",  # 1536 dimensions, best value
    "openai/text-embedding-3-large",  # 3072 dimensions, highest quality
    "openai/text-embedding-ada-002",  # 1536 dimensions, legacy
]

# With dimension reduction (3-large only)
provider = LiteLLMProvider(
    model="openai/text-embedding-3-large",
    dimensions=1024  # Reduce from 3072 to 1024
)

# Environment setup
# export OPENAI_API_KEY="your-key"
```

### Anthropic (Voyage AI)

```python
# Anthropic's embedding models via Voyage
provider = LiteLLMProvider(
    model="voyage/voyage-2",  # Or voyage-large-2, voyage-code-2
    api_key=os.getenv("VOYAGE_API_KEY")
)

# Best for: General text, semantic search
# Dimensions: 1024 (voyage-2), 1536 (voyage-large-2)
```

### Cohere

```python
# Cohere embedding models
models = [
    "cohere/embed-english-v3.0",     # English only, 1024 dims
    "cohere/embed-multilingual-v3.0", # 100+ languages, 1024 dims
    "cohere/embed-english-light-v3.0", # Lightweight, 384 dims
]

provider = LiteLLMProvider(
    model="cohere/embed-english-v3.0",
    api_key=os.getenv("COHERE_API_KEY"),
    input_type="search_document"  # or "search_query"
)

# Cohere requires specifying input_type
embedded_docs = embed_frames(
    frames, 
    model="cohere/embed-english-v3.0",
    input_type="search_document"
)
```

### Local Models (Ollama)

```python
# Using Ollama for local embeddings
provider = LiteLLMProvider(
    model="ollama/nomic-embed-text",
    api_base="http://localhost:11434"  # Ollama default
)

# Popular Ollama embedding models:
# - ollama/nomic-embed-text (768 dims)
# - ollama/mxbai-embed-large (1024 dims)
# - ollama/all-minilm (384 dims)

# No API key needed for local models
embedded_frames = embed_frames(frames, model="ollama/nomic-embed-text")
```

### Hugging Face

```python
# Via Hugging Face Inference API
provider = LiteLLMProvider(
    model="huggingface/sentence-transformers/all-MiniLM-L6-v2",
    api_key=os.getenv("HUGGINGFACE_API_KEY")
)

# Via Hugging Face Inference Endpoints
provider = LiteLLMProvider(
    model="huggingface/https://your-endpoint.endpoints.huggingface.cloud",
    api_key=os.getenv("HUGGINGFACE_API_KEY")
)
```

### AWS Bedrock

```python
# Bedrock embedding models
provider = LiteLLMProvider(
    model="bedrock/amazon.titan-embed-text-v1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region_name="us-east-1"
)

# Also supports Cohere models on Bedrock
provider = LiteLLMProvider(
    model="bedrock/cohere.embed-english-v3"
)
```

### Azure OpenAI

```python
# Azure-hosted OpenAI models
provider = LiteLLMProvider(
    model="azure/your-deployment-name",
    api_key=os.getenv("AZURE_API_KEY"),
    api_base="https://your-resource.openai.azure.com",
    api_version="2024-02-01"
)
```

## Advanced Usage

### Batch Processing with Progress

```python
from contextframe.embed import embed_frames
from pathlib import Path

# Large document set
documents = Path("./documents").glob("**/*.txt")
frames = []

for doc_path in documents:
    with open(doc_path) as f:
        frames.append(FrameRecord(
            uri=str(doc_path),
            content=f.read()
        ))

# Embed with progress tracking
embedded_frames = embed_frames(
    frames,
    model="openai/text-embedding-3-small",
    batch_size=100,  # Process 100 at a time
    show_progress=True  # Display progress bar
)
```

### Custom Embedding Strategies

```python
from contextframe.embed import EmbeddingConfig

# Configure embedding behavior
config = EmbeddingConfig(
    chunk_overlap_for_embedding=50,  # Token overlap between chunks
    max_tokens_per_chunk=8192,       # Max tokens per embedding
    embedding_batch_size=100,        # API batch size
    retry_attempts=3,                # Retry failed embeddings
    cache_embeddings=True            # Cache results
)

# Apply configuration
embedded_frames = embed_frames(
    frames,
    model="openai/text-embedding-3-small",
    config=config
)
```

### Multi-Model Embeddings

```python
# Use different models for different content types
def smart_embed(frames):
    code_frames = [f for f in frames if f.metadata.get("type") == "code"]
    text_frames = [f for f in frames if f.metadata.get("type") != "code"]
    
    # Code-specific embeddings
    if code_frames:
        code_embedded = embed_frames(
            code_frames,
            model="voyage/voyage-code-2"  # Optimized for code
        )
    
    # Text embeddings
    if text_frames:
        text_embedded = embed_frames(
            text_frames,
            model="openai/text-embedding-3-small"
        )
    
    return code_embedded + text_embedded
```

## Cost Optimization

### 1. Choose the Right Model

| Provider | Model | Dimensions | Cost per 1M tokens | Best For |
|----------|-------|------------|-------------------|----------|
| OpenAI | text-embedding-3-small | 1536 | $0.02 | General use, best value |
| OpenAI | text-embedding-3-large | 3072 | $0.13 | Highest quality |
| Cohere | embed-english-light-v3.0 | 384 | $0.02 | Budget option |
| Ollama | nomic-embed-text | 768 | Free | Local deployment |

### 2. Implement Caching

```python
from contextframe.embed import CachedLiteLLMProvider

# Use cached provider to avoid re-embedding
provider = CachedLiteLLMProvider(
    model="openai/text-embedding-3-small",
    cache_dir=".embedding_cache"
)

# Embeddings are cached locally
embedded_frames = embed_frames(frames, provider=provider)
```

### 3. Batch Efficiently

```python
# Optimal batch sizes by provider
batch_sizes = {
    "openai": 100,      # API limit
    "cohere": 96,       # API limit
    "anthropic": 100,   # Recommended
    "ollama": 10,       # Local processing
}

embedded_frames = embed_frames(
    frames,
    model="openai/text-embedding-3-small",
    batch_size=batch_sizes["openai"]
)
```

## Error Handling and Debugging

### Common Issues

1. **Rate Limits**
```python
# LiteLLM handles retries automatically
provider = LiteLLMProvider(
    model="openai/text-embedding-3-small",
    max_retries=5,
    retry_delay=1.0  # Exponential backoff
)
```

2. **Token Limits**
```python
# Handle large documents
from contextframe.extract.chunking import semantic_splitter

# Pre-chunk large documents
if len(frame.content) > 8000:  # Rough token estimate
    chunks = semantic_splitter(
        [frame.content],
        chunk_size=4000,
        chunk_overlap=200
    )
    # Create frames for each chunk
```

3. **Provider Errors**
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# LiteLLM will log detailed error information
try:
    embedded = embed_frames(frames, model="openai/text-embedding-3-small")
except Exception as e:
    print(f"Embedding failed: {e}")
    # Fallback to local model
    embedded = embed_frames(frames, model="ollama/nomic-embed-text")
```

## Best Practices

1. **Choose Models Wisely**
   - Use smaller models for large-scale indexing
   - Use larger models for high-precision retrieval
   - Use specialized models for code or multilingual content

2. **Optimize for Your Use Case**
   - Semantic search: Focus on quality (larger models)
   - Document clustering: Balance quality and cost
   - Real-time applications: Prioritize speed (local models)

3. **Monitor Usage**
   ```python
   # Track embedding costs
   from contextframe.embed import track_embedding_usage
   
   with track_embedding_usage() as tracker:
       embedded_frames = embed_frames(frames, model="openai/text-embedding-3-small")
   
   print(f"Tokens used: {tracker.total_tokens}")
   print(f"Estimated cost: ${tracker.estimated_cost}")
   ```

4. **Handle Failures Gracefully**
   - Always have a fallback model
   - Cache embeddings to avoid re-processing
   - Monitor for API deprecations

## Complete Example

Here's a production-ready embedding pipeline:

```python
import os
from pathlib import Path
from contextframe import FrameDataset, FrameRecord
from contextframe.embed import embed_frames, LiteLLMProvider
from contextframe.extract import DirectoryExtractor
import logging

logging.basicConfig(level=logging.INFO)

def create_embedded_dataset(
    directory: str,
    dataset_path: str,
    model: str = "openai/text-embedding-3-small",
    fallback_model: str = "ollama/nomic-embed-text"
):
    """Create an embedded dataset from a directory of documents."""
    
    # Extract documents
    extractor = DirectoryExtractor()
    extraction_result = extractor.extract(directory)
    
    # Convert to frames
    frames = []
    for doc in extraction_result.documents:
        frames.append(FrameRecord(
            uri=doc.uri,
            title=doc.title,
            content=doc.content,
            metadata=doc.metadata
        ))
    
    # Embed with fallback
    try:
        logging.info(f"Embedding {len(frames)} documents with {model}")
        embedded_frames = embed_frames(
            frames,
            model=model,
            batch_size=100,
            show_progress=True
        )
    except Exception as e:
        logging.warning(f"Primary model failed: {e}")
        logging.info(f"Falling back to {fallback_model}")
        embedded_frames = embed_frames(
            frames,
            model=fallback_model,
            show_progress=True
        )
    
    # Store in dataset
    dataset = FrameDataset(dataset_path)
    dataset.add(embedded_frames)
    
    logging.info(f"Created dataset with {len(embedded_frames)} embedded documents")
    return dataset

# Usage
if __name__ == "__main__":
    dataset = create_embedded_dataset(
        directory="./documents",
        dataset_path="./embedded_docs.lance",
        model="openai/text-embedding-3-small"
    )
```

## Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/docs/embedding/supported_embedding)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cohere Embed API](https://docs.cohere.com/reference/embed)
- [Ollama Embeddings](https://ollama.ai/blog/embedding-models)

## Conclusion

ContextFrame's LiteLLM integration provides maximum flexibility for embeddings:

1. **One Interface**: Use any provider with the same code
2. **Easy Migration**: Switch providers by changing one parameter
3. **Cost Control**: Choose models based on your budget
4. **Local Options**: Run completely offline with Ollama
5. **Enterprise Ready**: Support for Azure, AWS, and private deployments

Start with `openai/text-embedding-3-small` for the best balance of quality and cost, then optimize based on your specific needs.