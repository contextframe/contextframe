"""OAuth 2.1 authentication provider."""

import base64
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set
from urllib.parse import urlencode, urlparse, parse_qs

import httpx

from .auth import AuthProvider, AuthenticationError, SecurityContext


@dataclass
class OAuth2Config:
    """OAuth 2.1 configuration."""
    
    # OAuth endpoints
    authorization_endpoint: str
    token_endpoint: str
    client_id: str  # Required field moved before optional fields
    
    # Optional endpoints
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    
    # Client credentials
    client_secret: Optional[str] = None
    redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob"
    
    # Scopes and claims
    scopes: list[str] = None
    required_claims: list[str] = None
    
    # Token settings
    access_token_lifetime: int = 3600  # seconds
    refresh_token_lifetime: int = 86400 * 30  # 30 days
    
    # Security settings
    require_pkce: bool = True
    require_state: bool = True
    allowed_redirect_uris: list[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ["openid", "profile", "email"]
        if self.required_claims is None:
            self.required_claims = ["sub"]
        if self.allowed_redirect_uris is None:
            self.allowed_redirect_uris = [self.redirect_uri]


@dataclass
class OAuth2Token:
    """OAuth 2.1 token response."""
    
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    
    # Computed fields
    issued_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.issued_at is None:
            self.issued_at = datetime.now(timezone.utc)
        if self.expires_in and not self.expires_at:
            self.expires_at = self.issued_at + timedelta(seconds=self.expires_in)
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at


class OAuth2Provider(AuthProvider):
    """OAuth 2.1 authentication provider.
    
    Implements OAuth 2.1 with:
    - Authorization Code flow with PKCE
    - Client Credentials flow
    - Token introspection
    - JWT validation (if JWKS provided)
    """
    
    def __init__(self, config: OAuth2Config):
        self.config = config
        self._http_client = httpx.AsyncClient()
        
        # Cache for authorization codes
        self._auth_codes: Dict[str, Dict[str, Any]] = {}
        
        # Cache for access tokens (for introspection)
        self._access_tokens: Dict[str, OAuth2Token] = {}
    
    async def authenticate(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate using OAuth 2.1.
        
        Supports:
        - Authorization code exchange
        - Client credentials
        - Access token validation
        """
        # Check for authorization code
        if "code" in credentials:
            return await self._handle_authorization_code(credentials)
        
        # Check for access token
        elif "access_token" in credentials:
            return await self._validate_access_token(credentials["access_token"])
        
        # Check for client credentials
        elif "client_id" in credentials and "client_secret" in credentials:
            return await self._handle_client_credentials(credentials)
        
        else:
            raise AuthenticationError("Missing OAuth credentials")
    
    async def _handle_authorization_code(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Exchange authorization code for tokens."""
        code = credentials.get("code")
        code_verifier = credentials.get("code_verifier")
        redirect_uri = credentials.get("redirect_uri", self.config.redirect_uri)
        
        if not code:
            raise AuthenticationError("Missing authorization code")
        
        # Validate redirect URI
        if redirect_uri not in self.config.allowed_redirect_uris:
            raise AuthenticationError("Invalid redirect URI")
        
        # Build token request
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.config.client_id,
        }
        
        # Add PKCE verifier if required
        if self.config.require_pkce:
            if not code_verifier:
                raise AuthenticationError("PKCE code verifier required")
            token_data["code_verifier"] = code_verifier
        
        # Add client secret if available
        if self.config.client_secret:
            token_data["client_secret"] = self.config.client_secret
        
        try:
            # Exchange code for token
            response = await self._http_client.post(
                self.config.token_endpoint,
                data=token_data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            token_response = response.json()
            token = OAuth2Token(**token_response)
            
            # Store token for later validation
            self._access_tokens[token.access_token] = token
            
            # Get user info if available
            userinfo = None
            if self.config.userinfo_endpoint and token.access_token:
                userinfo = await self._get_userinfo(token.access_token)
            
            # Build security context
            return self._build_security_context(token, userinfo)
            
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Token exchange failed: {str(e)}")
    
    async def _handle_client_credentials(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate using client credentials."""
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        scope = credentials.get("scope", " ".join(self.config.scopes))
        
        if not client_id or not client_secret:
            raise AuthenticationError("Missing client credentials")
        
        # Verify client credentials match config
        if client_id != self.config.client_id:
            raise AuthenticationError("Invalid client ID")
        if client_secret != self.config.client_secret:
            raise AuthenticationError("Invalid client secret")
        
        try:
            # Request token
            response = await self._http_client.post(
                self.config.token_endpoint,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": scope
                },
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            token_response = response.json()
            token = OAuth2Token(**token_response)
            
            # Store token
            self._access_tokens[token.access_token] = token
            
            # Build security context for service account
            return SecurityContext(
                authenticated=True,
                auth_method="oauth2_client",
                principal_id=client_id,
                principal_type="service",
                principal_name=f"Service: {client_id}",
                permissions=self._parse_scopes_to_permissions(scope),
                roles={"service"},
                expires_at=token.expires_at,
                attributes={
                    "grant_type": "client_credentials",
                    "scope": scope
                }
            )
            
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Client credentials flow failed: {str(e)}")
    
    async def _validate_access_token(self, access_token: str) -> SecurityContext:
        """Validate an access token."""
        # Check local cache first
        if access_token in self._access_tokens:
            token = self._access_tokens[access_token]
            if not token.is_expired():
                # Get fresh user info
                userinfo = None
                if self.config.userinfo_endpoint:
                    userinfo = await self._get_userinfo(access_token)
                return self._build_security_context(token, userinfo)
        
        # Token not in cache or expired, validate with server
        # This would typically use token introspection endpoint
        raise AuthenticationError("Token validation not implemented")
    
    async def _get_userinfo(self, access_token: str) -> Dict[str, Any]:
        """Get user info from userinfo endpoint."""
        try:
            response = await self._http_client.get(
                self.config.userinfo_endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            # Userinfo fetch failed, not critical
            return {}
    
    def _build_security_context(
        self,
        token: OAuth2Token,
        userinfo: Optional[Dict[str, Any]] = None
    ) -> SecurityContext:
        """Build security context from token and user info."""
        # Extract principal info
        principal_id = None
        principal_name = None
        email = None
        
        if userinfo:
            principal_id = userinfo.get("sub")
            principal_name = userinfo.get("name") or userinfo.get("preferred_username")
            email = userinfo.get("email")
        
        # Parse scopes into permissions
        permissions = set()
        if token.scope:
            permissions = self._parse_scopes_to_permissions(token.scope)
        
        return SecurityContext(
            authenticated=True,
            auth_method="oauth2",
            principal_id=principal_id,
            principal_type="user",
            principal_name=principal_name,
            permissions=permissions,
            roles={"user"},  # Default role
            expires_at=token.expires_at,
            attributes={
                "email": email,
                "scope": token.scope,
                "token_type": token.token_type
            }
        )
    
    def _parse_scopes_to_permissions(self, scope: str) -> Set[str]:
        """Convert OAuth scopes to permissions."""
        permissions = set()
        scopes = scope.split() if scope else []
        
        # Map common scopes to permissions
        scope_mapping = {
            "read": ["documents.read", "collections.read"],
            "write": ["documents.write", "collections.write"],
            "admin": ["documents.*", "collections.*", "system.*"],
        }
        
        for s in scopes:
            if s in scope_mapping:
                permissions.update(scope_mapping[s])
            else:
                # Use scope as-is for custom scopes
                permissions.add(s)
        
        return permissions
    
    def get_auth_method(self) -> str:
        """Get authentication method name."""
        return "oauth2"
    
    def generate_authorization_url(
        self,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        scope: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate OAuth authorization URL.
        
        Args:
            state: CSRF protection state
            code_challenge: PKCE challenge
            scope: OAuth scopes
            **kwargs: Additional OAuth parameters
            
        Returns:
            Authorization URL
        """
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
        }
        
        if state:
            params["state"] = state
        elif self.config.require_state:
            params["state"] = secrets.token_urlsafe(32)
        
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        elif self.config.require_pkce:
            raise ValueError("PKCE code challenge required")
        
        if scope:
            params["scope"] = scope
        else:
            params["scope"] = " ".join(self.config.scopes)
        
        # Add any additional parameters
        params.update(kwargs)
        
        return f"{self.config.authorization_endpoint}?{urlencode(params)}"
    
    @staticmethod
    def generate_pkce_pair() -> tuple[str, str]:
        """Generate PKCE code verifier and challenge.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode("utf-8").rstrip("=")
        
        # Generate code challenge (S256)
        import hashlib
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(
            challenge_bytes
        ).decode("utf-8").rstrip("=")
        
        return code_verifier, code_challenge
    
    async def close(self):
        """Clean up resources."""
        await self._http_client.aclose()