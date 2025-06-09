# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Environment
```bash
# Run in devbox environment
devbox shell

# Run commands via devbox
devbox run <command>
```

### Environment Variables
```bash
# This project uses Doppler for environment variable management
# No .env files are used

# Run commands with Doppler-injected environment variables
doppler run -- <command>

# Example: Run tests with environment variables
doppler run -- pytest

# Example: Run the application
doppler run -- python -m contextframe
```

### Build and Installation
```bash
# Install package in development mode with all dependencies
uv pip install -e ".[dev]"

# Or using task
task install

# Build package for distribution
uv pip install build && python -m build

# Install package normally
uv pip install .
```

### Code Quality
```bash
# Run linter and auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Type checking
mypy contextframe

# Check dependencies
deptry .

# Or run all quality checks via task
task lint
task format
task typecheck
```

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=contextframe --cov-report=term-missing

# Or using task
task test

# With environment variables from Doppler
doppler run -- task test
```

### Documentation
```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Or using task
task docs
task docs-serve
```

## Architecture

ContextFrame provides a standardized schema and abstractions for managing document context data for LLMs, built on the Lance columnar data format.

### Core Components

1. **Data Model**
   - `FrameRecord`: In-memory representation of documents with metadata, content, and embeddings
   - `FrameDataset`: High-level wrapper around Lance datasets providing CRUD operations

2. **Schema System**
   - Dual schema approach: JSON Schema for validation (`schema/contextframe_schema.json`), Arrow Schema for storage (`schema/contextframe_schema.py`)
   - Validation enforced on all write operations
   - Extensible via `custom_metadata` and `context` fields

3. **Storage Layer**
   - Built on Lance format (creates `.lance` directories)
   - Supports local and cloud storage (S3, GCS, Azure)
   - Versioned, columnar storage with efficient queries

### Lance Files (.lance)

ContextFrame relies on Lance as its fundamental storage primitive. Key characteristics:

1. **Directory Structure**: Each Lance dataset is a directory (`.lance`) containing:
   - Data files: Columnar data stored in fragments
   - Manifest files: Metadata about versions and schema
   - Index files: Optional indexes for fast queries

2. **Versioning**: Lance provides built-in version control:
   - Each write creates a new version
   - Old versions are retained until compaction
   - Can query specific versions or time-travel

3. **Columnar Format**: 
   - Efficient for analytical queries
   - Supports pushdown predicates
   - Native vector storage for embeddings
   - Zero-copy reads with memory mapping

4. **Operations on .lance**:
   - Datasets are self-contained directories
   - Can be copied/moved as directories
   - Support for remote storage (s3://, gs://, az://)
   - Atomic operations via manifest updates

### Key Patterns

1. **Record Types**: Documents are categorized as `document`, `collection_header`, or `dataset_header` for self-describing datasets

2. **Relationships**: Explicit tracking of document relationships (parent/child, related, reference, member_of) with multiple identifier types

3. **Collections**: Documents can be grouped into collections with headers providing context and position tracking

4. **Vector Operations**: Native support for embeddings with KNN search, full-text search, and SQL-style filtering

5. **CRUD Pattern**: Complete operations via `FrameDataset` with atomic updates (delete-then-add) and upsert semantics

### Development Notes

- Python 3.10-3.12 required
- Tests go in `contextframe/tests/`
- Use type hints throughout
- Schema changes require updating both JSON and Arrow schemas
- Lance datasets are directories, not single files
- When working with .lance directories, treat them as atomic units
- Never modify individual files within .lance directories
- Use Lance APIs for all data operations
- Use Doppler for environment variables - never create .env files
- Wrap commands with `doppler run --` when environment variables are needed

## Important Notes

- Do not use emojis
- Avoid writing  "🤖 Generated with Claude Code" when making commits or PRs

