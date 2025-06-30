# Connectors API Reference

ContextFrame connectors enable integration with external systems and data sources. This reference covers the base connector interface and built-in connector implementations.

## Base Connector Interface

### SourceConnector Protocol

::: contextframe.connectors.base.SourceConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      show_if_no_docstring: false

### ConnectorConfig

::: contextframe.connectors.base.ConnectorConfig
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

### SyncResult

::: contextframe.connectors.base.SyncResult
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

### AuthType

::: contextframe.connectors.base.AuthType
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list

## Built-in Connectors

### GitHub Connector

::: contextframe.connectors.github.GitHubConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false
      filters:
        - "!^_"

#### Usage Example

```python
from contextframe import FrameDataset
from contextframe.connectors import GitHubConnector

# Initialize connector
connector = GitHubConnector(token="github_pat_...")

# Create dataset
dataset = FrameDataset.create("github_kb.lance")

# Sync issues
issues = connector.sync_issues(
    owner="myorg",
    repo="myrepo",
    state="all",
    since="2024-01-01T00:00:00Z"
)

# Convert and add to dataset
for issue in issues:
    record = connector.map_to_frame_record(issue)
    dataset.add(record)

# Sync pull requests
prs = connector.sync_pull_requests(
    owner="myorg",
    repo="myrepo",
    include_comments=True,
    include_reviews=True
)

for pr in prs:
    record = connector.map_to_frame_record(pr)
    dataset.add(record)
```

### Linear Connector

::: contextframe.connectors.linear.LinearConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false
      filters:
        - "!^_"

#### Usage Example

```python
from contextframe.connectors import LinearConnector

# Initialize connector
connector = LinearConnector(api_key="lin_api_...")

# Sync issues with filters
issues = connector.sync_issues(
    team_id="team_123",
    state_ids=["state_todo", "state_in_progress"],
    include_comments=True,
    modified_since="2024-01-01T00:00:00Z"
)

# Sync projects
projects = connector.sync_projects(
    include_archived=False
)

# Map to records
for issue in issues:
    record = connector.map_to_frame_record(issue)
    # Process record
```

### Google Drive Connector

::: contextframe.connectors.googledrive.GoogleDriveConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false
      filters:
        - "!^_"

#### Usage Example

```python
from contextframe.connectors import GoogleDriveConnector

# OAuth 2.0 authentication
connector = GoogleDriveConnector(
    client_id="your-client-id.apps.googleusercontent.com",
    client_secret="your-secret",
    refresh_token="your-refresh-token"
)

# Or service account
connector = GoogleDriveConnector(
    service_account_file="/path/to/service-account.json"
)

# Sync documents from folder
documents = connector.sync_documents(
    folder_id="folder_123",
    recursive=True,
    mime_types=[
        "application/vnd.google-apps.document",
        "application/vnd.google-apps.spreadsheet"
    ]
)

# Search documents
results = connector.search_documents(
    query="project proposal",
    spaces=["drive"],
    max_results=50
)
```

### Notion Connector

::: contextframe.connectors.notion.NotionConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false
      filters:
        - "!^_"

#### Usage Example

```python
from contextframe.connectors import NotionConnector

# Initialize with API key
connector = NotionConnector(api_key="secret_...")

# Sync all accessible pages
pages = connector.sync_pages()

# Sync specific database
database_id = "database_123"
entries = connector.sync_database(
    database_id=database_id,
    filter={
        "property": "Status",
        "select": {"equals": "Published"}
    }
)

# Query with pagination
results = connector.query_database(
    database_id=database_id,
    page_size=100
)
```

### Slack Connector

::: contextframe.connectors.slack.SlackConnector
    options:
      show_source: false
      show_bases: true
      show_signature_annotations: true
      members_order: source
      heading_level: 3
      docstring_section_style: list
      inherited_members: false
      filters:
        - "!^_"

#### Usage Example

```python
from contextframe.connectors import SlackConnector

# Initialize with bot token
connector = SlackConnector(
    token="xoxb-...",
    user_token="xoxp-..."  # Optional, for user-specific actions
)

# List channels
channels = connector.list_channels(
    types=["public_channel", "private_channel"]
)

# Sync channel messages
messages = connector.sync_channel_messages(
    channel_id="C1234567890",
    oldest="2024-01-01T00:00:00Z",
    include_threads=True
)

# Search messages
results = connector.search_messages(
    query="deployment",
    count=100
)
```

## Common Patterns

### Authentication

```python
# API Key
connector = SomeConnector(api_key="key_...")

# OAuth Token
connector = SomeConnector(token="token_...")

# OAuth with refresh
connector = SomeConnector(
    client_id="...",
    client_secret="...",
    refresh_token="..."
)

# Service Account
connector = SomeConnector(
    service_account_file="path/to/credentials.json"
)

# Environment variables
import os
connector = SomeConnector(
    api_key=os.getenv("CONNECTOR_API_KEY")
)
```

