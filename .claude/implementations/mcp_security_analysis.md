# MCP Security Implementation Analysis

## Overview

The MCP (Model Context Protocol) security implementation in ContextFrame provides a comprehensive, multi-layered security system designed to protect dataset access and operations. The implementation follows security best practices with defense-in-depth principles, providing authentication, authorization, rate limiting, and audit logging capabilities.

## Architecture

The security system is composed of several modular components that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                            │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   Security Middleware      │
                    │ ┌────────────────────────┐ │
                    │ │   1. Authentication   │ │
                    │ │   - API Key           │ │
                    │ │   - OAuth 2.1         │ │
                    │ │   - JWT                │ │
                    │ └────────────┬───────────┘ │
                    │              │             │
                    │ ┌────────────▼───────────┐ │
                    │ │   2. Rate Limiting     │ │
                    │ │   - Global limits      │ │
                    │ │   - Per-client limits  │ │
                    │ │   - Operation limits   │ │
                    │ └────────────┬───────────┘ │
                    │              │             │
                    │ ┌────────────▼───────────┐ │
                    │ │   3. Authorization     │ │
                    │ │   - RBAC              │ │
                    │ │   - Resource policies  │ │
                    │ │   - Permission checks │ │
                    │ └────────────┬───────────┘ │
                    │              │             │
                    │ ┌────────────▼───────────┐ │
                    │ │   4. Audit Logging     │ │
                    │ │   - Event recording    │ │
                    │ │   - Security events    │ │
                    │ │   - Compliance trail   │ │
                    │ └────────────────────────┘ │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │     MCP Handler            │
                    │   (Process Request)        │
                    └────────────────────────────┘
```

## 1. Authentication Providers

### 1.1 API Key Authentication (`auth.py`)

**Purpose**: Simple, stateless authentication using pre-shared keys.

**Implementation**:
```python
class APIKeyAuth(AuthProvider):
    def __init__(self, api_keys: Dict[str, Dict[str, Any]]):
        # Keys are hashed using SHA-256 for secure storage
        self._hashed_keys = {
            self._hash_key(key): metadata
            for key, metadata in self.api_keys.items()
        }
```

**Security Guarantees**:
- API keys are never stored in plaintext (SHA-256 hashed)
- Supports key expiration
- Constant-time comparison to prevent timing attacks
- Keys include metadata for permissions and roles

**Configuration Example**:
```json
{
  "api_keys": {
    "sk_live_...": {
      "principal_id": "user-123",
      "principal_name": "Production Service",
      "principal_type": "service",
      "permissions": ["documents.read", "collections.read"],
      "roles": ["viewer"],
      "expires_at": "2024-12-31T23:59:59Z"
    }
  }
}
```

**Best Practices**:
- Generate keys using `APIKeyAuth.generate_api_key()` (32 bytes, URL-safe)
- Rotate keys regularly
- Use different keys for different environments
- Never commit keys to version control

### 1.2 OAuth 2.1 Provider (`oauth.py`)

**Purpose**: Industry-standard authentication with support for authorization code flow.

**Implementation Features**:
- PKCE (Proof Key for Code Exchange) support for enhanced security
- Authorization code flow with state validation
- Client credentials flow for service accounts
- Token introspection capabilities
- Configurable redirect URI validation

**Security Guarantees**:
- PKCE prevents authorization code interception attacks
- State parameter prevents CSRF attacks
- Strict redirect URI validation
- Token expiration enforcement
- Secure token storage

**Configuration Example**:
```python
oauth_config = OAuth2Config(
    authorization_endpoint="https://auth.example.com/authorize",
    token_endpoint="https://auth.example.com/token",
    userinfo_endpoint="https://auth.example.com/userinfo",
    client_id="contextframe-client",
    client_secret="secret",  # Store securely!
    redirect_uri="http://localhost:8080/callback",
    scopes=["openid", "profile", "email"],
    require_pkce=True,
    require_state=True,
    allowed_redirect_uris=["http://localhost:8080/callback"]
)
```

**Integration Pattern**:
```python
# Generate authorization URL
provider = OAuth2Provider(oauth_config)
verifier, challenge = OAuth2Provider.generate_pkce_pair()
auth_url = provider.generate_authorization_url(
    state=secrets.token_urlsafe(32),
    code_challenge=challenge
)

