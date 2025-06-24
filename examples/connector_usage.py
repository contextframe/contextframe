"""Example usage of ContextFrame external system connectors."""

import os
from pathlib import Path

from contextframe import FrameDataset
from contextframe.connectors import (
    GitHubConnector,
    LinearConnector,
    ConnectorConfig,
    AuthType,
)


def example_github_sync():
    """Example of syncing a GitHub repository."""
    
    # Create or load dataset
    dataset_path = Path("data/github_contextframe.lance")
    if dataset_path.exists():
        dataset = FrameDataset(dataset_path)
    else:
        dataset = FrameDataset.create(dataset_path)
    
    # Configure GitHub connector
    config = ConnectorConfig(
        name="ContextFrame GitHub",
        auth_type=AuthType.TOKEN,
        auth_config={
            "token": os.getenv("GITHUB_TOKEN"),  # Set GITHUB_TOKEN env var
        },
        sync_config={
            "owner": "contextframe",
            "repo": "contextframe",
            "branch": "main",
            "paths": ["/contextframe", "/docs"],  # Sync specific paths
            "file_patterns": ["*.py", "*.md"],  # Only Python and Markdown files
            "exclude_patterns": ["*test*", "*__pycache__*"],  # Exclude tests
        }
    )
    
    # Create and run connector
    connector = GitHubConnector(config, dataset)
    
    # Validate connection
    if not connector.validate_connection():
        print("Failed to connect to GitHub")
        return
        
    # Discover content
    print("Discovering repository content...")
    discovery = connector.discover_content()
    print(f"Found {discovery['stats']['total_files']} files")
    print(f"File types: {discovery['stats']['file_types']}")
    
    # Sync content
    print("\nSyncing repository...")
    result = connector.sync(incremental=True)
    
    print(f"\nSync completed!")
    print(f"- Created: {result.frames_created} frames")
    print(f"- Updated: {result.frames_updated} frames")
    print(f"- Failed: {result.frames_failed} frames")
    
    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
            

def example_linear_sync():
    """Example of syncing Linear workspace data."""
    
    # Create or load dataset
    dataset_path = Path("data/linear_workspace.lance")
    if dataset_path.exists():
        dataset = FrameDataset(dataset_path)
    else:
        dataset = FrameDataset.create(dataset_path)
    
    # Configure Linear connector
    config = ConnectorConfig(
        name="Linear Workspace",
        auth_type=AuthType.API_KEY,
        auth_config={
            "api_key": os.getenv("LINEAR_API_KEY"),  # Set LINEAR_API_KEY env var
        },
        sync_config={
            "sync_teams": True,
            "sync_projects": True,
            "sync_issues": True,
            "include_archived": False,
            "include_comments": True,
            # Optional filters:
            # "team_ids": ["team-uuid-1", "team-uuid-2"],
            # "project_ids": ["project-uuid-1"],
            # "issue_states": ["In Progress", "Todo"],
        }
    )
    
    # Create and run connector
    connector = LinearConnector(config, dataset)
    
    # Validate connection
    if not connector.validate_connection():
        print("Failed to connect to Linear")
        return
        
    # Discover content
    print("Discovering Linear workspace...")
    discovery = connector.discover_content()
    print(f"Organization: {discovery['workspace']['organization']['name']}")
    print(f"Teams: {len(discovery['teams'])}")
    print(f"Projects: {len(discovery['projects'])}")
    print(f"Issues: {discovery['issue_stats']['total']}")
    
    # Sync content
    print("\nSyncing workspace...")
    result = connector.sync(incremental=True)
    
    print(f"\nSync completed!")
    print(f"- Created: {result.frames_created} frames")
    print(f"- Updated: {result.frames_updated} frames")
    print(f"- Failed: {result.frames_failed} frames")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
            

def example_combined_workflow():
    """Example of combining data from multiple sources."""
    
    # Create unified dataset
    dataset_path = Path("data/unified_knowledge.lance")
    if dataset_path.exists():
        dataset = FrameDataset(dataset_path)
    else:
        dataset = FrameDataset.create(dataset_path)
    
    # Sync GitHub documentation
    github_config = ConnectorConfig(
        name="Docs from GitHub",
        auth_type=AuthType.TOKEN,
        auth_config={"token": os.getenv("GITHUB_TOKEN")},
        sync_config={
            "owner": "myorg",
            "repo": "documentation",
            "paths": ["/docs"],
            "file_patterns": ["*.md"],
        }
    )
    
    github_connector = GitHubConnector(github_config, dataset)
    if github_connector.validate_connection():
        print("Syncing GitHub documentation...")
        github_result = github_connector.sync()
        print(f"GitHub: {github_result.frames_created} new docs")
    
    # Sync Linear issues related to documentation
    linear_config = ConnectorConfig(
        name="Doc Issues from Linear",
        auth_type=AuthType.API_KEY,
        auth_config={"api_key": os.getenv("LINEAR_API_KEY")},
        sync_config={
            "sync_teams": False,
            "sync_projects": False,
            "sync_issues": True,
            "issue_states": ["Todo", "In Progress"],
            # Filter for documentation-related issues
        }
    )
    
    linear_connector = LinearConnector(linear_config, dataset)
    if linear_connector.validate_connection():
        print("Syncing Linear issues...")
        linear_result = linear_connector.sync()
        print(f"Linear: {linear_result.frames_created} new issues")
    
    # Search across unified dataset
    print("\nSearching unified knowledge base...")
    results = dataset.search("documentation bug", limit=5)
    for result in results:
        print(f"- {result.metadata['title']} ({result.metadata['source_type']})")


if __name__ == "__main__":
    # Run examples based on available credentials
    if os.getenv("GITHUB_TOKEN"):
        print("=== GitHub Sync Example ===")
        example_github_sync()
        print("\n")
    else:
        print("Set GITHUB_TOKEN environment variable to run GitHub example")
        
    if os.getenv("LINEAR_API_KEY"):
        print("=== Linear Sync Example ===")
        example_linear_sync()
        print("\n")
    else:
        print("Set LINEAR_API_KEY environment variable to run Linear example")
        
    if os.getenv("GITHUB_TOKEN") and os.getenv("LINEAR_API_KEY"):
        print("=== Combined Workflow Example ===")
        example_combined_workflow()
    else:
        print("\nSet both GITHUB_TOKEN and LINEAR_API_KEY to run combined example")