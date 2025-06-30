# CLI Commands Reference

This page provides detailed documentation for all ContextFrame CLI commands.

## Dataset Commands

### `contextframe dataset create`

Create a new ContextFrame dataset.

```bash
contextframe dataset create [OPTIONS] PATH
```

**Arguments:**
- `PATH` - Path where the dataset will be created (e.g., `my_docs.lance`)

**Options:**
- `--embedding-dim` - Dimension of embeddings (default: 1536)
- `--description` - Dataset description
- `--storage-options` - JSON string of storage options for cloud backends

**Examples:**
```bash
# Create local dataset
contextframe dataset create documents.lance

# Create dataset on S3
contextframe dataset create s3://bucket/docs.lance \
  --storage-options '{"region": "us-east-1"}'

# Create with custom embedding dimension
contextframe dataset create docs.lance --embedding-dim 768
```

### `contextframe dataset info`

Display information about a dataset.

```bash
contextframe dataset info [OPTIONS] PATH
```

**Options:**
- `--stats` - Show detailed statistics
- `--schema` - Display schema information
- `--versions` - List dataset versions

**Example:**
```bash
contextframe dataset info documents.lance --stats
```

### `contextframe dataset list`

List all datasets in a directory.

```bash
contextframe dataset list [OPTIONS] [DIRECTORY]
```

**Options:**
- `--format` - Output format: table, json, csv (default: table)
- `--sort` - Sort by: name, size, modified (default: name)

### `contextframe dataset compact`

Compact dataset to optimize storage and performance.

```bash
contextframe dataset compact [OPTIONS] PATH
```

**Options:**
- `--keep-versions` - Number of versions to keep (default: 10)
- `--vacuum` - Remove deleted data completely

## Record Commands

### `contextframe record add`

Add a new record to a dataset.

```bash
contextframe record add [OPTIONS] DATASET
```

**Options:**
- `--file` - File to import
- `--text` - Text content (alternative to file)
- `--title` - Document title
- `--author` - Document author
- `--tags` - Comma-separated tags
- `--metadata` - JSON string of custom metadata
- `--no-embedding` - Skip embedding generation

**Examples:**
```bash
# Add a text file
contextframe record add docs.lance --file report.txt --title "Q4 Report"

# Add with metadata
contextframe record add docs.lance --file doc.pdf \
  --metadata '{"project": "alpha", "version": "1.2"}'

# Add text directly
contextframe record add docs.lance \
  --text "This is the document content" \
  --title "Quick Note"
```

### `contextframe record get`

Retrieve a record by ID.

```bash
contextframe record get [OPTIONS] DATASET RECORD_ID
```

**Options:**
- `--format` - Output format: json, yaml, table
- `--include-embedding` - Include embedding vector in output

### `contextframe record update`

Update an existing record.

```bash
contextframe record update [OPTIONS] DATASET RECORD_ID
```

**Options:**
- `--title` - New title
- `--status` - New status
- `--metadata` - JSON string of metadata updates
- `--add-tags` - Tags to add
- `--remove-tags` - Tags to remove

### `contextframe record delete`

Delete records from a dataset.

```bash
contextframe record delete [OPTIONS] DATASET RECORD_IDS...
```

**Options:**
- `--confirm` - Skip confirmation prompt
- `--where` - SQL-style WHERE clause for bulk deletion

**Example:**
```bash
# Delete specific records
contextframe record delete docs.lance abc123 def456 --confirm

# Delete by condition
contextframe record delete docs.lance --where "status = 'archived'"
```

## Search Commands

### `contextframe search vector`

Perform vector similarity search.

```bash
contextframe search vector [OPTIONS] DATASET QUERY
```

**Options:**
- `--limit` - Number of results (default: 10)
- `--threshold` - Minimum similarity score
- `--filter` - SQL-style filter expression
- `--include-scores` - Show similarity scores

**Examples:**
```bash
# Basic vector search
contextframe search vector docs.lance "machine learning concepts"

# Search with filters
contextframe search vector docs.lance "security best practices" \
  --filter "author = 'john' AND status != 'draft'" \
  --limit 20
```

### `contextframe search text`

Perform full-text search.

```bash
contextframe search text [OPTIONS] DATASET QUERY
```

**Options:**
- `--limit` - Number of results
- `--fields` - Fields to search in
- `--filter` - Additional filters

### `contextframe search hybrid`

Combine vector and text search.

```bash
contextframe search hybrid [OPTIONS] DATASET QUERY
```

**Options:**
- `--alpha` - Weight between vector (0) and text (1) search
- `--limit` - Number of results
- `--rerank` - Use reranking model

## Import/Export Commands

### `contextframe import`

Import documents into a dataset.

```bash
contextframe import [OPTIONS] DATASET SOURCE
```

**Subcommands:**
- `json` - Import from JSON
- `csv` - Import from CSV
- `parquet` - Import from Parquet
- `directory` - Import from directory

**Examples:**
```bash
# Import JSON file
contextframe import json docs.lance data.json \
  --text-field content \
  --title-field name

# Import directory of documents
contextframe import directory docs.lance ./documents \
  --extensions .txt,.md,.pdf \
  --recursive
```

### `contextframe export`

Export dataset to various formats.

```bash
contextframe export [OPTIONS] FORMAT DATASET OUTPUT
```

**Formats:**
- `json` - Export to JSON
- `csv` - Export to CSV
- `parquet` - Export to Parquet
- `jsonl` - Export to JSON Lines

**Options:**
- `--filter` - SQL-style filter
- `--limit` - Maximum records to export
- `--include-embeddings` - Include embedding vectors

**Example:**
```bash
# Export to JSON with filter
contextframe export json docs.lance output.json \
  --filter "created_at > '2024-01-01'" \
  --limit 1000
```

## Version Commands

### `contextframe version list`

List all versions of a dataset.

```bash
contextframe version list [OPTIONS] DATASET
```

**Options:**
- `--limit` - Number of versions to show
- `--format` - Output format

### `contextframe version checkout`

Checkout a specific version of the dataset.

```bash
contextframe version checkout [OPTIONS] DATASET VERSION
```

### `contextframe version compact`

Compact old versions to save space.

```bash
contextframe version compact [OPTIONS] DATASET
```

**Options:**
- `--keep` - Number of versions to keep
- `--older-than` - Remove versions older than date

## Utility Commands

### `contextframe config`

Manage CLI configuration.

```bash
contextframe config [SUBCOMMAND]
```

**Subcommands:**
- `show` - Display current configuration
- `set` - Set configuration value
- `get` - Get specific configuration value

**Example:**
```bash
# Set default embedding model
contextframe config set default_embedding_model "openai/text-embedding-3-large"

# Show all configuration
contextframe config show
```

### `contextframe validate`

Validate dataset integrity.

```bash
contextframe validate [OPTIONS] DATASET
```

**Options:**
- `--check-embeddings` - Verify embedding dimensions
- `--check-schema` - Validate schema compliance
- `--repair` - Attempt to repair issues

## Environment Variables

The CLI respects these environment variables:

- `CONTEXTFRAME_CONFIG` - Path to configuration file
- `CONTEXTFRAME_CACHE_DIR` - Cache directory for models
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `CONTEXTFRAME_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Exit Codes

The CLI uses standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Dataset not found
- `4` - Permission denied
- `5` - Network error