# ContextFrame: Simplifying LLM Context Management with Enhanced Lance Files

ContextFrame is a Python package and file specification designed to streamline context management for Large Language Models (LLMs) in applied AI/ML workflows. It builds upon the powerful `.lance` columnar data format, providing a standardized schema, validation tools, and user-friendly abstractions to enhance its usability.

## The Problem: Managing Context for LLMs

Effectively managing the context provided to LLMs is crucial for generating relevant and accurate responses. This often involves handling diverse documents, maintaining structured metadata, tracking relationships, ensuring data consistency, **and crucially, annotating content with user-specific context relevant to the task at hand** – tasks that can become complex in real-world applications.

## The Solution: ContextFrame + Lance

ContextFrame addresses these challenges by leveraging the `.lance` format's strengths (performance, versioning, vector support) and adding a layer of structure and semantics inspired by the original MDP project:

-   **Standardized Schema**: Defines a specific, extensible schema (`contextframe/schema/contextframe_schema.json`) for storing document content, **rich metadata** (including authorship, timestamps, status, source information), **relationships**, **collection linkage**, and vector embeddings within a `.lance` file. This ensures consistency and provides a common structure for LLM context.
    -   **Record Type (`record_type`):** An **enum** column distinguishing between normal `document` rows and special control rows like `collection_header` or `dataset_header`.  This enables efficient filtering and makes datasets self-describing.
    -   **Relationships:** The schema includes a dedicated `relationships` field (a list of structs) to explicitly link related documents (e.g., parent/child, related, reference, member_of) using various identifiers (UUID, URI, Path, CID).
    -   **Collections:** Fields like `collection`, `collection_id`, and `position` facilitate organizing documents into logical groups or sequences.
    -   **Source Tracking:** Fields like `source_file`, `source_type`, and `source_url` allow tracking the origin of content, useful for ingestion pipelines.
    -   **User-Defined Context:** Fields like `context` (string) and `custom_metadata` (map) are explicitly designed to be **editable by the user**, allowing them to add workflow-specific annotations, descriptions of relevance (e.g., "This document is crucial for Project 123 because..."), or task-specific labels beyond the original source metadata.
-   **Schema-Aware Abstractions**: Offers Python classes (`FrameRecord`, `FrameDataset`) that simplify interactions with Lance datasets conforming to the ContextFrame spec.
    -   `FrameRecord`: Represents a single document (row) in memory. It handles data validation against the schema, manages default values (like UUIDs and timestamps), provides convenience accessors **and allows direct modification** of common metadata fields (including `context` and `custom_metadata`), includes helpers for managing relationships (e.g., `add_relationship`), and converts data to/from the Arrow format required by Lance. This enables users to easily layer their own semantic context onto the data.
    -   `FrameDataset`: Wraps the core `lance.LanceDataset`, providing schema-aware methods for common dataset operations:
        -   **Creation (`.create`)**: Initializes a new `.lance` directory with the correct ContextFrame schema (using `lance.write_dataset`).
        -   **Opening (`.open`)**: Loads an existing ContextFrame dataset (using `lance.dataset`).
        -   **Adding Records (`.add`, `.add_many`)**: Validates `FrameRecord` metadata against the schema and inserts the data into the Lance dataset (using `LanceDataset.insert`).
        -   **Retrieval (`.from_dataset_row`)**: Fetches a specific record by UUID (using `LanceDataset.scanner` with a filter).
        -   **Vector & Text Search Helpers**
            -   `knn_search(...)` – convenient nearest-neighbour search that returns fully-materialised `FrameRecord` objects and supports additional SQL filters.
            -   `full_text_search(...)` – wraps Lance BM25 full-text search for one-liner relevance queries.
        -   **Rich Query Helpers** – pre-built helpers for common metadata look-ups (e.g. `find_by_status`, `find_by_tag`, `find_related_to`, `find_by_author`, date-range helpers, etc.).
        -   **Record Management (`.update_record`, `.delete_record`, `.upsert_record`)**: Idiomatic helpers to update, remove, or upsert records by UUID while preserving schema integrity.
        -   **Collection Helpers (`.get_collection_header`, `.get_collection_members`, `.get_members_linked_to_header`)**: Convenience methods to work with logical document collections identified by `collection` + `record_type='collection_header'`.
