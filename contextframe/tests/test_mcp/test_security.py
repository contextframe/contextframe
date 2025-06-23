"""Test security components for MCP server."""

import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from contextframe.mcp.security.audit import (
    AuditConfig,
    AuditEvent,
    AuditEventType,
    AuditLogger,
)
from contextframe.mcp.security.auth import (
    APIKeyAuth,
    AuthenticationError,
    MultiAuthProvider,
    SecurityContext,
)
from contextframe.mcp.security.authorization import (
    AccessControl,
    AuthorizationError,
    Permission,
    ResourcePolicy,
    Role,
    STANDARD_ROLES,
)
from contextframe.mcp.security.jwt import JWTConfig, JWTHandler
from contextframe.mcp.security.oauth import OAuth2Config, OAuth2Provider
from contextframe.mcp.security.rate_limiting import (
    RateLimitConfig,
    RateLimiter,
    RateLimitExceeded,
)


class TestAPIKeyAuth:
    """Test API key authentication."""
    
    @pytest.fixture
    def api_keys(self):
        """Sample API keys."""
        return {
            "test-key-1": {
                "principal_id": "user-1",
                "principal_name": "Test User 1",
                "permissions": ["documents.read", "collections.read"],
                "roles": ["viewer"],
            },
            "test-key-2": {
                "principal_id": "service-1",
                "principal_type": "service",
                "principal_name": "Test Service",
                "permissions": ["documents.*", "collections.*"],
                "roles": ["admin"],
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
            },
        }
    
    @pytest.mark.asyncio
    async def test_api_key_authentication_success(self, api_keys):
        """Test successful API key authentication."""
        auth = APIKeyAuth(api_keys)
        
        context = await auth.authenticate({"api_key": "test-key-1"})
        
        assert context.authenticated
        assert context.auth_method == "api_key"
        assert context.principal_id == "user-1"
        assert context.principal_name == "Test User 1"
        assert "documents.read" in context.permissions
        assert "viewer" in context.roles
    
    @pytest.mark.asyncio
    async def test_api_key_authentication_failure(self, api_keys):
        """Test failed API key authentication."""
        auth = APIKeyAuth(api_keys)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth.authenticate({"api_key": "invalid-key"})
        
        assert "Invalid API key" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_api_key_expiration(self, api_keys):
        """Test expired API key rejection."""
        # Add expired key
        api_keys["expired-key"] = {
            "principal_id": "user-2",
            "expires_at": datetime.now(timezone.utc) - timedelta(days=1),
        }
        
        auth = APIKeyAuth(api_keys)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth.authenticate({"api_key": "expired-key"})
        
        assert "API key expired" in str(exc_info.value)
    
    def test_generate_api_key(self):
        """Test API key generation."""
        key1 = APIKeyAuth.generate_api_key()
        key2 = APIKeyAuth.generate_api_key()
        
        assert len(key1) > 20
        assert key1 != key2


class TestJWTHandler:
    """Test JWT authentication."""
    
    @pytest.fixture
    def jwt_config(self):
        """JWT configuration."""
        return JWTConfig(
            algorithm="HS256",
            secret_key="test-secret-key-for-testing-only",
            issuer="test-issuer",
            audience="test-audience",
            token_lifetime=3600,
        )
    
    @pytest.mark.asyncio
    async def test_jwt_create_and_verify(self, jwt_config):
        """Test JWT creation and verification."""
        handler = JWTHandler(jwt_config)
        
        # Create token
        token = handler.create_token(
            principal_id="user-123",
            principal_name="Test User",
            principal_type="user",
            permissions={"documents.read", "collections.read"},
            roles={"viewer"},
        )
        
        # Verify token
        context = await handler.authenticate({"token": token})
        
        assert context.authenticated
        assert context.auth_method == "jwt"
        assert context.principal_id == "user-123"
        assert context.principal_name == "Test User"
        assert "documents.read" in context.permissions
        assert "viewer" in context.roles
    
    @pytest.mark.asyncio
    async def test_jwt_expired_token(self, jwt_config):
        """Test expired JWT rejection."""
        jwt_config.token_lifetime = -1  # Immediate expiration
        handler = JWTHandler(jwt_config)
        
        token = handler.create_token(principal_id="user-123")
        
        with pytest.raises(AuthenticationError) as exc_info:
            await handler.authenticate({"token": token})
        
        assert "expired" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_jwt_invalid_signature(self, jwt_config):
        """Test JWT with invalid signature."""
        handler = JWTHandler(jwt_config)
        
        # Create token with different secret
        jwt_config.secret_key = "different-secret"
        bad_handler = JWTHandler(jwt_config)
        token = bad_handler.create_token(principal_id="user-123")
        
        with pytest.raises(AuthenticationError) as exc_info:
            await handler.authenticate({"token": token})
        
        assert "Invalid JWT token" in str(exc_info.value)


