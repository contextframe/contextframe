# Data Import/Export Guide

This comprehensive guide covers ContextFrame's import and export capabilities, including bulk operations, format conversions, streaming for large datasets, backup strategies, and cross-region replication.

## Overview

ContextFrame provides flexible import/export functionality designed for:

- **Multiple Formats**: JSON, CSV, Parquet, Arrow, and custom formats
- **Scalability**: Stream processing for datasets of any size
- **Reliability**: Checkpoint-based resumable operations
- **Performance**: Parallel processing and optimized I/O
- **Compatibility**: Integration with common data pipeline tools

## Import Strategies

### JSON Import

#### Single File Import

```python
from contextframe import FrameDataset, FrameRecord, create_metadata, generate_uuid
import json

def import_json_file(json_path, dataset_path="imported_data.lance"):
    """Import documents from a JSON file."""
    
    dataset = FrameDataset.create(dataset_path)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Handle both single object and array formats
    if isinstance(data, dict):
        data = [data]
    
    records = []
    for item in data:
        # Extract fields with fallbacks
        text_content = (item.get('content') or 
                       item.get('text') or 
                       item.get('body', ''))
        
        title = (item.get('title') or 
                item.get('name') or 
                f"Document {item.get('id', 'Unknown')}")
        
        # Build metadata
        metadata_fields = {k: v for k, v in item.items() 
                          if k not in ['content', 'text', 'body', 'title', 'name', 'embedding']}
        
        metadata = create_metadata(
            title=title,
            source="json_import",
            **metadata_fields
        )
        
        # Handle pre-existing embeddings
        embedding = item.get('embedding')
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            embedding=embedding
        )
        
        records.append(record)
    
    dataset.add_many(records, generate_embeddings=(embedding is None))
    
    print(f"Imported {len(records)} documents from JSON")
    return dataset
```

#### Streaming JSON Import

For large JSON files, use streaming:

```python
import ijson

def stream_import_json(json_path, dataset_path="imported_data.lance", batch_size=1000):
    """Stream import large JSON files."""
    
    dataset = FrameDataset.create(dataset_path)
    
    records = []
    total_imported = 0
    
    with open(json_path, 'rb') as f:
        # Parse JSON array items one by one
        parser = ijson.items(f, 'item')
        
        for item in parser:
            # Process item
            record = create_record_from_json(item)
            records.append(record)
            
            # Batch insert
            if len(records) >= batch_size:
                dataset.add_many(records)
                total_imported += len(records)
                print(f"Imported {total_imported} documents")
                records = []
        
        # Import remaining records
        if records:
            dataset.add_many(records)
            total_imported += len(records)
    
    print(f"Total imported: {total_imported} documents")
    return dataset
```

### CSV Import

#### Basic CSV Import

```python
import csv
from datetime import datetime

def import_csv_file(csv_path, dataset_path="imported_data.lance",
                   text_column='content', title_column='title',
                   delimiter=',', encoding='utf-8'):
    """Import documents from CSV file."""
    
    dataset = FrameDataset.create(dataset_path)
    
    records = []
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        
        for row_num, row in enumerate(reader):
            # Extract content and title
            text_content = row.get(text_column, '')
            title = row.get(title_column, f"Row {row_num + 1}")
            
            # All other columns become metadata
            metadata_fields = {k: v for k, v in row.items() 
                             if k not in [text_column, title_column]}
            
            # Convert numeric strings if possible
            for key, value in metadata_fields.items():
                try:
                    # Try integer
                    metadata_fields[key] = int(value)
                except ValueError:
                    try:
                        # Try float
                        metadata_fields[key] = float(value)
                    except ValueError:
                        # Keep as string
                        pass
            
            metadata = create_metadata(
                title=title,
                source="csv_import",
                row_number=row_num + 1,
                **metadata_fields
            )
            
            record = FrameRecord(
                text_content=text_content,
                metadata=metadata,
                unique_id=generate_uuid()
            )
            
            records.append(record)
    
    dataset.add_many(records)
    
    print(f"Imported {len(records)} documents from CSV")
    return dataset
```

#### Advanced CSV Import with Type Detection

