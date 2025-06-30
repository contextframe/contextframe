# Google Drive Connector

The Google Drive connector enables importing documents, spreadsheets, presentations, and other files from Google Drive into ContextFrame. This guide covers authentication, usage patterns, and best practices.

## Overview

The Google Drive connector can import:
- Google Docs (converted to markdown)
- Google Sheets (as structured data)
- Google Slides (as text content)
- PDFs and text files
- Images with OCR support
- Folder hierarchies
- Shared drives and team folders

## Installation

The Google Drive connector requires additional dependencies:

```bash
pip install "contextframe[connectors]"
# Or specifically
pip install google-api-python-client google-auth google-auth-httplib2
```

```python
from contextframe.connectors import GoogleDriveConnector
```

## Authentication

### OAuth 2.0 (Recommended)

For user-specific access:

```python
connector = GoogleDriveConnector(
    client_id="your-client-id.apps.googleusercontent.com",
    client_secret="your-client-secret",
    refresh_token="your-refresh-token"
)
```

### Service Account

For server-to-server authentication:

```python
connector = GoogleDriveConnector(
    service_account_file="/path/to/service-account-key.json"
)

# Or with credentials dict
connector = GoogleDriveConnector(
    service_account_credentials={
        "type": "service_account",
        "project_id": "your-project",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...",
        # ... other fields
    }
)
```

### Setting Up Authentication

#### OAuth 2.0 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URIs
6. Download credentials.json

```python
# First-time authentication flow
from google_auth_oauthlib.flow import Flow

flow = Flow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)

# Get authorization URL
auth_url, _ = flow.authorization_url(prompt='consent')
print(f"Visit: {auth_url}")

# After authorization, exchange code for tokens
code = input("Enter authorization code: ")
flow.fetch_token(code=code)

# Save refresh token
refresh_token = flow.credentials.refresh_token
print(f"Refresh token: {refresh_token}")
```

#### Service Account Setup

1. Create service account in Google Cloud Console
2. Download JSON key file
3. Share Google Drive folders with service account email

```python
# Service account email format
# your-service-account@your-project.iam.gserviceaccount.com
```

## Basic Usage

### Import Files from Drive

```python
from contextframe import FrameDataset
from contextframe.connectors import GoogleDriveConnector

# Create dataset
dataset = FrameDataset.create("gdrive_docs.lance")

# Setup connector
connector = GoogleDriveConnector(
    service_account_file="service-account.json"
)

# Authenticate
connector.authenticate()

# List files in root
files = connector.list_files()
for file in files:
    print(f"{file.name} ({file.mimeType})")

# Import all documents
documents = connector.sync_documents(
    folder_id=None,  # Root folder
    mime_types=['application/vnd.google-apps.document']
)

# Convert to FrameRecords
for doc in documents:
    record = connector.map_to_frame_record(doc)
    dataset.add(record)

print(f"Imported {len(documents)} documents")
```

### Import from Specific Folder

```python
# Get folder ID from URL or use API
# URL format: https://drive.google.com/drive/folders/FOLDER_ID
folder_id = "1a2b3c4d5e6f7g8h9i0j"

# Sync folder contents
documents = connector.sync_documents(
    folder_id=folder_id,
    recursive=True,  # Include subfolders
    mime_types=[
        'application/vnd.google-apps.document',
        'application/vnd.google-apps.spreadsheet',
        'application/pdf'
    ]
)

# Import with folder context
for doc in documents:
    record = connector.map_to_frame_record(doc)
    
    # Add folder path to metadata
    record.metadata['custom_metadata']['folder_path'] = doc.folder_path
    record.metadata['collection'] = f"gdrive-{doc.folder_name}"
    
    dataset.add(record)
```

### Import Shared Drives