-   **Validation**: Integrates metadata validation using the JSON schema before writing data, preventing inconsistencies.
-   **Focus on Usability**: Aims to enhance the developer experience for managing context data within `.lance` files, without reimplementing Lance's core file I/O or advanced query capabilities. The underlying `LanceDataset` is always accessible (`FrameDataset._native`) for advanced use cases.

## Key Features

-   **Lance-Based**: Built on the high-performance, version-aware `.lance` format.
-   **Rich, Editable & Standardized Metadata**: Comprehensive schema for essential document details, including provenance, collections, status, **and importantly, user-editable fields (`context`, `custom_metadata`) for adding workflow-specific relevance and annotations.**
-   **Optional Raw Multimodal Data**  Store raw binary data (images, audio, video, PDFs, etc.) directly in the dataset using the **`raw_data`** (bytes) and **`raw_data_type`** (IANA MIME type) columns added to the canonical schema.  A helper `MimeTypes` enum under `contextframe.schema` exposes common constants (e.g., `MimeTypes.IMAGE_JPEG`).
-   **Explicit Record Typing**  The `RecordType` enum (`contextframe.schema.RecordType`) provides canonical constants (`DOCUMENT`, `COLLECTION_HEADER`, `DATASET_HEADER`).
-   **Explicit Relationships**: Dedicated schema support and helpers for defining connections between documents.
-   **Vector Embedding Support**: Natively handles vector embeddings alongside text and metadata.
-   **Schema Validation**: Ensures data consistency and integrity against the ContextFrame specification.
-   **Pythonic API**: Provides intuitive classes (`FrameRecord`, `FrameDataset`) for interacting with ContextFrame data.
-   **Full CRUD Helpers**: Built-in `.update_record`, `.delete_record`, and `.upsert_record` methods enable convenient record modifications.
-   **Lightweight Abstraction**: Focuses on schema, validation, and usability, relying on the underlying `lance` library for core storage and query operations.

## Core vs Extended Functionality

The `contextframe` package provides the core specification, schema, validation rules, and Python abstractions (`FrameRecord`, `FrameDataset`). It requires the `lance` library as a dependency.

While ContextFrame defines fields to track document source and relationships, the actual **data conversion/ingestion** (e.g., from PDF, HTML, other formats) and **complex relationship graph analysis** are considered extended functionalities. Users should leverage other libraries or build specific tools that produce or consume ContextFrame-compliant `.lance` files for these purposes.

## Installation

### Core Package (Minimal)
```bash
# Core functionality only - fast, lightweight install
pip install contextframe
```

### With Optional Features
```bash
# Document extraction (PDF, DOCX, HTML, PPTX, XLSX)
pip install "contextframe[extract]"

# Embedding generation (OpenAI, Anthropic, Cohere, Sentence Transformers)
pip install "contextframe[embed]"

# AI-powered enhancement (summarization, metadata extraction)
pip install "contextframe[enhance]"

# MP4 encoding for universal distribution
pip install "contextframe[encode]"

# MCP server for LLM/agent integration
pip install "contextframe[serve]"

# Install everything
pip install "contextframe[all]"
```

### Installation Decision Tree
- **Just managing Lance datasets?** → Use core package
- **Need to extract content from documents?** → Add `[extract]`
- **Creating embeddings?** → Add `[embed]`
- **Using LLMs for enrichment?** → Add `[enhance]`
- **Distributing datasets as MP4?** → Add `[encode]`
- **Serving to LLMs via MCP?** → Add `[serve]`

## Basic Usage (Conceptual)

