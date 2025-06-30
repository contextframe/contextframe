# Import/Export

ContextFrame provides comprehensive import and export capabilities for moving data between different formats and systems. This guide covers all supported formats, batch operations, and migration strategies.

## Overview

Import/Export capabilities include:
- Multiple format support (JSON, CSV, Parquet, Markdown)
- Batch import with progress tracking
- Export with filtering and transformation
- Connector-based imports from external systems
- Migration tools for system transitions
- Incremental import/export strategies

## Import Operations

### JSON Import

```python
import json
from contextframe import FrameDataset, FrameRecord

def import_json_file(dataset, json_path, batch_size=1000):
    """Import documents from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Handle both single document and array
    if isinstance(data, dict):
        documents = [data]
    else:
        documents = data
    
    total = len(documents)
    imported = 0
    
    # Process in batches
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        records = []
        
        for doc in batch:
            # Map JSON fields to FrameRecord
            record = FrameRecord.create(
                title=doc.get('title', 'Untitled'),
                content=doc.get('content', doc.get('text', '')),
                author=doc.get('author'),
                tags=doc.get('tags', []),
                status=doc.get('status', 'imported'),
                custom_metadata=doc.get('metadata', doc.get('custom_metadata', {}))
            )
            
            # Handle existing UUID
            if 'uuid' in doc:
                record.metadata['uuid'] = doc['uuid']
            
            # Handle timestamps
            if 'created_at' in doc:
                record.metadata['created_at'] = doc['created_at']
            
            records.append(record)
        
        # Add to dataset
        dataset.add_many(records)
        imported += len(records)
        print(f"Imported {imported}/{total} documents")
    
    return imported

def import_jsonl_file(dataset, jsonl_path, batch_size=1000):
    """Import documents from JSON Lines file."""
    records = []
    imported = 0
    
    with open(jsonl_path, 'r') as f:
        for line in f:
            doc = json.loads(line.strip())
            
            record = FrameRecord.create(
                title=doc.get('title', 'Untitled'),
                content=doc.get('content', ''),
                **{k: v for k, v in doc.items() 
                   if k not in ['title', 'content', 'uuid']}
            )
            
            if 'uuid' in doc:
                record.metadata['uuid'] = doc['uuid']
            
            records.append(record)
            
            # Batch insert
            if len(records) >= batch_size:
                dataset.add_many(records)
                imported += len(records)
                print(f"Imported {imported} documents")
                records = []
    
    # Insert remaining
    if records:
        dataset.add_many(records)
        imported += len(records)
    
    return imported
```

### CSV Import

```python
import csv
import pandas as pd

def import_csv_file(dataset, csv_path, text_column='content', title_column='title'):
    """Import documents from CSV file."""
    # Use pandas for better handling
    df = pd.read_csv(csv_path)
    
    records = []
    for _, row in df.iterrows():
        # Get main content
        content = str(row.get(text_column, ''))
        title = str(row.get(title_column, f'Document {_}'))
        
        # Map other columns to metadata
        metadata = {}
        for col in df.columns:
            if col not in [text_column, title_column]:
                value = row[col]
                # Handle NaN values
                if pd.notna(value):
                    metadata[col] = value
        
        record = FrameRecord.create(
            title=title,
            content=content,
            custom_metadata=metadata
        )
        records.append(record)
    
    # Batch import
    dataset.add_many(records)
    print(f"Imported {len(records)} documents from CSV")
    
    return len(records)

def import_csv_advanced(dataset, csv_path, mapping=None):
    """Import CSV with custom field mapping."""
    df = pd.read_csv(csv_path)
    
    # Default mapping
    default_mapping = {
        'title': 'title',
        'content': 'content',
        'text': 'content',
        'author': 'author',
        'date': 'created_at',
        'tags': 'tags',
        'category': 'tags'
    }
    
    mapping = {**default_mapping, **(mapping or {})}
    
    records = []
    for _, row in df.iterrows():
        # Build FrameRecord fields
        record_data = {
            'title': 'Untitled',
            'content': ''
        }
        
        custom_metadata = {}
        
        for csv_col, frame_field in mapping.items():
            if csv_col in row and pd.notna(row[csv_col]):
                value = row[csv_col]
                
                # Handle special fields
                if frame_field == 'tags':
                    # Convert string to list
                    if isinstance(value, str):
                        value = [tag.strip() for tag in value.split(',')]
                    record_data['tags'] = value
                elif frame_field in ['title', 'content', 'author', 'status']:
                    record_data[frame_field] = str(value)
                else:
                    custom_metadata[frame_field] = value
        
        # Add unmapped columns to custom metadata
        for col in df.columns:
            if col not in mapping and pd.notna(row[col]):
                custom_metadata[col] = row[col]
        
        record = FrameRecord.create(
            **record_data,
            custom_metadata=custom_metadata
        )
        records.append(record)
    
    dataset.add_many(records)
    return len(records)
```

