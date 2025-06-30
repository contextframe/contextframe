# Utilities API Reference

ContextFrame provides a comprehensive set of utility functions for working with metadata, relationships, versioning, and data validation.

## Metadata Functions

### create_metadata

::: contextframe.helpers.metadata_utils.create_metadata
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import create_metadata

# Basic metadata
metadata = create_metadata(
    title="My Document",
    source="manual",
    author="John Doe"
)

# With relationships
metadata = create_metadata(
    title="Chapter 2",
    source="book",
    relationships=[
        {
            "relationship_type": "parent",
            "target_id": "book_001"
        },
        {
            "relationship_type": "previous",
            "target_id": "chapter_001"
        }
    ]
)

# With custom fields
metadata = create_metadata(
    title="Research Paper",
    source="arxiv",
    custom_fields={
        "arxiv_id": "2024.12345",
        "categories": ["cs.AI", "cs.LG"],
        "peer_reviewed": True
    }
)
```

### create_relationship

::: contextframe.helpers.metadata_utils.create_relationship
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import create_relationship

# Simple relationship
rel = create_relationship(
    relationship_type="parent",
    target_id="doc_123"
)

# With metadata
rel = create_relationship(
    relationship_type="references",
    target_id="paper_456",
    metadata={
        "citation_type": "journal",
        "year": 2024,
        "relevance_score": 0.95
    }
)

# Different relationship types
parent_rel = create_relationship("parent", "collection_001")
child_rel = create_relationship("child", "section_002")
reference_rel = create_relationship("references", "source_003")
related_rel = create_relationship("related", "similar_004")
member_rel = create_relationship("member_of", "group_005")
```

### add_relationship_to_metadata

::: contextframe.helpers.metadata_utils.add_relationship_to_metadata
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import create_metadata, add_relationship_to_metadata

# Start with basic metadata
metadata = create_metadata(title="Document")

# Add relationships incrementally
metadata = add_relationship_to_metadata(
    metadata,
    relationship_type="parent",
    target_id="collection_001"
)

metadata = add_relationship_to_metadata(
    metadata,
    relationship_type="references",
    target_id="source_123",
    metadata={"page": 42}
)

# Result: metadata with two relationships
```

### validate_relationships

::: contextframe.helpers.metadata_utils.validate_relationships
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import validate_relationships, RelationshipError

# Valid relationships
relationships = [
    {"relationship_type": "parent", "target_id": "doc_1"},
    {"relationship_type": "child", "target_id": "doc_2"}
]

try:
    validate_relationships(relationships)
    print("Relationships are valid")
except RelationshipError as e:
    print(f"Invalid relationships: {e}")

# Invalid - missing required field
invalid = [
    {"relationship_type": "parent"}  # Missing target_id
]

try:
    validate_relationships(invalid)
except RelationshipError as e:
    print(f"Error: {e}")  # Will raise error
```

### get_standard_fields

::: contextframe.helpers.metadata_utils.get_standard_fields
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import get_standard_fields

# Get list of standard metadata fields
standard = get_standard_fields()
print(standard)
# ['title', 'source', 'created_at', 'modified_at', 'author', ...]

# Validate custom fields
def validate_metadata(metadata):
    standard = get_standard_fields()
    custom = []
    
    for key in metadata:
        if key not in standard and key != "relationships":
            custom.append(key)
    
    if custom:
        print(f"Custom fields found: {custom}")
```

## Version Management

### is_semantic_version

::: contextframe.helpers.metadata_utils.is_semantic_version
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import is_semantic_version

# Valid versions
assert is_semantic_version("1.0.0") == True
assert is_semantic_version("2.1.3") == True
assert is_semantic_version("0.0.1") == True

# Invalid versions
assert is_semantic_version("1.0") == False
assert is_semantic_version("v1.0.0") == False
assert is_semantic_version("1.0.0-beta") == False
```

### compare_semantic_versions

::: contextframe.helpers.metadata_utils.compare_semantic_versions
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import compare_semantic_versions

# Compare versions
assert compare_semantic_versions("1.0.0", "2.0.0") == -1  # v1 < v2
assert compare_semantic_versions("2.0.0", "1.0.0") == 1   # v1 > v2
assert compare_semantic_versions("1.0.0", "1.0.0") == 0   # v1 == v2

# More complex comparisons
assert compare_semantic_versions("1.2.3", "1.2.4") == -1  # Patch differs
assert compare_semantic_versions("1.2.0", "1.3.0") == -1  # Minor differs
assert compare_semantic_versions("1.0.0", "2.0.0") == -1  # Major differs

