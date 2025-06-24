"""GitHub connector for importing repository content into ContextFrame."""

import base64
import mimetypes
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse


class GitHubConnector(SourceConnector):
    """Connector for importing GitHub repository content."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize GitHub connector.

        Args:
            config: Connector configuration with GitHub-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Validate required config
        self.owner = config.sync_config.get("owner")
        self.repo = config.sync_config.get("repo")
        self.branch = config.sync_config.get("branch", "main")
        self.paths = config.sync_config.get("paths", ["/"])
        self.file_patterns = config.sync_config.get("file_patterns", ["*"])
        self.exclude_patterns = config.sync_config.get("exclude_patterns", [])

        if not self.owner or not self.repo:
            raise ValueError(
                "GitHub connector requires 'owner' and 'repo' in sync_config"
            )

        # Set up GitHub API client
        self._setup_client()

    def _setup_client(self):
        """Set up GitHub API client."""
        try:
            from github import Github
            from github.GithubException import GithubException

            self.GithubException = GithubException
        except ImportError:
            raise ImportError(
                "PyGithub is required for GitHub connector. Install with: pip install PyGithub"
            )

        # Initialize client based on auth type
        if self.config.auth_type == AuthType.TOKEN:
            token = self.config.auth_config.get("token")
            if not token:
                raise ValueError("GitHub token required for authentication")
            self.client = Github(token)
        elif self.config.auth_type == AuthType.NONE:
            # Public repos only
            self.client = Github()
        else:
            raise ValueError(
                f"Unsupported auth type for GitHub: {self.config.auth_type}"
            )

        # Get repository object
        try:
            self.github_repo = self.client.get_repo(f"{self.owner}/{self.repo}")
        except Exception as e:
            raise ValueError(
                f"Failed to access repository {self.owner}/{self.repo}: {e}"
            )

    def validate_connection(self) -> bool:
        """Validate GitHub connection and repository access."""
        try:
            # Try to get repository info
            _ = self.github_repo.full_name
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate GitHub connection: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover repository structure and content."""
        discovery = {
            "repository": {
                "owner": self.owner,
                "name": self.repo,
                "full_name": self.github_repo.full_name,
                "description": self.github_repo.description,
                "default_branch": self.github_repo.default_branch,
                "size": self.github_repo.size,
                "language": self.github_repo.language,
                "topics": list(self.github_repo.get_topics()),
            },
            "branches": [],
            "file_tree": {},
            "stats": {
                "total_files": 0,
                "file_types": {},
                "total_size": 0,
            },
        }

        # Get branches
        try:
            for branch in self.github_repo.get_branches():
                discovery["branches"].append(branch.name)
        except Exception as e:
            self.logger.warning(f"Failed to get branches: {e}")

        # Analyze file tree for specified paths
        for path in self.paths:
            try:
                self._discover_path(path.strip("/"), discovery)
            except Exception as e:
                self.logger.warning(f"Failed to discover path {path}: {e}")

        return discovery

    def _discover_path(self, path: str, discovery: dict[str, Any]):
        """Recursively discover files in a path."""
        try:
            contents = self.github_repo.get_contents(path, ref=self.branch)

            if not isinstance(contents, list):
                contents = [contents]

            for content in contents:
                if content.type == "file":
                    # Check if file matches patterns
                    if self._matches_patterns(content.path):
                        discovery["stats"]["total_files"] += 1
                        discovery["stats"]["total_size"] += content.size

                        # Track file types
                        ext = Path(content.name).suffix.lower()
                        discovery["stats"]["file_types"][ext] = (
                            discovery["stats"]["file_types"].get(ext, 0) + 1
                        )

                        # Add to tree
                        self._add_to_tree(discovery["file_tree"], content.path)

                elif content.type == "dir":
                    # Recursively discover subdirectories
                    self._discover_path(content.path, discovery)

        except self.GithubException as e:
            if e.status == 404:
                self.logger.warning(f"Path not found: {path}")
            else:
                raise

    def _add_to_tree(self, tree: dict, path: str):
        """Add a file path to the tree structure."""
        parts = path.split("/")
        current = tree

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Leaf node (file)
                current[part] = None
            else:
                # Directory node
                if part not in current:
                    current[part] = {}
                current = current[part]

    def _matches_patterns(self, path: str) -> bool:
        """Check if a file path matches the configured patterns."""
        path_obj = Path(path)

        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if path_obj.match(pattern):
                return False

        # Check include patterns
        if not self.file_patterns:
            return True

        for pattern in self.file_patterns:
            if pattern == "*" or path_obj.match(pattern):
                return True

        return False

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync repository content to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create collection for this repository
        collection_id = self.create_collection(
            f"{self.owner}/{self.repo}",
            f"GitHub repository: {self.github_repo.description or 'No description'}",
        )

        # Track processed files
        processed_files: set[str] = set()

        # Process each configured path
        for path in self.paths:
            try:
                self._sync_path(
                    path.strip("/"),
                    collection_id,
                    result,
                    last_sync_state,
                    processed_files,
                )
            except Exception as e:
                result.add_error(f"Failed to sync path {path}: {e}")
                result.success = False

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "branch": self.branch,
                "commit": self.github_repo.get_branch(self.branch).commit.sha,
                "processed_files": list(processed_files),
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _sync_path(
        self,
        path: str,
        collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_files: set[str],
    ):
        """Sync a specific path in the repository."""
        try:
            contents = self.github_repo.get_contents(path, ref=self.branch)

            if not isinstance(contents, list):
                contents = [contents]

            for content in contents:
                if content.type == "file" and self._matches_patterns(content.path):
                    # Check if file needs update
                    if incremental and last_sync_state:
                        last_commit = last_sync_state.get("commit")
                        if last_commit:
                            # Check if file changed since last sync
                            commits = list(
                                self.github_repo.get_commits(
                                    sha=self.branch,
                                    path=content.path,
                                    since=datetime.fromisoformat(
                                        last_sync_state["last_sync"]
                                    ),
                                )
                            )
                            if not commits:
                                continue

                    # Process file
                    frame = self.map_to_frame(content)
                    if frame:
                        frame.metadata["collection"] = collection_id
                        frame.metadata["collection_id"] = collection_id

                        try:
                            # Check if frame exists
                            existing = self.dataset.search(
                                f"source_url:'{content.html_url}'", limit=1
                            )

                            if existing:
                                self.dataset.update(existing[0].metadata["uuid"], frame)
                                result.frames_updated += 1
                            else:
                                self.dataset.add(frame)
                                result.frames_created += 1

                            processed_files.add(content.path)

                        except Exception as e:
                            result.frames_failed += 1
                            result.add_error(f"Failed to import {content.path}: {e}")

                elif content.type == "dir":
                    # Recursively sync subdirectories
                    self._sync_path(
                        content.path,
                        collection_id,
                        result,
                        last_sync_state,
                        processed_files,
                    )

        except self.GithubException as e:
            if e.status != 404:
                raise

    def map_to_frame(self, source_data: Any) -> FrameRecord | None:
        """Map GitHub file to FrameRecord."""
        try:
            # Get file content
            content_data = source_data.decoded_content

            # Determine content type
            mime_type, _ = mimetypes.guess_type(source_data.name)

            # Create base metadata
            metadata = {
                "title": source_data.name,
                "record_type": RecordType.DOCUMENT,
                "source_type": "github",
                "source_file": source_data.path,
                "source_url": source_data.html_url,
                "custom_metadata": {
                    "x_github_sha": source_data.sha,
                    "x_github_size": str(source_data.size),
                    "x_github_type": source_data.type,
                },
            }

            # Handle different file types
            text_content = None
            raw_data = None
            raw_data_type = None

            if mime_type and mime_type.startswith("text/"):
                # Text file - decode as string
                try:
                    text_content = content_data.decode("utf-8")
                except UnicodeDecodeError:
                    # Fall back to binary
                    raw_data = content_data
                    raw_data_type = mime_type or "application/octet-stream"
            elif mime_type and mime_type.startswith("image/"):
                # Image file - store as binary
                raw_data = content_data
                raw_data_type = mime_type
                text_content = f"Image file: {source_data.name}"
            else:
                # Try to decode as text, fall back to binary
                try:
                    text_content = content_data.decode("utf-8")
                except UnicodeDecodeError:
                    raw_data = content_data
                    raw_data_type = mime_type or "application/octet-stream"
                    text_content = f"Binary file: {source_data.name}"

            # Extract README content as context
            if source_data.name.lower() in ["readme.md", "readme.txt", "readme"]:
                metadata["context"] = text_content[:1000] if text_content else ""

            # Create frame
            frame = FrameRecord(
                text_content=text_content,
                metadata=metadata,
                raw_data=raw_data,
                raw_data_type=raw_data_type,
            )

            # Add relationships if this is a code file
            if mime_type in ["text/x-python", "text/x-java", "text/javascript"]:
                # TODO: Extract imports and create relationships
                pass

            return frame

        except Exception as e:
            self.logger.error(f"Failed to map file {source_data.path}: {e}")
            return None