### Markdown Import

```python
import os
import re
from pathlib import Path

def import_markdown_file(dataset, md_path):
    """Import a single markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter if present
    metadata = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            content = parts[2].strip()
            
            # Parse YAML frontmatter
            import yaml
            try:
                metadata = yaml.safe_load(frontmatter)
            except:
                pass
    
    # Extract title from first heading or filename
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = metadata.get('title', Path(md_path).stem)
    
    # Create record
    record = FrameRecord.create(
        title=title,
        content=content,
        source_file=str(md_path),
        source_type='file',
        tags=metadata.get('tags', []),
        author=metadata.get('author'),
        custom_metadata={k: v for k, v in metadata.items() 
                        if k not in ['title', 'tags', 'author']}
    )
    
    dataset.add(record)
    return record

def import_markdown_directory(dataset, directory_path, pattern="**/*.md"):
    """Import all markdown files from directory."""
    from pathlib import Path
    
    base_path = Path(directory_path)
    md_files = list(base_path.glob(pattern))
    
    imported = 0
    errors = []
    
    for md_file in md_files:
        try:
            import_markdown_file(dataset, md_file)
            imported += 1
            print(f"Imported: {md_file.relative_to(base_path)}")
        except Exception as e:
            errors.append((str(md_file), str(e)))
            print(f"Error importing {md_file}: {e}")
    
    print(f"\nImported {imported} files")
    if errors:
        print(f"Failed to import {len(errors)} files")
    
    return imported, errors
```

### Parquet Import

```python
import pyarrow.parquet as pq

def import_parquet_file(dataset, parquet_path, batch_size=5000):
    """Import documents from Parquet file."""
    # Read parquet file
    table = pq.read_table(parquet_path)
    
    total_rows = table.num_rows
    imported = 0
    
    # Process in batches
    for i in range(0, total_rows, batch_size):
        # Get batch
        batch = table.slice(i, min(batch_size, total_rows - i))
        
        records = []
        for row in batch.to_pylist():
            # Map fields to FrameRecord
            record = FrameRecord.create(
                title=row.get('title', 'Untitled'),
                content=row.get('content', row.get('text', '')),
                author=row.get('author'),
                tags=row.get('tags', []),
                status=row.get('status', 'imported')
            )
            
            # Handle vector if present
            if 'embedding' in row and row['embedding']:
                record.vector = np.array(row['embedding'], dtype=np.float32)
                record.embed_dim = len(row['embedding'])
            
            # Custom metadata from other columns
            excluded_cols = {'title', 'content', 'text', 'author', 'tags', 
                           'status', 'embedding', 'uuid', 'created_at', 'updated_at'}
            custom_metadata = {k: v for k, v in row.items() 
                             if k not in excluded_cols and v is not None}
            
            if custom_metadata:
                record.metadata['custom_metadata'] = custom_metadata
            
            records.append(record)
        
        # Add to dataset
        dataset.add_many(records)
        imported += len(records)
        print(f"Imported {imported}/{total_rows} rows")
    
    return imported
```

## Export Operations

### JSON Export

