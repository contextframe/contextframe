"""Authentication components for MCP server."""

import hashlib
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set

from contextframe.mcp.errors import MCPError


class AuthenticationError(MCPError):
    """Authentication failed error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(code=-32001, message=message)


@dataclass
class SecurityContext:
    """Security context for authenticated requests."""
    
    # Authentication info
    authenticated: bool = False
    auth_method: Optional[str] = None  # "api_key", "oauth", "jwt"
    
    # Principal identity
    principal_id: Optional[str] = None  # User/agent ID
    principal_type: Optional[str] = None  # "user", "agent", "service"
    principal_name: Optional[str] = None
    
    # Permissions and roles
    permissions: Set[str] = None
    roles: Set[str] = None
    
    # Session info
    session_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    # Additional claims/attributes
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = set()
        if self.roles is None:
            self.roles = set()
        if self.attributes is None:
            self.attributes = {}
    
    def has_permission(self, permission: str) -> bool:
        """Check if context has a specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Check if context has a specific role."""
        return role in self.roles
    
    def is_expired(self) -> bool:
        """Check if the security context has expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at


class AuthProvider(ABC):
    """Base class for authentication providers."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate using the provided credentials.
        
        Args:
            credentials: Provider-specific credentials
            
        Returns:
            SecurityContext if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_auth_method(self) -> str:
        """Get the authentication method name."""
        pass


class APIKeyAuth(AuthProvider):
    """API key authentication provider."""
    
    def __init__(self, api_keys: Dict[str, Dict[str, Any]] = None):
        """Initialize API key auth provider.
        
        Args:
            api_keys: Mapping of API key -> metadata
                     Metadata should include:
                     - principal_id: ID of the principal
                     - principal_name: Name of the principal
                     - permissions: Set of permissions
                     - roles: Set of roles
                     - expires_at: Optional expiration datetime
        """
        self.api_keys = api_keys or {}
        # Hash API keys for secure storage
        self._hashed_keys = {
            self._hash_key(key): metadata
            for key, metadata in self.api_keys.items()
        }
    
    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure comparison."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def authenticate(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate using API key."""
        api_key = credentials.get("api_key")
        if not api_key:
            raise AuthenticationError("Missing API key")
        
        # Hash the provided key
        hashed_key = self._hash_key(api_key)
        
        # Look up key metadata
        metadata = self._hashed_keys.get(hashed_key)
        if not metadata:
            raise AuthenticationError("Invalid API key")
        
        # Check expiration
        expires_at = metadata.get("expires_at")
        if expires_at and datetime.now(timezone.utc) > expires_at:
            raise AuthenticationError("API key expired")
        
        # Build security context
        return SecurityContext(
            authenticated=True,
            auth_method="api_key",
            principal_id=metadata.get("principal_id"),
            principal_type=metadata.get("principal_type", "agent"),
            principal_name=metadata.get("principal_name"),
            permissions=set(metadata.get("permissions", [])),
            roles=set(metadata.get("roles", [])),
            expires_at=expires_at,
            attributes=metadata.get("attributes", {})
        )
    
    def get_auth_method(self) -> str:
        """Get authentication method name."""
        return "api_key"
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)


class MultiAuthProvider(AuthProvider):
    """Combines multiple authentication providers."""
    
    def __init__(self, providers: list[AuthProvider]):
        """Initialize with multiple providers.
        
        Args:
            providers: List of auth providers to try in order
        """
        self.providers = providers
    
    async def authenticate(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Try each provider in order until one succeeds."""
        errors = []
        
        for provider in self.providers:
            try:
                return await provider.authenticate(credentials)
            except AuthenticationError as e:
                errors.append(f"{provider.get_auth_method()}: {str(e)}")
                continue
        
        # All providers failed
        raise AuthenticationError(
            f"All authentication methods failed: {'; '.join(errors)}"
        )
    
    def get_auth_method(self) -> str:
        """Get authentication method name."""
        methods = [p.get_auth_method() for p in self.providers]
        return f"multi[{','.join(methods)}]"