```python
# List shared drives
shared_drives = connector.list_shared_drives()
for drive in shared_drives:
    print(f"Drive: {drive.name} (ID: {drive.id})")

# Import from shared drive
documents = connector.sync_documents(
    drive_id="0ABcDeFgHiJkLmNoP",
    include_shared=True,
    mime_types=['application/vnd.google-apps.document']
)

# Process with drive context
for doc in documents:
    record = connector.map_to_frame_record(doc)
    record.metadata['custom_metadata']['drive_name'] = drive.name
    record.metadata['custom_metadata']['drive_type'] = 'shared'
    dataset.add(record)
```

## Advanced Features

### Document Conversion

```python
class GoogleDocConverter:
    """Convert Google Docs to markdown."""
    
    def __init__(self, connector):
        self.connector = connector
    
    def convert_document(self, file_id):
        """Convert Google Doc to markdown with formatting."""
        # Get document content
        doc = self.connector.get_document(file_id)
        
        # Export as HTML for rich formatting
        html_content = self.connector.export_file(
            file_id,
            mime_type='text/html'
        )
        
        # Convert HTML to Markdown
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        
        markdown = h.handle(html_content)
        
        # Clean up Google Docs artifacts
        markdown = self.clean_markdown(markdown)
        
        return markdown
    
    def clean_markdown(self, markdown):
        """Clean up converted markdown."""
        import re
        
        # Remove multiple blank lines
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
        
        # Fix list formatting
        markdown = re.sub(r'^\s*\*\s+', '- ', markdown, flags=re.MULTILINE)
        
        # Remove Google Docs comments
        markdown = re.sub(r'\[.\d+\]', '', markdown)
        
        return markdown.strip()
```

### Spreadsheet Import

```python
def import_spreadsheet(connector, dataset, file_id):
    """Import Google Sheets with structure preservation."""
    
    # Get spreadsheet metadata
    spreadsheet = connector.get_spreadsheet(file_id)
    
    # Process each sheet
    for sheet in spreadsheet.sheets:
        # Export sheet as CSV
        csv_content = connector.export_file(
            file_id,
            mime_type='text/csv',
            sheet_id=sheet.id
        )
        
        # Parse CSV
        import csv
        import io
        
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        
        # Create collection header for sheet
        sheet_record = FrameRecord.create(
            title=f"{spreadsheet.name} - {sheet.name}",
            content=f"Spreadsheet: {spreadsheet.name}\nSheet: {sheet.name}\nRows: {len(rows)}",
            record_type="collection_header",
            collection=f"gdrive-sheet-{file_id[:8]}",
            source_type="google_drive",
            custom_metadata={
                "gdrive_file_id": file_id,
                "gdrive_sheet_id": sheet.id,
                "gdrive_sheet_name": sheet.name,
                "row_count": len(rows),
                "column_count": len(rows[0]) if rows else 0
            }
        )
        dataset.add(sheet_record)
        
        # Import rows as documents
        for i, row in enumerate(rows):
            # Create searchable content
            content = "\n".join(f"{key}: {value}" for key, value in row.items())
            
            record = FrameRecord.create(
                title=f"Row {i+1}: {row.get(reader.fieldnames[0], 'Untitled')}",
                content=content,
                collection=f"gdrive-sheet-{file_id[:8]}",
                source_type="google_drive",
                tags=["spreadsheet-row"],
                custom_metadata={
                    "gdrive_file_id": file_id,
                    "gdrive_sheet_id": sheet.id,
                    "row_number": i + 1,
                    "row_data": row
                }
            )
            
            # Link to sheet header
            record.add_relationship(
                sheet_record.uuid,
                "child",
                title=f"Row in {sheet.name}"
            )
            
            dataset.add(record)
```

### OCR for Images