```python
def export_to_json(dataset, output_path, filter=None, include_embeddings=False):
    """Export dataset to JSON file."""
    documents = []
    
    # Create scanner with optional filter
    scanner = dataset.scanner(filter=filter) if filter else dataset.scanner()
    
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            doc = {
                'uuid': row['uuid'],
                'title': row['title'],
                'content': row.get('text_content', ''),
                'author': row.get('author'),
                'tags': row.get('tags', []),
                'status': row.get('status'),
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'metadata': row.get('custom_metadata', {})
            }
            
            # Include embeddings if requested
            if include_embeddings and row.get('embedding'):
                doc['embedding'] = row['embedding']
            
            # Include relationships
            if row.get('relationships'):
                doc['relationships'] = row['relationships']
            
            documents.append(doc)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(documents)} documents to {output_path}")
    return len(documents)

def export_to_jsonl(dataset, output_path, filter=None, batch_size=1000):
    """Export dataset to JSON Lines file."""
    exported = 0
    
    scanner = dataset.scanner(filter=filter) if filter else dataset.scanner()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for batch in scanner.to_batches(batch_size=batch_size):
            for row in batch.to_pylist():
                doc = {
                    'uuid': row['uuid'],
                    'title': row['title'],
                    'content': row.get('text_content', ''),
                    'author': row.get('author'),
                    'tags': row.get('tags', []),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                
                # Add non-null fields
                for field in ['status', 'version', 'collection']:
                    if row.get(field):
                        doc[field] = row[field]
                
                # Add custom metadata
                if row.get('custom_metadata'):
                    doc['metadata'] = row['custom_metadata']
                
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
                exported += 1
        
        if exported % 1000 == 0:
            print(f"Exported {exported} documents")
    
    print(f"Total exported: {exported} documents")
    return exported
```

### CSV Export

```python
def export_to_csv(dataset, output_path, columns=None, filter=None):
    """Export dataset to CSV file."""
    # Get data
    if filter:
        table = dataset.scanner(filter=filter).to_table()
    else:
        table = dataset.to_table()
    
    # Convert to pandas
    df = table.to_pandas()
    
    # Select columns if specified
    if columns:
        # Ensure requested columns exist
        available_cols = df.columns.tolist()
        columns = [col for col in columns if col in available_cols]
        df = df[columns]
    
    # Flatten nested structures
    if 'tags' in df.columns:
        df['tags'] = df['tags'].apply(lambda x: ','.join(x) if x else '')
    
    if 'custom_metadata' in df.columns:
        # Expand custom metadata into columns
        metadata_df = pd.json_normalize(df['custom_metadata'])
        metadata_df.columns = [f'metadata.{col}' for col in metadata_df.columns]
        df = pd.concat([df.drop('custom_metadata', axis=1), metadata_df], axis=1)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} rows to {output_path}")
    
    return len(df)

def export_to_csv_custom(dataset, output_path, field_mapping):
    """Export with custom field mapping."""
    rows = []
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            csv_row = {}
            
            for csv_field, accessor in field_mapping.items():
                if callable(accessor):
                    # Custom accessor function
                    csv_row[csv_field] = accessor(row)
                elif '.' in accessor:
                    # Nested field access
                    value = row
                    for part in accessor.split('.'):
                        value = value.get(part, '') if value else ''
                    csv_row[csv_field] = value
                else:
                    # Direct field access
                    csv_row[csv_field] = row.get(accessor, '')
            
            rows.append(csv_row)
    
    # Create DataFrame and save
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    
    return len(df)

# Example usage
field_mapping = {
    'ID': 'uuid',
    'Title': 'title',
    'Author': 'author',
    'Word Count': lambda row: len(row.get('text_content', '').split()),
    'Department': 'custom_metadata.department',
    'Quality Score': 'custom_metadata.quality_score.score'
}

export_to_csv_custom(dataset, 'custom_export.csv', field_mapping)
```

### Markdown Export

```python
def export_to_markdown(dataset, output_dir, filter=None, include_metadata=True):
    """Export documents as markdown files."""
    from pathlib import Path
    import yaml
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    exported = 0
    scanner = dataset.scanner(filter=filter) if filter else dataset.scanner()
    
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            # Create filename from title or UUID
            title = row.get('title', 'Untitled')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            
            filename = f"{safe_title}_{row['uuid'][:8]}.md"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write frontmatter
                if include_metadata:
                    frontmatter = {
                        'title': row['title'],
                        'uuid': row['uuid'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                    
                    # Add optional fields
                    for field in ['author', 'tags', 'status', 'version']:
                        if row.get(field):
                            frontmatter[field] = row[field]
                    
                    # Add custom metadata
                    if row.get('custom_metadata'):
                        frontmatter['metadata'] = row['custom_metadata']
                    
                    f.write('---\n')
                    f.write(yaml.dump(frontmatter, default_flow_style=False))
                    f.write('---\n\n')
                
                # Write content
                content = row.get('text_content', '')
                
                # Ensure title is in content
                if not content.startswith('#'):
                    f.write(f"# {row['title']}\n\n")
                
                f.write(content)
            
            exported += 1
            if exported % 100 == 0:
                print(f"Exported {exported} documents")
    
    print(f"Exported {exported} documents to {output_dir}")
    return exported
```

