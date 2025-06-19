# Phase 3.4: Subscription System Implementation Plan

## Overview

Implement a transport-aware subscription system that allows clients to watch for dataset changes. Since Lance doesn't have built-in change notifications, we'll implement a polling-based system that works efficiently with both stdio and HTTP transports.

## Timeline
**Week 4 of Phase 3 Implementation (3-4 days)**

## Context and Constraints

### Lance Dataset Versioning
- **Version tracking**: Each write creates a new immutable version
- **No built-in subscriptions**: Must implement polling mechanism
- **Version comparison**: Can detect changes by comparing version numbers
- **Efficient access**: `checkout_version()` is optimized for version switching

### Transport Considerations
- **Stdio**: Return change tokens for client-side polling
- **HTTP**: Can use SSE for real-time updates (future)
- **Unified API**: Same subscription interface for both transports

## Architecture Design

### Core Components

```python
# Subscription Manager
class SubscriptionManager:
    """Manages all active subscriptions and change detection."""
    
    def __init__(self, dataset: FrameDataset):
        self.dataset = dataset
        self.subscriptions: Dict[str, SubscriptionState] = {}
        self._polling_task: Optional[asyncio.Task] = None
        self._change_queue: asyncio.Queue = asyncio.Queue()
    
    async def start(self):
        """Start the polling task."""
        self._polling_task = asyncio.create_task(self._poll_changes())
    
    async def create_subscription(
        self, 
        resource_type: str,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new subscription."""
        subscription_id = str(uuid4())
        # Implementation details...
        return subscription_id

# Subscription State
@dataclass
class SubscriptionState:
    id: str
    resource_type: str  # "documents", "collections", "all"
    filters: Dict[str, Any]
    created_at: datetime
    last_version: int
    last_poll_token: str
    change_buffer: List[Change]
    options: Dict[str, Any]  # polling_interval, batch_size, etc.

# Change Event
@dataclass
class Change:
    type: str  # "created", "updated", "deleted"
    resource_type: str
    resource_id: str
    version: int
    timestamp: datetime
    old_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
```

### Subscription Tools

#### 1. `subscribe_changes`
Creates a subscription to watch for dataset changes.

```python
async def subscribe_changes(params: SubscribeChangesParams) -> Dict[str, Any]:
    """
    Create a subscription to monitor dataset changes.
    
    Args:
        resource_type: Type to monitor ("documents", "collections", "all")
        filters: Optional filters (e.g., {"collection_id": "..."})
        options: Subscription options
            - polling_interval: Seconds between polls (default: 5)
            - include_data: Include full document data in changes
            - batch_size: Max changes per poll response
    
    Returns:
        subscription_id: Unique subscription identifier
        poll_token: Initial token for polling
        polling_interval: Recommended polling interval
    """
```

#### 2. `poll_changes`
Poll for changes since last check (stdio-friendly).

```python
async def poll_changes(params: PollChangesParams) -> Dict[str, Any]:
    """
    Poll for changes since the last poll.
    
    Args:
        subscription_id: Active subscription ID
        poll_token: Token from last poll (or None for first poll)
        timeout: Max seconds to wait for changes (long polling)
    
    Returns:
        changes: List of change events
        poll_token: Token for next poll
        has_more: Whether more changes are available
        subscription_active: Whether subscription is still valid
    """
```

#### 3. `unsubscribe`
Cancel an active subscription.

```python
async def unsubscribe(params: UnsubscribeParams) -> Dict[str, Any]:
    """
    Cancel an active subscription.
    
    Args:
        subscription_id: Subscription to cancel
        
    Returns:
        cancelled: Whether cancellation succeeded
        final_poll_token: Token to get any remaining changes
    """
```

#### 4. `get_subscriptions`
List all active subscriptions.

```python
async def get_subscriptions(params: GetSubscriptionsParams) -> Dict[str, Any]:
    """
    Get list of active subscriptions.
    
    Args:
        resource_type: Filter by resource type (optional)
        
    Returns:
        subscriptions: List of active subscriptions with details
        total_count: Total number of subscriptions
    """
```

