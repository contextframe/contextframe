# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-07-02

### Fixed

- Fixed `pylance` dependency (was incorrectly named `lance` in v0.1.1)
- Fixed 38 failing integration tests related to API differences
- Added "member_of" to valid relationship types for collection support
- Fixed custom metadata string validation in collections
- Implemented workaround for Lance v0.30.0 vector search bug on small datasets
- Fixed UUID property access in edge case tests
- Fixed `len()` usage on Lance datasets (now uses `count_rows()`)
- Improved error messages with field context and helpful hints

### Added

- Full-text search index creation support (`create_fts_index()` method)
- UUID override support at creation time (`uuid` parameter in `FrameRecord.create()`)
- Auto-indexing option for full-text search (`auto_index` parameter)
- Enhanced `create_scalar_index()` with index type support (BITMAP, BTREE, INVERTED, FTS)
- API improvements roadmap document (`docs/roadmap/api-improvements-v02.md`)
- Migration guide for v0.1.2 (`docs/migration/api-changes-v012.md`)

### Changed

- **BREAKING**: Replaced LlamaIndex text splitter with lightweight `semantic-text-splitter` (Rust-based)
  - Removed `llama_index_splitter` function from `contextframe.extract.chunking`
  - Renamed to `semantic_splitter` with updated parameters
  - Significantly reduced dependency footprint (no PyTorch required)
  - All tree-sitter language packages now included in base `extract` dependencies
- Error handling now uses custom `ValidationError` with better messages
- Test structure reorganized into `tests/unit/` and `tests/integration/`

### Known Issues

- Lance v0.30.0 has a bug causing "Task was aborted" errors on vector search with small datasets (<10 rows)
  - Workaround implemented: returns empty results with warning
  - Tracking issue: [Lance #2464](https://github.com/lancedb/lance/issues/2464)
  - Linear task: CFOS-45

### Documentation

- Comprehensive embedding provider documentation (`docs/embedding_providers.md`)
- Example demonstrating all embedding provider options (`examples/embedding_providers_demo.py`)
- External extraction tool examples:
  - `examples/external_tools/docling_pdf_pipeline.py` - Docling integration pattern
  - `examples/external_tools/unstructured_io_pipeline.py` - Unstructured.io API and local usage
  - `examples/external_tools/chunkr_pipeline.py` - Intelligent chunking service
  - `examples/external_tools/reducto_pipeline.py` - Scientific document processing
- Documentation for external extraction tools (`docs/external_extraction_tools.md`)
- Documentation for extraction patterns (`docs/extraction_patterns.md`)

## [0.1.0] - 2025-05-05

Initial release of ContextFrame.

### Added

- Core functionality for managing LLM context with Lance files
- Schema validation and standardized metadata
- Document extraction and chunking capabilities
- Embedding generation with multiple providers
- Example pipelines and documentation

### Fixed

- N/A (initial release)