```python
import pandas as pd
import numpy as np

def import_csv_advanced(csv_path, dataset_path="imported_data.lance",
                       parse_dates=True, chunk_size=10000):
    """Import CSV with automatic type detection and chunking."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Read CSV in chunks for memory efficiency
    total_imported = 0
    
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size, 
                            parse_dates=parse_dates, 
                            infer_datetime_format=True):
        records = []
        
        for idx, row in chunk.iterrows():
            # Convert row to dict, handling NaN values
            row_dict = row.replace({np.nan: None}).to_dict()
            
            # Identify content columns
            text_columns = identify_text_columns(row_dict)
            text_content = ' '.join([str(row_dict[col]) 
                                   for col in text_columns 
                                   if row_dict[col] is not None])
            
            # Generate title from first few columns
            title = generate_title_from_row(row_dict)
            
            # Convert timestamps to ISO format
            for key, value in row_dict.items():
                if isinstance(value, pd.Timestamp):
                    row_dict[key] = value.isoformat()
            
            metadata = create_metadata(
                title=title,
                source="csv_import",
                row_index=idx,
                **{k: v for k, v in row_dict.items() 
                   if k not in text_columns and v is not None}
            )
            
            record = FrameRecord(
                text_content=text_content,
                metadata=metadata,
                unique_id=generate_uuid()
            )
            
            records.append(record)
        
        dataset.add_many(records)
        total_imported += len(records)
        print(f"Imported {total_imported} documents")
    
    return dataset

def identify_text_columns(row_dict):
    """Identify columns likely containing text content."""
    text_columns = []
    for key, value in row_dict.items():
        if value and isinstance(value, str) and len(value) > 50:
            text_columns.append(key)
    return text_columns or list(row_dict.keys())[:3]  # Fallback to first 3 columns
```

### Parquet Import

#### Direct Parquet Import

```python
import pyarrow.parquet as pq
import pyarrow as pa

def import_parquet_file(parquet_path, dataset_path="imported_data.lance",
                       text_columns=None, batch_size=10000):
    """Import documents from Parquet file with efficient columnar processing."""
    
    dataset = FrameDataset.create(dataset_path)
    
    # Read Parquet file
    parquet_file = pq.ParquetFile(parquet_path)
    
    # Get schema information
    schema = parquet_file.schema_arrow
    print(f"Parquet schema: {schema}")
    
    total_imported = 0
    
    # Process in batches
    for batch in parquet_file.iter_batches(batch_size=batch_size):
        records = []
        
        # Convert to pandas for easier processing
        df = batch.to_pandas()
        
        for idx, row in df.iterrows():
            # Determine text content
            if text_columns:
                text_content = ' '.join([str(row[col]) 
                                       for col in text_columns 
                                       if col in row and pd.notna(row[col])])
            else:
                # Auto-detect text columns
                text_cols = [col for col in df.columns 
                           if df[col].dtype == 'object']
                text_content = ' '.join([str(row[col]) 
                                       for col in text_cols 
                                       if pd.notna(row[col])])
            
            # Build metadata from all columns
            metadata_dict = {}
            for col in df.columns:
                if pd.notna(row[col]):
                    value = row[col]
                    # Convert numpy types to Python types
                    if hasattr(value, 'item'):
                        value = value.item()
                    metadata_dict[col] = value
            
            metadata = create_metadata(
                title=f"Record {total_imported + idx + 1}",
                source="parquet_import",
                **metadata_dict
            )
            
            record = FrameRecord(
                text_content=text_content,
                metadata=metadata,
                unique_id=generate_uuid()
            )
            
            records.append(record)
        
        dataset.add_many(records)
        total_imported += len(records)
        print(f"Imported {total_imported} records")
    
    return dataset
```

#### Parquet to Lance Direct Conversion

For optimal performance, convert Parquet directly to Lance:

```python
def convert_parquet_to_lance(parquet_path, dataset_path="imported_data.lance"):
    """Direct Parquet to Lance conversion for maximum efficiency."""
    
    import lance
    
    # Read Parquet file
    table = pq.read_table(parquet_path)
    
    # Add ContextFrame required columns
    num_rows = len(table)
    
    # Generate UUIDs
    unique_ids = pa.array([generate_uuid() for _ in range(num_rows)])
    
    # Add record type
    record_types = pa.array(['document'] * num_rows)
    
    # Add timestamps
    import time
    current_time = time.time()
    created_at = pa.array([current_time] * num_rows)
    updated_at = pa.array([current_time] * num_rows)
    
    # Combine into new table
    new_columns = [
        ('unique_id', unique_ids),
        ('record_type', record_types),
        ('created_at', created_at),
        ('updated_at', updated_at)
    ]
    
    for name, col in new_columns:
        table = table.append_column(name, col)
    
    # Write to Lance
    lance.write_dataset(table, dataset_path)
    
    print(f"Converted {num_rows} records from Parquet to Lance")
    return dataset_path
```

### Custom Format Import

#### XML Import Example

```python
import xml.etree.ElementTree as ET

def import_xml_file(xml_path, dataset_path="imported_data.lance",
                   record_xpath='.//record', content_fields=None):
    """Import documents from XML file."""
    
    dataset = FrameDataset.create(dataset_path)
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    records = []
    for elem in root.findall(record_xpath):
        # Extract all text content
        if content_fields:
            text_parts = []
            for field in content_fields:
                field_elem = elem.find(field)
                if field_elem is not None and field_elem.text:
                    text_parts.append(field_elem.text)
            text_content = ' '.join(text_parts)
        else:
            # Get all text from element
            text_content = ' '.join(elem.itertext())
        
        # Extract metadata from attributes and child elements
        metadata_dict = dict(elem.attrib)
        for child in elem:
            if child.text:
                metadata_dict[child.tag] = child.text
        
        metadata = create_metadata(
            title=metadata_dict.get('title', elem.get('id', 'Unknown')),
            source="xml_import",
            **metadata_dict
        )
        
        record = FrameRecord(
            text_content=text_content,
            metadata=metadata,
            unique_id=generate_uuid()
        )
        
        records.append(record)
    
    dataset.add_many(records)
    
    print(f"Imported {len(records)} documents from XML")
    return dataset
```

## Export Strategies

### JSON Export

#### Full Export

```python
def export_to_json(dataset, output_path, include_embeddings=False):
    """Export entire dataset to JSON."""
    
    documents = []
    
    # Iterate through all records
    for record in dataset.iterate():
        doc = {
            'unique_id': str(record.unique_id),
            'title': record.metadata.title,
            'content': record.text_content,
            'metadata': record.metadata.custom_metadata,
            'created_at': record.created_at,
            'updated_at': record.updated_at,
            'record_type': record.record_type
        }
        
        if include_embeddings and record.embedding is not None:
            doc['embedding'] = record.embedding.tolist()
        
        # Include relationships
        if record.relationships:
            doc['relationships'] = record.relationships
        
        documents.append(doc)
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(documents, f, indent=2, default=str)
    
    print(f"Exported {len(documents)} documents to JSON")
    return output_path
```

#### Streaming JSON Export

```python
def export_to_json_streaming(dataset, output_path, batch_size=1000):
    """Export large datasets to JSON using streaming."""
    
    with open(output_path, 'w') as f:
        f.write('[\n')
        
        first = True
        total_exported = 0
        
        # Process in batches
        for batch in dataset.iterate_batches(batch_size=batch_size):
            for record in batch:
                if not first:
                    f.write(',\n')
                first = False
                
                doc = record_to_dict(record)
                json.dump(doc, f, default=str)
                total_exported += 1
            
            print(f"Exported {total_exported} documents")
        
        f.write('\n]')
    
    print(f"Total exported: {total_exported} documents")
    return output_path
```

### CSV Export

#### Flattened CSV Export