### Parquet Export

```python
def export_to_parquet(dataset, output_path, filter=None, include_embeddings=True):
    """Export dataset to Parquet file."""
    # Get filtered data
    if filter:
        table = dataset.scanner(filter=filter).to_table()
    else:
        table = dataset.to_table()
    
    # Optionally remove embeddings to reduce size
    if not include_embeddings and 'embedding' in table.column_names:
        columns = [col for col in table.column_names if col != 'embedding']
        table = table.select(columns)
    
    # Write to parquet
    pq.write_table(table, output_path, compression='snappy')
    
    print(f"Exported {table.num_rows} rows to {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    
    return table.num_rows
```

## Connector Imports

### GitHub Import

```python
from contextframe.connectors import GitHubConnector

def import_from_github(dataset, owner, repo, path="", file_pattern="**/*.md"):
    """Import documents from GitHub repository."""
    connector = GitHubConnector(
        token=os.getenv("GITHUB_TOKEN"),
        owner=owner,
        repo=repo
    )
    
    # Sync documents
    documents = connector.sync_documents(
        path=path,
        file_pattern=file_pattern,
        include_content=True
    )
    
    # Convert to FrameRecords
    records = []
    for doc in documents:
        record = FrameRecord.create(
            title=doc.title,
            content=doc.content,
            source_url=doc.source_url,
            source_type="github",
            author=doc.metadata.get("author"),
            tags=["github", repo],
            custom_metadata={
                "github_path": doc.metadata.get("path"),
                "github_sha": doc.metadata.get("sha"),
                "github_size": doc.metadata.get("size"),
                "github_url": doc.source_url
            }
        )
        records.append(record)
    
    # Add to dataset
    dataset.add_many(records)
    print(f"Imported {len(records)} documents from GitHub")
    
    return len(records)
```

### External System Import

```python
class ExternalSystemImporter:
    """Generic importer for external systems."""
    
    def __init__(self, dataset):
        self.dataset = dataset
    
    def import_from_api(self, api_url, headers=None, params=None):
        """Import from REST API."""
        import requests
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle pagination
        all_items = []
        if isinstance(data, dict) and 'items' in data:
            all_items.extend(data['items'])
            
            # Follow pagination
            while 'next' in data:
                response = requests.get(data['next'], headers=headers)
                data = response.json()
                all_items.extend(data.get('items', []))
        else:
            all_items = data if isinstance(data, list) else [data]
        
        # Convert to FrameRecords
        records = []
        for item in all_items:
            record = self.map_to_framerecord(item)
            if record:
                records.append(record)
        
        # Add to dataset
        self.dataset.add_many(records)
        return len(records)
    
    def map_to_framerecord(self, item):
        """Override this method for custom mapping."""
        return FrameRecord.create(
            title=item.get('title', 'Untitled'),
            content=item.get('content', item.get('description', '')),
            source_url=item.get('url'),
            custom_metadata=item
        )
```

## Migration Tools

### Dataset Migration

```python
def migrate_dataset(source_dataset, target_dataset, transform_fn=None, batch_size=1000):
    """Migrate data between datasets with optional transformation."""
    migrated = 0
    errors = []
    
    for batch in source_dataset.to_batches(batch_size=batch_size):
        records = []
        
        for row in batch.to_pylist():
            try:
                # Convert to FrameRecord
                record = FrameRecord.from_arrow(row)
                
                # Apply transformation if provided
                if transform_fn:
                    record = transform_fn(record)
                
                records.append(record)
            except Exception as e:
                errors.append((row.get('uuid', 'unknown'), str(e)))
        
        # Add to target
        if records:
            target_dataset.add_many(records)
            migrated += len(records)
            print(f"Migrated {migrated} documents")
    
    print(f"Migration complete: {migrated} documents migrated")
    if errors:
        print(f"Errors: {len(errors)} documents failed")
    
    return migrated, errors

# Example transformation
def upgrade_schema_v1_to_v2(record):
    """Transform records from schema v1 to v2."""
    # Add new required field
    if 'record_type' not in record.metadata:
        record.metadata['record_type'] = 'document'
    
    # Migrate old field names
    if 'category' in record.metadata:
        if 'tags' not in record.metadata:
            record.metadata['tags'] = []
        record.metadata['tags'].append(f"category:{record.metadata['category']}")
        del record.metadata['category']
    
    # Update version
    record.metadata['schema_version'] = '2.0'
    
    return record
```

