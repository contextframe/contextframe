# Integration Overview

ContextFrame provides a powerful connector system for importing documents from various external sources. This guide covers the connector architecture, available connectors, and common integration patterns.

## What are Connectors?

Connectors are plugins that enable ContextFrame to import documents from external systems like GitHub, Notion, Slack, and more. Each connector:

- Handles authentication with the external service
- Maps external data formats to FrameRecords
- Manages incremental synchronization
- Preserves source metadata and relationships

## Available Connectors

ContextFrame includes the following built-in connectors:

| Connector | Source Type | Authentication | Use Case |
|-----------|------------|----------------|----------|
| **GitHub** | Code repositories | Token/OAuth | Import code, docs, issues |
| **Linear** | Project management | API Key | Import issues, projects, docs |
| **Google Drive** | Cloud storage | OAuth | Import documents, spreadsheets |
| **Notion** | Knowledge base | API Key | Import pages, databases |
| **Slack** | Communication | OAuth | Import messages, threads |
| **Discord** | Communication | Bot Token | Import messages, channels |
| **Obsidian** | Local knowledge | File system | Import markdown notes |
| **Custom** | Any source | Configurable | Build your own |

## Architecture

### Connector Base Class

All connectors inherit from the `BaseConnector` class:

```python
from contextframe.connectors import BaseConnector
from contextframe import FrameRecord

class BaseConnector:
    """Base class for all connectors."""
    
    def __init__(self, **config):
        self.config = config
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with the external service."""
        raise NotImplementedError
    
    def sync_documents(self, **options):
        """Sync documents from the external source."""
        raise NotImplementedError
    
    def map_to_frame_record(self, external_doc):
        """Map external document to FrameRecord."""
        raise NotImplementedError
```

### Common Patterns

1. **Authentication Flow**
```python
connector = GitHubConnector(token="your-token")
connector.authenticate()
if connector.authenticated:
    documents = connector.sync_documents()
```

2. **Incremental Sync**
```python
# First sync
documents = connector.sync_documents()

# Later - only get updates
documents = connector.sync_documents(
    since="2024-01-01T00:00:00Z",
    modified_only=True
)
```

3. **Filtering**
```python
# Sync specific content
documents = connector.sync_documents(
    filter_type="issues",
    labels=["bug", "feature"],
    state="open"
)
```

## Authentication

### API Key Authentication

Used by: Linear, Notion

```python
from contextframe.connectors import LinearConnector

connector = LinearConnector(
    api_key="lin_api_xxx",
    team_id="your-team-id"
)
```

### OAuth Authentication

Used by: GitHub, Google Drive, Slack

```python
from contextframe.connectors import GoogleDriveConnector

connector = GoogleDriveConnector(
    client_id="your-client-id",
    client_secret="your-client-secret",
    refresh_token="your-refresh-token"
)

# Or use service account
connector = GoogleDriveConnector(
    service_account_file="/path/to/credentials.json"
)
```

### Token Authentication

Used by: GitHub, Discord

```python
from contextframe.connectors import GitHubConnector

connector = GitHubConnector(
    token="ghp_xxx",
    owner="octocat",
    repo="hello-world"
)
```

### Environment Variables

Best practice is to use environment variables:

```python
import os

connector = GitHubConnector(
    token=os.getenv("GITHUB_TOKEN"),
    owner=os.getenv("GITHUB_OWNER"),
    repo=os.getenv("GITHUB_REPO")
)
```

## Data Mapping

### Standard Mapping

Each connector maps external data to FrameRecord fields:

```python
def map_to_frame_record(self, github_file):
    """Map GitHub file to FrameRecord."""
    return FrameRecord.create(
        title=github_file.name,
        content=github_file.decoded_content,
        source_url=github_file.html_url,
        source_type="github",
        author=github_file.last_committer,
        custom_metadata={
            "github_path": github_file.path,
            "github_sha": github_file.sha,
            "github_size": github_file.size,
            "github_type": github_file.type
        }
    )
```

### Preserving Metadata

Connectors preserve source metadata in `custom_metadata`:

```python
# Linear issue → FrameRecord
{
    "title": issue.title,
    "content": issue.description,
    "custom_metadata": {
        "linear_id": issue.id,
        "linear_number": issue.number,
        "linear_state": issue.state.name,
        "linear_priority": issue.priority,
        "linear_assignee": issue.assignee.name,
        "linear_labels": [label.name for label in issue.labels],
        "linear_project": issue.project.name if issue.project else None
    }
}
```

