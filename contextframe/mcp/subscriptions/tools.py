"""MCP tools for subscription management."""

from .manager import SubscriptionManager
from contextframe import FrameDataset
from contextframe.mcp.errors import InvalidParams
from contextframe.mcp.schemas import (
    GetSubscriptionsParams,
    GetSubscriptionsResult,
    PollChangesParams,
    PollResult,
    SubscribeChangesParams,
    SubscribeResult,
    UnsubscribeParams,
    UnsubscribeResult,
)
from typing import Any, Dict, Optional

# Global subscription managers per dataset
_managers: dict[str, SubscriptionManager] = {}


def _get_or_create_manager(dataset: FrameDataset) -> SubscriptionManager:
    """Get or create a subscription manager for a dataset.

    Args:
        dataset: The dataset to manage

    Returns:
        The subscription manager
    """
    dataset_id = id(dataset)  # Use object ID as key

    if dataset_id not in _managers:
        _managers[dataset_id] = SubscriptionManager(dataset)

    return _managers[dataset_id]


async def subscribe_changes(
    params: SubscribeChangesParams, dataset: FrameDataset, **kwargs
) -> dict[str, Any]:
    """Create a subscription to monitor dataset changes.

    Creates a subscription that allows clients to watch for changes in the dataset.
    Since Lance doesn't have built-in change notifications, this implements a
    polling-based system that efficiently detects changes between versions.

    Args:
        params: Subscription parameters
        dataset: The dataset to monitor

    Returns:
        Subscription information including ID and polling details
    """
    try:
        # Get or create manager
        manager = _get_or_create_manager(dataset)

        # Create subscription
        subscription_id = await manager.create_subscription(
            resource_type=params.resource_type,
            filters=params.filters,
            options=params.options,
        )

        # Generate initial poll token
        poll_token = f"{subscription_id}:0"

        result = SubscribeResult(
            subscription_id=subscription_id,
            poll_token=poll_token,
            polling_interval=params.options.get("polling_interval", 5),
        )

        return result.model_dump()

    except Exception as e:
        raise InvalidParams(f"Failed to create subscription: {str(e)}")


async def poll_changes(
    params: PollChangesParams, dataset: FrameDataset, **kwargs
) -> dict[str, Any]:
    """Poll for changes since the last poll.

    This tool implements long polling for change detection. It will wait up to
    the specified timeout for changes to occur, returning immediately if changes
    are available.

    Args:
        params: Poll parameters
        dataset: The dataset being monitored

    Returns:
        Changes since last poll, new poll token, and subscription status
    """
    try:
        # Get manager
        manager = _get_or_create_manager(dataset)

        # Poll for changes
        poll_result = await manager.poll_subscription(
            subscription_id=params.subscription_id,
            poll_token=params.poll_token,
            timeout=params.timeout,
        )

        result = PollResult(**poll_result)

        return result.model_dump()

    except Exception as e:
        raise InvalidParams(f"Failed to poll changes: {str(e)}")


async def unsubscribe(
    params: UnsubscribeParams, dataset: FrameDataset, **kwargs
) -> dict[str, Any]:
    """Cancel an active subscription.

    Cancels a subscription and stops monitoring for changes. The subscription
    can still be polled one final time to retrieve any remaining buffered changes.

    Args:
        params: Unsubscribe parameters
        dataset: The dataset being monitored

    Returns:
        Cancellation status and final poll token
    """
    try:
        # Get manager
        manager = _get_or_create_manager(dataset)

        # Cancel subscription
        cancelled = await manager.cancel_subscription(params.subscription_id)

        result = UnsubscribeResult(
            cancelled=cancelled,
            final_poll_token=f"{params.subscription_id}:final" if cancelled else None,
        )

        return result.model_dump()

    except Exception as e:
        raise InvalidParams(f"Failed to unsubscribe: {str(e)}")


async def get_subscriptions(
    params: GetSubscriptionsParams, dataset: FrameDataset, **kwargs
) -> dict[str, Any]:
    """Get list of active subscriptions.

    Returns information about all active subscriptions, optionally filtered
    by resource type.

    Args:
        params: Query parameters
        dataset: The dataset being monitored

    Returns:
        List of active subscriptions with details
    """
    try:
        # Get manager
        manager = _get_or_create_manager(dataset)

        # Get subscriptions
        subscriptions = manager.get_subscriptions(resource_type=params.resource_type)

        result = GetSubscriptionsResult(
            subscriptions=subscriptions, total_count=len(subscriptions)
        )

        return result.model_dump()

    except Exception as e:
        raise InvalidParams(f"Failed to get subscriptions: {str(e)}")


# Tool definitions for registration
SUBSCRIPTION_TOOLS = [
    {
        "name": "subscribe_changes",
        "description": "Create a subscription to monitor dataset changes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resource_type": {
                    "type": "string",
                    "enum": ["documents", "collections", "all"],
                    "default": "all",
                    "description": "Type of resources to monitor",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters (e.g., {'collection_id': '...'})",
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "polling_interval": {
                            "type": "integer",
                            "default": 5,
                            "description": "Seconds between polls",
                        },
                        "include_data": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include full document data in changes",
                        },
                        "batch_size": {
                            "type": "integer",
                            "default": 100,
                            "description": "Max changes per poll response",
                        },
                    },
                },
            },
        },
    },
    {
        "name": "poll_changes",
        "description": "Poll for changes since the last poll",
        "inputSchema": {
            "type": "object",
            "required": ["subscription_id"],
            "properties": {
                "subscription_id": {
                    "type": "string",
                    "description": "Active subscription ID",
                },
                "poll_token": {
                    "type": "string",
                    "description": "Token from last poll (optional for first poll)",
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 0,
                    "maximum": 300,
                    "description": "Max seconds to wait for changes (long polling)",
                },
            },
        },
    },
    {
        "name": "unsubscribe",
        "description": "Cancel an active subscription",
        "inputSchema": {
            "type": "object",
            "required": ["subscription_id"],
            "properties": {
                "subscription_id": {
                    "type": "string",
                    "description": "Subscription to cancel",
                }
            },
        },
    },
    {
        "name": "get_subscriptions",
        "description": "Get list of active subscriptions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resource_type": {
                    "type": "string",
                    "enum": ["documents", "collections", "all"],
                    "description": "Filter by resource type (optional)",
                }
            },
        },
    },
]
