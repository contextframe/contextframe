"""Rate limiting for MCP server."""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from contextframe.mcp.errors import MCPError


class RateLimitExceeded(MCPError):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(code=-32003, message=message)
        self.retry_after = retry_after


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    
    # Global limits
    global_requests_per_minute: int = 600
    global_burst_size: int = 100
    
    # Per-client limits
    client_requests_per_minute: int = 60
    client_burst_size: int = 10
    
    # Per-operation limits
    operation_limits: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    # Format: {"operation": (requests_per_minute, burst_size)}
    
    # Advanced settings
    cleanup_interval: int = 60  # seconds
    use_sliding_window: bool = True
    track_by: str = "principal_id"  # or "ip_address"
    
    def __post_init__(self):
        # Set default operation limits
        if not self.operation_limits:
            self.operation_limits = {
                # Expensive operations have lower limits
                "tools/call": (30, 5),
                "batch/*": (10, 2),
                "export/*": (5, 1),
                
                # Read operations have higher limits
                "resources/read": (120, 20),
                "resources/list": (120, 20),
                
                # Monitoring operations
                "monitoring/*": (60, 10),
            }


class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> Tuple[bool, Optional[float]]:
        """Try to consume tokens.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (success, wait_time_seconds)
        """
        async with self._lock:
            # Refill tokens based on elapsed time
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, None
            else:
                # Calculate wait time
                deficit = tokens - self.tokens
                wait_time = deficit / self.refill_rate
                return False, wait_time
    
    async def reset(self):
        """Reset bucket to full capacity."""
        async with self._lock:
            self.tokens = float(self.capacity)
            self.last_refill = time.monotonic()


class SlidingWindowCounter:
    """Sliding window counter for rate limiting."""
    
    def __init__(self, window_size: int, max_requests: int):
        """Initialize sliding window counter.
        
        Args:
            window_size: Window size in seconds
            max_requests: Maximum requests in window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def add_request(self) -> Tuple[bool, Optional[float]]:
        """Add a request and check if within limit.
        
        Returns:
            Tuple of (allowed, wait_time_seconds)
        """
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside window
            cutoff = now - self.window_size
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            # Check if we're at limit
            if len(self.requests) >= self.max_requests:
                # Calculate when oldest request expires
                oldest = self.requests[0]
                wait_time = oldest + self.window_size - now
                return False, wait_time
            
            # Add request
            self.requests.append(now)
            return True, None
    
    async def reset(self):
        """Reset counter."""
        async with self._lock:
            self.requests.clear()


class RateLimiter:
    """Rate limiter for MCP server."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        
        # Global rate limiter
        self.global_limiter = TokenBucket(
            capacity=config.global_burst_size,
            refill_rate=config.global_requests_per_minute / 60.0
        )
        
        # Per-client limiters
        self.client_limiters: Dict[str, Any] = {}
        
        # Per-operation limiters
        self.operation_limiters: Dict[str, Any] = {}
        
        # Initialize operation limiters
        for operation, (rpm, burst) in config.operation_limits.items():
            if config.use_sliding_window:
                self.operation_limiters[operation] = SlidingWindowCounter(
                    window_size=60,
                    max_requests=rpm
                )
            else:
                self.operation_limiters[operation] = TokenBucket(
                    capacity=burst,
                    refill_rate=rpm / 60.0
                )
        
        # Cleanup task
        self._cleanup_task = None
    
    async def start(self):
        """Start the rate limiter."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the rate limiter."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old limiters."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                # Clean up inactive client limiters
                # This is a simplified version - in production you'd track
                # last access time and remove old entries
                
            except asyncio.CancelledError:
                break
    
    def _get_client_limiter(self, client_id: str) -> Any:
        """Get or create client limiter."""
        if client_id not in self.client_limiters:
            if self.config.use_sliding_window:
                self.client_limiters[client_id] = SlidingWindowCounter(
                    window_size=60,
                    max_requests=self.config.client_requests_per_minute
                )
            else:
                self.client_limiters[client_id] = TokenBucket(
                    capacity=self.config.client_burst_size,
                    refill_rate=self.config.client_requests_per_minute / 60.0
                )
        
        return self.client_limiters[client_id]
    
    def _match_operation(self, operation: str) -> Optional[str]:
        """Find matching operation pattern."""
        # Exact match
        if operation in self.operation_limiters:
            return operation
        
        # Wildcard match
        for pattern in self.operation_limiters:
            if pattern.endswith("/*"):
                prefix = pattern[:-2]
                if operation.startswith(prefix):
                    return pattern
        
        return None
    
    async def check_rate_limit(
        self,
        client_id: Optional[str] = None,
        operation: Optional[str] = None,
        tokens: int = 1
    ) -> None:
        """Check rate limits, raising error if exceeded.
        
        Args:
            client_id: Client identifier
            operation: Operation being performed
            tokens: Number of tokens to consume
            
        Raises:
            RateLimitExceeded: If any rate limit is exceeded
        """
        retry_after = None
        
        # Check global limit
        if isinstance(self.global_limiter, TokenBucket):
            allowed, wait_time = await self.global_limiter.consume(tokens)
        else:
            allowed, wait_time = await self.global_limiter.add_request()
        
        if not allowed:
            retry_after = int(wait_time + 1) if wait_time else 60
            raise RateLimitExceeded(
                "Global rate limit exceeded",
                retry_after=retry_after
            )
        
        # Check client limit
        if client_id:
            client_limiter = self._get_client_limiter(client_id)
            
            if isinstance(client_limiter, TokenBucket):
                allowed, wait_time = await client_limiter.consume(tokens)
            else:
                allowed, wait_time = await client_limiter.add_request()
            
            if not allowed:
                retry_after = int(wait_time + 1) if wait_time else 60
                raise RateLimitExceeded(
                    f"Client rate limit exceeded for {client_id}",
                    retry_after=retry_after
                )
        
        # Check operation limit
        if operation:
            pattern = self._match_operation(operation)
            if pattern:
                op_limiter = self.operation_limiters[pattern]
                
                if isinstance(op_limiter, TokenBucket):
                    allowed, wait_time = await op_limiter.consume(tokens)
                else:
                    allowed, wait_time = await op_limiter.add_request()
                
                if not allowed:
                    retry_after = int(wait_time + 1) if wait_time else 60
                    raise RateLimitExceeded(
                        f"Operation rate limit exceeded for {operation}",
                        retry_after=retry_after
                    )
    
    async def reset_client_limit(self, client_id: str):
        """Reset rate limit for a specific client."""
        if client_id in self.client_limiters:
            await self.client_limiters[client_id].reset()
    
    async def reset_all_limits(self):
        """Reset all rate limits."""
        await self.global_limiter.reset()
        
        for limiter in self.client_limiters.values():
            await limiter.reset()
        
        for limiter in self.operation_limiters.values():
            await limiter.reset()
    
    def get_limit_status(
        self,
        client_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get current rate limit status.
        
        Returns:
            Dictionary with limit information
        """
        status = {
            "global": {
                "requests_per_minute": self.config.global_requests_per_minute,
                "burst_size": self.config.global_burst_size,
            }
        }
        
        if client_id:
            status["client"] = {
                "requests_per_minute": self.config.client_requests_per_minute,
                "burst_size": self.config.client_burst_size,
            }
        
        if operation:
            pattern = self._match_operation(operation)
            if pattern:
                rpm, burst = self.config.operation_limits[pattern]
                status["operation"] = {
                    "pattern": pattern,
                    "requests_per_minute": rpm,
                    "burst_size": burst,
                }
        
        return status