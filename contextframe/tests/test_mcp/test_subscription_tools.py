"""Tests for MCP subscription tools."""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.subscriptions.manager import (
    SubscriptionManager, 
    SubscriptionState, 
    Change
)
from contextframe.mcp.subscriptions.tools import (
    subscribe_changes,
    poll_changes,
    unsubscribe,
    get_subscriptions
)
from contextframe.mcp.schemas import (
    SubscribeChangesParams,
    PollChangesParams,
    UnsubscribeParams,
    GetSubscriptionsParams
)


@pytest.fixture
def mock_dataset():
    """Create a mock dataset."""
    dataset = Mock(spec=FrameDataset)
    dataset.version = 1
    dataset.checkout_version = Mock()
    dataset.scanner = Mock()
    return dataset


@pytest.fixture
def subscription_manager(mock_dataset):
    """Create a subscription manager."""
    return SubscriptionManager(mock_dataset)


class TestSubscriptionManager:
    """Test subscription manager functionality."""
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, subscription_manager):
        """Test creating a subscription."""
        sub_id = await subscription_manager.create_subscription(
            resource_type="documents",
            filters={"collection_id": "test"},
            options={"polling_interval": 10}
        )
        
        assert sub_id in subscription_manager.subscriptions
        subscription = subscription_manager.subscriptions[sub_id]
        assert subscription.resource_type == "documents"
        assert subscription.filters == {"collection_id": "test"}
        assert subscription.options["polling_interval"] == 10
        
    @pytest.mark.asyncio
    async def test_poll_subscription_no_changes(self, subscription_manager):
        """Test polling with no changes."""
        # Create subscription
        sub_id = await subscription_manager.create_subscription("all")
        
        # Poll immediately (no changes)
        result = await subscription_manager.poll_subscription(sub_id, timeout=0)
        
        assert result["changes"] == []
        assert result["subscription_active"] is True
        assert result["has_more"] is False
        
    @pytest.mark.asyncio
    async def test_poll_subscription_with_changes(self, subscription_manager):
        """Test polling with buffered changes."""
        # Create subscription
        sub_id = await subscription_manager.create_subscription("documents")
        subscription = subscription_manager.subscriptions[sub_id]
        
        # Add changes to buffer
        change = Change(
            type="created",
            resource_type="document",
            resource_id="doc-123",
            version=2,
            timestamp=datetime.now(timezone.utc)
        )
        subscription.change_buffer.append(change)
        
        # Poll for changes
        result = await subscription_manager.poll_subscription(sub_id)
        
        assert len(result["changes"]) == 1
        assert result["changes"][0]["type"] == "created"
        assert result["changes"][0]["resource_id"] == "doc-123"
        
    @pytest.mark.asyncio
    async def test_cancel_subscription(self, subscription_manager):
        """Test cancelling a subscription."""
        # Create subscription
        sub_id = await subscription_manager.create_subscription("all")
        
        # Cancel it
        cancelled = await subscription_manager.cancel_subscription(sub_id)
        assert cancelled is True
        
        # Verify it's inactive
        subscription = subscription_manager.subscriptions[sub_id]
        assert subscription.is_active is False
        
    def test_get_subscriptions(self, subscription_manager):
        """Test listing subscriptions."""
        # Create multiple subscriptions manually
        sub1 = SubscriptionState(
            id="sub1",
            resource_type="documents",
            filters={},
            created_at=datetime.now(timezone.utc),
            last_version=1,
            last_poll_token="sub1:0"
        )
        sub2 = SubscriptionState(
            id="sub2",
            resource_type="collections",
            filters={},
            created_at=datetime.now(timezone.utc),
            last_version=1,
            last_poll_token="sub2:0"
        )
        
        subscription_manager.subscriptions = {"sub1": sub1, "sub2": sub2}
        
        # Get all subscriptions
        all_subs = subscription_manager.get_subscriptions()
        assert len(all_subs) == 2
        
        # Filter by type
        doc_subs = subscription_manager.get_subscriptions("documents")
        assert len(doc_subs) == 1
        assert doc_subs[0]["resource_type"] == "documents"
        
    @pytest.mark.asyncio
    async def test_detect_changes(self, subscription_manager, mock_dataset):
        """Test change detection between versions."""
        # Mock version checkouts
        old_dataset = Mock()
        new_dataset = Mock()
        mock_dataset.checkout_version.side_effect = [old_dataset, new_dataset]
        
        # Mock UUID retrieval and has_changed check
        with patch.object(
            subscription_manager,
            '_get_version_uuids',
            side_effect=[
                {"doc1", "doc2"},  # Old version
                {"doc2", "doc3"}   # New version
            ]
        ):
            # Mock _has_changed to avoid calling search
            with patch.object(
                subscription_manager,
                '_has_changed',
                return_value=False  # doc2 hasn't changed
            ):
                changes = await subscription_manager._detect_changes(1, 2)
            
        assert len(changes) == 2
        
        # Check for created document
        created = [c for c in changes if c.type == "created"]
        assert len(created) == 1
        assert created[0].resource_id == "doc3"
        
        # Check for deleted document
        deleted = [c for c in changes if c.type == "deleted"]
        assert len(deleted) == 1
        assert deleted[0].resource_id == "doc1"