# Use in version checking
def check_compatibility(required, current):
    if compare_semantic_versions(current, required) < 0:
        print(f"Upgrade needed: {current} -> {required}")
    else:
        print("Version compatible")
```

### next_version

::: contextframe.helpers.metadata_utils.next_version
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import next_version

# Current version
current = "1.2.3"

# Generate next versions
patch = next_version(current, "patch")    # "1.2.4"
minor = next_version(current, "minor")    # "1.3.0"
major = next_version(current, "major")    # "2.0.0"

# Version management workflow
def release_new_version(current_version, change_type):
    new_version = next_version(current_version, change_type)
    print(f"Releasing {new_version} ({change_type} update)")
    return new_version

# Example releases
v1 = release_new_version("1.0.0", "patch")  # "1.0.1" - Bug fix
v2 = release_new_version(v1, "minor")       # "1.1.0" - New feature
v3 = release_new_version(v2, "major")       # "2.0.0" - Breaking change
```

## UUID Management

### generate_uuid

::: contextframe.helpers.metadata_utils.generate_uuid
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import generate_uuid

# Generate random UUID
uuid1 = generate_uuid()
print(uuid1)  # e.g., "550e8400-e29b-41d4-a716-446655440000"

# Generate with namespace (deterministic)
namespace = "my_namespace"
name = "document_123"
uuid2 = generate_uuid(namespace=namespace, name=name)
uuid3 = generate_uuid(namespace=namespace, name=name)
assert uuid2 == uuid3  # Same input = same UUID

# Use for consistent IDs
def create_stable_id(doc_type, doc_id):
    return generate_uuid(
        namespace=f"{doc_type}_namespace",
        name=str(doc_id)
    )

# Always generates same ID for same input
id1 = create_stable_id("article", 123)
id2 = create_stable_id("article", 123)
assert id1 == id2
```

### is_valid_uuid

::: contextframe.helpers.metadata_utils.is_valid_uuid
    options:
      show_source: false
      show_signature_annotations: true
      heading_level: 3
      docstring_section_style: list

#### Usage Examples

```python
from contextframe import is_valid_uuid

# Valid UUIDs
assert is_valid_uuid("550e8400-e29b-41d4-a716-446655440000") == True
assert is_valid_uuid("123e4567-e89b-12d3-a456-426614174000") == True

# Invalid UUIDs
assert is_valid_uuid("not-a-uuid") == False
assert is_valid_uuid("550e8400-e29b-41d4-a716") == False  # Too short
assert is_valid_uuid("") == False

# Validation in practice
def validate_document_id(doc_id):
    if not is_valid_uuid(doc_id):
        raise ValueError(f"Invalid document ID: {doc_id}")
    return doc_id
```

## I/O Utilities

### FrameSetExporter

::: contextframe.io.FrameSetExporter
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false

#### Usage Examples

```python
from contextframe import FrameDataset
from contextframe.io import FrameSetExporter, ExportFormat

# Open dataset
dataset = FrameDataset("my_docs.lance")

# Create exporter
exporter = FrameSetExporter(dataset)

# Export to different formats
exporter.export("export.parquet", format=ExportFormat.PARQUET)
exporter.export("export.json", format=ExportFormat.JSON)
exporter.export("export.csv", format=ExportFormat.CSV)

# Export with filters
exporter.export(
    "filtered.json",
    format=ExportFormat.JSON,
    filter="metadata.source = 'github'",
    columns=["text_content", "metadata", "timestamp"]
)

# Export to pandas DataFrame
df = exporter.to_pandas()
print(f"Exported {len(df)} records")
```

### FrameSetImporter

::: contextframe.io.FrameSetImporter
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false

#### Usage Examples

```python
from contextframe import FrameDataset
from contextframe.io import FrameSetImporter

# Create dataset
dataset = FrameDataset.create("imported.lance")

# Create importer
importer = FrameSetImporter(dataset)

# Import from JSON
count = importer.import_json("data.json")
print(f"Imported {count} records from JSON")

# Import from CSV with mapping
count = importer.import_csv(
    "data.csv",
    text_column="content",
    metadata_columns=["title", "author", "date"]
)

# Import from pandas DataFrame
import pandas as pd
df = pd.read_csv("documents.csv")
count = importer.import_pandas(
    df,
    text_column="text",
    metadata_columns=["title", "source"]
)

# Import with validation
try:
    count = importer.import_json("invalid.json", validate=True)
