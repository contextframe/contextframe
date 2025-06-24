# External System Connectors

ContextFrame provides connectors to import data from external systems like GitHub, Linear, Google Drive, and more. These connectors enable you to build a unified knowledge base from your existing tools and platforms.

## Overview

External connectors allow you to:
- Import documents, code, and issues from various platforms
- Keep your ContextFrame dataset synchronized with source systems
- Preserve relationships and metadata from the original systems
- Perform incremental updates to avoid re-importing unchanged data

## Available Connectors

### GitHub Connector

Import repositories, files, and code from GitHub.

**Features:**
- Import specific paths or entire repositories
- Filter by file patterns (e.g., `*.py`, `*.md`)
- Preserve file structure as collections
- Support for public and private repositories
- Incremental sync based on commits

**Example:**
```python
from contextframe import FrameDataset
from contextframe.connectors import GitHubConnector, ConnectorConfig, AuthType

# Configure connector
config = ConnectorConfig(
    name="My GitHub Repo",
    auth_type=AuthType.TOKEN,
    auth_config={"token": "github_pat_xxxxx"},
    sync_config={
        "owner": "myorg",
        "repo": "myrepo",
        "branch": "main",
        "paths": ["/src", "/docs"],
        "file_patterns": ["*.py", "*.md"],
        "exclude_patterns": ["*test*", "*__pycache__*"]
    }
)

# Create connector and sync
dataset = FrameDataset("my_knowledge.lance")
connector = GitHubConnector(config, dataset)

if connector.validate_connection():
    result = connector.sync(incremental=True)
    print(f"Imported {result.frames_created} new files")
```

### Linear Connector

Import teams, projects, issues, and comments from Linear.

**Features:**
- Import complete workspace hierarchy
- Preserve relationships between teams, projects, and issues
- Include issue comments and metadata
- Filter by teams, projects, or issue states
- Support for custom field mapping

**Example:**
```python
from contextframe.connectors import LinearConnector, ConnectorConfig, AuthType

config = ConnectorConfig(
    name="Linear Workspace",
    auth_type=AuthType.API_KEY,
    auth_config={"api_key": "lin_api_xxxxx"},
    sync_config={
        "sync_teams": True,
        "sync_projects": True,
        "sync_issues": True,
        "include_comments": True,
        "include_archived": False,
        # Optional filters:
        "team_ids": ["team-uuid"],
        "issue_states": ["Todo", "In Progress"]
    }
)

connector = LinearConnector(config, dataset)
result = connector.sync()
```

## Base Connector Architecture

All connectors inherit from the `SourceConnector` base class:

```python
from contextframe.connectors import SourceConnector, ConnectorConfig, SyncResult
from contextframe import FrameRecord

class MyConnector(SourceConnector):
    def validate_connection(self) -> bool:
        """Validate connection to source system"""
        pass
        
    def discover_content(self) -> dict[str, Any]:
        """Discover available content"""
        pass
        
    def sync(self, incremental: bool = True) -> SyncResult:
        """Perform the sync operation"""
        pass
        
    def map_to_frame(self, source_data: dict) -> FrameRecord | None:
        """Map source data to FrameRecord"""
        pass
```

## Authentication

Connectors support various authentication methods:

```python
from contextframe.connectors import AuthType

# API Key
config = ConnectorConfig(
    name="My Connector",
    auth_type=AuthType.API_KEY,
    auth_config={"api_key": "xxxxx"}
)

# OAuth Token
config = ConnectorConfig(
    name="My Connector", 
    auth_type=AuthType.TOKEN,
    auth_config={"token": "xxxxx"}
)

# Basic Auth
config = ConnectorConfig(
    name="My Connector",
    auth_type=AuthType.BASIC,
    auth_config={"username": "user", "password": "pass"}
)
```

## Incremental Sync

Connectors support incremental synchronization to import only changed data:

```python
# First sync - imports everything
result = connector.sync(incremental=False)

# Subsequent syncs - only changes
result = connector.sync(incremental=True)

# Check what was synced
print(f"Created: {result.frames_created}")
print(f"Updated: {result.frames_updated}")
print(f"Failed: {result.frames_failed}")
```

## Error Handling

Connectors provide detailed error and warning information:

```python
result = connector.sync()

if not result.success:
    print("Sync failed!")
    for error in result.errors:
        print(f"Error: {error}")
        
if result.warnings:
    print("Warnings:")
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

## Collections and Organization

Connectors automatically organize imported content into collections:

- GitHub: Creates collections for repositories and folders
- Linear: Creates collections for teams and projects
- Documents are linked to appropriate collections
- Relationships between items are preserved

## Custom Connectors

To create a custom connector:

1. Inherit from `SourceConnector`
2. Implement required methods
3. Handle authentication
4. Map source data to FrameRecords

Example custom connector:

```python
from contextframe.connectors import SourceConnector, ConnectorConfig, SyncResult
from contextframe import FrameRecord

class NotionConnector(SourceConnector):
    def __init__(self, config: ConnectorConfig, dataset):
        super().__init__(config, dataset)
        self.workspace_id = config.sync_config.get("workspace_id")
        
    def validate_connection(self) -> bool:
        try:
            # Test API connection
            response = self._api_call("/v1/users/me")
            return response.status_code == 200
        except:
            return False
            
    def discover_content(self) -> dict[str, Any]:
        # Discover pages, databases, etc.
        return {
            "pages": self._list_pages(),
            "databases": self._list_databases()
        }
        
    def sync(self, incremental: bool = True) -> SyncResult:
        result = SyncResult(success=True)
        
        # Get pages to sync
        pages = self._get_pages_to_sync(incremental)
        
        # Import each page
        for page in pages:
            frame = self.map_to_frame(page)
            if frame:
                self.dataset.add(frame)
                result.frames_created += 1
                
        result.complete()
        return result
        
    def map_to_frame(self, page_data: dict) -> FrameRecord | None:
        return FrameRecord(
            title=page_data["title"],
            text_content=page_data["content"],
            metadata={
                "source_type": "notion_page",
                "source_url": page_data["url"],
                "created_at": page_data["created_time"],
                "updated_at": page_data["last_edited_time"]
            }
        )
```

## Best Practices

1. **Use Incremental Sync**: After initial import, use incremental sync to reduce API calls
2. **Handle Rate Limits**: Configure appropriate timeouts and retry logic
3. **Filter Content**: Use path and pattern filters to import only relevant content
4. **Monitor Sync Results**: Check errors and warnings after each sync
5. **Test Connection**: Always validate connection before syncing

## Environment Variables

For security, store credentials in environment variables:

```bash
export GITHUB_TOKEN="github_pat_xxxxx"
export LINEAR_API_KEY="lin_api_xxxxx"
```

Then use in your code:
```python
import os

config = ConnectorConfig(
    name="GitHub",
    auth_type=AuthType.TOKEN,
    auth_config={"token": os.getenv("GITHUB_TOKEN")}
)
```

## Troubleshooting

### Connection Issues
- Verify credentials are correct
- Check network connectivity
- Ensure API permissions are sufficient

### Sync Failures
- Review error messages in SyncResult
- Check API rate limits
- Verify source data format matches expectations

### Performance
- Use incremental sync when possible
- Filter unnecessary content
- Adjust batch sizes for large imports