### Incremental Import

```python
class IncrementalImporter:
    """Handle incremental imports with deduplication."""
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.imported_ids = set()
        self._load_existing_ids()
    
    def _load_existing_ids(self):
        """Load existing document IDs."""
        for batch in self.dataset.to_batches(columns=['uuid']):
            for row in batch.to_pylist():
                self.imported_ids.add(row['uuid'])
    
    def import_incremental(self, documents, id_field='uuid'):
        """Import only new documents."""
        new_documents = []
        skipped = 0
        
        for doc in documents:
            doc_id = doc.get(id_field)
            
            if doc_id and doc_id in self.imported_ids:
                skipped += 1
                continue
            
            new_documents.append(doc)
            if doc_id:
                self.imported_ids.add(doc_id)
        
        print(f"Skipped {skipped} existing documents")
        
        # Import new documents
        if new_documents:
            records = [self._convert_to_record(doc) for doc in new_documents]
            self.dataset.add_many(records)
            print(f"Imported {len(records)} new documents")
        
        return len(new_documents)
    
    def _convert_to_record(self, doc):
        """Convert document to FrameRecord."""
        return FrameRecord.create(
            title=doc.get('title', 'Untitled'),
            content=doc.get('content', ''),
            **{k: v for k, v in doc.items() 
               if k not in ['title', 'content']}
        )
```

## Bulk Operations

### Parallel Import

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob

def parallel_import_files(dataset, file_pattern, import_function, max_workers=4):
    """Import multiple files in parallel."""
    files = glob.glob(file_pattern)
    total_files = len(files)
    
    if total_files == 0:
        print("No files found matching pattern")
        return 0
    
    print(f"Found {total_files} files to import")
    
    imported_total = 0
    errors = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(import_function, dataset, file): file
            for file in files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                count = future.result()
                imported_total += count
                print(f"✓ {file}: {count} documents")
            except Exception as e:
                errors.append((file, str(e)))
                print(f"✗ {file}: {e}")
    
    print(f"\nTotal imported: {imported_total} documents from {total_files - len(errors)} files")
    if errors:
        print(f"Failed files: {len(errors)}")
    
    return imported_total, errors
```

### Streaming Export

```python
def streaming_export_json(dataset, output_file, filter=None, chunk_size=1000):
    """Export large datasets with streaming."""
    import ijson
    
    scanner = dataset.scanner(filter=filter) if filter else dataset.scanner()
    
    with open(output_file, 'w') as f:
        f.write('[')  # Start JSON array
        first = True
        
        for batch in scanner.to_batches(batch_size=chunk_size):
            for row in batch.to_pylist():
                if not first:
                    f.write(',')
                first = False
                
                # Write single document
                doc = {
                    'uuid': row['uuid'],
                    'title': row['title'],
                    'content': row.get('text_content', ''),
                    'metadata': row.get('custom_metadata', {})
                }
                
                f.write('\n  ')
                f.write(json.dumps(doc, ensure_ascii=False))
        
        f.write('\n]')  # End JSON array
