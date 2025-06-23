"""JWT authentication and token handling."""

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .auth import AuthProvider, AuthenticationError, SecurityContext


@dataclass
class JWTConfig:
    """JWT configuration."""
    
    # Signing configuration
    algorithm: str = "RS256"  # RS256, HS256, etc.
    secret_key: Optional[str] = None  # For HMAC algorithms
    private_key: Optional[str] = None  # For RSA/ECDSA
    public_key: Optional[str] = None  # For RSA/ECDSA
    
    # Token settings
    issuer: str = "contextframe-mcp"
    audience: Optional[str] = None
    token_lifetime: int = 3600  # seconds
    refresh_token_lifetime: int = 86400 * 7  # 7 days
    
    # Validation settings
    verify_signature: bool = True
    verify_exp: bool = True
    verify_nbf: bool = True
    verify_iat: bool = True
    verify_aud: bool = True
    verify_iss: bool = True
    require_exp: bool = True
    require_nbf: bool = False
    require_iat: bool = True
    
    # Claims mapping
    principal_id_claim: str = "sub"
    principal_name_claim: str = "name"
    principal_type_claim: str = "type"
    permissions_claim: str = "permissions"
    roles_claim: str = "roles"


class JWTHandler(AuthProvider):
    """JWT token handler for authentication."""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        
        # Initialize keys if not provided
        if self.config.algorithm.startswith("RS") and not self.config.private_key:
            # Generate RSA key pair for testing
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.config.private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            self.config.public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
    
    async def authenticate(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate using JWT token."""
        token = credentials.get("token") or credentials.get("jwt")
        if not token:
            raise AuthenticationError("Missing JWT token")
        
        try:
            # Decode and verify token
            payload = self._verify_token(token)
            
            # Build security context from claims
            return self._build_security_context(payload)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("JWT token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid JWT token: {str(e)}")
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        # Determine verification key
        if self.config.algorithm.startswith("HS"):
            # HMAC algorithms use secret key
            key = self.config.secret_key
        else:
            # RSA/ECDSA algorithms use public key
            key = self.config.public_key
        
        if not key:
            raise AuthenticationError("Missing verification key")
        
        # Build verification options
        options = {
            "verify_signature": self.config.verify_signature,
            "verify_exp": self.config.verify_exp,
            "verify_nbf": self.config.verify_nbf,
            "verify_iat": self.config.verify_iat,
            "verify_aud": self.config.verify_aud if self.config.audience else False,
            "verify_iss": self.config.verify_iss,
            "require_exp": self.config.require_exp,
            "require_nbf": self.config.require_nbf,
            "require_iat": self.config.require_iat,
        }
        
        # Decode token
        payload = jwt.decode(
            token,
            key,
            algorithms=[self.config.algorithm],
            options=options,
            audience=self.config.audience,
            issuer=self.config.issuer
        )
        
        return payload
    
    def _build_security_context(self, payload: Dict[str, Any]) -> SecurityContext:
        """Build security context from JWT claims."""
        # Extract principal information
        principal_id = payload.get(self.config.principal_id_claim)
        principal_name = payload.get(self.config.principal_name_claim)
        principal_type = payload.get(self.config.principal_type_claim, "user")
        
        # Extract permissions and roles
        permissions = set(payload.get(self.config.permissions_claim, []))
        roles = set(payload.get(self.config.roles_claim, []))
        
        # Calculate expiration
        expires_at = None
        if "exp" in payload:
            expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Extract additional claims
        standard_claims = {
            "sub", "name", "type", "permissions", "roles",
            "exp", "nbf", "iat", "iss", "aud", "jti"
        }
        attributes = {
            k: v for k, v in payload.items()
            if k not in standard_claims
        }
        
        return SecurityContext(
            authenticated=True,
            auth_method="jwt",
            principal_id=principal_id,
            principal_type=principal_type,
            principal_name=principal_name,
            permissions=permissions,
            roles=roles,
            session_id=payload.get("jti"),  # JWT ID as session ID
            expires_at=expires_at,
            attributes=attributes
        )
    
    def get_auth_method(self) -> str:
        """Get authentication method name."""
        return "jwt"
    
    def create_token(
        self,
        principal_id: str,
        principal_name: Optional[str] = None,
        principal_type: str = "user",
        permissions: Optional[Set[str]] = None,
        roles: Optional[Set[str]] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
        lifetime: Optional[int] = None
    ) -> str:
        """Create a new JWT token.
        
        Args:
            principal_id: Subject/principal ID
            principal_name: Human-readable name
            principal_type: Type of principal (user, agent, service)
            permissions: Set of permissions
            roles: Set of roles
            additional_claims: Extra claims to include
            lifetime: Token lifetime in seconds
            
        Returns:
            Signed JWT token
        """
        now = datetime.now(timezone.utc)
        lifetime = lifetime or self.config.token_lifetime
        
        # Build payload
        payload = {
            # Standard claims
            "iss": self.config.issuer,
            "sub": principal_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=lifetime)).timestamp()),
            
            # Custom claims
            self.config.principal_name_claim: principal_name,
            self.config.principal_type_claim: principal_type,
            self.config.permissions_claim: list(permissions or []),
            self.config.roles_claim: list(roles or []),
        }
        
        # Add audience if configured
        if self.config.audience:
            payload["aud"] = self.config.audience
        
        # Add additional claims
        if additional_claims:
            payload.update(additional_claims)
        
        # Determine signing key
        if self.config.algorithm.startswith("HS"):
            key = self.config.secret_key
        else:
            key = self.config.private_key
        
        if not key:
            raise ValueError("Missing signing key")
        
        # Create token
        token = jwt.encode(
            payload,
            key,
            algorithm=self.config.algorithm
        )
        
        return token
    
    def create_refresh_token(
        self,
        principal_id: str,
        token_id: str,
        lifetime: Optional[int] = None
    ) -> str:
        """Create a refresh token.
        
        Args:
            principal_id: Subject/principal ID
            token_id: ID of the access token this refreshes
            lifetime: Token lifetime in seconds
            
        Returns:
            Signed refresh token
        """
        lifetime = lifetime or self.config.refresh_token_lifetime
        
        payload = {
            "iss": self.config.issuer,
            "sub": principal_id,
            "iat": int(time.time()),
            "exp": int(time.time() + lifetime),
            "token_type": "refresh",
            "token_id": token_id,
        }
        
        # Determine signing key
        if self.config.algorithm.startswith("HS"):
            key = self.config.secret_key
        else:
            key = self.config.private_key
        
        return jwt.encode(payload, key, algorithm=self.config.algorithm)
    
    def decode_token_unsafe(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)."""
        return jwt.decode(token, options={"verify_signature": False})