```python
def export_to_csv(dataset, output_path, columns=None, delimiter=','):
    """Export dataset to CSV with flattened structure."""
    
    import csv
    
    # Determine columns if not specified
    if not columns:
        # Sample first 100 records to find all possible fields
        sample_records = list(dataset.iterate(limit=100))
        columns = set(['unique_id', 'title', 'content', 'created_at', 'updated_at'])
        
        for record in sample_records:
            columns.update(record.metadata.custom_metadata.keys())
        
        columns = sorted(list(columns))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=delimiter)
        writer.writeheader()
        
        total_exported = 0
        for record in dataset.iterate():
            row = {
                'unique_id': str(record.unique_id),
                'title': record.metadata.title,
                'content': record.text_content,
                'created_at': record.created_at,
                'updated_at': record.updated_at
            }
            
            # Add custom metadata
            row.update(record.metadata.custom_metadata)
            
            # Fill missing columns with empty string
            for col in columns:
                if col not in row:
                    row[col] = ''
            
            writer.writerow(row)
            total_exported += 1
            
            if total_exported % 1000 == 0:
                print(f"Exported {total_exported} documents")
    
    print(f"Total exported: {total_exported} documents to CSV")
    return output_path
```

### Parquet Export

#### Efficient Parquet Export

```python
def export_to_parquet(dataset, output_path, compression='snappy', batch_size=10000):
    """Export dataset to Parquet format."""
    
    import pyarrow as pa
    import pyarrow.parquet as pq
    from collections import defaultdict
    
    # Prepare schema
    schema_fields = [
        ('unique_id', pa.string()),
        ('title', pa.string()),
        ('content', pa.string()),
        ('record_type', pa.string()),
        ('created_at', pa.float64()),
        ('updated_at', pa.float64())
    ]
    
    # Sample for additional metadata fields
    sample_record = next(dataset.iterate())
    for key, value in sample_record.metadata.custom_metadata.items():
        if isinstance(value, bool):
            schema_fields.append((key, pa.bool_()))
        elif isinstance(value, int):
            schema_fields.append((key, pa.int64()))
        elif isinstance(value, float):
            schema_fields.append((key, pa.float64()))
        else:
            schema_fields.append((key, pa.string()))
    
    schema = pa.schema(schema_fields)
    
    # Open Parquet writer
    with pq.ParquetWriter(output_path, schema, compression=compression) as writer:
        batch_data = defaultdict(list)
        batch_count = 0
        
        for record in dataset.iterate():
            # Add base fields
            batch_data['unique_id'].append(str(record.unique_id))
            batch_data['title'].append(record.metadata.title)
            batch_data['content'].append(record.text_content)
            batch_data['record_type'].append(record.record_type)
            batch_data['created_at'].append(record.created_at)
            batch_data['updated_at'].append(record.updated_at)
            
            # Add metadata fields
            for key in sample_record.metadata.custom_metadata.keys():
                value = record.metadata.custom_metadata.get(key)
                batch_data[key].append(value)
            
            batch_count += 1
            
            # Write batch
            if batch_count >= batch_size:
                table = pa.table(batch_data, schema=schema)
                writer.write_table(table)
                batch_data = defaultdict(list)
                batch_count = 0
                print(f"Exported {writer.num_rows} records")
        
        # Write remaining records
        if batch_count > 0:
            table = pa.table(batch_data, schema=schema)
            writer.write_table(table)
    
    print(f"Total exported: {writer.num_rows} documents to Parquet")
    return output_path
```

### Lance Export

#### Direct Lance Export

```python
def export_lance_to_lance(source_dataset, target_path, filter_expr=None):
    """Export Lance dataset to another Lance dataset with optional filtering."""
    
    import lance
    
    # Open source dataset
    source = lance.dataset(source_dataset.path)
    
    if filter_expr:
        # Apply filter
        filtered = source.filter(filter_expr)
        lance.write_dataset(filtered, target_path)
    else:
        # Direct copy
        import shutil
        shutil.copytree(source_dataset.path, target_path)
    
    print(f"Exported dataset to {target_path}")
    return target_path
```

## Streaming Large Datasets

### Memory-Efficient Processing

