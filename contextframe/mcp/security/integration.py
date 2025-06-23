"""Integration of security components with MCP server."""

import uuid
from typing import Any, Dict, Optional

from contextframe.mcp.handlers import MessageHandler as BaseMessageHandler
from contextframe.mcp.errors import MCPError

from .audit import AuditEventType, AuditLogger
from .auth import AuthenticationError, SecurityContext, AuthProvider
from .authorization import AuthorizationError, AccessControl, Permission
from .rate_limiting import RateLimitExceeded, RateLimiter


class SecurityMiddleware:
    """Security middleware for MCP server.
    
    Provides authentication, authorization, rate limiting, and audit logging
    for all MCP operations.
    """
    
    def __init__(
        self,
        auth_provider: Optional[AuthProvider] = None,
        access_control: Optional[AccessControl] = None,
        rate_limiter: Optional[RateLimiter] = None,
        audit_logger: Optional[AuditLogger] = None,
        anonymous_allowed: bool = False,
        anonymous_permissions: Optional[set] = None
    ):
        """Initialize security middleware.
        
        Args:
            auth_provider: Authentication provider
            access_control: Access control manager
            rate_limiter: Rate limiter
            audit_logger: Audit logger
            anonymous_allowed: Allow anonymous access
            anonymous_permissions: Permissions for anonymous users
        """
        self.auth_provider = auth_provider
        self.access_control = access_control
        self.rate_limiter = rate_limiter
        self.audit_logger = audit_logger
        self.anonymous_allowed = anonymous_allowed
        self.anonymous_permissions = anonymous_permissions or set()
    
    async def start(self):
        """Start security components."""
        if self.rate_limiter:
            await self.rate_limiter.start()
        if self.audit_logger:
            await self.audit_logger.start()
    
    async def stop(self):
        """Stop security components."""
        if self.rate_limiter:
            await self.rate_limiter.stop()
        if self.audit_logger:
            await self.audit_logger.stop()
    
    def _get_request_metadata(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract request metadata from message."""
        return {
            "request_id": message.get("id"),
            "method": message.get("method"),
            "params": message.get("params", {}),
            "client_ip": message.get("_client_ip"),
            "user_agent": message.get("_user_agent"),
        }
    
    async def authenticate(self, message: Dict[str, Any]) -> SecurityContext:
        """Authenticate the request.
        
        Args:
            message: JSON-RPC message
            
        Returns:
            Security context
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Extract credentials from message
        credentials = {}
        
        # Check for API key in params
        params = message.get("params", {})
        if isinstance(params, dict):
            if "api_key" in params:
                credentials["api_key"] = params["api_key"]
            elif "_api_key" in params:
                credentials["api_key"] = params["_api_key"]
        
        # Check for bearer token in metadata
        if "_authorization" in message:
            auth_header = message["_authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                credentials["token"] = token
        
        # Check for OAuth code
        if "code" in params:
            credentials["code"] = params["code"]
            credentials["code_verifier"] = params.get("code_verifier")
            credentials["redirect_uri"] = params.get("redirect_uri")
        
        # Try authentication
        if credentials and self.auth_provider:
            try:
                context = await self.auth_provider.authenticate(credentials)
                
                # Log successful authentication
                if self.audit_logger:
                    metadata = self._get_request_metadata(message)
                    await self.audit_logger.log_event(
                        event_type=AuditEventType.AUTH_SUCCESS,
                        success=True,
                        principal_id=context.principal_id,
                        principal_type=context.principal_type,
                        principal_name=context.principal_name,
                        auth_method=context.auth_method,
                        operation=metadata["method"],
                        request_id=metadata["request_id"],
                        client_ip=metadata["client_ip"],
                        user_agent=metadata["user_agent"],
                    )
                
                return context
                
            except AuthenticationError as e:
                # Log failed authentication
                if self.audit_logger:
                    metadata = self._get_request_metadata(message)
                    await self.audit_logger.log_event(
                        event_type=AuditEventType.AUTH_FAILURE,
                        success=False,
                        operation=metadata["method"],
                        request_id=metadata["request_id"],
                        client_ip=metadata["client_ip"],
                        user_agent=metadata["user_agent"],
                        error_code=e.code,
                        error_message=str(e),
                        details={"credentials_type": list(credentials.keys())}
                    )
                raise
        
        # Check if anonymous access is allowed
        if self.anonymous_allowed:
            return SecurityContext(
                authenticated=False,
                auth_method="anonymous",
                principal_id="anonymous",
                principal_type="anonymous",
                permissions=self.anonymous_permissions.copy(),
            )
        
        # No credentials and anonymous not allowed
        raise AuthenticationError("Authentication required")
    
    async def authorize(
        self,
        context: SecurityContext,
        operation: str,
        params: Dict[str, Any]
    ) -> None:
        """Authorize the operation.
        
        Args:
            context: Security context from authentication
            operation: Operation being performed
            params: Operation parameters
            
        Raises:
            AuthorizationError: If not authorized
        """
        if not self.access_control:
            # No access control configured, allow all
            return
        
        # Map operations to permissions
        permission_map = {
            # Document operations
            "get_document": Permission.DOCUMENTS_READ,
            "search_documents": Permission.DOCUMENTS_READ,
            "add_document": Permission.DOCUMENTS_WRITE,
            "update_document": Permission.DOCUMENTS_WRITE,
            "delete_document": Permission.DOCUMENTS_DELETE,
            
            # Collection operations
            "get_collection": Permission.COLLECTIONS_READ,
            "list_collections": Permission.COLLECTIONS_READ,
            "create_collection": Permission.COLLECTIONS_WRITE,
            "update_collection": Permission.COLLECTIONS_WRITE,
            "delete_collection": Permission.COLLECTIONS_DELETE,
            
            # Tool operations
            "tools/list": Permission.TOOLS_EXECUTE,
            "tools/call": Permission.TOOLS_EXECUTE,
            
            # System operations
            "resources/list": Permission.SYSTEM_READ,
            "resources/read": Permission.SYSTEM_READ,
            
            # Monitoring operations
            "get_usage_metrics": Permission.MONITORING_READ,
            "get_performance_metrics": Permission.MONITORING_READ,
            "get_cost_report": Permission.MONITORING_READ,
            "export_metrics": Permission.MONITORING_EXPORT,
        }
        
        # Get required permission
        permission = permission_map.get(operation)
        if not permission:
            # Unknown operation, check for wildcards
            if operation.startswith("monitoring/"):
                permission = Permission.MONITORING_READ
            elif operation.startswith("tools/"):
                permission = Permission.TOOLS_EXECUTE
            else:
                # Default to system read
                permission = Permission.SYSTEM_READ
        
        # Extract resource info from params
        resource_type = None
        resource_id = None
        
        if "document_id" in params:
            resource_type = "document"
            resource_id = params["document_id"]
        elif "collection_id" in params:
            resource_type = "collection"
            resource_id = params["collection_id"]
        elif "name" in params and operation == "tools/call":
            resource_type = "tool"
            resource_id = params["name"]
        elif "uri" in params and operation == "resources/read":
            resource_type = "resource"
            resource_id = params["uri"]
        
        try:
            # Check authorization
            self.access_control.require_permission(
                context,
                permission,
                resource_type,
                resource_id,
                params
            )
            
            # Log successful authorization
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTHZ_GRANTED,
                    success=True,
                    principal_id=context.principal_id,
                    principal_type=context.principal_type,
                    auth_method=context.auth_method,
                    operation=operation,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={"permission": permission}
                )
            
        except AuthorizationError as e:
            # Log authorization denial
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTHZ_DENIED,
                    success=False,
                    principal_id=context.principal_id,
                    principal_type=context.principal_type,
                    auth_method=context.auth_method,
                    operation=operation,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    error_code=e.code,
                    error_message=str(e),
                    details={"permission": permission}
                )
            raise
    
    async def check_rate_limit(
        self,
        context: SecurityContext,
        operation: str
    ) -> None:
        """Check rate limits.
        
        Args:
            context: Security context
            operation: Operation being performed
            
        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        if not self.rate_limiter:
            return
        
        try:
            await self.rate_limiter.check_rate_limit(
                client_id=context.principal_id,
                operation=operation
            )
        except RateLimitExceeded as e:
            # Log rate limit exceeded
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                    success=False,
                    principal_id=context.principal_id,
                    principal_type=context.principal_type,
                    operation=operation,
                    error_code=e.code,
                    error_message=str(e),
                    details={"retry_after": e.retry_after}
                )
            raise


class SecuredMessageHandler(BaseMessageHandler):
    """Message handler with integrated security."""
    
    def __init__(
        self,
        server: Any,
        security: SecurityMiddleware
    ):
        super().__init__(server)
        self.security = security
        
        # Override method handlers to add security
        self._secured_handlers = {}
        for method, handler in self._method_handlers.items():
            self._secured_handlers[method] = self._wrap_handler(handler, method)
        self._method_handlers = self._secured_handlers
    
    def _wrap_handler(self, handler, method: str):
        """Wrap handler with security checks."""
        async def secured_handler(params: Dict[str, Any]) -> Any:
            # Get current message context
            message = getattr(self, "_current_message", {})
            
            # Authenticate
            context = await self.security.authenticate(message)
            
            # Store context for use in handler
            self._current_context = context
            
            # Check rate limit
            await self.security.check_rate_limit(context, method)
            
            # Authorize
            await self.security.authorize(context, method, params)
            
            # Call original handler
            try:
                result = await handler(params)
                
                # Log successful operation
                if self.security.audit_logger:
                    resource_type = None
                    resource_id = None
                    
                    if method.startswith("tools/"):
                        event_type = AuditEventType.TOOL_EXECUTED
                        resource_type = "tool"
                        resource_id = params.get("name")
                    elif method.startswith("resources/"):
                        event_type = AuditEventType.RESOURCE_READ
                        resource_type = "resource"
                        resource_id = params.get("uri")
                    else:
                        event_type = AuditEventType.RESOURCE_READ
                    
                    await self.security.audit_logger.log_event(
                        event_type=event_type,
                        success=True,
                        principal_id=context.principal_id,
                        principal_type=context.principal_type,
                        auth_method=context.auth_method,
                        operation=method,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        request_id=message.get("id"),
                        session_id=context.session_id,
                    )
                
                return result
                
            except Exception as e:
                # Log operation failure
                if self.security.audit_logger:
                    await self.security.audit_logger.log_event(
                        event_type=AuditEventType.TOOL_FAILED if method.startswith("tools/") else AuditEventType.SYSTEM_ERROR,
                        success=False,
                        principal_id=context.principal_id,
                        principal_type=context.principal_type,
                        auth_method=context.auth_method,
                        operation=method,
                        request_id=message.get("id"),
                        error_message=str(e),
                    )
                raise
        
        return secured_handler
    
    async def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        """Handle message with security context."""
        # Store message for security checks
        self._current_message = message
        
        try:
            return await super().handle(message)
        finally:
            # Clean up
            self._current_message = None
            self._current_context = None