### Error Handling

```python
from contextframe.connectors import ConnectorError, AuthenticationError

try:
    connector.authenticate()
    results = connector.sync_documents()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ConnectorError as e:
    print(f"Connector error: {e}")
```

### Batch Processing

```python
# Process in batches to avoid memory issues
batch_size = 100
offset = 0

while True:
    batch = connector.sync_documents(
        limit=batch_size,
        offset=offset
    )
    
    if not batch:
        break
        
    for item in batch:
        record = connector.map_to_frame_record(item)
        dataset.add(record)
    
    offset += batch_size
    print(f"Processed {offset} items...")
```

### Incremental Sync

```python
from datetime import datetime, timedelta

# Track last sync time
last_sync = datetime.now() - timedelta(days=7)

# Sync only new/modified items
items = connector.sync_documents(
    modified_since=last_sync.isoformat()
)

# Update last sync time
last_sync = datetime.now()
```

### Custom Mapping

```python
def custom_mapper(item, connector):
    """Custom mapping logic."""
    # Get base mapping
    record = connector.map_to_frame_record(item)
    
    # Enhance metadata
    record.metadata.update({
        "custom_field": extract_custom_field(item),
        "processed_at": datetime.now().isoformat()
    })
    
    # Add relationships
    if item.get("parent_id"):
        record.metadata["relationships"] = [{
            "relationship_type": "parent",
            "target_id": item["parent_id"]
        }]
    
    return record

# Use custom mapper
for item in items:
    record = custom_mapper(item, connector)
    dataset.add(record)
```

## Building Custom Connectors

To create a custom connector, implement the `SourceConnector` protocol:

```python
from contextframe.connectors.base import SourceConnector
from contextframe import FrameRecord
from typing import Dict, List, Any, Optional

class MyConnector:
    """Custom connector implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Verify API credentials."""
        # Implementation
        self.authenticated = True
        return True
    
    def sync_documents(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch documents from source."""
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        
        # Implementation
        return []
    
    def map_to_frame_record(self, item: Dict[str, Any]) -> FrameRecord:
        """Convert source item to FrameRecord."""
        return FrameRecord(
            text_content=item.get("content", ""),
            metadata={
                "source": "my_system",
                "id": item.get("id"),
                "title": item.get("title"),
                **item.get("metadata", {})
            }
        )
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search documents in source."""
        # Optional implementation
        pass
    
    @property
    def connector_type(self) -> str:
        """Return connector type identifier."""
        return "my_connector"
    
    @property
    def supports_incremental_sync(self) -> bool:
        """Whether connector supports incremental sync."""
        return True
```

## Testing Connectors

```python
import pytest
from unittest.mock import Mock, patch

def test_connector_authentication():
    connector = MyConnector(api_key="test_key")
    
    with patch.object(connector, "_verify_credentials") as mock:
        mock.return_value = True
        assert connector.authenticate() is True
        assert connector.authenticated is True

def test_sync_documents():
    connector = MyConnector(api_key="test_key")
    connector.authenticated = True
    
    # Mock API response
    mock_response = [
        {"id": 1, "content": "Doc 1"},
        {"id": 2, "content": "Doc 2"}
    ]
    
    with patch.object(connector, "_fetch_data") as mock:
        mock.return_value = mock_response
        docs = connector.sync_documents()
        
    assert len(docs) == 2
    assert docs[0]["id"] == 1

def test_mapping():
    connector = MyConnector(api_key="test_key")
    
    item = {
        "id": "123",
        "title": "Test Doc",
        "content": "Test content",
        "metadata": {"tag": "test"}
    }
    
    record = connector.map_to_frame_record(item)
    
    assert record.text_content == "Test content"
    assert record.metadata["id"] == "123"
    assert record.metadata["title"] == "Test Doc"
    assert record.metadata["tag"] == "test"
```

## Performance Tips

1. **Use batch operations** when available
2. **Implement pagination** for large result sets
3. **Cache authentication tokens** to avoid repeated auth calls
4. **Use connection pooling** for HTTP requests
5. **Implement retry logic** with exponential backoff
6. **Process results in streams** to avoid memory issues
7. **Use async operations** when supported

## See Also

- [Custom Connectors Guide](../integration/custom.md) - Building custom connectors
- [Integration Overview](../integration/overview.md) - Connector concepts
- [Module Guides](../modules/frame-dataset.md) - Using connectors with datasets
- [Cookbook Examples](../cookbook/multi-source-search.md) - Real-world examples