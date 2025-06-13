# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **BREAKING**: Replaced LlamaIndex text splitter with lightweight `semantic-text-splitter` (Rust-based)
  - Removed `llama_index_splitter` function from `contextframe.extract.chunking`
  - Renamed to `semantic_splitter` with updated parameters
  - Significantly reduced dependency footprint (no PyTorch required)
  - All tree-sitter language packages now included in base `extract` dependencies

### Added

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
