# Configuration Guide

The ContextFrame MCP server offers flexible configuration options to suit various deployment scenarios, from development to production. This guide covers all configuration aspects.

## Configuration Overview

Configuration can be provided through:
1. **Configuration files** (YAML/JSON)
2. **Environment variables**
3. **Command-line arguments**
4. **Default values**

Priority order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Configuration Files

### Basic Configuration

Create a `contextframe-mcp.yaml` file:

```yaml
# Server configuration
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  
# Dataset configuration
dataset:
  path: /data/contextframe/dataset.lance
  create_if_missing: true
  
# Transport configuration
transport:
  type: http  # or "stdio"
  http:
    cors:
      enabled: true
      origins: ["http://localhost:3000"]
    
# Security configuration
security:
  enabled: true
  auth:
    type: api_key
    api_key: ${CONTEXTFRAME_API_KEY}
    
# Monitoring configuration
monitoring:
  enabled: true
  level: INFO
  metrics:
    enabled: true
    export_interval: 60
```

### Using the Configuration

```bash
# Specify config file
contextframe-mcp serve --config /path/to/config.yaml

# Or use default location
# Looks for: ./contextframe-mcp.yaml, ~/.contextframe/mcp.yaml
contextframe-mcp serve
```

## Environment Variables

All configuration options can be set via environment variables:

```bash
# Server settings
export CONTEXTFRAME_HOST=0.0.0.0
export CONTEXTFRAME_PORT=8000
export CONTEXTFRAME_WORKERS=4

# Dataset settings
export CONTEXTFRAME_DATASET_PATH=/data/dataset.lance
export CONTEXTFRAME_DATASET_CREATE_IF_MISSING=true

# Security settings
export CONTEXTFRAME_SECURITY_ENABLED=true
export CONTEXTFRAME_API_KEY=your-secret-key

# Monitoring settings
export CONTEXTFRAME_MONITORING_ENABLED=true
export CONTEXTFRAME_LOG_LEVEL=INFO
```

### Environment Variable Naming

- Prefix: `CONTEXTFRAME_`
- Nested values use underscores: `CONTEXTFRAME_SECURITY_AUTH_TYPE`
- Lists use comma separation: `CONTEXTFRAME_CORS_ORIGINS=http://localhost:3000,https://app.example.com`

## Configuration Sections

### Server Configuration

Basic server settings:

```yaml
server:
  # Network binding
  host: 0.0.0.0              # Listen address
  port: 8000                 # Listen port
  
  # Performance
  workers: 4                 # Number of worker processes
  worker_class: uvicorn      # Worker type
  
  # Timeouts
  timeout: 30                # Request timeout (seconds)
  keepalive: 5               # Keep-alive timeout
  
  # SSL/TLS
  ssl:
    enabled: false
    cert_file: /path/to/cert.pem
    key_file: /path/to/key.pem
    
  # Development
  reload: false              # Auto-reload on changes
  debug: false               # Debug mode
```

### Dataset Configuration

Lance dataset settings:

```yaml
dataset:
  # Primary dataset
  path: /data/dataset.lance
  create_if_missing: true
  
  # Storage backend
  storage:
    type: local              # local, s3, gcs, azure
    options:
      # S3 example
      # bucket: my-bucket
      # region: us-east-1
      # access_key_id: ${AWS_ACCESS_KEY_ID}
      # secret_access_key: ${AWS_SECRET_ACCESS_KEY}
  
  # Performance
  cache:
    enabled: true
    size_mb: 1024            # Cache size in MB
    ttl_seconds: 3600        # Cache TTL
    
  # Indexing
  index:
    vector:
      enabled: true
      dimensions: 768        # Embedding dimensions
      metric: cosine         # cosine, euclidean, dot
    text:
      enabled: true
      analyzer: standard     # standard, english, multilingual
```

### Security Configuration

Detailed security guide at [Security Configuration](security.md):

```yaml
security:
  enabled: true
  
  # Authentication
  auth:
    type: multiple           # api_key, bearer, basic, oauth2, multiple
    providers:
      - type: api_key
        header: X-API-Key
        keys:
          - ${API_KEY_1}
          - ${API_KEY_2}
      - type: bearer
        jwt:
          secret: ${JWT_SECRET}
          algorithm: HS256
          
  # Authorization
  authorization:
    enabled: true
    default_role: reader
    roles:
      reader:
        - tools:read
        - documents:read
      writer:
        - tools:*
        - documents:*
        - collections:*
        
  # Rate limiting
  rate_limiting:
    enabled: true
    default:
      requests: 100
      window: 60             # seconds
    by_endpoint:
      search_documents:
        requests: 50
        window: 60
```

### Monitoring Configuration

Detailed monitoring guide at [Monitoring Setup](monitoring.md):