```python
def import_images_with_ocr(connector, dataset, folder_id):
    """Import images with text extraction."""
    
    # Get image files
    images = connector.sync_documents(
        folder_id=folder_id,
        mime_types=['image/jpeg', 'image/png', 'image/gif']
    )
    
    for image in images:
        # Use Google Drive's OCR capability
        try:
            # Create a Google Doc from the image (triggers OCR)
            doc_file = connector.create_document_from_image(image.id)
            
            # Get OCR text
            text_content = connector.export_file(
                doc_file.id,
                mime_type='text/plain'
            )
            
            # Create record with OCR content
            record = FrameRecord.create(
                title=image.name,
                content=text_content,
                source_type="google_drive",
                source_url=image.webViewLink,
                tags=["image", "ocr"],
                custom_metadata={
                    "gdrive_file_id": image.id,
                    "gdrive_mime_type": image.mimeType,
                    "image_size": image.size,
                    "ocr_extracted": True,
                    "original_image_url": image.webContentLink
                }
            )
            
            dataset.add(record)
            
            # Clean up temporary doc
            connector.delete_file(doc_file.id)
            
        except Exception as e:
            print(f"OCR failed for {image.name}: {e}")
```

### Folder Structure Preservation

```python
def import_with_hierarchy(connector, dataset, root_folder_id):
    """Import files preserving folder structure."""
    
    def process_folder(folder_id, path=[]):
        """Recursively process folder."""
        # Get folder metadata
        if folder_id:
            folder = connector.get_file(folder_id)
            current_path = path + [folder.name]
        else:
            current_path = []
        
        # List folder contents
        items = connector.list_files(
            folder_id=folder_id,
            include_folders=True
        )
        
        subfolders = []
        files = []
        
        for item in items:
            if item.mimeType == 'application/vnd.google-apps.folder':
                subfolders.append(item)
            else:
                files.append(item)
        
        # Process files in current folder
        for file in files:
            record = connector.map_to_frame_record(file)
            
            # Add hierarchy metadata
            record.metadata['custom_metadata']['folder_path'] = '/'.join(current_path)
            record.metadata['custom_metadata']['folder_depth'] = len(current_path)
            record.metadata['collection'] = f"gdrive-{'-'.join(current_path[:2])}" if current_path else "gdrive-root"
            
            # Add path-based tags
            record.metadata['tags'].extend([
                f"folder:{folder}" for folder in current_path
            ])
            
            dataset.add(record)
        
        # Recursively process subfolders
        for subfolder in subfolders:
            process_folder(subfolder.id, current_path)
    
    # Start processing from root
    process_folder(root_folder_id)
```

## Data Mapping

### Default File Mapping

```python
def map_to_frame_record(self, gdrive_file):
    """Map Google Drive file to FrameRecord."""
    
    # Get content based on mime type
    content = self.get_file_content(gdrive_file)
    
    # Extract metadata
    metadata = {
        "gdrive_file_id": gdrive_file.id,
        "gdrive_mime_type": gdrive_file.mimeType,
        "gdrive_size": gdrive_file.size,
        "gdrive_version": gdrive_file.version,
        "gdrive_web_view_link": gdrive_file.webViewLink,
        "gdrive_created_time": gdrive_file.createdTime.isoformat(),
        "gdrive_modified_time": gdrive_file.modifiedTime.isoformat(),
        "gdrive_shared": gdrive_file.shared,
        "gdrive_starred": gdrive_file.starred,
        "gdrive_trashed": gdrive_file.trashed
    }
    
    # Add owner/creator info
    if hasattr(gdrive_file, 'owners'):
        metadata['gdrive_owners'] = [
            owner.emailAddress for owner in gdrive_file.owners
        ]
    
    # Add parent folders
    if hasattr(gdrive_file, 'parents'):
        metadata['gdrive_parents'] = gdrive_file.parents
    
    # Create record
    return FrameRecord.create(
        title=gdrive_file.name,
        content=content,
        author=gdrive_file.owners[0].displayName if gdrive_file.owners else "Unknown",
        source_url=gdrive_file.webViewLink,
        source_type="google_drive",
        created_at=gdrive_file.createdTime.isoformat(),
        updated_at=gdrive_file.modifiedTime.isoformat(),
        tags=self.generate_tags(gdrive_file),
        custom_metadata=metadata
    )

def generate_tags(self, gdrive_file):
    """Generate tags from file metadata."""
    tags = ["google-drive"]
    
    # Add type-based tags
    mime_type_tags = {
        'application/vnd.google-apps.document': 'gdoc',
        'application/vnd.google-apps.spreadsheet': 'gsheet',
        'application/vnd.google-apps.presentation': 'gslides',
        'application/pdf': 'pdf',
        'image/': 'image',
        'video/': 'video'
    }
    
    for mime_prefix, tag in mime_type_tags.items():
        if gdrive_file.mimeType.startswith(mime_prefix):
            tags.append(tag)
            break
    
    # Add sharing tags
    if gdrive_file.shared:
        tags.append('shared')
    if gdrive_file.starred:
        tags.append('starred')
    
    return tags
```

