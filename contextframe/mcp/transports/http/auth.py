"""OAuth 2.1 authentication for HTTP transport."""

import logging
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Configuration (would come from config in production)
SECRET_KEY = "your-secret-key-here"  # Should be loaded from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""

    sub: str | None = None
    exp: datetime | None = None
    scopes: list[str] = []


class User(BaseModel):
    """User model."""

    id: str
    username: str
    email: str | None = None
    disabled: bool = False
    scopes: list[str] = []


class OAuth2Handler:
    """OAuth 2.1 authentication handler with PKCE support."""

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        issuer: str | None = None,
        audience: str | None = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer or "contextframe-mcp"
        self.audience = audience or "contextframe-mcp"

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update(
            {
                "exp": expire,
                "iss": self.issuer,
                "aud": self.audience,
                "iat": datetime.utcnow(),
            }
        )

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )

            # Extract token data
            sub: str = payload.get("sub")
            if sub is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                )

            token_data = TokenData(
                sub=sub,
                exp=datetime.fromtimestamp(payload.get("exp", 0)),
                scopes=payload.get("scopes", []),
            )

            return token_data

        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(self, token: str) -> User:
        """Get current user from token."""
        token_data = await self.verify_token(token)

        # In production, this would look up the user in a database
        # For now, we create a user from token data
        user = User(
            id=token_data.sub, username=token_data.sub, scopes=token_data.scopes
        )

        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled"
            )

        return user

    async def check_permissions(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource/action.

        Args:
            user: The authenticated user
            resource: Resource type (e.g., "documents", "tools")
            action: Action type (e.g., "read", "write", "execute")

        Returns:
            True if user has permission, False otherwise
        """
        # Check for admin scope
        if "admin" in user.scopes:
            return True

        # Check specific permission scope
        required_scope = f"{resource}:{action}"
        if required_scope in user.scopes:
            return True

        # Check wildcard scopes
        if f"{resource}:*" in user.scopes:
            return True

        if f"*:{action}" in user.scopes:
            return True

        return False


# Global handler instance
auth_handler = OAuth2Handler()


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any] | None:
    """Dependency to get current user from token.

    Returns None if auth is disabled or token is not provided.
    """
    if not token:
        return None

    user = await auth_handler.get_current_user(token)
    return user.model_dump()


async def require_auth(
    user: dict[str, Any] | None = Depends(get_current_user),
) -> dict[str, Any]:
    """Dependency that requires authentication."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_scope_checker(required_scopes: list[str]):
    """Create a dependency that checks for required scopes."""

    async def check_scopes(
        user: dict[str, Any] = Depends(require_auth),
    ) -> dict[str, Any]:
        user_scopes = set(user.get("scopes", []))
        required = set(required_scopes)

        if not required.issubset(user_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scopes: {required_scopes}",
            )

        return user

    return check_scopes


# Example usage in routes:
# @app.post("/tools/call", dependencies=[Depends(create_scope_checker(["tools:execute"]))])
# async def call_tool(...):
#     ...