### Handling Relationships

Connectors can preserve relationships between documents:

```python
# Notion page hierarchy
parent_page = FrameRecord.create(
    title=notion_page.title,
    record_type="collection_header"
)

for child in notion_page.children:
    child_record = map_to_frame_record(child)
    child_record.add_relationship(
        parent_page.uuid,
        "child",
        title=f"Child of {parent_page.title}"
    )
```

## Sync Strategies

### Full Sync

Import all documents from the source:

```python
def full_sync(connector, dataset):
    """Perform full synchronization."""
    documents = connector.sync_documents()
    
    records = []
    for doc in documents:
        record = connector.map_to_frame_record(doc)
        records.append(record)
    
    dataset.add_many(records)
    return len(records)
```

### Incremental Sync

Only sync new or modified documents:

```python
def incremental_sync(connector, dataset, last_sync_time):
    """Sync only changes since last sync."""
    # Get existing document IDs
    existing_ids = set()
    for batch in dataset.to_batches(columns=['custom_metadata']):
        for row in batch.to_pylist():
            source_id = row['custom_metadata'].get('source_id')
            if source_id:
                existing_ids.add(source_id)
    
    # Sync new/modified documents
    documents = connector.sync_documents(
        since=last_sync_time,
        modified_only=True
    )
    
    new_records = []
    updated_records = []
    
    for doc in documents:
        source_id = doc.metadata.get('id')
        record = connector.map_to_frame_record(doc)
        
        if source_id in existing_ids:
            # Update existing
            updated_records.append((source_id, record))
        else:
            # Add new
            new_records.append(record)
    
    # Apply changes
    if new_records:
        dataset.add_many(new_records)
    
    for source_id, record in updated_records:
        # Find and update by source_id
        results = dataset.scanner(
            filter=f"custom_metadata.source_id = '{source_id}'"
        ).to_table().to_pylist()
        
        if results:
            dataset.update_record(results[0]['uuid'], record)
    
    return len(new_records), len(updated_records)
```

### Selective Sync

Sync only specific content:

```python
def selective_sync(connector, dataset, filters):
    """Sync with filters."""
    documents = connector.sync_documents(**filters)
    
    # Example filters:
    # - file_pattern="*.md" (GitHub)
    # - database_id="xxx" (Notion)
    # - folder_id="xxx" (Google Drive)
    # - channel_ids=["C123", "C456"] (Slack)
    
    records = [connector.map_to_frame_record(doc) for doc in documents]
    dataset.add_many(records)
    
    return len(records)
```

## Usage Examples

### Basic Import

```python
from contextframe import FrameDataset
from contextframe.connectors import GitHubConnector

# Setup
dataset = FrameDataset.create("my_knowledge_base.lance")
connector = GitHubConnector(
    token="ghp_xxx",
    owner="myorg",
    repo="documentation"
)

# Authenticate
connector.authenticate()

# Sync documents
documents = connector.sync_documents(
    path="docs",
    file_pattern="**/*.md"
)

# Import to dataset
records = []
for doc in documents:
    record = connector.map_to_frame_record(doc)
    records.append(record)

dataset.add_many(records)
print(f"Imported {len(records)} documents from GitHub")
```

### Multi-Source Import

```python
def import_from_multiple_sources(dataset):
    """Import from multiple connectors."""
    
    connectors = [
        {
            'name': 'GitHub Docs',
            'connector': GitHubConnector(
                token=os.getenv("GITHUB_TOKEN"),
                owner="myorg",
                repo="docs"
            ),
            'options': {
                'path': 'documentation',
                'file_pattern': '**/*.md'
            }
        },
        {
            'name': 'Linear Issues',
            'connector': LinearConnector(
                api_key=os.getenv("LINEAR_API_KEY")
            ),
            'options': {
                'team_id': 'TEAM123',
                'states': ['In Progress', 'Done']
            }
        },
        {
            'name': 'Notion KB',
            'connector': NotionConnector(
                api_key=os.getenv("NOTION_API_KEY")
            ),
            'options': {
                'database_id': 'db123'
            }
        }
    ]
    
    total_imported = 0
    
    for source in connectors:
        print(f"Importing from {source['name']}...")
        
        try:
            source['connector'].authenticate()
            documents = source['connector'].sync_documents(**source['options'])
            
            records = []
            for doc in documents:
                record = source['connector'].map_to_frame_record(doc)
                # Tag by source
                record.metadata['tags'] = record.metadata.get('tags', [])
                record.metadata['tags'].append(f"source:{source['name'].lower()}")
                records.append(record)
            
            dataset.add_many(records)
            print(f"  Imported {len(records)} documents")
            total_imported += len(records)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    return total_imported
```

