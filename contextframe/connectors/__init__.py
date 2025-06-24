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
from contextframe.connectors.github import GitHubConnector
from contextframe.connectors.linear import LinearConnector

__all__ = [
    "SourceConnector",
    "ConnectorConfig",
    "SyncResult",
    "AuthType",
    "GitHubConnector",
    "LinearConnector",
]
