# ContextFrame MCP Server Architecture Analysis

## Overview

The ContextFrame MCP (Model Context Protocol) server provides a standardized API for LLMs and AI agents to interact with ContextFrame datasets. The architecture follows a modular, extensible design with clear separation of concerns and support for multiple transport mechanisms.

## Core Architecture Components

### 1. Main Server Component (`server.py`)

**ContextFrameMCPServer** is the central orchestrator that:
- Manages dataset connections via `FrameDataset`
- Initializes and coordinates all subsystems
- Handles graceful startup and shutdown
- Supports multiple transport types (stdio, HTTP, both)

**MCPConfig** dataclass provides comprehensive configuration:
- Server identity (name, version, protocol version)
- Transport selection and configuration
- HTTP-specific settings (host, port, CORS, SSL)
- Monitoring configuration (metrics, pricing, retention)
- Security configuration (auth providers, permissions, audit)

### 2. Message Handling (`handlers.py`)

**MessageHandler** implements the JSON-RPC 2.0 protocol:
- Routes incoming messages to appropriate handlers
- Validates requests and parameters
- Handles errors with proper JSON-RPC error responses
- Supports both request-response and notification patterns

Core message types handled:
- `initialize/initialized`: Protocol handshake
- `tools/list` and `tools/call`: Tool discovery and execution
- `resources/list` and `resources/read`: Resource access
- `shutdown`: Graceful termination

### 3. Tool System (`tools.py`)

**ToolRegistry** manages available tools:
- Document CRUD operations (add, get, list, update, delete)
- Search capabilities (vector, text, hybrid)
- Automatic tool registration and discovery
- Extensible architecture for additional tool modules

Tool categories:
- **Core document tools**: Basic CRUD and search
- **Enhancement tools**: LLM-powered document enrichment
- **Extraction tools**: Content extraction from various sources
- **Batch tools**: Bulk operations with transaction support
- **Collection tools**: Document organization and management
- **Subscription tools**: Change monitoring and notifications
- **Analytics tools**: Usage metrics and performance analysis

### 4. Resource System (`resources.py`)

**ResourceRegistry** provides dataset exploration:
- Dataset information and statistics
- Schema introspection
- Collection listings
- Relationship discovery
- URI-based resource addressing (`contextframe://`)

### 5. Transport Abstraction

#### Base Transport (`core/transport.py`)

**TransportAdapter** abstract base class defines:
- Message sending/receiving interface
- Progress reporting capabilities
- Subscription handling
- Streaming support detection

Key design decisions:
- Transport-agnostic tool implementations
- Unified progress and subscription handling
- Support for both streaming and polling models

#### Stdio Transport (`transports/stdio.py`)

**StdioAdapter** implements:
- Standard input/output communication
- Progress updates included in responses
- Polling-based subscriptions
- Backward compatibility with existing StdioTransport

#### HTTP Transport (`transports/http/`)

**HttpAdapter** provides HTTP-first architecture:
- Primary transport method with JSON responses
- Optional SSE (Server-Sent Events) for streaming
- Real-time progress tracking
- WebSocket-like subscriptions via SSE
- Operation context management

HTTP transport is designed as the primary MCP transport, with SSE as an optional enhancement for specific streaming use cases.

## Integration Layers

### 1. Monitoring Integration

**MonitoringSystem** wraps core components:
- **MetricsCollector**: Centralized metrics storage
- **UsageTracker**: Query and document access tracking
- **PerformanceMonitor**: Operation timing and profiling
- **CostCalculator**: Resource usage pricing

**MonitoredMessageHandler** and **MonitoredToolRegistry** provide:
- Automatic operation tracking
- Agent-specific metrics
- Tool usage statistics
- Document access patterns

### 2. Security Integration

**SecurityMiddleware** implements comprehensive security:
- **Authentication**: Multi-provider support (API key, OAuth, JWT)
- **Authorization**: Fine-grained permission control
- **Rate Limiting**: Request throttling and quotas
- **Audit Logging**: Comprehensive activity tracking

Security features:
- Anonymous access with configurable permissions
- Request metadata extraction and tracking
- Automatic audit trail generation
- Flexible authentication provider chaining

## Key Design Patterns

### 1. Dependency Injection
The server uses constructor injection for all major components, enabling:
- Easy testing with mock components
- Runtime configuration flexibility
- Clear dependency relationships

### 2. Adapter Pattern
Transport adapters provide a uniform interface while allowing transport-specific optimizations:
- Stdio uses buffered I/O and polling
- HTTP uses direct responses and SSE streaming

### 3. Registry Pattern
Tool and resource registries enable:
- Dynamic feature discovery
- Plugin-style extensibility
- Runtime tool registration

### 4. Middleware Pattern
Monitoring and security wrap core components:
- Transparent metric collection
- Non-intrusive security enforcement
- Composable behavior modification

### 5. Context Management
Operation contexts track long-running operations:
- Automatic cleanup on completion
- Progress tracking association
- Error handling and recovery

## Configuration Flexibility

The architecture supports multiple deployment scenarios:

1. **Minimal Setup**: Basic stdio transport with no monitoring/security
2. **Production HTTP**: Full HTTP server with auth, monitoring, and SSL
3. **Development Mode**: Both transports for maximum compatibility
4. **Enterprise**: Complete security, monitoring, and analytics

## Extension Points

1. **Custom Tools**: Register via ToolRegistry
2. **Auth Providers**: Implement AuthProvider interface
3. **Transport Types**: Extend TransportAdapter
4. **Metrics Backends**: Custom MetricsCollector implementations
5. **Resource Types**: Add new resource URIs

## Important Design Decisions

1. **HTTP-First Design**: While stdio is supported for compatibility, HTTP is the primary transport as it aligns with modern API practices and the MCP specification direction.

2. **Optional Streaming**: SSE is available but not required. Most operations use simple request-response patterns for reliability.

3. **Modular Security**: Security components can be enabled/disabled independently based on deployment needs.

4. **Backward Compatibility**: The architecture maintains compatibility with existing Lance datasets and FrameDataset APIs.

5. **Agent-Aware**: The system tracks agent IDs throughout for multi-tenant scenarios and usage attribution.

6. **Transaction Support**: Batch operations support atomic transactions with rollback capabilities.

7. **Async-First**: All components use async/await for scalability and non-blocking I/O.

## Performance Considerations

1. **Lazy Loading**: Components are initialized only when needed
2. **Connection Pooling**: Reuse database connections
3. **Streaming Responses**: Large results can be streamed
4. **Caching**: Frequently accessed resources are cached
5. **Batch Processing**: Bulk operations minimize round trips

## Security Architecture

1. **Defense in Depth**: Multiple security layers
2. **Zero Trust**: Authenticate and authorize every request
3. **Audit Everything**: Comprehensive logging for compliance
4. **Rate Limiting**: Prevent abuse and ensure fair usage
5. **Secure by Default**: Security enabled unless explicitly disabled

## Monitoring Architecture

1. **Non-Intrusive**: Monitoring doesn't affect core functionality
2. **Comprehensive**: Tracks all aspects of system behavior
3. **Performant**: Metrics collection is asynchronous
4. **Extensible**: Easy to add new metrics and monitors
5. **Cost-Aware**: Built-in support for usage-based pricing

## Future Extensibility

The architecture is designed to support:
1. Additional transport types (WebSocket, gRPC)
2. New tool categories (ML operations, data pipelines)
3. Advanced security features (mTLS, SAML)
4. Enhanced monitoring (distributed tracing, alerting)
5. Multi-dataset federation
6. Real-time collaboration features