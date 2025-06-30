---
title: "Connector Introduction"
---

# Connector Introduction

ContextFrame connectors enable seamless integration with external platforms and services, allowing you to import content from various sources into the standardized ContextFrame format.

## What are Connectors?

Connectors are modules that:
- Authenticate with external services
- Fetch content and metadata from those services
- Transform the data into ContextFrame's schema
- Handle incremental updates and synchronization
- Manage rate limits and API constraints

## Available Connectors

ContextFrame provides built-in connectors for popular platforms:

### Productivity & Collaboration
- **[Slack](../slack.md)** - Import conversations, threads, and shared files
- **[Discord](../discord.md)** - Import messages, threads, and attachments
- **[Notion](../notion.md)** - Import pages, databases, and blocks
- **[Linear](../linear.md)** - Import issues, projects, and documentation
- **[Google Drive](../google-drive.md)** - Import documents, spreadsheets, and presentations

### Development & Documentation
- **[GitHub](../github.md)** - Import repositories, issues, pull requests, and wikis
- **[Obsidian](../obsidian.md)** - Import markdown notes and vault structure

## Common Features

All connectors share these capabilities:

### Authentication
- OAuth2 flow support
- API key authentication
- Token refresh handling
- Secure credential storage

### Data Import
- Full initial import
- Incremental updates
- Metadata preservation
- Relationship mapping
- Attachment handling

### Error Handling
- Rate limit management
- Retry logic with backoff
- Partial failure recovery
- Detailed error reporting

## Basic Usage

### 1. Import a Connector

```python
from contextframe.connectors import SlackConnector

# Initialize with credentials
connector = SlackConnector(
    token="xoxb-your-token",
    workspace="your-workspace"
)
```

### 2. Configure Import Options

```python
# Set import parameters
config = {
    "channels": ["general", "engineering"],
    "include_threads": True,
    "include_attachments": True,
    "date_from": "2024-01-01"
}
```

### 3. Import Content

```python
# Import to a FrameDataset
dataset = connector.import_to_dataset(
    dataset_path="./slack_import.lance",
    config=config
)

# Or import as FrameRecords
frames = connector.import_frames(config=config)
```

## Authentication Methods

### OAuth2 Flow

```python
# For services that use OAuth2
from contextframe.connectors import NotionConnector

connector = NotionConnector()
auth_url = connector.get_auth_url(
    client_id="your-client-id",
    redirect_uri="http://localhost:8080/callback"
)
# User visits auth_url and authorizes
# Then exchange code for token
connector.set_tokens(code="auth-code-from-callback")
```

### API Key

```python
# For services that use API keys
from contextframe.connectors import LinearConnector

connector = LinearConnector(api_key="lin_api_your_key")
```

### Environment Variables

```python
# Connectors can read from environment
# Set: SLACK_TOKEN=xoxb-your-token
from contextframe.connectors import SlackConnector

connector = SlackConnector()  # Reads from env
```

## Incremental Updates

Connectors support efficient incremental updates:

```python
# Initial import
dataset = connector.import_to_dataset(
    dataset_path="./data.lance",
    config={"initial_import": True}
)

# Later, import only new/updated content
dataset = connector.import_to_dataset(
    dataset_path="./data.lance",
    config={"since_last_sync": True}
)
```

## Error Handling

Connectors provide detailed error information:

```python
try:
    frames = connector.import_frames(config)
except ConnectorAuthError as e:
    print(f"Authentication failed: {e}")
except ConnectorRateLimitError as e:
    print(f"Rate limit hit, retry after: {e.retry_after}")
except ConnectorError as e:
    print(f"Import failed: {e}")
```

## Custom Connectors

You can create custom connectors by extending the base class:

```python
from contextframe.connectors.base import BaseConnector

class MyCustomConnector(BaseConnector):
    def authenticate(self, **kwargs):
        # Implement authentication
        pass
    
    def fetch_content(self, **kwargs):
        # Implement content fetching
        pass
    
    def transform_to_frames(self, raw_data):
        # Transform to FrameRecords
        pass
```

See [Custom Connectors](../custom.md) for detailed implementation guide.

## Best Practices

1. **Use Incremental Updates**: Don't re-import everything each time
2. **Handle Rate Limits**: Respect API limits to avoid blocking
3. **Store Credentials Securely**: Use environment variables or secure vaults
4. **Log Progress**: Monitor long-running imports
5. **Test with Small Datasets**: Validate configuration before full imports

## Configuration Examples

### Slack Import with Filters

```python
config = {
    "channels": ["general", "random"],
    "users": ["U12345", "U67890"],  # Specific users
    "include_threads": True,
    "include_reactions": False,
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "message_types": ["message", "file_share"]
}
```

### GitHub Repository Import

```python
config = {
    "repos": ["org/repo1", "org/repo2"],
    "include_issues": True,
    "include_prs": True,
    "include_wiki": True,
    "include_releases": True,
    "state": "all",  # open, closed, all
    "labels": ["bug", "feature"]
}
```

### Notion Database Import

```python
config = {
    "databases": ["database-id-1", "database-id-2"],
    "include_pages": True,
    "include_comments": True,
    "include_attachments": True,
    "recursive": True  # Include child pages
}
```

## Next Steps

- Review specific [connector documentation](../overview.md#available-connectors)
- Learn about [custom connector development](../custom.md)
- Explore [connector configuration options](../validation.md)
- See [integration examples](../../cookbook/index.md)