class TestSubscriptionTools:
    """Test subscription tool functions."""
    
    @pytest.mark.asyncio
    async def test_subscribe_changes(self, mock_dataset):
        """Test subscribe_changes tool."""
        params = SubscribeChangesParams(
            resource_type="documents",
            filters={"collection_id": "test"},
            options={"polling_interval": 10}
        )
        
        result = await subscribe_changes(params, mock_dataset)
        
        assert "subscription_id" in result
        assert result["polling_interval"] == 10
        assert "poll_token" in result
        
    @pytest.mark.asyncio
    async def test_poll_changes(self, mock_dataset):
        """Test poll_changes tool."""
        # First create a subscription
        sub_params = SubscribeChangesParams(resource_type="all")
        sub_result = await subscribe_changes(sub_params, mock_dataset)
        
        # Then poll it
        poll_params = PollChangesParams(
            subscription_id=sub_result["subscription_id"],
            poll_token=sub_result["poll_token"],
            timeout=0
        )
        
        result = await poll_changes(poll_params, mock_dataset)
        
        assert "changes" in result
        assert "poll_token" in result
        assert "has_more" in result
        assert result["subscription_active"] is True
        
    @pytest.mark.asyncio
    async def test_unsubscribe(self, mock_dataset):
        """Test unsubscribe tool."""
        # Create subscription
        sub_params = SubscribeChangesParams(resource_type="all")
        sub_result = await subscribe_changes(sub_params, mock_dataset)
        
        # Unsubscribe
        unsub_params = UnsubscribeParams(
            subscription_id=sub_result["subscription_id"]
        )
        
        result = await unsubscribe(unsub_params, mock_dataset)
        
        assert result["cancelled"] is True
        assert result["final_poll_token"] is not None
        
    @pytest.mark.asyncio
    async def test_get_subscriptions(self, mock_dataset):
        """Test get_subscriptions tool."""
        # Create some subscriptions
        await subscribe_changes(
            SubscribeChangesParams(resource_type="documents"),
            mock_dataset
        )
        await subscribe_changes(
            SubscribeChangesParams(resource_type="collections"),
            mock_dataset
        )
        
        # Get all subscriptions
        params = GetSubscriptionsParams()
        result = await get_subscriptions(params, mock_dataset)
        
        assert result["total_count"] == 2
        assert len(result["subscriptions"]) == 2
        
        # Filter by type
        params = GetSubscriptionsParams(resource_type="documents")
        result = await get_subscriptions(params, mock_dataset)
        
        assert result["total_count"] == 1
        assert result["subscriptions"][0]["resource_type"] == "documents"
        
    @pytest.mark.asyncio
    async def test_subscription_lifecycle(self, mock_dataset):
        """Test complete subscription lifecycle."""
        # 1. Create subscription
        sub_params = SubscribeChangesParams(
            resource_type="all",
            options={"include_data": True}
        )
        sub_result = await subscribe_changes(sub_params, mock_dataset)
        sub_id = sub_result["subscription_id"]
        
        # 2. Poll for changes (should be empty)
        poll_params = PollChangesParams(
            subscription_id=sub_id,
            timeout=0
        )
        poll_result = await poll_changes(poll_params, mock_dataset)
        assert len(poll_result["changes"]) == 0
        
        # 3. List subscriptions
        list_params = GetSubscriptionsParams()
        list_result = await get_subscriptions(list_params, mock_dataset)
        assert list_result["total_count"] == 1
        
        # 4. Unsubscribe
        unsub_params = UnsubscribeParams(subscription_id=sub_id)
        unsub_result = await unsubscribe(unsub_params, mock_dataset)
        assert unsub_result["cancelled"] is True
        
        # 5. Poll should show inactive
        final_poll = await poll_changes(poll_params, mock_dataset)
        assert final_poll["subscription_active"] is False