```

## Format Conversion

### Universal Converter

```python
class FormatConverter:
    """Convert between different formats."""
    
    @staticmethod
    def json_to_csv(json_path, csv_path):
        """Convert JSON to CSV."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            data = [data]
        
        # Flatten nested structures
        flattened = []
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, (list, dict)):
                    flat_item[key] = json.dumps(value)
                else:
                    flat_item[key] = value
            flattened.append(flat_item)
        
        # Create DataFrame and save
        df = pd.DataFrame(flattened)
        df.to_csv(csv_path, index=False)
        
        return len(df)
    
    @staticmethod
    def csv_to_jsonl(csv_path, jsonl_path):
        """Convert CSV to JSON Lines."""
        df = pd.read_csv(csv_path)
        
        with open(jsonl_path, 'w') as f:
            for _, row in df.iterrows():
                # Convert row to dict, handling NaN
                row_dict = {}
                for col, value in row.items():
                    if pd.notna(value):
                        # Try to parse JSON strings
                        if isinstance(value, str) and value.startswith('['):
                            try:
                                value = json.loads(value)
                            except:
                                pass
                        row_dict[col] = value
                
                f.write(json.dumps(row_dict) + '\n')
        
        return len(df)
    
    @staticmethod
    def markdown_to_json(md_dir, json_path):
        """Convert markdown files to JSON."""
        documents = []
        
        for md_file in Path(md_dir).glob("**/*.md"):
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            metadata = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        metadata = yaml.safe_load(parts[1])
                        content = parts[2].strip()
                    except:
                        pass
            
            doc = {
                'title': metadata.get('title', md_file.stem),
                'content': content,
                'source_file': str(md_file),
                'metadata': metadata
            }
            documents.append(doc)
        
        with open(json_path, 'w') as f:
            json.dump(documents, f, indent=2)
        
        return len(documents)
```

## Best Practices

### 1. Validation

```python
def validate_import_data(documents, required_fields=['title']):
    """Validate documents before import."""
    valid = []
    invalid = []
    
    for i, doc in enumerate(documents):
        errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in doc or not doc[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types
        if 'tags' in doc and not isinstance(doc['tags'], list):
            errors.append("Tags must be a list")
        
        if 'created_at' in doc:
            try:
                datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00'))
            except:
                errors.append("Invalid created_at timestamp")
        
        if errors:
            invalid.append({
                'index': i,
                'document': doc,
                'errors': errors
            })
        else:
            valid.append(doc)
    
    return valid, invalid

def import_with_validation(dataset, documents):
    """Import with validation and error handling."""
    valid, invalid = validate_import_data(documents)
    
    print(f"Valid documents: {len(valid)}")
    print(f"Invalid documents: {len(invalid)}")
    
    if invalid:
        # Save invalid documents for review
        with open('import_errors.json', 'w') as f:
            json.dump(invalid, f, indent=2)
        print("Invalid documents saved to import_errors.json")
    
    # Import valid documents
    if valid:
        records = []
        for doc in valid:
            record = FrameRecord.create(
                title=doc['title'],
                content=doc.get('content', ''),
                **{k: v for k, v in doc.items() 
                   if k not in ['title', 'content']}
            )
            records.append(record)
        
        dataset.add_many(records)
        print(f"Imported {len(records)} documents")
    
    return len(valid), len(invalid)
```

### 2. Progress Tracking

```python
from tqdm import tqdm

class ImportProgress:
    """Track import progress with statistics."""
    
    def __init__(self, total_items):
        self.total = total_items
        self.processed = 0
        self.succeeded = 0
        self.failed = 0
        self.start_time = time.time()
        self.pbar = tqdm(total=total_items, desc="Importing")
    
    def update(self, success=True):
        """Update progress."""
        self.processed += 1
        if success:
            self.succeeded += 1
        else:
            self.failed += 1
        
        self.pbar.update(1)
        self.pbar.set_postfix({
            'success': self.succeeded,
            'failed': self.failed,
            'rate': f"{self.get_rate():.1f}/s"
        })
    
    def get_rate(self):
        """Get processing rate."""
        elapsed = time.time() - self.start_time
        return self.processed / elapsed if elapsed > 0 else 0
    
    def close(self):
        """Close progress bar and show summary."""
        self.pbar.close()
        
        elapsed = time.time() - self.start_time
        print(f"\nImport Summary:")
        print(f"  Total: {self.total}")
        print(f"  Succeeded: {self.succeeded}")
        print(f"  Failed: {self.failed}")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Rate: {self.get_rate():.1f} items/s")
```

### 3. Memory Management

```python
def memory_efficient_import(dataset, large_file, file_type='json'):
    """Import large files with minimal memory usage."""
    
    if file_type == 'json':
        # Use streaming JSON parser
        import ijson
        
        with open(large_file, 'rb') as f:
            parser = ijson.items(f, 'item')
            
            batch = []
            for item in parser:
                record = FrameRecord.create(
                    title=item.get('title', 'Untitled'),
                    content=item.get('content', '')
                )
                batch.append(record)
                
                if len(batch) >= 1000:
                    dataset.add_many(batch)
                    batch = []
            
            # Add remaining
            if batch:
                dataset.add_many(batch)
    
    elif file_type == 'csv':
        # Use chunked CSV reading
        for chunk in pd.read_csv(large_file, chunksize=1000):
            records = []
            for _, row in chunk.iterrows():
                record = FrameRecord.create(
                    title=row.get('title', 'Untitled'),
                    content=row.get('content', '')
                )
                records.append(record)
            
            dataset.add_many(records)
```

## Next Steps

- Explore [External Connectors](../integration/overview.md)
- See [Migration Examples](../cookbook/data-migration.md)
- Check [Performance Guide](../mcp/guides/performance.md)
- Review the [API Reference](../api/import-export.md)