# Exchange code for token
context = await provider.authenticate({
    "code": authorization_code,
    "code_verifier": verifier,
    "redirect_uri": redirect_uri
})
```

### 1.3 JWT Handler (`jwt.py`)

**Purpose**: Stateless authentication using JSON Web Tokens.

**Implementation Features**:
- Support for RS256 (RSA) and HS256 (HMAC) algorithms
- Automatic RSA key pair generation for testing
- Comprehensive claim validation
- Token creation and verification
- Refresh token support

**Security Guarantees**:
- Signature verification prevents token tampering
- Expiration validation prevents replay attacks
- Audience and issuer validation
- Support for custom claims

**Configuration Example**:
```python
jwt_config = JWTConfig(
    algorithm="RS256",
    private_key=private_key_pem,  # For signing
    public_key=public_key_pem,    # For verification
    issuer="contextframe-mcp",
    audience="contextframe-api",
    token_lifetime=3600,  # 1 hour
    verify_exp=True,
    verify_aud=True,
    verify_iss=True
)
```

**Token Creation**:
```python
handler = JWTHandler(jwt_config)
token = handler.create_token(
    principal_id="user-123",
    principal_name="John Doe",
    permissions={"documents.read", "collections.write"},
    roles={"editor"},
    additional_claims={"department": "engineering"}
)
```

### 1.4 Multi-Provider Authentication

**Purpose**: Support multiple authentication methods simultaneously.

**Implementation**:
```python
multi_auth = MultiAuthProvider([
    APIKeyAuth(api_keys),
    OAuth2Provider(oauth_config),
    JWTHandler(jwt_config)
])

# Tries each provider in order
context = await multi_auth.authenticate(credentials)
```

## 2. Authorization System (`authorization.py`)

### 2.1 Role-Based Access Control (RBAC)

**Standard Roles**:

1. **Viewer**: Read-only access
   - `documents.read`
   - `collections.read`

2. **Editor**: Read and write access
   - All viewer permissions
   - `documents.write`
   - `collections.write`
   - `tools.execute`

3. **Admin**: Full access
   - All permissions via wildcards
   - `documents.*`
   - `collections.*`
   - `tools.*`
   - `system.*`

4. **Monitor**: Monitoring access
   - `monitoring.read`
   - `monitoring.export`
   - `system.read`

5. **Service**: Service account
   - `documents.read`
   - `collections.read`
   - `tools.execute`

### 2.2 Permission System

**Wildcard Support**:
```python
# Permission "documents.*" matches:
# - documents.read
# - documents.write
# - documents.delete
# - documents.custom_action
```

**Permission Hierarchy**:
```
documents.*
├── documents.read
├── documents.write
├── documents.delete
└── documents.admin

collections.*
├── collections.read
├── collections.write
├── collections.delete
└── collections.admin

tools.*
├── tools.execute
└── tools.admin

system.*
├── system.read
└── system.admin

monitoring.*
├── monitoring.read
├── monitoring.export
└── monitoring.admin
```

### 2.3 Resource-Level Policies

**Purpose**: Fine-grained access control for specific resources.

**Implementation**:
```python
# Policy for specific document access
policy = ResourcePolicy(
    resource_type="document",
    resource_id="sensitive-doc-*",  # Wildcard pattern
    permissions={"documents.read"},
    conditions={
        "principal_type": "user",
        "department": {"$in": ["legal", "compliance"]}
    }
)
```

**Condition Operators**:
- `$eq`: Exact match
- `$ne`: Not equal
- `$in`: Value in list
- `$regex`: Regular expression match

### 2.4 Authorization Flow

```python
access_control = AccessControl(
    roles=STANDARD_ROLES,
    policies=[policy1, policy2],
    default_allow=False  # Deny by default
)

# Check authorization
if access_control.authorize(
    context=security_context,
    permission="documents.write",
    resource_type="document",
    resource_id="doc-123"
):
    # Allowed
    pass
else:
    # Denied
    raise AuthorizationError()
```

## 3. Rate Limiting (`rate_limiting.py`)

### 3.1 Multi-Level Rate Limiting

**Levels**:
1. **Global**: Overall system capacity
2. **Per-Client**: Individual client limits
3. **Per-Operation**: Operation-specific limits

**Default Configuration**:
```python
config = RateLimitConfig(
    # Global limits
    global_requests_per_minute=600,
    global_burst_size=100,
    
    # Per-client limits
    client_requests_per_minute=60,
    client_burst_size=10,
    
    # Operation-specific limits
    operation_limits={
        "tools/call": (30, 5),      # 30 rpm, burst 5
        "batch/*": (10, 2),         # 10 rpm, burst 2
        "export/*": (5, 1),         # 5 rpm, burst 1
        "resources/read": (120, 20), # 120 rpm, burst 20
    }
)
```

### 3.2 Rate Limiting Algorithms

**Token Bucket** (Default for burst handling):
- Allows burst traffic up to bucket capacity
- Smooth refill rate
- Good for APIs with occasional spikes

**Sliding Window** (Optional for strict limits):
- Precise request counting
- No burst allowance
- Better for strict rate enforcement

### 3.3 Rate Limit Headers

When rate limits are exceeded, the response includes:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1634567890
Retry-After: 42
```

