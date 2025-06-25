"""Comprehensive examples of all ContextFrame external system connectors."""

import os
from pathlib import Path

from contextframe import FrameDataset
from contextframe.connectors import (
    GitHubConnector,
    LinearConnector,
    GoogleDriveConnector,
    NotionConnector,
    SlackConnector,
    DiscordConnector,
    ObsidianConnector,
    ConnectorConfig,
    AuthType,
)


def example_google_drive_sync():
    """Example of syncing Google Drive documents."""
    
    dataset_path = Path("data/google_drive.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    # Service account authentication (recommended for production)
    config = ConnectorConfig(
        name="Google Drive Documents",
        auth_type=AuthType.API_KEY,
        auth_config={
            "service_account_info": {
                # Service account JSON key content
                "type": "service_account",
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        sync_config={
            "folder_ids": ["folder-id-1", "folder-id-2"],  # Specific folders
            "export_google_formats": True,  # Convert Google Docs to text
            "include_trashed": False,
            "file_patterns": ["*.pdf", "*.docx", "*.txt"],
        }
    )
    
    connector = GoogleDriveConnector(config, dataset)
    
    if connector.validate_connection():
        print("Discovering Drive content...")
        discovery = connector.discover_content()
        print(f"Found {discovery['file_stats']['total_files']} files")
        
        print("\nSyncing Drive...")
        result = connector.sync(incremental=True)
        print(f"Created: {result.frames_created}, Updated: {result.frames_updated}")


def example_notion_sync():
    """Example of syncing Notion workspace."""
    
    dataset_path = Path("data/notion_workspace.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    config = ConnectorConfig(
        name="Notion Knowledge Base",
        auth_type=AuthType.TOKEN,
        auth_config={
            "token": os.getenv("NOTION_TOKEN"),  # Notion integration token
        },
        sync_config={
            "sync_databases": True,
            "sync_pages": True,
            "include_archived": False,
            "include_comments": True,
            # "database_ids": ["db-uuid-1", "db-uuid-2"],  # Specific databases
            # "page_ids": ["page-uuid-1"],  # Specific pages
        }
    )
    
    connector = NotionConnector(config, dataset)
    
    if connector.validate_connection():
        print("Discovering Notion content...")
        discovery = connector.discover_content()
        print(f"Found {discovery['stats']['total_pages']} pages and {discovery['stats']['total_databases']} databases")
        
        print("\nSyncing Notion...")
        result = connector.sync(incremental=True)
        print(f"Created: {result.frames_created}, Updated: {result.frames_updated}")


def example_slack_sync():
    """Example of syncing Slack workspace."""
    
    dataset_path = Path("data/slack_workspace.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    config = ConnectorConfig(
        name="Slack Team Chat",
        auth_type=AuthType.TOKEN,
        auth_config={
            "token": os.getenv("SLACK_BOT_TOKEN"),  # Slack bot token (xoxb-...)
        },
        sync_config={
            "channel_names": ["general", "engineering", "product"],  # Specific channels
            "include_threads": True,
            "include_reactions": True,
            "days_to_sync": 30,  # Last 30 days
            "include_private": False,  # Only public channels
            "include_bots": False,  # Skip bot messages
        }
    )
    
    connector = SlackConnector(config, dataset)
    
    if connector.validate_connection():
        print("Discovering Slack content...")
        discovery = connector.discover_content()
        print(f"Workspace: {discovery['workspace']['name']}")
        print(f"Found {discovery['stats']['total_channels']} channels")
        
        print("\nSyncing Slack...")
        result = connector.sync(incremental=True)
        print(f"Created: {result.frames_created}, Updated: {result.frames_updated}")


def example_discord_sync():
    """Example of syncing Discord server."""
    
    dataset_path = Path("data/discord_server.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    config = ConnectorConfig(
        name="Discord Community",
        auth_type=AuthType.TOKEN,
        auth_config={
            "bot_token": os.getenv("DISCORD_BOT_TOKEN"),  # Discord bot token
        },
        sync_config={
            "guild_ids": [123456789],  # Server IDs
            "channel_names": ["general", "development", "support"],
            "include_threads": True,
            "include_forum_posts": True,
            "days_to_sync": 14,  # Last 2 weeks
            "include_reactions": True,
            "include_bots": False,
        }
    )
    
    # Note: Discord connector requires async execution
    print("Discord connector requires async execution - see documentation for async examples")


def example_obsidian_sync():
    """Example of syncing Obsidian vault."""
    
    dataset_path = Path("data/obsidian_vault.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    config = ConnectorConfig(
        name="Personal Knowledge Vault",
        auth_type=AuthType.NONE,  # Local file access
        sync_config={
            "vault_path": "/path/to/obsidian/vault",  # Path to Obsidian vault
            "include_attachments": True,
            "include_daily_notes": True,
            "include_templates": False,
            "folders_to_exclude": [".obsidian", ".trash", "Archive"],
            "extract_frontmatter": True,
            "extract_tags": True,
            "extract_backlinks": True,
        }
    )
    
    connector = ObsidianConnector(config, dataset)
    
    if connector.validate_connection():
        print("Discovering Obsidian vault...")
        discovery = connector.discover_content()
        print(f"Vault: {discovery['vault_name']}")
        print(f"Found {discovery['file_stats']['total_notes']} notes")
        print(f"Found {len(discovery['metadata']['tags_found'])} unique tags")
        
        print("\nSyncing Obsidian...")
        result = connector.sync(incremental=True)
        print(f"Created: {result.frames_created}, Updated: {result.frames_updated}")


def example_enterprise_knowledge_base():
    """Example of building a comprehensive enterprise knowledge base."""
    
    # Create unified dataset
    dataset_path = Path("data/enterprise_knowledge.lance")
    dataset = FrameDataset.create(dataset_path) if not dataset_path.exists() else FrameDataset(dataset_path)
    
    connectors = []
    
    # 1. GitHub - Code and documentation
    if os.getenv("GITHUB_TOKEN"):
        github_config = ConnectorConfig(
            name="Company GitHub",
            auth_type=AuthType.TOKEN,
            auth_config={"token": os.getenv("GITHUB_TOKEN")},
            sync_config={
                "owner": "mycompany",
                "repo": "documentation",
                "paths": ["/docs", "/README.md"],
                "file_patterns": ["*.md", "*.rst"],
            }
        )
        connectors.append(("GitHub", GitHubConnector(github_config, dataset)))
    
    # 2. Notion - Product requirements and specs
    if os.getenv("NOTION_TOKEN"):
        notion_config = ConnectorConfig(
            name="Product Specs",
            auth_type=AuthType.TOKEN,
            auth_config={"token": os.getenv("NOTION_TOKEN")},
            sync_config={
                "sync_databases": True,
                "sync_pages": True,
                "include_archived": False,
            }
        )
        connectors.append(("Notion", NotionConnector(notion_config, dataset)))
    
    # 3. Linear - Project management and issues
    if os.getenv("LINEAR_API_KEY"):
        linear_config = ConnectorConfig(
            name="Engineering Issues",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": os.getenv("LINEAR_API_KEY")},
            sync_config={
                "sync_teams": True,
                "sync_projects": True,
                "sync_issues": True,
                "include_archived": False,
            }
        )
        connectors.append(("Linear", LinearConnector(linear_config, dataset)))
    
    # 4. Slack - Team discussions and decisions
    if os.getenv("SLACK_BOT_TOKEN"):
        slack_config = ConnectorConfig(
            name="Team Discussions",
            auth_type=AuthType.TOKEN,
            auth_config={"token": os.getenv("SLACK_BOT_TOKEN")},
            sync_config={
                "channel_names": ["engineering", "product", "general"],
                "include_threads": True,
                "days_to_sync": 14,
            }
        )
        connectors.append(("Slack", SlackConnector(slack_config, dataset)))
    
    # Sync all sources
    total_created = 0
    total_updated = 0
    
    for name, connector in connectors:
        if connector.validate_connection():
            print(f"\nSyncing {name}...")
            result = connector.sync(incremental=True)
            print(f"{name}: {result.frames_created} created, {result.frames_updated} updated")
            total_created += result.frames_created
            total_updated += result.frames_updated
            
            if result.errors:
                print(f"{name} errors: {len(result.errors)}")
        else:
            print(f"Failed to connect to {name}")
    
    print(f"\n=== Enterprise Knowledge Base Complete ===")
    print(f"Total frames created: {total_created}")
    print(f"Total frames updated: {total_updated}")
    
    # Demonstrate unified search
    print("\n=== Cross-Platform Search Examples ===")
    
    # Search for API documentation across all sources
    api_docs = dataset.search("API documentation", limit=5)
    print(f"\nFound {len(api_docs)} API-related documents:")
    for doc in api_docs:
        source = doc.metadata.get('source_type', 'unknown')
        title = doc.metadata.get('title', 'Untitled')
        print(f"  - {title} ({source})")
    
    # Search for security-related content
    security_content = dataset.search("security authentication", limit=5)
    print(f"\nFound {len(security_content)} security-related items:")
    for doc in security_content:
        source = doc.metadata.get('source_type', 'unknown')
        title = doc.metadata.get('title', 'Untitled')
        print(f"  - {title} ({source})")


def example_dependencies_check():
    """Check which connectors can be used based on installed dependencies."""
    
    connectors_status = {
        "GitHub": ("PyGithub", "github"),
        "Linear": ("linear-python", "linear"),
        "Google Drive": ("google-api-python-client", "googleapiclient"),
        "Notion": ("notion-client", "notion_client"),
        "Slack": ("slack-sdk", "slack_sdk"),
        "Discord": ("discord.py", "discord"),
        "Obsidian": ("Built-in", None),  # No external dependencies
    }
    
    print("=== Connector Dependencies Status ===")
    
    for connector_name, (package_name, import_name) in connectors_status.items():
        if import_name is None:
            status = "✅ Available"
        else:
            try:
                __import__(import_name)
                status = "✅ Available"
            except ImportError:
                status = f"❌ Missing (install: pip install {package_name})"
        
        print(f"{connector_name:15} : {status}")


if __name__ == "__main__":
    print("=== ContextFrame Connectors Examples ===")
    
    # Check dependencies first
    example_dependencies_check()
    print()
    
    # Run individual examples based on available credentials
    examples = [
        ("Google Drive", example_google_drive_sync, ["GOOGLE_PROJECT_ID", "GOOGLE_CLIENT_EMAIL"]),
        ("Notion", example_notion_sync, ["NOTION_TOKEN"]),
        ("Slack", example_slack_sync, ["SLACK_BOT_TOKEN"]),
        ("Obsidian", example_obsidian_sync, []),  # No credentials needed
    ]
    
    for name, example_func, required_env_vars in examples:
        if not required_env_vars or all(os.getenv(var) for var in required_env_vars):
            print(f"\n=== {name} Example ===")
            try:
                example_func()
            except ImportError as e:
                print(f"Skipping {name}: Missing dependency ({e})")
            except Exception as e:
                print(f"Error in {name} example: {e}")
        else:
            missing = [var for var in required_env_vars if not os.getenv(var)]
            print(f"\nSkipping {name}: Set {', '.join(missing)} environment variable(s)")
    
    # Enterprise example if multiple sources available
    if (os.getenv("GITHUB_TOKEN") and os.getenv("NOTION_TOKEN") and 
        os.getenv("LINEAR_API_KEY") and os.getenv("SLACK_BOT_TOKEN")):
        print("\n=== Enterprise Knowledge Base Example ===")
        example_enterprise_knowledge_base()
    else:
        print("\nSet multiple credentials to run the enterprise knowledge base example")