except ValidationError as e:
    print(f"Import failed: {e}")
```

### ExportFormat

::: contextframe.io.ExportFormat
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

## Error Types

### ContextFrameError

Base exception for all ContextFrame errors:

```python
from contextframe import ContextFrameError

try:
    # Some operation
    pass
except ContextFrameError as e:
    print(f"ContextFrame error: {e}")
```

### Specific Error Types

```python
from contextframe import (
    ValidationError,      # Schema validation errors
    RelationshipError,    # Invalid relationships
    VersioningError,      # Version management errors
    ConflictError,       # Data conflicts
    FormatError         # Format conversion errors
)

# Validation errors
try:
    record = FrameRecord(text_content=None)  # Invalid
except ValidationError as e:
    print(f"Validation failed: {e}")

# Relationship errors
try:
    validate_relationships([{"type": "invalid"}])
except RelationshipError as e:
    print(f"Invalid relationship: {e}")

# Version errors
try:
    compare_semantic_versions("1.0", "2.0.0")  # Invalid format
except VersioningError as e:
    print(f"Version error: {e}")

# Format errors
try:
    exporter.export("file.xyz", format="invalid")
except FormatError as e:
    print(f"Format error: {e}")
```

## Utility Patterns

### Metadata Builders

```python
from contextframe import create_metadata, add_relationship_to_metadata

class MetadataBuilder:
    """Fluent interface for building metadata."""
    
    def __init__(self):
        self.metadata = {}
    
    def title(self, title):
        self.metadata["title"] = title
        return self
    
    def source(self, source):
        self.metadata["source"] = source
        return self
    
    def author(self, author):
        self.metadata["author"] = author
        return self
    
    def relationship(self, rel_type, target_id, **kwargs):
        self.metadata = add_relationship_to_metadata(
            self.metadata, rel_type, target_id, **kwargs
        )
        return self
    
    def custom(self, **fields):
        self.metadata.update(fields)
        return self
    
    def build(self):
        return self.metadata

# Usage
metadata = (MetadataBuilder()
    .title("My Document")
    .source("api")
    .author("Jane Doe")
    .relationship("parent", "collection_001")
    .custom(tags=["important", "reviewed"])
    .build())
```

### Batch Processing

```python
from contextframe import FrameRecord, create_metadata, generate_uuid

def batch_create_records(items, source="import"):
    """Create records with consistent metadata."""
    records = []
    batch_id = generate_uuid()
    
    for i, item in enumerate(items):
        metadata = create_metadata(
            title=item.get("title", f"Document {i}"),
            source=source,
            batch_id=batch_id,
            position=i,
            **item.get("metadata", {})
        )
        
        record = FrameRecord(
            text_content=item["content"],
            metadata=metadata,
            unique_id=generate_uuid(
                namespace=batch_id,
                name=str(i)
            )
        )
        records.append(record)
    
    return records
```

### Migration Helpers

```python
from contextframe import compare_semantic_versions, next_version

class SchemaMigrator:
    """Handle schema migrations."""
    
    def __init__(self, current_version):
        self.current_version = current_version
        self.migrations = {}
    
    def register_migration(self, from_version, to_version, func):
        """Register a migration function."""
        self.migrations[(from_version, to_version)] = func
    
    def migrate_to(self, target_version):
        """Migrate to target version."""
        if compare_semantic_versions(self.current_version, target_version) >= 0:
            return  # Already at or past target
        
        # Find migration path
        version = self.current_version
        while compare_semantic_versions(version, target_version) < 0:
            next_ver = self._find_next_version(version, target_version)
            
            migration = self.migrations.get((version, next_ver))
            if not migration:
                raise VersioningError(f"No migration from {version} to {next_ver}")
            
            print(f"Migrating {version} -> {next_ver}")
            migration()
            version = next_ver
        
        self.current_version = target_version
```

## Performance Tips

1. **Batch Metadata Creation**: Create metadata objects once and reuse
2. **UUID Caching**: Use deterministic UUIDs for consistent references
3. **Relationship Validation**: Validate relationships before adding to records
4. **Version Comparison**: Cache version comparisons in hot paths
5. **Export Optimization**: Use column selection to reduce export size

## See Also

- [FrameRecord API](frame-record.md) - Using metadata with records
- [Schema API](schema.md) - Schema validation utilities
- [Module Guides](../modules/frame-record.md) - Conceptual overview
- [Cookbook Examples](../cookbook/index.md) - Practical utility usage