### Custom Content Extraction

```python
class EnhancedGDriveConnector(GoogleDriveConnector):
    """Enhanced connector with custom content extraction."""
    
    def get_file_content(self, gdrive_file):
        """Extract content based on file type."""
        
        mime_type = gdrive_file.mimeType
        
        if mime_type == 'application/vnd.google-apps.document':
            # Export as markdown
            return self.export_as_markdown(gdrive_file.id)
        
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            # Export as structured text
            return self.export_spreadsheet_as_text(gdrive_file.id)
        
        elif mime_type == 'application/vnd.google-apps.presentation':
            # Export slides as text
            return self.export_slides_as_text(gdrive_file.id)
        
        elif mime_type.startswith('image/'):
            # Try OCR
            return self.extract_text_from_image(gdrive_file.id)
        
        elif mime_type == 'application/pdf':
            # Extract PDF text
            return self.extract_pdf_text(gdrive_file.id)
        
        else:
            # Default text export
            try:
                return self.export_file(gdrive_file.id, 'text/plain')
            except:
                return f"File: {gdrive_file.name} (Binary content)"
    
    def export_spreadsheet_as_text(self, file_id):
        """Convert spreadsheet to searchable text."""
        # Get all sheets
        sheets_data = []
        spreadsheet = self.get_spreadsheet(file_id)
        
        for sheet in spreadsheet.sheets:
            # Get sheet data
            values = self.get_sheet_values(file_id, sheet.name)
            
            if values:
                # Format as markdown table
                sheet_text = f"## {sheet.name}\n\n"
                
                # Headers
                headers = values[0] if values else []
                sheet_text += "| " + " | ".join(headers) + " |\n"
                sheet_text += "|" + "|".join(["---"] * len(headers)) + "|\n"
                
                # Rows
                for row in values[1:]:
                    # Pad row to match headers
                    padded_row = row + [''] * (len(headers) - len(row))
                    sheet_text += "| " + " | ".join(str(v) for v in padded_row) + " |\n"
                
                sheets_data.append(sheet_text)
        
        return "\n\n".join(sheets_data)
```

## Sync Strategies

### Incremental Sync

```python
def incremental_sync_drive(connector, dataset, last_sync_time=None):
    """Sync only changed files since last sync."""
    
    # Build query
    query_parts = []
    
    if last_sync_time:
        # Only files modified after last sync
        query_parts.append(f"modifiedTime > '{last_sync_time.isoformat()}'")
    
    # Exclude trashed files
    query_parts.append("trashed = false")
    
    query = " and ".join(query_parts) if query_parts else None
    
    # Get changed files
    changed_files = connector.search_files(query)
    
    # Track updates
    new_count = 0
    updated_count = 0
    
    for file in changed_files:
        # Check if file exists in dataset
        existing = dataset.scanner(
            filter=f"custom_metadata.gdrive_file_id = '{file.id}'"
        ).to_table().to_pylist()
        
        record = connector.map_to_frame_record(file)
        
        if existing:
            # Update existing record
            dataset.update_record(existing[0]['uuid'], record)
            updated_count += 1
        else:
            # Add new record
            dataset.add(record)
            new_count += 1
    
    print(f"Sync complete: {new_count} new, {updated_count} updated")
    return new_count, updated_count
```