### Scheduled Sync

```python
import schedule
import time
from datetime import datetime

class ConnectorSync:
    """Scheduled connector synchronization."""
    
    def __init__(self, dataset, connectors):
        self.dataset = dataset
        self.connectors = connectors
        self.last_sync = {}
    
    def sync_connector(self, name, connector, options):
        """Sync single connector."""
        print(f"[{datetime.now()}] Syncing {name}...")
        
        try:
            # Incremental sync if supported
            if hasattr(connector, 'sync_incremental'):
                last_sync = self.last_sync.get(name)
                documents = connector.sync_incremental(
                    since=last_sync,
                    **options
                )
            else:
                documents = connector.sync_documents(**options)
            
            # Import documents
            records = []
            for doc in documents:
                record = connector.map_to_frame_record(doc)
                record.metadata['sync_timestamp'] = datetime.now().isoformat()
                records.append(record)
            
            if records:
                self.dataset.add_many(records)
                print(f"  Added {len(records)} new documents")
            
            self.last_sync[name] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"  Error syncing {name}: {e}")
    
    def sync_all(self):
        """Sync all connectors."""
        for conn_config in self.connectors:
            self.sync_connector(
                conn_config['name'],
                conn_config['connector'],
                conn_config.get('options', {})
            )
    
    def run_scheduled(self):
        """Run scheduled sync."""
        # Schedule different sources at different intervals
        schedule.every(15).minutes.do(
            lambda: self.sync_connector(
                'Slack',
                self.connectors[0]['connector'],
                self.connectors[0].get('options', {})
            )
        )
        
        schedule.every(1).hour.do(
            lambda: self.sync_connector(
                'GitHub',
                self.connectors[1]['connector'],
                self.connectors[1].get('options', {})
            )
        )
        
        schedule.every(6).hours.do(self.sync_all)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
```

## Error Handling

### Retry Logic

```python
import time
from typing import Optional

def sync_with_retry(connector, max_retries=3, backoff_factor=2):
    """Sync with exponential backoff retry."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            if not connector.authenticated:
                connector.authenticate()
            
            documents = connector.sync_documents()
            return documents
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"Error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
    
    raise last_error
```

### Partial Success

```python
def sync_with_partial_success(connector, dataset):
    """Handle partial sync failures gracefully."""
    documents = connector.sync_documents()
    
    succeeded = []
    failed = []
    
    for doc in documents:
        try:
            record = connector.map_to_frame_record(doc)
            dataset.add(record)
            succeeded.append(doc.id)
        except Exception as e:
            failed.append({
                'document_id': doc.id,
                'error': str(e),
                'document': doc
            })
    
    # Log failures
    if failed:
        with open('sync_failures.json', 'w') as f:
            json.dump(failed, f, indent=2)
    
    print(f"Synced: {len(succeeded)} succeeded, {len(failed)} failed")
    return succeeded, failed
```

## Configuration

### Connector Configuration

```python
# config.yaml
connectors:
  github:
    enabled: true
    token: ${GITHUB_TOKEN}
    owner: myorg
    repos:
      - documentation
      - api-specs
      - examples
    sync_options:
      file_patterns:
        - "**/*.md"
        - "**/*.mdx"
      exclude_paths:
        - "**/node_modules/**"
        - "**/build/**"
  
  linear:
    enabled: true
    api_key: ${LINEAR_API_KEY}
    team_id: TEAM123
    sync_options:
      states:
        - "In Progress"
        - "Done"
      labels:
        - "documentation"
  
  notion:
    enabled: false
    api_key: ${NOTION_API_KEY}
    databases:
      - db_id: abc123
        name: "Product Wiki"
      - db_id: def456
        name: "Engineering Notes"

# Load configuration
import yaml

def load_connector_config(config_file):
    """Load connector configuration."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Expand environment variables
    import os
    import re
    
    def expand_env_vars(value):
        if isinstance(value, str):
            return re.sub(r'\${(\w+)}', lambda m: os.getenv(m.group(1), ''), value)
        elif isinstance(value, dict):
            return {k: expand_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [expand_env_vars(v) for v in value]
        return value
    
    return expand_env_vars(config)
```

