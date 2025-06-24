"""Base classes and interfaces for external system connectors."""

import logging
from abc import ABC, abstractmethod
from contextframe import FrameDataset, FrameRecord
from contextframe.schema import RecordType
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class AuthType(Enum):
    """Supported authentication types for connectors."""

    API_KEY = "api_key"
    OAUTH = "oauth"
    BASIC = "basic"
    TOKEN = "token"
    NONE = "none"


@dataclass
class ConnectorConfig:
    """Configuration for a source connector."""

    name: str
    """Name of the connector instance."""

    auth_type: AuthType = AuthType.NONE
    """Type of authentication to use."""

    auth_config: dict[str, Any] = field(default_factory=dict)
    """Authentication configuration (API keys, tokens, etc)."""

    sync_config: dict[str, Any] = field(default_factory=dict)
    """Sync-specific configuration (filters, mappings, etc)."""

    rate_limit: int | None = None
    """Maximum requests per minute (if applicable)."""

    timeout: int = 30
    """Request timeout in seconds."""

    retry_count: int = 3
    """Number of retries for failed requests."""


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    """Whether the sync completed successfully."""

    frames_created: int = 0
    """Number of new frames created."""

    frames_updated: int = 0
    """Number of existing frames updated."""

    frames_failed: int = 0
    """Number of frames that failed to import."""

    errors: list[str] = field(default_factory=list)
    """List of error messages."""

    warnings: list[str] = field(default_factory=list)
    """List of warning messages."""

    start_time: datetime = field(default_factory=datetime.now)
    """When the sync started."""

    end_time: datetime | None = None
    """When the sync completed."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional sync metadata (last cursor, etc)."""

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def complete(self) -> None:
        """Mark the sync as complete."""
        self.end_time = datetime.now()

    @property
    def duration(self) -> float | None:
        """Duration of the sync in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@runtime_checkable
class AuthProvider(Protocol):
    """Protocol for authentication providers."""

    def authenticate(self) -> dict[str, Any]:
        """Authenticate and return auth headers/tokens."""
        ...

    def refresh(self) -> dict[str, Any]:
        """Refresh authentication if needed."""
        ...

    def is_valid(self) -> bool:
        """Check if current auth is valid."""
        ...


class SourceConnector(ABC):
    """Base class for all external system connectors."""

    def __init__(self, config: ConnectorConfig, dataset: FrameDataset):
        """Initialize the connector.

        Args:
            config: Connector configuration
            dataset: Target FrameDataset to import into
        """
        self.config = config
        self.dataset = dataset
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._auth_provider: AuthProvider | None = None

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate that the connector can connect to the source system.

        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def discover_content(self) -> dict[str, Any]:
        """Discover available content in the source system.

        Returns:
            Dictionary describing available content structure
        """
        pass

    @abstractmethod
    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync content from the source system.

        Args:
            incremental: Whether to perform incremental sync (vs full sync)

        Returns:
            Result of the sync operation
        """
        pass

    @abstractmethod
    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Map source system data to a FrameRecord.

        Args:
            source_data: Data from the source system

        Returns:
            FrameRecord if mapping successful, None otherwise
        """
        pass

    def get_last_sync_state(self) -> dict[str, Any] | None:
        """Get the last sync state for incremental syncs.

        Returns:
            Last sync state if available
        """
        # Look for a dataset header or sync state frame
        try:
            results = self.dataset.search(
                f"record_type:{RecordType.DATASET_HEADER} AND title:'{self.config.name} Sync State'",
                limit=1,
            )
            if results:
                frame = results[0]
                return frame.metadata.get("sync_state", {})
        except Exception as e:
            self.logger.warning(f"Failed to get last sync state: {e}")
        return None

    def save_sync_state(self, state: dict[str, Any]) -> None:
        """Save the current sync state for incremental syncs.

        Args:
            state: Sync state to save
        """
        try:
            # Create or update sync state frame
            sync_frame = FrameRecord(
                title=f"{self.config.name} Sync State",
                text_content=f"Sync state for {self.config.name} connector",
                metadata={
                    "record_type": RecordType.DATASET_HEADER,
                    "sync_state": state,
                    "connector_name": self.config.name,
                    "last_sync": datetime.now().isoformat(),
                },
            )

            # Try to update existing or create new
            existing = self.dataset.search(
                f"record_type:{RecordType.DATASET_HEADER} AND title:'{self.config.name} Sync State'",
                limit=1,
            )
            if existing:
                self.dataset.update(existing[0].metadata["uuid"], sync_frame)
            else:
                self.dataset.add(sync_frame)

        except Exception as e:
            self.logger.error(f"Failed to save sync state: {e}")

    def create_collection(self, name: str, description: str) -> str:
        """Create a collection for organizing imported content.

        Args:
            name: Collection name
            description: Collection description

        Returns:
            Collection ID
        """
        collection_header = FrameRecord(
            title=name,
            text_content=description,
            metadata={
                "record_type": RecordType.COLLECTION_HEADER,
                "connector": self.config.name,
                "created_by": "connector",
            },
        )

        self.dataset.add(collection_header)
        return collection_header.metadata["uuid"]

    def batch_import(
        self, frames: list[FrameRecord], batch_size: int = 100
    ) -> SyncResult:
        """Import frames in batches for efficiency.

        Args:
            frames: List of frames to import
            batch_size: Number of frames per batch

        Returns:
            Result of the import operation
        """
        result = SyncResult(success=True)

        for i in range(0, len(frames), batch_size):
            batch = frames[i : i + batch_size]
            try:
                for frame in batch:
                    try:
                        self.dataset.add(frame)
                        result.frames_created += 1
                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(
                            f"Failed to add frame '{frame.metadata.get('title', 'Unknown')}': {e}"
                        )

            except Exception as e:
                result.success = False
                result.add_error(f"Batch import failed: {e}")
                break

        result.complete()
        return result
