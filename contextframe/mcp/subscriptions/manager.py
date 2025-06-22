"""Subscription manager for tracking dataset changes."""

import asyncio
from contextframe import FrameDataset
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


@dataclass
class SubscriptionState:
    """State tracking for a subscription."""

    id: str
    resource_type: str  # "documents", "collections", "all"
    filters: dict[str, Any]
    created_at: datetime
    last_version: int
    last_poll_token: str
    last_poll_time: datetime | None = None
    change_buffer: list["Change"] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class Change:
    """Represents a change in the dataset."""

    type: str  # "created", "updated", "deleted"
    resource_type: str  # "document", "collection"
    resource_id: str
    version: int
    timestamp: datetime
    old_data: dict[str, Any] | None = None
    new_data: dict[str, Any] | None = None


class SubscriptionManager:
    """Manages subscriptions for dataset change monitoring."""

    def __init__(self, dataset: FrameDataset):
        """Initialize subscription manager.

        Args:
            dataset: The FrameDataset to monitor
        """
        self.dataset = dataset
        self.subscriptions: dict[str, SubscriptionState] = {}
        self._polling_task: asyncio.Task | None = None
        self._change_queue: asyncio.Queue = asyncio.Queue()
        self._last_check_version: int | None = None
        self._running = False

    async def start(self):
        """Start the subscription manager polling."""
        if self._running:
            return

        self._running = True
        self._last_check_version = self.dataset.version
        self._polling_task = asyncio.create_task(self._poll_changes())

    async def stop(self):
        """Stop the subscription manager."""
        self._running = False
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

    async def create_subscription(
        self,
        resource_type: str,
        filters: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Create a new subscription.

        Args:
            resource_type: Type of resources to monitor
            filters: Optional filters for the subscription
            options: Subscription options (polling_interval, include_data, etc.)

        Returns:
            Subscription ID
        """
        subscription_id = str(uuid4())
        poll_token = f"{subscription_id}:0"

        subscription = SubscriptionState(
            id=subscription_id,
            resource_type=resource_type,
            filters=filters or {},
            created_at=datetime.now(UTC),
            last_version=self.dataset.version,
            last_poll_token=poll_token,
            options=options
            or {"polling_interval": 5, "include_data": False, "batch_size": 100},
        )

        self.subscriptions[subscription_id] = subscription

        # Ensure polling is running
        if not self._running:
            await self.start()

        return subscription_id

    async def poll_subscription(
        self, subscription_id: str, poll_token: str | None = None, timeout: int = 30
    ) -> dict[str, Any]:
        """Poll for changes in a subscription.

        Args:
            subscription_id: The subscription to poll
            poll_token: Token from last poll (for ordering)
            timeout: Max seconds to wait for changes

        Returns:
            Dict with changes, new poll token, and status
        """
        if subscription_id not in self.subscriptions:
            return {
                "changes": [],
                "poll_token": None,
                "has_more": False,
                "subscription_active": False,
            }

        subscription = self.subscriptions[subscription_id]

        if not subscription.is_active:
            return {
                "changes": [],
                "poll_token": subscription.last_poll_token,
                "has_more": False,
                "subscription_active": False,
            }

        # Update last poll time
        subscription.last_poll_time = datetime.now(UTC)

        # Check for buffered changes
        changes = []
        if subscription.change_buffer:
            batch_size = subscription.options.get("batch_size", 100)
            changes = subscription.change_buffer[:batch_size]
            subscription.change_buffer = subscription.change_buffer[batch_size:]

        # If no buffered changes, wait for new ones (with timeout)
        if not changes and timeout > 0:
            try:
                # Wait for changes with timeout
                await asyncio.wait_for(
                    self._wait_for_changes(subscription_id), timeout=timeout
                )
                # Check buffer again
                if subscription.change_buffer:
                    batch_size = subscription.options.get("batch_size", 100)
                    changes = subscription.change_buffer[:batch_size]
                    subscription.change_buffer = subscription.change_buffer[batch_size:]
            except TimeoutError:
                pass  # No changes within timeout

        # Update poll token
        new_version = changes[-1].version if changes else subscription.last_version
        new_poll_token = f"{subscription_id}:{new_version}"
        subscription.last_poll_token = new_poll_token

        # Convert changes to dict format
        change_dicts = []
        for change in changes:
            change_dict = {
                "type": change.type,
                "resource_type": change.resource_type,
                "resource_id": change.resource_id,
                "version": change.version,
                "timestamp": change.timestamp.isoformat(),
            }

            # Include data if requested
            if subscription.options.get("include_data", False):
                if change.old_data:
                    change_dict["old_data"] = change.old_data
                if change.new_data:
                    change_dict["new_data"] = change.new_data

            change_dicts.append(change_dict)

        return {
            "changes": change_dicts,
            "poll_token": new_poll_token,
            "has_more": len(subscription.change_buffer) > 0,
            "subscription_active": subscription.is_active,
        }

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription.

        Args:
            subscription_id: The subscription to cancel

        Returns:
            Whether the subscription was cancelled
        """
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].is_active = False
            # Keep subscription for final poll
            return True
        return False

    def get_subscriptions(
        self, resource_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get list of active subscriptions.

        Args:
            resource_type: Optional filter by resource type

        Returns:
            List of subscription info
        """
        subscriptions = []

        for sub in self.subscriptions.values():
            if not sub.is_active:
                continue

            if resource_type and sub.resource_type != resource_type:
                continue

            subscriptions.append(
                {
                    "subscription_id": sub.id,
                    "resource_type": sub.resource_type,
                    "filters": sub.filters,
                    "created_at": sub.created_at.isoformat(),
                    "last_poll": sub.last_poll_time.isoformat()
                    if sub.last_poll_time
                    else None,
                    "options": sub.options,
                }
            )

        return subscriptions

    async def _poll_changes(self):
        """Background task to poll for dataset changes."""
        while self._running:
            try:
                # Check current version
                current_version = self.dataset.version

                if (
                    self._last_check_version
                    and current_version > self._last_check_version
                ):
                    # Detect changes between versions
                    changes = await self._detect_changes(
                        self._last_check_version, current_version
                    )

                    # Distribute changes to subscriptions
                    for change in changes:
                        await self._distribute_change(change)

                self._last_check_version = current_version

                # Sleep based on minimum polling interval
                min_interval = min(
                    (
                        sub.options.get("polling_interval", 5)
                        for sub in self.subscriptions.values()
                        if sub.is_active
                    ),
                    default=5,
                )
                await asyncio.sleep(min_interval)

            except Exception as e:
                # Log error but keep polling
                print(f"Error in subscription polling: {e}")
                await asyncio.sleep(5)

    async def _detect_changes(self, old_version: int, new_version: int) -> list[Change]:
        """Detect changes between dataset versions.

        Args:
            old_version: Previous version number
            new_version: Current version number

        Returns:
            List of detected changes
        """
        changes = []
        timestamp = datetime.now(UTC)

        # Get all UUIDs from both versions
        old_uuids = await self._get_version_uuids(old_version)
        new_uuids = await self._get_version_uuids(new_version)

        # Detect created documents
        created = new_uuids - old_uuids
        for uuid in created:
            changes.append(
                Change(
                    type="created",
                    resource_type="document",
                    resource_id=uuid,
                    version=new_version,
                    timestamp=timestamp,
                )
            )

        # Detect deleted documents
        deleted = old_uuids - new_uuids
        for uuid in deleted:
            changes.append(
                Change(
                    type="deleted",
                    resource_type="document",
                    resource_id=uuid,
                    version=new_version,
                    timestamp=timestamp,
                )
            )

        # Detect updated documents (same UUID, different content/metadata)
        common = old_uuids & new_uuids
        for uuid in common:
            if await self._has_changed(uuid, old_version, new_version):
                changes.append(
                    Change(
                        type="updated",
                        resource_type="document",
                        resource_id=uuid,
                        version=new_version,
                        timestamp=timestamp,
                    )
                )

        return changes

    async def _get_version_uuids(self, version: int) -> set[str]:
        """Get all document UUIDs from a specific version.

        Args:
            version: Version number

        Returns:
            Set of UUIDs
        """
        # Use Lance's checkout_version capability
        versioned_dataset = self.dataset.checkout_version(version)

        # Get all UUIDs
        scanner = versioned_dataset.scanner(columns=["uuid"])
        uuids = set()

        for batch in scanner.to_batches():
            for uuid in batch["uuid"]:
                if uuid:
                    uuids.add(str(uuid))

        return uuids

    async def _has_changed(self, uuid: str, old_version: int, new_version: int) -> bool:
        """Check if a document has changed between versions.

        Args:
            uuid: Document UUID
            old_version: Previous version
            new_version: Current version

        Returns:
            Whether the document changed
        """
        # Get document from both versions
        old_dataset = self.dataset.checkout_version(old_version)
        new_dataset = self.dataset.checkout_version(new_version)

        # Compare timestamps
        old_record = old_dataset.search(filter=f"uuid = '{uuid}'", limit=1)
        new_record = new_dataset.search(filter=f"uuid = '{uuid}'", limit=1)

        if not old_record or not new_record:
            return True  # Something changed if we can't find it

        old_record = old_record[0]
        new_record = new_record[0]

        # Compare updated_at timestamps
        old_updated = old_record.metadata.get("updated_at", "")
        new_updated = new_record.metadata.get("updated_at", "")

        return old_updated != new_updated

    async def _distribute_change(self, change: Change):
        """Distribute a change to relevant subscriptions.

        Args:
            change: The change to distribute
        """
        for subscription in self.subscriptions.values():
            if not subscription.is_active:
                continue

            # Check if change matches subscription
            if not self._matches_subscription(change, subscription):
                continue

            # Add to buffer
            subscription.change_buffer.append(change)

            # Notify waiting pollers
            self._change_queue.put_nowait(subscription.id)

    def _matches_subscription(
        self, change: Change, subscription: SubscriptionState
    ) -> bool:
        """Check if a change matches a subscription's filters.

        Args:
            change: The change to check
            subscription: The subscription to match against

        Returns:
            Whether the change matches
        """
        # Check resource type
        if subscription.resource_type != "all":
            if (
                subscription.resource_type == "documents"
                and change.resource_type != "document"
            ):
                return False
            if (
                subscription.resource_type == "collections"
                and change.resource_type != "collection"
            ):
                return False

        # TODO: Apply additional filters from subscription.filters
        # For now, match all changes of the correct type

        return True

    async def _wait_for_changes(self, subscription_id: str):
        """Wait for changes to arrive for a subscription.

        Args:
            subscription_id: The subscription to wait for
        """
        while True:
            sub_id = await self._change_queue.get()
            if sub_id == subscription_id:
                return