### Watch for Changes

```python
import time
from datetime import datetime, timezone

class DriveWatcher:
    """Watch Google Drive for changes."""
    
    def __init__(self, connector, dataset):
        self.connector = connector
        self.dataset = dataset
        self.page_token = None
    
    def start_watching(self):
        """Initialize change tracking."""
        # Get starting page token
        response = self.connector.service.changes().getStartPageToken().execute()
        self.page_token = response.get('startPageToken')
        print(f"Watching for changes from token: {self.page_token}")
    
    def check_changes(self):
        """Check for and process changes."""
        if not self.page_token:
            self.start_watching()
            return
        
        changes = []
        page_token = self.page_token
        
        while page_token:
            response = self.connector.service.changes().list(
                pageToken=page_token,
                spaces='drive',
                fields='nextPageToken, newStartPageToken, changes'
            ).execute()
            
            changes.extend(response.get('changes', []))
            page_token = response.get('nextPageToken')
            
            if 'newStartPageToken' in response:
                self.page_token = response['newStartPageToken']
        
        # Process changes
        for change in changes:
            self.process_change(change)
        
        return len(changes)
    
    def process_change(self, change):
        """Process a single change."""
        file_id = change['fileId']
        
        if change.get('removed'):
            # File was deleted
            self.handle_deletion(file_id)
        else:
            # File was added or modified
            file = change.get('file')
            if file:
                self.handle_file_change(file)
    
    def handle_file_change(self, file):
        """Handle file addition or modification."""
        # Skip folders and trashed files
        if (file['mimeType'] == 'application/vnd.google-apps.folder' or
            file.get('trashed', False)):
            return
        
        # Map to FrameRecord
        record = self.connector.map_to_frame_record(file)
        
        # Check if exists
        existing = self.dataset.scanner(
            filter=f"custom_metadata.gdrive_file_id = '{file['id']}'"
        ).to_table().to_pylist()
        
        if existing:
            self.dataset.update_record(existing[0]['uuid'], record)
            print(f"Updated: {file['name']}")
        else:
            self.dataset.add(record)
            print(f"Added: {file['name']}")
    
    def handle_deletion(self, file_id):
        """Handle file deletion."""
        # Find and remove from dataset
        existing = self.dataset.scanner(
            filter=f"custom_metadata.gdrive_file_id = '{file_id}'"
        ).to_table().to_pylist()
        
        if existing:
            self.dataset.delete_record(existing[0]['uuid'])
            print(f"Deleted: {existing[0]['title']}")
    
    def watch_continuous(self, interval=60):
        """Continuously watch for changes."""
        while True:
            try:
                changes = self.check_changes()
                if changes:
                    print(f"Processed {changes} changes")
                else:
                    print("No changes detected")
            except Exception as e:
                print(f"Error checking changes: {e}")
            
            time.sleep(interval)
```

## Search and Query

### Drive-Specific Search

