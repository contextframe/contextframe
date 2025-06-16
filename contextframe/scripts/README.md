# ContextFrame Bash Scripts

This directory contains bash script wrappers that provide convenient CLI access to ContextFrame functionality. These scripts are designed to be used by CLI-driven agents like Claude Code, as well as directly by users.

## Installation

Add the scripts directory to your PATH:

```bash
export PATH="$PATH:/path/to/contextframe/contextframe/scripts"
```

Or create symlinks in a directory already in your PATH:

```bash
ln -s /path/to/contextframe/contextframe/scripts/contextframe-* /usr/local/bin/
```

## Available Commands

### contextframe-search

Search documents in a ContextFrame dataset using vector, text, or hybrid search.

```bash
# Basic search
contextframe-search data.lance "machine learning"

# Text-only search with more results
contextframe-search data.lance "python" --type text --limit 20

# Vector search (requires embeddings and API credentials)
contextframe-search data.lance "AI research" --type vector

# Search within a collection
contextframe-search data.lance "deep learning" --collection "research-papers"

# With SQL filter
contextframe-search data.lance "tutorial" --filter "record_type = 'document'"
```

**Options:**
- `--limit N`: Number of results to return (default: 10)
- `--type TYPE`: Search type: vector, text, or hybrid (default: hybrid)
- `--filter SQL`: Lance SQL filter expression
- `--collection NAME`: Filter by collection name

### contextframe-add

Add documents to a ContextFrame dataset.

```bash
# Add a single file
contextframe-add data.lance document.txt

# Add all files in a directory
contextframe-add data.lance docs/

# Add to a collection with embeddings
contextframe-add data.lance paper.pdf --collection "research" --embeddings

# Add with chunking for large documents
contextframe-add data.lance book.txt --chunk-size 1000 --chunk-overlap 100

# Add with custom identifier
contextframe-add data.lance important.md --identifier "doc-001"
```

**Options:**
- `--collection NAME`: Add to collection with this name
- `--type TYPE`: Record type: document, collection_header, dataset_header
- `--identifier ID`: Custom identifier (auto-generated if not provided)
- `--embeddings`: Generate embeddings for documents
- `--chunk-size N`: Split documents into chunks of N characters
- `--chunk-overlap N`: Overlap between chunks (requires --chunk-size)

### contextframe-get

Get a specific document from a dataset by its identifier.

```bash
# Get document as text
contextframe-get data.lance doc-123

# Get as JSON
contextframe-get data.lance doc-123 --format json

# Get as formatted Markdown
contextframe-get data.lance doc-123 --format markdown
```

**Options:**
- `--format FORMAT`: Output format: json, text, or markdown (default: text)

### contextframe-list

List documents in a dataset with filtering and formatting options.

```bash
# List all documents (default limit: 50)
contextframe-list data.lance

# List more results
contextframe-list data.lance --limit 100

# List as JSON
contextframe-list data.lance --format json

# List only identifiers
contextframe-list data.lance --format ids

# Filter by collection
contextframe-list data.lance --collection "tutorials"

# Filter by type
contextframe-list data.lance --type document

# Complex filter
contextframe-list data.lance --filter "title LIKE '%Python%'" --limit 20
```

**Options:**
- `--limit N`: Number of records to return (default: 50)
- `--filter SQL`: Lance SQL filter expression
- `--format FORMAT`: Output format: table, json, or ids (default: table)
- `--collection NAME`: Filter by collection name
- `--type TYPE`: Filter by record type

## Environment Variables

### Embedding Configuration

For vector search and embedding generation, configure your provider:

```bash
# OpenAI (default)
export OPENAI_API_KEY="sk-..."
export CONTEXTFRAME_EMBED_MODEL="text-embedding-ada-002"

# Cohere
export COHERE_API_KEY="..."
export CONTEXTFRAME_EMBED_MODEL="cohere/embed-english-v3.0"

# Local Ollama
export CONTEXTFRAME_EMBED_MODEL="ollama/all-minilm"
```

## Use Cases

### 1. Building a Knowledge Base

```bash
# Create dataset and add documents
contextframe-add knowledge.lance docs/ --collection "documentation" --embeddings

# Search the knowledge base
contextframe-search knowledge.lance "how to install" --type hybrid
```

### 2. Document Analysis Pipeline

```bash
# Add documents with chunking
contextframe-add analysis.lance reports/*.pdf --chunk-size 500 --embeddings

# List all chunks
contextframe-list analysis.lance --filter "custom_metadata.chunk_index IS NOT NULL"

# Get specific chunk
contextframe-get analysis.lance "report-001_chunk_5"
```

### 3. Collection Management

```bash
# Add collection header
echo "# Research Papers Collection" > header.md
contextframe-add data.lance header.md --type collection_header --identifier "research-papers"

# Add documents to collection
contextframe-add data.lance papers/*.pdf --collection "research-papers"

# List collection contents
contextframe-list data.lance --collection "research-papers"
```

## Notes

- Datasets are Lance directories (`.lance` folders) containing columnar data
- All scripts respect Lance's SQL filtering syntax
- Vector search requires pre-computed embeddings in the dataset
- Embeddings require API credentials for the configured provider
- Scripts are designed to be composable in Unix pipelines

## Integration with Claude Code

These scripts are optimized for use with Claude Code and similar CLI agents:

1. **Simple, predictable interfaces** - Each script does one thing well
2. **Machine-readable output** - JSON format available for all commands
3. **Error handling** - Clear error messages to stderr
4. **Exit codes** - Standard Unix conventions (0 for success, non-zero for errors)
5. **No interactive prompts** - All options via command-line arguments

Example Claude Code usage:

```
Human: Search for Python tutorials in my dataset