class TestOAuth2Provider:
    """Test OAuth 2.1 authentication."""
    
    @pytest.fixture
    def oauth_config(self):
        """OAuth configuration."""
        return OAuth2Config(
            authorization_endpoint="https://auth.example.com/authorize",
            token_endpoint="https://auth.example.com/token",
            userinfo_endpoint="https://auth.example.com/userinfo",
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/callback",
            scopes=["openid", "profile", "email"],
        )
    
    def test_generate_authorization_url(self, oauth_config):
        """Test authorization URL generation."""
        provider = OAuth2Provider(oauth_config)
        
        url = provider.generate_authorization_url(
            state="test-state",
            code_challenge="test-challenge",
        )
        
        assert oauth_config.authorization_endpoint in url
        assert "client_id=test-client-id" in url
        assert "state=test-state" in url
        assert "code_challenge=test-challenge" in url
    
    def test_generate_pkce_pair(self):
        """Test PKCE verifier and challenge generation."""
        verifier, challenge = OAuth2Provider.generate_pkce_pair()
        
        assert len(verifier) > 40
        assert len(challenge) > 40
        assert verifier != challenge


class TestAuthorization:
    """Test authorization and access control."""
    
    @pytest.fixture
    def security_context(self):
        """Sample security context."""
        return SecurityContext(
            authenticated=True,
            auth_method="api_key",
            principal_id="user-1",
            principal_type="user",
            permissions={"documents.read"},
            roles={"viewer"},
        )
    
    def test_role_permissions(self):
        """Test role permission checks."""
        viewer_role = STANDARD_ROLES["viewer"]
        admin_role = STANDARD_ROLES["admin"]
        
        assert viewer_role.has_permission(Permission.DOCUMENTS_READ)
        assert not viewer_role.has_permission(Permission.DOCUMENTS_WRITE)
        
        assert admin_role.has_permission(Permission.DOCUMENTS_READ)
        assert admin_role.has_permission(Permission.DOCUMENTS_WRITE)
        assert admin_role.has_permission("documents.custom")  # Wildcard
    
    def test_access_control_direct_permission(self, security_context):
        """Test authorization with direct permissions."""
        access_control = AccessControl()
        
        # Should allow - has direct permission
        assert access_control.authorize(
            security_context,
            Permission.DOCUMENTS_READ
        )
        
        # Should deny - no permission
        assert not access_control.authorize(
            security_context,
            Permission.DOCUMENTS_WRITE
        )
    
    def test_access_control_role_permission(self, security_context):
        """Test authorization with role-based permissions."""
        access_control = AccessControl()
        
        # Viewer role allows collections.read
        assert access_control.authorize(
            security_context,
            Permission.COLLECTIONS_READ
        )
        
        # Viewer role doesn't allow collections.write
        assert not access_control.authorize(
            security_context,
            Permission.COLLECTIONS_WRITE
        )
    
    def test_access_control_resource_policy(self, security_context):
        """Test resource-level access control."""
        access_control = AccessControl()
        
        # Add policy allowing write to specific document
        policy = ResourcePolicy(
            resource_type="document",
            resource_id="doc-123",
            permissions={Permission.DOCUMENTS_WRITE},
            conditions={"principal_id": "user-1"}
        )
        access_control.add_policy(policy)
        
        # Should allow - policy matches
        assert access_control.authorize(
            security_context,
            Permission.DOCUMENTS_WRITE,
            resource_type="document",
            resource_id="doc-123"
        )
        
        # Should deny - different document
        assert not access_control.authorize(
            security_context,
            Permission.DOCUMENTS_WRITE,
            resource_type="document",
            resource_id="doc-456"
        )
    
    def test_require_permission_raises(self, security_context):
        """Test require_permission raises on denial."""
        access_control = AccessControl()
        
        with pytest.raises(AuthorizationError) as exc_info:
            access_control.require_permission(
                security_context,
                Permission.DOCUMENTS_DELETE
            )
        
        assert "Permission 'documents.delete' required" in str(exc_info.value)


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter with test config."""
        config = RateLimitConfig(
            global_requests_per_minute=60,
            global_burst_size=10,
            client_requests_per_minute=30,
            client_burst_size=5,
            use_sliding_window=False,  # Use token bucket for testing
        )
        return RateLimiter(config)
    
    @pytest.mark.asyncio
    async def test_rate_limit_allows_normal_traffic(self, rate_limiter):
        """Test rate limiter allows normal traffic."""
        # Should allow first few requests
        for _ in range(5):
            await rate_limiter.check_rate_limit(client_id="user-1")
        
        # No exception means allowed
    
    @pytest.mark.asyncio
    async def test_client_rate_limit_exceeded(self, rate_limiter):
        """Test client rate limit enforcement."""
        # Exhaust client burst
        for _ in range(5):
            await rate_limiter.check_rate_limit(client_id="user-1")
        
        # Next request should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            await rate_limiter.check_rate_limit(client_id="user-1")
        
        assert "Client rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.retry_after > 0
    
    @pytest.mark.asyncio
    async def test_operation_rate_limit(self, rate_limiter):
        """Test operation-specific rate limits."""
        # Tools have lower limits
        for _ in range(5):
            await rate_limiter.check_rate_limit(
                client_id="user-1",
                operation="tools/call"
            )
        
        with pytest.raises(RateLimitExceeded) as exc_info:
            await rate_limiter.check_rate_limit(
                client_id="user-1",
                operation="tools/call"
            )
        
        assert "Operation rate limit exceeded" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, rate_limiter):
        """Test rate limit reset."""
        # Exhaust limit
        for _ in range(5):
            await rate_limiter.check_rate_limit(client_id="user-1")
        
        # Reset
        await rate_limiter.reset_client_limit("user-1")
        
        # Should allow again
        await rate_limiter.check_rate_limit(client_id="user-1")


class TestAuditLogging:
    """Test audit logging functionality."""
    
    @pytest.fixture
    def audit_logger(self):
        """Create audit logger with memory backend."""
        config = AuditConfig(
            storage_backend="memory",
            max_events_memory=100,
            buffer_size=10,
        )
        return AuditLogger(config)
    
    @pytest.mark.asyncio
    async def test_log_authentication_event(self, audit_logger):
        """Test logging authentication events."""
        await audit_logger.start()
        
        await audit_logger.log_event(
            event_type=AuditEventType.AUTH_SUCCESS,
            success=True,
            principal_id="user-1",
            principal_type="user",
            auth_method="api_key",
            operation="initialize",
            client_ip="127.0.0.1",
        )
        
        # Force flush
        await audit_logger._flush_buffer()
        
        # Check event was logged
        events = await audit_logger.search_events(
            event_types=[AuditEventType.AUTH_SUCCESS]
        )
        
        assert len(events) == 1
        assert events[0].principal_id == "user-1"
        assert events[0].auth_method == "api_key"
        
        await audit_logger.stop()
    
    @pytest.mark.asyncio
    async def test_log_authorization_event(self, audit_logger):
        """Test logging authorization events."""
        await audit_logger.start()
        
        await audit_logger.log_event(
            event_type=AuditEventType.AUTHZ_DENIED,
            success=False,
            principal_id="user-1",
            operation="delete_document",
            resource_type="document",
            resource_id="doc-123",
            error_message="Permission denied",
        )
        
        await audit_logger._flush_buffer()
        
        events = await audit_logger.search_events(
            event_types=[AuditEventType.AUTHZ_DENIED]
        )
        
        assert len(events) == 1
        assert events[0].resource_id == "doc-123"
        assert events[0].severity == "warning"
        
        await audit_logger.stop()
    
    @pytest.mark.asyncio
    async def test_search_events_with_filters(self, audit_logger):
        """Test searching events with filters."""
        await audit_logger.start()
        
        # Log various events
        await audit_logger.log_event(
            AuditEventType.AUTH_SUCCESS,
            principal_id="user-1",
        )
        await audit_logger.log_event(
            AuditEventType.AUTH_SUCCESS,
            principal_id="user-2",
        )
        await audit_logger.log_event(
            AuditEventType.TOOL_EXECUTED,
            principal_id="user-1",
            resource_type="tool",
            resource_id="test_tool",
        )
        
        await audit_logger._flush_buffer()
        
        # Search by principal
        events = await audit_logger.search_events(principal_id="user-1")
        assert len(events) == 2
        
        # Search by event type
        events = await audit_logger.search_events(
            event_types=[AuditEventType.TOOL_EXECUTED]
        )
        assert len(events) == 1
        assert events[0].resource_id == "test_tool"
        
        await audit_logger.stop()
    
    def test_sensitive_data_redaction(self, audit_logger):
        """Test sensitive data is redacted."""
        details = {
            "username": "test",
            "password": "secret123",
            "api_key": "key-12345",
            "other_data": "visible",
        }
        
        redacted = audit_logger._redact_sensitive_data(details)
        
        assert redacted["username"] == "test"
        assert redacted["password"] == "[REDACTED]"
        assert redacted["api_key"] == "[REDACTED]"
        assert redacted["other_data"] == "visible"


class TestSecurityIntegration:
    """Test security middleware integration."""
    
    @pytest.mark.asyncio
    async def test_security_middleware_authentication(self):
        """Test security middleware authentication flow."""
        from contextframe.mcp.security.integration import SecurityMiddleware
        
        # Create components
        api_keys = {
            "test-key": {
                "principal_id": "user-1",
                "permissions": ["documents.read"],
                "roles": ["viewer"],
            }
        }
        auth_provider = APIKeyAuth(api_keys)
        
        middleware = SecurityMiddleware(
            auth_provider=auth_provider,
            anonymous_allowed=False,
        )
        
        # Test successful auth
        message = {
            "method": "test",
            "params": {"api_key": "test-key"},
            "id": 1,
        }
        
        context = await middleware.authenticate(message)
        assert context.authenticated
        assert context.principal_id == "user-1"
        
        # Test failed auth
        message["params"]["api_key"] = "wrong-key"
        
        with pytest.raises(AuthenticationError):
            await middleware.authenticate(message)
    
    @pytest.mark.asyncio
    async def test_security_middleware_full_flow(self):
        """Test complete security flow."""
        from contextframe.mcp.security.integration import SecurityMiddleware
        
        # Create all components
        auth_provider = APIKeyAuth({
            "test-key": {
                "principal_id": "user-1",
                "permissions": ["documents.read"],
                "roles": ["viewer"],
            }
        })
        
        access_control = AccessControl()
        rate_limiter = RateLimiter(RateLimitConfig())
        audit_logger = AuditLogger(AuditConfig(storage_backend="memory"))
        
        middleware = SecurityMiddleware(
            auth_provider=auth_provider,
            access_control=access_control,
            rate_limiter=rate_limiter,
            audit_logger=audit_logger,
        )
        
        await middleware.start()
        
        # Test full security check
        message = {
            "method": "get_document",
            "params": {
                "api_key": "test-key",
                "document_id": "doc-123",
            },
            "id": 1,
        }
        
        # Authenticate
        context = await middleware.authenticate(message)
        
        # Check rate limit
        await middleware.check_rate_limit(context, "get_document")
        
        # Authorize
        await middleware.authorize(
            context,
            "get_document",
            message["params"]
        )
        
        # Verify audit log
        await audit_logger._flush_buffer()
        events = await audit_logger.search_events()
        assert len(events) > 0
        assert events[0].event_type == AuditEventType.AUTH_SUCCESS
        
        await middleware.stop()