```python
def search_drive_content(connector, query, file_types=None):
    """Search Google Drive with advanced queries."""
    
    # Build search query
    query_parts = [f"fullText contains '{query}'"]
    
    if file_types:
        mime_types = []
        for file_type in file_types:
            if file_type == 'docs':
                mime_types.append("mimeType = 'application/vnd.google-apps.document'")
            elif file_type == 'sheets':
                mime_types.append("mimeType = 'application/vnd.google-apps.spreadsheet'")
            elif file_type == 'slides':
                mime_types.append("mimeType = 'application/vnd.google-apps.presentation'")
            elif file_type == 'pdf':
                mime_types.append("mimeType = 'application/pdf'")
        
        if mime_types:
            query_parts.append(f"({' or '.join(mime_types)})")
    
    # Exclude trash
    query_parts.append("trashed = false")
    
    drive_query = " and ".join(query_parts)
    
    # Search files
    results = connector.search_files(drive_query)
    
    return results

def search_by_metadata(dataset, owner=None, shared=None, starred=None):
    """Search imported files by Drive metadata."""
    
    conditions = []
    
    if owner:
        conditions.append(f"custom_metadata.gdrive_owners.contains('{owner}')")
    
    if shared is not None:
        conditions.append(f"custom_metadata.gdrive_shared = {str(shared).lower()}")
    
    if starred is not None:
        conditions.append(f"custom_metadata.gdrive_starred = {str(starred).lower()}")
    
    filter_str = " AND ".join(conditions) if conditions else None
    
    return dataset.scanner(filter=filter_str).to_table()
```

### Cross-Reference Search

```python
def find_related_drive_files(dataset, file_id):
    """Find files related to a specific Drive file."""
    
    # Get the source file
    source_files = dataset.scanner(
        filter=f"custom_metadata.gdrive_file_id = '{file_id}'"
    ).to_table().to_pylist()
    
    if not source_files:
        return []
    
    source_file = source_files[0]
    related = []
    
    # Find files in same folder
    if source_file['custom_metadata'].get('gdrive_parents'):
        parent_id = source_file['custom_metadata']['gdrive_parents'][0]
        same_folder = dataset.scanner(
            filter=f"custom_metadata.gdrive_parents.contains('{parent_id}')"
        ).to_table().to_pylist()
        
        related.extend([
            {'file': f, 'relationship': 'same_folder'}
            for f in same_folder
            if f['uuid'] != source_file['uuid']
        ])
    
    # Find files by same owner
    if source_file['custom_metadata'].get('gdrive_owners'):
        owner = source_file['custom_metadata']['gdrive_owners'][0]
        same_owner = dataset.scanner(
            filter=f"custom_metadata.gdrive_owners.contains('{owner}')"
        ).to_table().to_pylist()
        
        related.extend([
            {'file': f, 'relationship': 'same_owner'}
            for f in same_owner[:5]  # Limit to 5
            if f['uuid'] != source_file['uuid']
        ])
    
    return related
```

## Performance Optimization

### Batch Operations

```python
def batch_import_drive(connector, dataset, folder_ids, batch_size=50):
    """Import multiple folders with batching."""
    
    all_files = []
    
    # Collect files from all folders
    for folder_id in folder_ids:
        print(f"Scanning folder: {folder_id}")
        files = connector.list_files(folder_id=folder_id, recursive=True)
        all_files.extend(files)
    
    print(f"Found {len(all_files)} total files")
    
    # Process in batches
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i + batch_size]
        records = []
        
        for file in batch:
            try:
                # Skip folders
                if file.mimeType == 'application/vnd.google-apps.folder':
                    continue
                
                record = connector.map_to_frame_record(file)
                records.append(record)
            except Exception as e:
                print(f"Error processing {file.name}: {e}")
        
        # Batch insert
        if records:
            dataset.add_many(records)
            print(f"Imported batch: {len(records)} files")
    
    return len(all_files)
```

### Parallel Downloads

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_download_content(connector, file_ids, max_workers=5):
    """Download file contents in parallel."""
    
    contents = {}
    
    def download_file(file_id):
        try:
            file = connector.get_file(file_id)
            content = connector.get_file_content(file)
            return file_id, content
        except Exception as e:
            print(f"Error downloading {file_id}: {e}")
            return file_id, None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {
            executor.submit(download_file, file_id): file_id
            for file_id in file_ids
        }
        
        for future in as_completed(future_to_id):
            file_id, content = future.result()
            if content:
                contents[file_id] = content
    
    return contents