### Dynamic Connector Loading

```python
def create_connector(connector_type, config):
    """Dynamically create connector instance."""
    connector_map = {
        'github': GitHubConnector,
        'linear': LinearConnector,
        'notion': NotionConnector,
        'gdrive': GoogleDriveConnector,
        'slack': SlackConnector,
        'discord': DiscordConnector,
        'obsidian': ObsidianConnector
    }
    
    connector_class = connector_map.get(connector_type)
    if not connector_class:
        raise ValueError(f"Unknown connector type: {connector_type}")
    
    return connector_class(**config)

# Usage
config = load_connector_config('connectors.yaml')
active_connectors = []

for conn_type, conn_config in config['connectors'].items():
    if conn_config.get('enabled', False):
        connector = create_connector(conn_type, conn_config)
        active_connectors.append({
            'name': conn_type,
            'connector': connector,
            'options': conn_config.get('sync_options', {})
        })
```

## Best Practices

### 1. Authentication Security

```python
# Never hardcode credentials
# Bad
connector = GitHubConnector(token="ghp_actualtoken123")

# Good
connector = GitHubConnector(token=os.getenv("GITHUB_TOKEN"))

# Better - use secret management
from contextframe.utils import SecretManager

secrets = SecretManager()
connector = GitHubConnector(token=secrets.get("github.token"))
```

### 2. Rate Limiting

```python
class RateLimitedConnector(BaseConnector):
    """Connector with rate limiting."""
    
    def __init__(self, rate_limit=60, **config):
        super().__init__(**config)
        self.rate_limit = rate_limit  # requests per minute
        self.request_times = []
    
    def _check_rate_limit(self):
        """Enforce rate limiting."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            # Wait until oldest request expires
            sleep_time = 60 - (now - self.request_times[0]) + 1
            time.sleep(sleep_time)
            self.request_times = self.request_times[1:]
        
        self.request_times.append(now)
    
    def sync_documents(self, **options):
        """Sync with rate limiting."""
        self._check_rate_limit()
        return super().sync_documents(**options)
```

### 3. Logging and Monitoring

```python
import logging

class LoggingConnector(BaseConnector):
    """Connector with comprehensive logging."""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.logger = logging.getLogger(f"connector.{self.__class__.__name__}")
    
    def sync_documents(self, **options):
        """Sync with logging."""
        self.logger.info(f"Starting sync with options: {options}")
        start_time = time.time()
        
        try:
            documents = super().sync_documents(**options)
            duration = time.time() - start_time
            
            self.logger.info(
                f"Sync completed: {len(documents)} documents in {duration:.2f}s"
            )
            
            # Log metrics
            self._log_metrics({
                'documents_synced': len(documents),
                'sync_duration': duration,
                'sync_timestamp': datetime.now().isoformat()
            })
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}", exc_info=True)
            raise
    
    def _log_metrics(self, metrics):
        """Log metrics for monitoring."""
        # Could send to monitoring service
        pass
```

### 4. Data Validation

```python
def validate_frame_record(record):
    """Validate FrameRecord before import."""
    errors = []
    
    # Required fields
    if not record.metadata.get('title'):
        errors.append("Missing title")
    
    if not record.text_content:
        errors.append("Missing content")
    
    # Source tracking
    if not record.metadata.get('source_type'):
        errors.append("Missing source_type")
    
    if not record.metadata.get('source_url'):
        errors.append("Missing source_url")
    
    # Metadata validation
    if record.metadata.get('created_at'):
        try:
            datetime.fromisoformat(record.metadata['created_at'])
        except:
            errors.append("Invalid created_at timestamp")
    
    return len(errors) == 0, errors

class ValidatingConnector(BaseConnector):
    """Connector with validation."""
    
    def map_to_frame_record(self, external_doc):
        """Map with validation."""
        record = super().map_to_frame_record(external_doc)
        
        is_valid, errors = validate_frame_record(record)
        if not is_valid:
            raise ValueError(f"Invalid record: {errors}")
        
        return record
```

## Next Steps

- Explore specific connectors:
  - [GitHub Connector](github.md)
  - [Linear Connector](linear.md)
  - [Google Drive Connector](google-drive.md)
  - [Notion Connector](notion.md)
  - [Slack Connector](slack.md)
  - [Discord Connector](discord.md)
  - [Obsidian Connector](obsidian.md)
- Learn to [Build Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/multi-source-sync.md)
- Check the [API Reference](../api/connectors.md)