## Implementation Strategy

### Phase 1: Core Infrastructure (Day 1)
1. Create `SubscriptionManager` class
2. Implement Lance version polling mechanism
3. Create change detection logic
4. Set up change event queue

### Phase 2: Change Detection (Day 2)
1. Implement efficient diff algorithm for documents
2. Add collection change detection
3. Create change event serialization
4. Implement filter matching

### Phase 3: Subscription Tools (Day 3)
1. Implement all 4 subscription tools
2. Add subscription persistence (for server restarts)
3. Create comprehensive tests
4. Add error handling and cleanup

### Phase 4: Transport Integration (Day 4)
1. Integrate with stdio transport (polling-based)
2. Prepare hooks for HTTP SSE (future)
3. Add performance optimizations
4. Documentation and examples

## Technical Challenges

### 1. Efficient Change Detection
```python
async def _detect_changes(
    self, 
    old_version: int, 
    new_version: int,
    filters: Dict[str, Any]
) -> List[Change]:
    """Detect changes between dataset versions."""
    # Challenge: Lance doesn't have built-in diff
    # Solution: Track document UUIDs and compare
    
    old_dataset = self.dataset.checkout_version(old_version)
    new_dataset = self.dataset.checkout_version(new_version)
    
    # Get all UUIDs from both versions
    old_uuids = set(self._get_all_uuids(old_dataset, filters))
    new_uuids = set(self._get_all_uuids(new_dataset, filters))
    
    # Detect changes
    created = new_uuids - old_uuids
    deleted = old_uuids - new_uuids
    potentially_updated = old_uuids & new_uuids
    
    # Check for actual updates (compare timestamps)
    changes = []
    for uuid in potentially_updated:
        if self._has_changed(uuid, old_dataset, new_dataset):
            changes.append(self._create_update_event(uuid))
    
    return changes
```

### 2. Subscription State Persistence
- Store subscription state in a dedicated Lance dataset
- Recover subscriptions after server restart
- Clean up expired subscriptions

### 3. Performance Optimization
- Cache frequently accessed version metadata
- Batch change detection for multiple subscriptions
- Implement smart polling intervals based on activity

## Testing Strategy

### Unit Tests
1. Test change detection accuracy
2. Test filter matching logic
3. Test subscription lifecycle
4. Test error handling

### Integration Tests
1. Test with concurrent modifications
2. Test subscription recovery after restart
3. Test with large datasets
4. Test transport-specific behavior

### Performance Tests
1. Measure polling overhead
2. Test with many active subscriptions
3. Benchmark change detection speed
4. Memory usage under load

## Success Criteria

- ✅ All 4 subscription tools working correctly
- ✅ Efficient change detection (<100ms for typical operations)
- ✅ Support for filtered subscriptions
- ✅ Graceful handling of missed changes
- ✅ Works identically with stdio transport
- ✅ Prepared for HTTP SSE integration
- ✅ Comprehensive test coverage (>90%)
- ✅ Clear documentation with examples

## Example Usage

### Stdio Client Example
```python
# Create subscription
result = await client.call_tool("subscribe_changes", {
    "resource_type": "documents",
    "filters": {"collection_id": "research-papers"},
    "options": {"polling_interval": 10}
})
subscription_id = result["subscription_id"]
poll_token = result["poll_token"]

# Poll for changes
while True:
    result = await client.call_tool("poll_changes", {
        "subscription_id": subscription_id,
        "poll_token": poll_token,
        "timeout": 30  # Long polling
    })
    
    for change in result["changes"]:
        print(f"{change['type']}: {change['resource_id']}")
    
    poll_token = result["poll_token"]
    if not result["subscription_active"]:
        break
    
    await asyncio.sleep(10)
```

## Next Steps

After Phase 3.4 completion:
1. Phase 3.5: Analytics Tools (leveraging change tracking)
2. Phase 3.6: Performance Tools
3. Phase 4: HTTP Transport with real SSE support