```

### Caching

```python
import pickle
import hashlib
from pathlib import Path

class CachedDriveConnector(GoogleDriveConnector):
    """Drive connector with local caching."""
    
    def __init__(self, cache_dir=".gdrive_cache", **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, file_id, operation):
        """Get cache file path."""
        key = f"{file_id}_{operation}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.pkl"
    
    def get_file_content(self, file):
        """Get content with caching."""
        cache_path = self._get_cache_path(file.id, 'content')
        
        # Check cache (with modification time check)
        if cache_path.exists():
            cached_data = pickle.load(open(cache_path, 'rb'))
            if cached_data['modified_time'] == file.modifiedTime:
                return cached_data['content']
        
        # Fetch content
        content = super().get_file_content(file)
        
        # Cache result
        cache_data = {
            'content': content,
            'modified_time': file.modifiedTime
        }
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        
        return content
```

## Integration Patterns

### Drive + GitHub Integration

```python
def sync_docs_to_github(drive_connector, github_connector, folder_id, repo_path):
    """Sync Google Docs to GitHub repository."""
    
    # Get documents from Drive
    documents = drive_connector.sync_documents(
        folder_id=folder_id,
        mime_types=['application/vnd.google-apps.document']
    )
    
    for doc in documents:
        # Convert to markdown
        markdown_content = drive_connector.export_as_markdown(doc.id)
        
        # Create file path
        safe_name = doc.name.replace(' ', '-').lower()
        file_path = f"{repo_path}/{safe_name}.md"
        
        # Check if file exists in GitHub
        try:
            existing_file = github_connector.get_file(file_path)
            
            # Update if content changed
            if existing_file.decoded_content != markdown_content:
                github_connector.update_file(
                    file_path,
                    markdown_content,
                    f"Update {doc.name} from Google Docs"
                )
                print(f"Updated: {file_path}")
        except:
            # Create new file
            github_connector.create_file(
                file_path,
                markdown_content,
                f"Add {doc.name} from Google Docs"
            )
            print(f"Created: {file_path}")
```

### Team Folder Organization

```python
def organize_team_content(connector, dataset, team_folders):
    """Organize content by team structure."""
    
    for team_name, folder_id in team_folders.items():
        print(f"Processing {team_name} folder...")
        
        # Create collection header
        team_record = FrameRecord.create(
            title=f"{team_name} Team Documents",
            content=f"Document collection for {team_name} team",
            record_type="collection_header",
            collection=f"team-{team_name.lower().replace(' ', '-')}",
            tags=["team-docs", team_name.lower()],
            custom_metadata={
                "team_name": team_name,
                "gdrive_folder_id": folder_id
            }
        )
        dataset.add(team_record)
        
        # Import team documents
        documents = connector.sync_documents(
            folder_id=folder_id,
            recursive=True
        )
        
        for doc in documents:
            record = connector.map_to_frame_record(doc)
            
            # Add team context
            record.metadata['collection'] = f"team-{team_name.lower().replace(' ', '-')}"
            record.metadata['tags'].append(f"team:{team_name.lower()}")
            record.metadata['custom_metadata']['team'] = team_name
            
            # Link to team header
            record.add_relationship(
                team_record.uuid,
                "member_of",
                title=f"Part of {team_name} documents"
            )
            
            dataset.add(record)
```

## Error Handling

### Quota Management

```python
import time
from google.api_core import retry

