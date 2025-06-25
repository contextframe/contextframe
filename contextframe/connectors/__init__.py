"""External system connectors for importing data into ContextFrame.

This module provides connectors to import data from various external systems
like GitHub, Linear, Google Drive, etc. into ContextFrame datasets.
"""

from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.connectors.discord import DiscordConnector
from contextframe.connectors.github import GitHubConnector
from contextframe.connectors.google_drive import GoogleDriveConnector
from contextframe.connectors.linear import LinearConnector
from contextframe.connectors.notion import NotionConnector
from contextframe.connectors.obsidian import ObsidianConnector
from contextframe.connectors.slack import SlackConnector

__all__ = [
    "SourceConnector",
    "ConnectorConfig",
    "SyncResult",
    "AuthType",
    "GitHubConnector",
    "LinearConnector",
    "GoogleDriveConnector",
    "NotionConnector",
    "SlackConnector",
    "DiscordConnector",
    "ObsidianConnector",
]
