"""Authorization and access control for MCP server."""

import fnmatch
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from contextframe.mcp.errors import MCPError

from .auth import SecurityContext


class AuthorizationError(MCPError):
    """Authorization failed error."""
    
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(code=-32002, message=message)


class Permission(str, Enum):
    """Standard MCP permissions."""
    
    # Document permissions
    DOCUMENTS_READ = "documents.read"
    DOCUMENTS_WRITE = "documents.write"
    DOCUMENTS_DELETE = "documents.delete"
    DOCUMENTS_ADMIN = "documents.admin"
    
    # Collection permissions
    COLLECTIONS_READ = "collections.read"
    COLLECTIONS_WRITE = "collections.write"
    COLLECTIONS_DELETE = "collections.delete"
    COLLECTIONS_ADMIN = "collections.admin"
    
    # Tool permissions
    TOOLS_EXECUTE = "tools.execute"
    TOOLS_ADMIN = "tools.admin"
    
    # System permissions
    SYSTEM_READ = "system.read"
    SYSTEM_ADMIN = "system.admin"
    
    # Monitoring permissions
    MONITORING_READ = "monitoring.read"
    MONITORING_EXPORT = "monitoring.export"
    MONITORING_ADMIN = "monitoring.admin"
    
    # Special permissions
    ALL = "*"  # Superuser permission


@dataclass
class Role:
    """Role definition with permissions."""
    
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        # Check for superuser
        if Permission.ALL in self.permissions:
            return True
        
        # Check exact match
        if permission in self.permissions:
            return True
        
        # Check wildcard patterns
        for perm in self.permissions:
            if fnmatch.fnmatch(permission, perm):
                return True
        
        return False


# Standard roles
STANDARD_ROLES = {
    "viewer": Role(
        name="viewer",
        description="Read-only access to documents and collections",
        permissions={
            Permission.DOCUMENTS_READ,
            Permission.COLLECTIONS_READ,
        }
    ),
    
    "editor": Role(
        name="editor",
        description="Read and write access to documents and collections",
        permissions={
            Permission.DOCUMENTS_READ,
            Permission.DOCUMENTS_WRITE,
            Permission.COLLECTIONS_READ,
            Permission.COLLECTIONS_WRITE,
            Permission.TOOLS_EXECUTE,
        }
    ),
    
    "admin": Role(
        name="admin",
        description="Full access to all resources",
        permissions={
            "documents.*",
            "collections.*",
            "tools.*",
            "system.*",
            "monitoring.*",
        }
    ),
    
    "monitor": Role(
        name="monitor",
        description="Access to monitoring and metrics",
        permissions={
            Permission.MONITORING_READ,
            Permission.MONITORING_EXPORT,
            Permission.SYSTEM_READ,
        }
    ),
    
    "service": Role(
        name="service",
        description="Service account with limited permissions",
        permissions={
            Permission.DOCUMENTS_READ,
            Permission.COLLECTIONS_READ,
            Permission.TOOLS_EXECUTE,
        }
    ),
}


