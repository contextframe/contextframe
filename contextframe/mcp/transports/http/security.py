"""Security features for HTTP transport including CORS and rate limiting."""

import asyncio
import logging
import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst: int = 10,
        cleanup_interval: int = 300,  # 5 minutes
    ):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.cleanup_interval = cleanup_interval

        # Token buckets for each client
        self._buckets: dict[str, TokenBucket] = {}
        self._last_cleanup = time.time()
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has available tokens.

        Args:
            client_id: Unique identifier for the client

        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            # Periodic cleanup of old buckets
            current_time = time.time()
            if current_time - self._last_cleanup > self.cleanup_interval:
                self._cleanup_buckets()
                self._last_cleanup = current_time

            # Get or create bucket for client
            if client_id not in self._buckets:
                self._buckets[client_id] = TokenBucket(
                    capacity=self.burst, refill_rate=self.requests_per_minute / 60.0
                )

            bucket = self._buckets[client_id]
            return bucket.consume()

    def _cleanup_buckets(self) -> None:
        """Remove inactive token buckets."""
        current_time = time.time()
        inactive_threshold = 600  # 10 minutes

        to_remove = []
        for client_id, bucket in self._buckets.items():
            if current_time - bucket.last_update > inactive_threshold:
                to_remove.append(client_id)

        for client_id in to_remove:
            del self._buckets[client_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive rate limit buckets")

    async def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        async with self._lock:
            return {
                "active_buckets": len(self._buckets),
                "requests_per_minute": self.requests_per_minute,
                "burst_size": self.burst,
            }


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        current_time = time.time()

        # Refill tokens based on elapsed time
        elapsed = current_time - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = current_time

        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter,
        key_func: callable | None = None,
        excluded_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.key_func = key_func or self._default_key_func
        self.excluded_paths = set(excluded_paths or ["/health", "/ready", "/metrics"])

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Get client identifier
        client_id = await self.key_func(request)

        # Check rate limit
        if not await self.rate_limiter.check_rate_limit(client_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_minute),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            self.rate_limiter.requests_per_minute
        )
        response.headers["X-RateLimit-Burst"] = str(self.rate_limiter.burst)

        return response

    async def _default_key_func(self, request: Request) -> str:
        """Default function to extract client identifier from request."""
        # Try to get authenticated user ID
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.get('id', 'unknown')}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"


class SecurityConfig:
    """Security configuration for HTTP transport."""

    def __init__(
        self,
        cors_origins: list[str] = None,
        cors_credentials: bool = True,
        cors_methods: list[str] = None,
        cors_headers: list[str] = None,
        rate_limit_enabled: bool = True,
        rate_limit_requests: int = 60,
        rate_limit_burst: int = 10,
        ssl_enabled: bool = False,
        ssl_cert: str | None = None,
        ssl_key: str | None = None,
    ):
        self.cors_origins = cors_origins or ["*"]
        self.cors_credentials = cors_credentials
        self.cors_methods = cors_methods or ["*"]
        self.cors_headers = cors_headers or ["*"]
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_burst = rate_limit_burst
        self.ssl_enabled = ssl_enabled
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key

    def apply_to_app(self, app) -> None:
        """Apply security configuration to FastAPI app."""
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins,
            allow_credentials=self.cors_credentials,
            allow_methods=self.cors_methods,
            allow_headers=self.cors_headers,
        )

        # Add rate limiting if enabled
        if self.rate_limit_enabled:
            rate_limiter = RateLimiter(
                requests_per_minute=self.rate_limit_requests,
                burst=self.rate_limit_burst,
            )
            app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

        logger.info("Security configuration applied to app")

    def get_uvicorn_config(self) -> dict[str, Any]:
        """Get Uvicorn SSL configuration if enabled."""
        config = {}

        if self.ssl_enabled:
            if not self.ssl_cert or not self.ssl_key:
                raise ValueError("SSL enabled but cert/key not provided")

            config.update(
                {
                    "ssl_keyfile": self.ssl_key,
                    "ssl_certfile": self.ssl_cert,
                }
            )

        return config


# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Add CSP for API endpoints
    if request.url.path.startswith("/mcp/"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none';"
        )

    return response