```yaml
monitoring:
  # Logging
  logging:
    level: INFO              # DEBUG, INFO, WARNING, ERROR
    format: json             # json, text
    output: stdout           # stdout, file
    file:
      path: /var/log/contextframe/mcp.log
      rotation: daily
      retention: 7           # days
      
  # Metrics
  metrics:
    enabled: true
    backend: prometheus      # prometheus, statsd
    export_interval: 60      # seconds
    endpoint: /metrics
    
  # Tracing
  tracing:
    enabled: false
    backend: jaeger          # jaeger, zipkin
    sample_rate: 0.1         # 10% sampling
    endpoint: http://localhost:14268
    
  # Health checks
  health:
    enabled: true
    endpoint: /health
    checks:
      - dataset
      - memory
      - disk
```

### Transport Configuration

Transport-specific settings:

```yaml
transport:
  type: http                 # http, stdio
  
  # HTTP transport
  http:
    # CORS
    cors:
      enabled: true
      origins: ["*"]         # Or specific origins
      methods: ["GET", "POST"]
      headers: ["Content-Type", "Authorization"]
      
    # Compression
    compression:
      enabled: true
      min_size: 1024         # Minimum size to compress
      
    # Request limits
    limits:
      max_request_size: 10485760  # 10MB
      max_header_size: 8192       # 8KB
      
  # Stdio transport
  stdio:
    buffer_size: 8192
    encoding: utf-8
    line_delimiter: "\n"
```

## Advanced Configuration

### Multi-Environment Setup

Use different configs for each environment:

```yaml
# config/development.yaml
extends: base.yaml
server:
  debug: true
  reload: true
security:
  enabled: false

# config/production.yaml
extends: base.yaml
server:
  workers: 8
security:
  enabled: true
  auth:
    type: oauth2
```

### Dynamic Configuration

Load configuration from external sources:

```yaml
# Load from AWS Parameter Store
config_source:
  type: aws_parameter_store
  prefix: /contextframe/mcp/
  region: us-east-1

# Load from Kubernetes ConfigMap
config_source:
  type: kubernetes
  configmap: contextframe-mcp-config
  namespace: default
```

### Feature Flags

Enable/disable features:

```yaml
features:
  # Experimental features
  experimental:
    streaming_search: false
    graph_relationships: false
    
  # Beta features
  beta:
    advanced_analytics: true
    custom_embeddings: true
```

## Configuration Validation

The server validates configuration on startup:

```bash
# Validate configuration without starting
contextframe-mcp validate-config --config config.yaml

# Show effective configuration
contextframe-mcp show-config --config config.yaml
```

## Common Configurations

### Development Setup

```yaml
server:
  host: localhost
  port: 8000
  reload: true
  debug: true
  
dataset:
  path: ./dev-dataset.lance
  create_if_missing: true
  
security:
  enabled: false
  
monitoring:
  logging:
    level: DEBUG
```

### Production Setup

```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: ${WORKERS:-4}
  ssl:
    enabled: true
    cert_file: /etc/ssl/certs/server.crt
    key_file: /etc/ssl/private/server.key
    
dataset:
  path: s3://my-bucket/prod-dataset.lance
  storage:
    type: s3
    options:
      region: ${AWS_REGION}
      
security:
  enabled: true
  auth:
    type: oauth2
    oauth2:
      issuer: https://auth.example.com
      audience: contextframe-mcp
      
monitoring:
  metrics:
    enabled: true
  tracing:
    enabled: true
    sample_rate: 0.1
```

### Docker Setup

```yaml
server:
  host: 0.0.0.0  # Important for Docker
  port: ${PORT:-8000}
  
dataset:
  path: /data/dataset.lance
  
# Use environment variables for secrets
security:
  auth:
    api_key: ${API_KEY}
```

## Configuration Best Practices

1. **Use Environment Variables for Secrets**
   ```yaml
   api_key: ${API_KEY}  # Good
   api_key: "hardcoded-key"  # Bad
   ```

2. **Separate Configs by Environment**
   - `config/base.yaml` - Shared settings
   - `config/dev.yaml` - Development
   - `config/prod.yaml` - Production

3. **Version Control Configuration**
   - Check in configuration files
   - Never commit secrets
   - Use `.gitignore` for local overrides

4. **Validate Before Deployment**
   ```bash
   contextframe-mcp validate-config --config prod.yaml
   ```

5. **Monitor Configuration Changes**
   - Log configuration on startup
   - Track configuration in monitoring
   - Alert on configuration errors

## Troubleshooting

### Configuration Not Loading

```bash
# Check configuration search paths
contextframe-mcp show-config-paths

# Validate YAML syntax
yamllint contextframe-mcp.yaml

# Check environment variables
env | grep CONTEXTFRAME_
```

### Invalid Configuration

```bash
# Show validation errors
contextframe-mcp validate-config --config config.yaml --verbose

# Test with minimal config
contextframe-mcp serve --config minimal.yaml
```

### Performance Issues

Check these settings:
- `workers`: Match CPU cores
- `cache.size_mb`: Increase for better performance
- `timeout`: Adjust for slow operations

## Next Steps

- [Security Configuration](security.md) - Detailed security setup
- [Monitoring Setup](monitoring.md) - Configure metrics and logging
- [Production Deployment](../guides/production-deployment.md) - Best practices
- [Performance Tuning](../guides/performance.md) - Optimization guide