@dataclass
class ResourcePolicy:
    """Policy for resource-level access control."""
    
    resource_type: str  # "document", "collection", "tool", etc.
    resource_id: Optional[str] = None  # Specific resource ID or pattern
    permissions: Set[str] = field(default_factory=set)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def matches_resource(self, resource_type: str, resource_id: str) -> bool:
        """Check if policy applies to a resource."""
        # Check resource type
        if self.resource_type != resource_type and self.resource_type != "*":
            return False
        
        # Check resource ID
        if self.resource_id:
            if "*" in self.resource_id or "?" in self.resource_id:
                # Wildcard pattern
                return fnmatch.fnmatch(resource_id, self.resource_id)
            else:
                # Exact match
                return resource_id == self.resource_id
        
        return True
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions."""
        for key, expected in self.conditions.items():
            actual = context.get(key)
            
            # Handle different condition types
            if isinstance(expected, dict):
                # Complex condition (e.g., {"$in": ["value1", "value2"]})
                operator = list(expected.keys())[0]
                value = expected[operator]
                
                if operator == "$in" and actual not in value:
                    return False
                elif operator == "$eq" and actual != value:
                    return False
                elif operator == "$ne" and actual == value:
                    return False
                elif operator == "$regex":
                    if not re.match(value, str(actual)):
                        return False
            else:
                # Simple equality
                if actual != expected:
                    return False
        
        return True


class AccessControl:
    """Access control manager for authorization decisions."""
    
    def __init__(
        self,
        roles: Optional[Dict[str, Role]] = None,
        policies: Optional[List[ResourcePolicy]] = None,
        default_allow: bool = False
    ):
        """Initialize access control.
        
        Args:
            roles: Role definitions (defaults to STANDARD_ROLES)
            policies: Resource-level policies
            default_allow: Default authorization decision
        """
        self.roles = roles or STANDARD_ROLES.copy()
        self.policies = policies or []
        self.default_allow = default_allow
    
    def authorize(
        self,
        context: SecurityContext,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Make authorization decision.
        
        Args:
            context: Security context from authentication
            permission: Required permission
            resource_type: Type of resource being accessed
            resource_id: ID of specific resource
            request_context: Additional context for conditions
            
        Returns:
            True if authorized, False otherwise
        """
        # Unauthenticated users have no permissions
        if not context.authenticated:
            return False
        
        # Check direct permissions
        if context.has_permission(permission) or context.has_permission(Permission.ALL):
            return True
        
        # Check role-based permissions
        for role_name in context.roles:
            role = self.roles.get(role_name)
            if role and role.has_permission(permission):
                return True
        
        # Check resource-level policies if resource specified
        if resource_type and resource_id:
            for policy in self.policies:
                if not policy.matches_resource(resource_type, resource_id):
                    continue
                
                # Check if policy grants the permission
                if permission not in policy.permissions and Permission.ALL not in policy.permissions:
                    continue
                
                # Evaluate conditions
                eval_context = {
                    "principal_id": context.principal_id,
                    "principal_type": context.principal_type,
                    "auth_method": context.auth_method,
                    **(request_context or {}),
                    **(context.attributes or {})
                }
                
                if policy.evaluate_conditions(eval_context):
                    return True
        
        # Default decision
        return self.default_allow
    
    def require_permission(
        self,
        context: SecurityContext,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Require a permission, raising error if not authorized.
        
        Args:
            context: Security context from authentication
            permission: Required permission
            resource_type: Type of resource being accessed
            resource_id: ID of specific resource
            request_context: Additional context for conditions
            
        Raises:
            AuthorizationError: If not authorized
        """
        if not self.authorize(
            context, permission, resource_type, resource_id, request_context
        ):
            resource_info = ""
            if resource_type and resource_id:
                resource_info = f" for {resource_type}/{resource_id}"
            
            raise AuthorizationError(
                f"Permission '{permission}' required{resource_info}"
            )
    
    def filter_permitted_resources(
        self,
        context: SecurityContext,
        permission: str,
        resources: List[Dict[str, Any]],
        resource_type: str,
        id_field: str = "id"
    ) -> List[Dict[str, Any]]:
        """Filter list of resources to only those permitted.
        
        Args:
            context: Security context
            permission: Required permission
            resources: List of resources to filter
            resource_type: Type of resources
            id_field: Field containing resource ID
            
        Returns:
            Filtered list of permitted resources
        """
        permitted = []
        
        for resource in resources:
            resource_id = resource.get(id_field)
            if resource_id and self.authorize(
                context, permission, resource_type, resource_id
            ):
                permitted.append(resource)
        
        return permitted
    
    def add_role(self, role: Role) -> None:
        """Add or update a role definition."""
        self.roles[role.name] = role
    
    def add_policy(self, policy: ResourcePolicy) -> None:
        """Add a resource policy."""
        self.policies.append(policy)
    
    def get_effective_permissions(
        self,
        context: SecurityContext,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> Set[str]:
        """Get all effective permissions for a context.
        
        Args:
            context: Security context
            resource_type: Optional resource type filter
            resource_id: Optional resource ID filter
            
        Returns:
            Set of effective permissions
        """
        permissions = set()
        
        # Add direct permissions
        permissions.update(context.permissions)
        
        # Add role permissions
        for role_name in context.roles:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        
        # Add policy permissions if resource specified
        if resource_type and resource_id:
            for policy in self.policies:
                if policy.matches_resource(resource_type, resource_id):
                    # Check conditions
                    eval_context = {
                        "principal_id": context.principal_id,
                        "principal_type": context.principal_type,
                        "auth_method": context.auth_method,
                        **(context.attributes or {})
                    }
                    
                    if policy.evaluate_conditions(eval_context):
                        permissions.update(policy.permissions)
        
        return permissions