```python
class StreamingProcessor:
    """Process large datasets without loading everything into memory."""
    
    def __init__(self, dataset, batch_size=1000):
        self.dataset = dataset
        self.batch_size = batch_size
    
    def process_with_callback(self, callback_func):
        """Process dataset with a callback function."""
        
        processed = 0
        for batch in self.dataset.iterate_batches(batch_size=self.batch_size):
            for record in batch:
                callback_func(record)
                processed += 1
            
            if processed % 10000 == 0:
                print(f"Processed {processed} records")
        
        return processed
    
    def transform_and_export(self, transform_func, output_dataset):
        """Transform records and export to new dataset."""
        
        transformed_records = []
        processed = 0
        
        for batch in self.dataset.iterate_batches(batch_size=self.batch_size):
            for record in batch:
                transformed = transform_func(record)
                if transformed:
                    transformed_records.append(transformed)
                
                if len(transformed_records) >= self.batch_size:
                    output_dataset.add_many(transformed_records)
                    transformed_records = []
                
                processed += 1
            
            print(f"Transformed {processed} records")
        
        # Add remaining records
        if transformed_records:
            output_dataset.add_many(transformed_records)
        
        return processed
```

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def parallel_export(dataset, export_func, num_workers=None, chunk_size=10000):
    """Export dataset using parallel processing."""
    
    num_workers = num_workers or multiprocessing.cpu_count()
    
    # Count total records
    total_records = dataset.count()
    
    # Calculate chunks
    chunks = []
    for offset in range(0, total_records, chunk_size):
        chunks.append({
            'offset': offset,
            'limit': min(chunk_size, total_records - offset)
        })
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        for i, chunk in enumerate(chunks):
            output_path = f"export_chunk_{i}.json"
            future = executor.submit(
                export_chunk,
                dataset.path,
                output_path,
                chunk['offset'],
                chunk['limit'],
                export_func
            )
            futures.append((future, output_path))
        
        # Collect results
        chunk_files = []
        for future, output_path in futures:
            future.result()  # Wait for completion
            chunk_files.append(output_path)
    
    # Merge chunk files
    merge_export_files(chunk_files, "final_export.json")
    
    return "final_export.json"

def export_chunk(dataset_path, output_path, offset, limit, export_func):
    """Export a chunk of the dataset."""
    dataset = FrameDataset.open(dataset_path)
    records = list(dataset.iterate(offset=offset, limit=limit))
    export_func(records, output_path)
```

## Backup and Recovery

### Automated Backup Strategy

```python
import os
import time
from datetime import datetime
import shutil