## 4. Audit Logging (`audit.py`)

### 4.1 Event Types

**Authentication Events**:
- `auth.success`: Successful authentication
- `auth.failure`: Failed authentication
- `auth.token_created`: New token issued
- `auth.token_revoked`: Token revoked

**Authorization Events**:
- `authz.granted`: Access granted
- `authz.denied`: Access denied

**Rate Limiting Events**:
- `rate_limit.exceeded`: Rate limit hit
- `rate_limit.reset`: Rate limit reset

**Resource Access Events**:
- `resource.read`: Resource accessed
- `resource.write`: Resource modified
- `resource.delete`: Resource deleted

**Security Configuration Events**:
- `security.config_changed`: Security settings modified
- `role.created/modified/deleted`: Role changes
- `policy.created/modified/deleted`: Policy changes

### 4.2 Storage Backends

**Memory** (Development):
```python
config = AuditConfig(
    storage_backend="memory",
    max_events_memory=10000
)
```

**File** (Production):
```python
config = AuditConfig(
    storage_backend="file",
    file_path="/var/log/mcp/audit.log",
    retention_days=90
)
```

**Dataset** (Advanced):
```python
config = AuditConfig(
    storage_backend="dataset",
    dataset_path="/data/audit.lance",
    retention_days=365
)
```

### 4.3 Event Structure

```python
@dataclass
class AuditEvent:
    # Event metadata
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    
    # Principal information
    principal_id: str
    principal_type: str
    principal_name: str
    auth_method: str
    
    # Request context
    operation: str
    resource_type: str
    resource_id: str
    request_id: str
    session_id: str
    
    # Network context
    client_ip: str
    user_agent: str
    
    # Event details
    success: bool
    error_code: int
    error_message: str
    details: Dict[str, Any]
    
    # Computed
    severity: str  # "info", "warning", "error"
```

### 4.4 Search and Compliance

```python
# Search audit events
events = await audit_logger.search_events(
    event_types=[AuditEventType.AUTH_FAILURE],
    principal_id="user-123",
    start_time=datetime.now() - timedelta(days=7),
    success=False,
    limit=100
)

# Generate compliance report
for event in events:
    print(f"{event.timestamp}: {event.principal_id} - {event.event_type}")
```

## 5. Security Integration (`integration.py`)

### 5.1 Security Middleware

The `SecurityMiddleware` class orchestrates all security components:

```python
middleware = SecurityMiddleware(
    auth_provider=multi_auth,
    access_control=access_control,
    rate_limiter=rate_limiter,
    audit_logger=audit_logger,
    anonymous_allowed=False,
    anonymous_permissions={"documents.read"}
)
```

### 5.2 Request Flow

1. **Authentication**: Extract and validate credentials
2. **Rate Limiting**: Check request limits
3. **Authorization**: Verify permissions
4. **Audit Logging**: Record security events
5. **Request Processing**: Execute if all checks pass

### 5.3 Integration with MCP Server

```python
# In server configuration
config = MCPConfig(
    security_enabled=True,
    auth_providers=["api_key", "oauth", "jwt"],
    anonymous_allowed=False,
    api_keys_file="/etc/mcp/api_keys.json",
    oauth_config_file="/etc/mcp/oauth.json",
    jwt_config_file="/etc/mcp/jwt.json",
    audit_log_file="/var/log/mcp/audit.log"
)

# Server automatically sets up security
server = ContextFrameMCPServer(dataset_path, config)
```

## 6. Threat Model and Security Guarantees

### 6.1 Threats Addressed

1. **Unauthorized Access**
   - Mitigated by: Multi-factor authentication, strong key generation
   - Residual risk: Compromised credentials

2. **Privilege Escalation**
   - Mitigated by: RBAC, resource policies, principle of least privilege
   - Residual risk: Misconfigured roles

3. **Denial of Service**
   - Mitigated by: Rate limiting, resource quotas
   - Residual risk: Distributed attacks

4. **Token/Session Hijacking**
   - Mitigated by: Token expiration, HTTPS enforcement, PKCE
   - Residual risk: Man-in-the-middle attacks

5. **Audit Trail Tampering**
   - Mitigated by: Append-only logs, secure storage
   - Residual risk: Privileged user abuse

### 6.2 Security Guarantees

1. **Authentication**: Every request is authenticated (unless anonymous allowed)
2. **Authorization**: All operations checked against permissions
3. **Non-repudiation**: Audit trail for all security events
4. **Rate Protection**: Prevents resource exhaustion
5. **Defense in Depth**: Multiple security layers

## 7. Configuration Examples

### 7.1 Development Configuration

```python
# Minimal security for development
dev_config = MCPConfig(
    security_enabled=True,
    auth_providers=["api_key"],
    anonymous_allowed=True,
    anonymous_permissions=["documents.read", "collections.read"]
)
```