class QuotaAwareDriveConnector(GoogleDriveConnector):
    """Drive connector with quota management."""
    
    def __init__(self, requests_per_minute=60, **kwargs):
        super().__init__(**kwargs)
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def _check_quota(self):
        """Check and enforce quota limits."""
        now = time.time()
        # Remove old requests
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                print(f"Quota limit reached. Waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
    
    @retry.Retry(predicate=retry.if_exception_type(Exception))
    def list_files(self, **kwargs):
        """List files with quota management and retry."""
        self._check_quota()
        self.request_times.append(time.time())
        
        try:
            return super().list_files(**kwargs)
        except Exception as e:
            if "quotaExceeded" in str(e):
                print("Quota exceeded. Waiting 60 seconds...")
                time.sleep(60)
                raise
            raise
```

### Permission Handling

```python
def handle_permission_errors(connector, file_id):
    """Handle file permission issues."""
    
    try:
        file = connector.get_file(file_id)
        content = connector.get_file_content(file)
        return content
    
    except Exception as e:
        error_str = str(e)
        
        if "403" in error_str or "forbidden" in error_str:
            print(f"Permission denied for file {file_id}")
            
            # Try to get basic metadata instead
            try:
                file = connector.get_file(file_id, fields="id,name,mimeType,webViewLink")
                return f"[Permission Denied]\nFile: {file.name}\nType: {file.mimeType}\nView: {file.webViewLink}"
            except:
                return "[Permission Denied - No access to file]"
        
        elif "404" in error_str:
            return "[File not found or deleted]"
        
        else:
            raise
```

## Best Practices

### 1. Authentication Security

```python
# Use environment variables
import os

connector = GoogleDriveConnector(
    service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
)

# Or use Google Cloud Secret Manager
from google.cloud import secretmanager

def get_service_account_key():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/PROJECT_ID/secrets/drive-service-account/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### 2. Efficient Querying

```python
# Good - use field masks
files = connector.list_files(
    fields="files(id,name,mimeType,modifiedTime,size)",
    pageSize=100  # Get more results per request
)

# Good - use search queries
recent_docs = connector.search_files(
    "mimeType='application/vnd.google-apps.document' and modifiedTime > '2024-01-01T00:00:00'"
)

# Bad - getting all files then filtering
all_files = connector.list_files()  # Gets everything
docs = [f for f in all_files if f.mimeType == 'application/vnd.google-apps.document']
```

### 3. Content Type Handling

```python
def get_optimal_export_format(mime_type):
    """Get best export format for content extraction."""
    
    export_formats = {
        'application/vnd.google-apps.document': 'text/markdown',
        'application/vnd.google-apps.spreadsheet': 'text/csv',
        'application/vnd.google-apps.presentation': 'text/plain',
        'application/vnd.google-apps.drawing': 'image/svg+xml',
        'application/pdf': 'text/plain'  # If OCR available
    }
    
    return export_formats.get(mime_type, 'text/plain')
```

## Troubleshooting

### Authentication Issues

```python
# Test authentication
try:
    connector.authenticate()
    about = connector.service.about().get(fields="user").execute()
    user = about.get('user', {})
    print(f"Authenticated as: {user.get('displayName')} ({user.get('emailAddress')})")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Check:")
    print("1. API is enabled in Google Cloud Console")
    print("2. Credentials are valid")
    print("3. Required scopes are authorized")
```

### API Errors

```python
def diagnose_api_error(error):
    """Diagnose common API errors."""
    
    error_str = str(error)
    
    if "HttpError 403" in error_str:
        if "quotaExceeded" in error_str:
            return "API quota exceeded. Wait or increase quota in Google Cloud Console."
        elif "forbidden" in error_str:
            return "Permission denied. Check file permissions and sharing settings."
        elif "rateLimitExceeded" in error_str:
            return "Rate limit hit. Implement exponential backoff."
    
    elif "HttpError 404" in error_str:
        return "File not found. It may have been deleted or you lack access."
    
    elif "HttpError 401" in error_str:
        return "Authentication failed. Token may be expired or invalid."
    
    return f"Unknown error: {error_str}"
```

## Next Steps

- Explore other connectors:
  - [Notion Connector](notion.md) for knowledge bases
  - [Slack Connector](slack.md) for conversations
  - [Linear Connector](linear.md) for project management
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/gdrive-sync.md)
- Check the [API Reference](../api/connectors.md#googledrive)