class BackupManager:
    """Manage dataset backups with rotation and compression."""
    
    def __init__(self, dataset_path, backup_dir, max_backups=7):
        self.dataset_path = dataset_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, compress=True):
        """Create a timestamped backup."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        print(f"Creating backup: {backup_name}")
        
        if compress:
            # Create compressed backup
            import tarfile
            tar_path = f"{backup_path}.tar.gz"
            
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(self.dataset_path, arcname=os.path.basename(self.dataset_path))
            
            backup_size = os.path.getsize(tar_path)
            print(f"Backup created: {tar_path} ({backup_size / 1024 / 1024:.2f} MB)")
            
            return tar_path
        else:
            # Direct copy
            shutil.copytree(self.dataset_path, backup_path)
            backup_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(backup_path)
                            for filename in filenames)
            print(f"Backup created: {backup_path} ({backup_size / 1024 / 1024:.2f} MB)")
            
            return backup_path
    
    def rotate_backups(self):
        """Remove old backups keeping only max_backups."""
        
        # List all backups
        backups = []
        for item in os.listdir(self.backup_dir):
            if item.startswith("backup_"):
                path = os.path.join(self.backup_dir, item)
                mtime = os.path.getmtime(path)
                backups.append((mtime, path))
        
        # Sort by modification time
        backups.sort(reverse=True)
        
        # Remove old backups
        for _, path in backups[self.max_backups:]:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"Removed old backup: {path}")
    
    def restore_backup(self, backup_path, target_path=None):
        """Restore from backup."""
        
        target_path = target_path or self.dataset_path
        
        print(f"Restoring from: {backup_path}")
        
        if backup_path.endswith('.tar.gz'):
            # Extract compressed backup
            import tarfile
            
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(os.path.dirname(target_path))
        else:
            # Direct copy
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(backup_path, target_path)
        
        print(f"Restored to: {target_path}")
        return target_path
    
    def verify_backup(self, backup_path):
        """Verify backup integrity."""
        
        temp_restore = f"{backup_path}_verify"
        
        try:
            # Restore to temporary location
            self.restore_backup(backup_path, temp_restore)
            
            # Open dataset to verify
            dataset = FrameDataset.open(temp_restore)
            record_count = dataset.count()
            
            # Clean up
            shutil.rmtree(temp_restore)
            
            print(f"Backup verified: {record_count} records")
            return True, record_count
            
        except Exception as e:
            print(f"Backup verification failed: {str(e)}")
            if os.path.exists(temp_restore):
                shutil.rmtree(temp_restore)
            return False, str(e)
```

### Incremental Backup

```python
def incremental_backup(dataset, last_backup_timestamp, backup_path):
    """Create incremental backup containing only changes since last backup."""
    
    import lance
    
    # Query for changed records
    filter_expr = f"updated_at > {last_backup_timestamp}"
    
    # Get changed records
    source = lance.dataset(dataset.path)
    changed = source.filter(filter_expr)
    
    # Write incremental backup
    lance.write_dataset(changed, backup_path)
    
    num_changes = changed.count_rows()
    print(f"Incremental backup created: {num_changes} changed records")
    
    return backup_path
```

## Cross-Region Replication

### Cloud Storage Replication

```python
class CrossRegionReplicator:
    """Replicate datasets across cloud regions."""
    
    def __init__(self, source_dataset, regions_config):
        self.source_dataset = source_dataset
        self.regions_config = regions_config
    
    def replicate_to_s3(self, bucket_configs):
        """Replicate to multiple S3 buckets in different regions."""
        
        import boto3
        import lance
        
        source = lance.dataset(self.source_dataset.path)
        
        results = {}
        for region, bucket_config in bucket_configs.items():
            print(f"Replicating to {region}...")
            
            # Configure S3 client for region
            s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=bucket_config['access_key'],
                aws_secret_access_key=bucket_config['secret_key']
            )
            
            # Write to S3
            s3_path = f"s3://{bucket_config['bucket']}/{bucket_config['prefix']}"
            
            try:
                lance.write_dataset(
                    source,
                    s3_path,
                    storage_options={
                        'aws_access_key_id': bucket_config['access_key'],
                        'aws_secret_access_key': bucket_config['secret_key'],
                        'region': region
                    }
                )
                results[region] = {'status': 'success', 'path': s3_path}
                print(f"Replicated to {region}: {s3_path}")
                
            except Exception as e:
                results[region] = {'status': 'failed', 'error': str(e)}
                print(f"Failed to replicate to {region}: {str(e)}")
        
        return results
    
    def sync_replicas(self, primary_region, replica_regions):
        """Sync changes from primary to replica regions."""
        
        # Get latest version from primary
        primary_dataset = self.load_from_region(primary_region)
        primary_version = primary_dataset.version
        
        sync_results = {}
        for region in replica_regions:
            replica_dataset = self.load_from_region(region)
            replica_version = replica_dataset.version
            
            if replica_version < primary_version:
                # Sync needed
                print(f"Syncing {region} from v{replica_version} to v{primary_version}")
                
                # Get changes since replica version
                changes = self.get_changes_since_version(
                    primary_dataset, 
                    replica_version
                )
                
                # Apply changes to replica
                self.apply_changes(replica_dataset, changes)
                
                sync_results[region] = {
                    'synced': True,
                    'from_version': replica_version,
                    'to_version': primary_version,
                    'changes': len(changes)
                }
            else:
                sync_results[region] = {
                    'synced': False,
                    'reason': 'already up to date'
                }
        
        return sync_results
```

### Multi-Cloud Replication

```python
def replicate_across_clouds(dataset, cloud_configs):
    """Replicate dataset across multiple cloud providers."""
    
    results = {}
    
    for cloud, config in cloud_configs.items():
        if cloud == 'aws':
            results['aws'] = replicate_to_s3(dataset, config)
        elif cloud == 'gcp':
            results['gcp'] = replicate_to_gcs(dataset, config)
        elif cloud == 'azure':
            results['azure'] = replicate_to_azure(dataset, config)
    
    return results

def replicate_to_gcs(dataset, config):
    """Replicate to Google Cloud Storage."""
    import lance
    
    gcs_path = f"gs://{config['bucket']}/{config['prefix']}"
    
    lance.write_dataset(
        dataset,
        gcs_path,
        storage_options={
            'service_account': config['service_account_path']
        }
    )
    
    return {'status': 'success', 'path': gcs_path}

def replicate_to_azure(dataset, config):
    """Replicate to Azure Blob Storage."""
    import lance
    
    azure_path = f"az://{config['container']}/{config['prefix']}"
    
    lance.write_dataset(
        dataset,
        azure_path,
        storage_options={
            'account_name': config['account_name'],
            'account_key': config['account_key']
        }
    )
    
    return {'status': 'success', 'path': azure_path}
```

## Performance Optimization

### Batch Processing Best Practices

```python
class OptimizedImporter:
    """Optimized import with progress tracking and error handling."""
    
    def __init__(self, dataset_path, batch_size=5000, num_workers=4):
        self.dataset = FrameDataset.create(dataset_path)
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.stats = {
            'processed': 0,
            'failed': 0,
            'start_time': time.time()
        }
    
    def import_with_progress(self, data_source, transform_func):
        """Import with progress bar and statistics."""
        
        from tqdm import tqdm
        
        # Estimate total items
        if hasattr(data_source, '__len__'):
            total = len(data_source)
            pbar = tqdm(total=total, desc="Importing")
        else:
            pbar = tqdm(desc="Importing")
        
        batch = []
        for item in data_source:
            try:
                # Transform item
                record = transform_func(item)
                if record:
                    batch.append(record)
                
                # Process batch
                if len(batch) >= self.batch_size:
                    self.dataset.add_many(batch)
                    self.stats['processed'] += len(batch)
                    pbar.update(len(batch))
                    batch = []
                    
                    # Print statistics
                    self.print_stats()
                    
            except Exception as e:
                self.stats['failed'] += 1
                print(f"Error processing item: {str(e)}")
        
        # Process remaining batch
        if batch:
            self.dataset.add_many(batch)
            self.stats['processed'] += len(batch)
            pbar.update(len(batch))
        
        pbar.close()
        self.print_final_stats()
    
    def print_stats(self):
        """Print current statistics."""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0
        
        print(f"\rProcessed: {self.stats['processed']} | "
              f"Failed: {self.stats['failed']} | "
              f"Rate: {rate:.1f} docs/sec", end='')
    
    def print_final_stats(self):
        """Print final import statistics."""
        elapsed = time.time() - self.stats['start_time']
        
        print(f"\n\nImport completed:")
        print(f"  Total processed: {self.stats['processed']}")
        print(f"  Total failed: {self.stats['failed']}")
        print(f"  Time elapsed: {elapsed:.2f} seconds")
        print(f"  Average rate: {self.stats['processed'] / elapsed:.1f} docs/sec")
```

## Validation and Testing

### Data Integrity Validation

```python
def validate_import_export(original_data, exported_path, reimport_func):
    """Validate that export/import preserves data integrity."""
    
    # Reimport exported data
    reimported_dataset = reimport_func(exported_path)
    
    # Compare counts
    original_count = len(original_data)
    reimported_count = reimported_dataset.count()
    
    validations = {
        'count_match': original_count == reimported_count,
        'content_match': validate_content_preservation(original_data, reimported_dataset),
        'metadata_match': validate_metadata_preservation(original_data, reimported_dataset),
        'relationship_match': validate_relationship_preservation(original_data, reimported_dataset)
    }
    
    return {
        'passed': all(validations.values()),
        'validations': validations,
        'original_count': original_count,
        'reimported_count': reimported_count
    }

def validate_content_preservation(original_data, reimported_dataset):
    """Check that content is preserved accurately."""
    
    # Sample comparison
    sample_size = min(100, len(original_data))
    
    matches = 0
    for i in range(sample_size):
        original = original_data[i]
        reimported = reimported_dataset.get_by_index(i)
        
        if original.text_content == reimported.text_content:
            matches += 1
    
    return matches == sample_size
```

## Next Steps

1. **Choose your import/export format** based on your data sources and requirements
2. **Test with small datasets** before processing large volumes
3. **Implement monitoring** for long-running operations
4. **Set up automated backups** for production datasets
5. **Plan replication strategy** for high availability

For additional examples and patterns, see the [Cookbook](../cookbook/index.md) section.