```python
from contextframe import FrameRecord, FrameDataset
from contextframe.schema.contextframe_schema import MimeTypes, RecordType
import numpy as np
import pyarrow as pa # Lance works closely with Arrow

# 1. Create FrameRecord objects (in-memory representation)
#    - Handles metadata validation and default values (e.g., uuid, dates)
#    - Prepares data for Lance/Arrow
#    - Includes helpers for relationships
record1 = FrameRecord.create(
    title="Introduction to Lance",
    content="Lance is a modern columnar format...",
    vector=np.random.rand(1536).astype(np.float32), # Example embedding
    author="LanceDB Team",
    tags=["lance", "columnar", "vector db"],
    custom_metadata={"project": "ContextFrame"}, # Example custom field
    record_type=RecordType.DOCUMENT,
)

# Example with raw embedded image content and collection header
# (demonstrates use of RecordType enum and collection helpers)
image_bytes = b"...binary jpeg bytes..."  # Replace with real bytes

# Create a *collection header* document which holds contextual information
collection_header = FrameRecord.create(
    title="Project X Docs – Collection Header",
    content="Overview and context for Project X documents...",
    vector=np.zeros(1536, dtype=np.float32),
    tags=["project-x"],
    collection="project_x",
    record_type=RecordType.COLLECTION_HEADER,
)

record2 = FrameRecord.create(
    title="Project X – Image Asset",
    content="This record stores an image relevant to Project X...",
    vector=np.random.rand(1536).astype(np.float32),
    collection="project_x",
    raw_data=image_bytes,
    raw_data_type=MimeTypes.IMAGE_JPEG,
)

# Later, add or modify context based on your workflow needs
# record1.metadata['context'] = "This is the primary specification document for the ContextFrame project."
# record1.metadata['custom_metadata']['review_status'] = 'approved'
# record1.tags.append('core_concept') # Tags are also mutable

# Add a relationship between records (managed within FrameRecord metadata)
record2.add_relationship(collection_header, relationship_type="member_of")

# FrameRecord handles conversion to Arrow Table format needed by Lance
# table1 = record1.to_table()
# print(table1.schema)

# 2. Use FrameDataset to manage records and interact with Lance files
#    - FrameDataset wraps the underlying lance.LanceDataset

dataset_path = "my_context_frames.lance"

# Create a new dataset (writes an empty .lance dir with ContextFrame schema)
# try:
#     frame_dataset = FrameDataset.create(dataset_path, embed_dim=1536)
# except FileExistsError: # Handle existing dataset
#     frame_dataset = FrameDataset.open(dataset_path)


# Add records (validates schema, converts FrameRecord to Arrow, uses LanceDataset.insert)
# frame_dataset.add(record1)
# frame_dataset.add(record2) # Can add records individually or use add_many

# Open an existing dataset
# existing_dataset = FrameDataset.open(dataset_path)
# print(f"Dataset URI: {existing_dataset._native.uri}")
# print(f"Schema: {existing_dataset._native.schema}")
# print(f"Versions: {existing_dataset.versions()}")

# Advanced query helpers

# 3-nearest neighbours restricted to a collection
# query_vector = np.random.rand(1536).astype(np.float32)
# top3 = existing_dataset.knn_search(query_vector, k=3, filter="collection = 'project_x'")
# print([r.title for r in top3])

# Full-text search across text_content
# hits = existing_dataset.full_text_search("vector database", k=10)
# for rec in hits:
#     print(rec.title, rec.metadata.get("score"))

# Metadata helpers
# published_docs = existing_dataset.find_by_status("published")
# tag_matches = existing_dataset.find_by_tag("lance")

# Load a specific record using the helper
# loaded_record = FrameRecord.from_dataset_row(dataset_path, uuid=record1.uuid)
# print(f"Loaded record title: {loaded_record.title}")
# print(f"Loaded record relationships: {loaded_record.metadata.get('relationships')}")
# print(f"Loaded record custom metadata: {loaded_record.metadata.get('custom_metadata')}")

# Access the native LanceDataset object if needed
# native_lance_dataset = existing_dataset._native
# print(f"Native dataset row count: {native_lance_dataset.count_rows()}")

# Update a record (delete-then-add under the hood)
# record1.title = "Introduction to Lance (Updated)"
# frame_dataset.update_record(record1)

# Delete a record by UUID
# frame_dataset.delete_record(record2.uuid)

# Upsert semantics – insert or replace
# frame_dataset.upsert_record(record1)

```

*(Please note: The usage example above is conceptual and may require adjustments based on the final API design. It illustrates the intended workflow.)*

## Optimising Performance with Indexes

`FrameDataset` exposes **index management helpers** that wrap Lance native functionality so you can optimise searches without reading the docs every time:

```python
# Build (or replace) a vector IVF+PQ index – essential for fast knn_search
frame_dataset.create_vector_index(index_type="IVF_PQ", num_partitions=256, num_sub_vectors=64)

# Create a bitmap index on the 'status' column to speed up filters
frame_dataset.create_scalar_index("status")
```

Behind the scenes these forward to `LanceDataset.create_index()` / `create_scalar_index()`.  See the [Lance docs](https://lancedb.github.io/lance/) for tuning parameters.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