### 7.2 Production Configuration

```python
# Full security for production
prod_config = MCPConfig(
    security_enabled=True,
    auth_providers=["oauth", "jwt"],
    anonymous_allowed=False,
    
    # OAuth configuration
    oauth_config_file="/secure/oauth_config.json",
    
    # JWT configuration  
    jwt_config_file="/secure/jwt_config.json",
    
    # Audit logging
    audit_log_file="/var/log/mcp/audit.log",
    audit_retention_days=365,
    
    # HTTPS only
    http_ssl_cert="/certs/server.crt",
    http_ssl_key="/certs/server.key"
)
```

### 7.3 Service Account Configuration

```python
# For automated services
service_config = {
    "api_keys": {
        "svc_analytics_prod": {
            "principal_id": "svc-analytics",
            "principal_type": "service",
            "principal_name": "Analytics Service",
            "permissions": ["documents.read", "monitoring.read"],
            "roles": ["service"],
            "expires_at": "2025-01-01T00:00:00Z"
        }
    }
}
```

## 8. Best Practices

### 8.1 Authentication

1. **API Keys**:
   - Rotate every 90 days
   - Use environment variables
   - Different keys per environment
   - Monitor key usage

2. **OAuth**:
   - Always use PKCE
   - Validate redirect URIs
   - Short-lived access tokens
   - Secure client secrets

3. **JWT**:
   - Use RS256 in production
   - Short expiration times
   - Include minimal claims
   - Rotate signing keys

### 8.2 Authorization

1. **Roles**:
   - Start with standard roles
   - Create custom roles sparingly
   - Regular permission audits
   - Document role purposes

2. **Policies**:
   - Be specific with resource IDs
   - Use conditions for context
   - Test policy combinations
   - Version policy changes

### 8.3 Rate Limiting

1. **Configuration**:
   - Start conservative
   - Monitor actual usage
   - Adjust based on patterns
   - Different limits per client type

2. **Handling**:
   - Respect Retry-After headers
   - Implement exponential backoff
   - Cache frequently accessed data
   - Batch operations when possible

### 8.4 Audit Logging

1. **Events**:
   - Log all security events
   - Include sufficient context
   - Avoid logging sensitive data
   - Use structured logging

2. **Retention**:
   - Follow compliance requirements
   - Archive old logs
   - Regular log analysis
   - Automated alerting

## 9. Common Pitfalls

### 9.1 Authentication

- **Pitfall**: Storing API keys in code
  - **Solution**: Use environment variables or secure vaults

- **Pitfall**: Long-lived tokens
  - **Solution**: Short expiration with refresh tokens

- **Pitfall**: Weak key generation
  - **Solution**: Use cryptographically secure methods

### 9.2 Authorization

- **Pitfall**: Over-permissive roles
  - **Solution**: Principle of least privilege

- **Pitfall**: Complex policy interactions
  - **Solution**: Keep policies simple and testable

- **Pitfall**: Missing resource checks
  - **Solution**: Always validate resource access

### 9.3 Rate Limiting

- **Pitfall**: Too restrictive limits
  - **Solution**: Monitor and adjust based on usage

- **Pitfall**: No burst allowance
  - **Solution**: Use token bucket for flexibility

- **Pitfall**: Ignoring operation costs
  - **Solution**: Different limits for expensive operations

### 9.4 Audit Logging

- **Pitfall**: Logging sensitive data
  - **Solution**: Implement redaction

- **Pitfall**: No log rotation
  - **Solution**: Implement retention policies

- **Pitfall**: Ignoring audit logs
  - **Solution**: Regular review and alerting

## 10. Security Deployment Checklist

### Pre-Deployment

- [ ] Generate strong API keys
- [ ] Configure OAuth providers
- [ ] Set up JWT signing keys
- [ ] Define roles and permissions
- [ ] Create resource policies
- [ ] Configure rate limits
- [ ] Set up audit logging
- [ ] Enable HTTPS
- [ ] Test authentication flows
- [ ] Test authorization rules
- [ ] Verify rate limiting
- [ ] Check audit trail

### Post-Deployment

- [ ] Monitor authentication failures
- [ ] Review authorization denials
- [ ] Track rate limit hits
- [ ] Analyze audit logs
- [ ] Update security policies
- [ ] Rotate credentials
- [ ] Security training
- [ ] Incident response plan

## Conclusion

The MCP security implementation provides a robust, enterprise-grade security system for protecting ContextFrame datasets. By following the configuration examples and best practices outlined in this document, you can ensure your MCP deployment is secure, compliant, and scalable.

The modular design allows you to enable only the security features you need, while the comprehensive nature ensures you can meet any security requirement. Regular monitoring of audit logs and security metrics will help maintain a strong security posture over time.