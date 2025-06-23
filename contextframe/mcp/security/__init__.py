"""Security components for MCP server.

Provides authentication, authorization, rate limiting, and audit logging
for the MCP server to ensure secure access to ContextFrame datasets.
"""

from .audit import AuditLogger, AuditEvent
from .auth import (
    AuthenticationError,
    AuthProvider,
    APIKeyAuth,
    SecurityContext,
)
from .authorization import (
    AuthorizationError,
    Permission,
    Role,
    AccessControl,
)
from .integration import SecurityMiddleware, SecuredMessageHandler
from .jwt import JWTHandler, JWTConfig
from .oauth import OAuth2Provider, OAuth2Config
from .rate_limiting import (
    RateLimiter,
    RateLimitExceeded,
    RateLimitConfig,
)

__all__ = [
    # Authentication
    "AuthenticationError",
    "AuthProvider",
    "APIKeyAuth",
    "SecurityContext",
    # Authorization
    "AuthorizationError",
    "Permission",
    "Role",
    "AccessControl",
    # OAuth 2.1
    "OAuth2Provider",
    "OAuth2Config",
    # JWT
    "JWTHandler",
    "JWTConfig",
    # Rate Limiting
    "RateLimiter",
    "RateLimitExceeded",
    "RateLimitConfig",
    # Audit
    "AuditLogger",
    "AuditEvent",
    # Integration
    "SecurityMiddleware",
    "SecuredMessageHandler",
]