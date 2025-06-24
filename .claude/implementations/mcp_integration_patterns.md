# MCP Integration Patterns and Real-World Use Cases

## Table of Contents
1. [Client Integration Patterns](#client-integration-patterns)
2. [Agent Integration Approaches](#agent-integration-approaches)
3. [Common Integration Scenarios](#common-integration-scenarios)
4. [Best Practices](#best-practices)
5. [Testing Patterns](#testing-patterns)
6. [Production Deployment](#production-deployment)
7. [Real-World Architecture Examples](#real-world-architecture-examples)

## Client Integration Patterns

### 1. Basic Stdio Client Pattern

The simplest integration for local development and testing:

```python
# contextframe/mcp/example_client.py pattern
class MCPClient:
    """Simple MCP client for stdio communication."""
    
    async def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an RPC call and wait for response."""
        await self.send_message(method, params)
        response = await self.read_response()
        
        if "error" in response:
            raise Exception(f"RPC Error: {response['error']}")
        
        return response.get("result", {})
```

**Use Cases:**
- Development and testing
- CLI tools
- Simple automation scripts
- Local agent integrations

### 2. HTTP-First Client Pattern (Recommended)

Modern approach using standard HTTP for reliability and scalability:

```python
# contextframe/mcp/http_client_example.py pattern
class MCPHttpClient:
    """HTTP client for MCP server - recommended approach."""
    
    async def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request using standard HTTP."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._next_id()
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/v1/jsonrpc",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")
        
        return result.get("result", {})
```

**Key Features:**
- Standard HTTP POST for all operations
- Convenience REST endpoints for common operations
- Optional SSE for progress tracking
- Built-in retry and timeout handling

### 3. Tool Discovery Pattern

Dynamic tool discovery for flexible integrations:

```python
async def discover_and_use_tools(client: MCPHttpClient):
    # 1. Initialize session
    init_result = await client.initialize({
        "name": "my-agent",
        "version": "1.0.0"
    })
    
    # 2. Discover available tools
    tools = await client.list_tools()
    tool_map = {tool['name']: tool for tool in tools['tools']}
    
    # 3. Dynamically call tools based on schema
    if "search_documents" in tool_map:
        schema = tool_map["search_documents"]["inputSchema"]
        # Parse schema to understand required/optional params
        
        result = await client.call_tool(
            "search_documents",
            {"query": "important topic", "limit": 10}
        )
```

### 4. Error Handling Pattern

Robust error handling with retry logic:

```python
async def robust_mcp_call(client, method, params, max_retries=3):
    """Call MCP method with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return await client.request(method, params)
        except Exception as e:
            if "error" in str(e):
                error_data = json.loads(str(e).split("MCP Error: ")[1])
                error_code = error_data.get("code", 0)
                
                # Don't retry client errors
                if -32600 <= error_code <= -32602:
                    raise
                
                # Retry server errors with backoff
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            raise
```

## Agent Integration Approaches

### 1. LangChain Integration Pattern

```python
from langchain.tools import Tool
from langchain.agents import AgentExecutor

class ContextFrameMCPTool:
    """LangChain tool wrapper for MCP."""
    
    def __init__(self, mcp_client: MCPHttpClient, tool_name: str, tool_schema: dict):
        self.client = mcp_client
        self.tool_name = tool_name
        self.schema = tool_schema
    
    async def _run(self, **kwargs):
        """Execute the MCP tool."""
        return await self.client.call_tool(self.tool_name, kwargs)
    
    def to_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name=self.tool_name,
            func=self._run,
            description=self.schema.get("description", ""),
            args_schema=self._schema_to_pydantic(self.schema["inputSchema"])
        )

# Usage
async def create_langchain_agent(mcp_url: str):
    client = MCPHttpClient(mcp_url)
    await client.initialize({"name": "langchain-agent"})
    
    # Get all tools
    tools_response = await client.list_tools()
    
    # Convert to LangChain tools
    langchain_tools = []
    for tool in tools_response["tools"]:
        wrapper = ContextFrameMCPTool(client, tool["name"], tool)
        langchain_tools.append(wrapper.to_langchain_tool())
    
    # Create agent with tools
    agent = AgentExecutor(tools=langchain_tools, ...)
```

### 2. Function Calling Pattern

For LLMs with function calling capabilities:

```python
async def prepare_function_definitions(client: MCPHttpClient):
    """Convert MCP tools to function definitions for LLMs."""
    tools = await client.list_tools()
    
    functions = []
    for tool in tools["tools"]:
        function_def = {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool["inputSchema"]
        }
        functions.append(function_def)
    
    return functions

async def execute_function_call(client: MCPHttpClient, function_call):
    """Execute function call from LLM."""
    return await client.call_tool(
        function_call["name"],
        json.loads(function_call["arguments"])
    )
```

### 3. Context Window Management

Efficiently managing large datasets within token limits:

```python
class ContextWindowManager:
    """Manage document retrieval within token limits."""
    
    def __init__(self, client: MCPHttpClient, max_tokens: int = 100000):
        self.client = client
        self.max_tokens = max_tokens
        self.token_counter = TikTokenCounter()  # Or your preferred counter
    
    async def get_relevant_context(self, query: str, max_docs: int = 20):
        """Get relevant documents within token limit."""
        # Start with more documents than needed
        search_result = await self.client.call_tool(
            "search_documents",
            {
                "query": query,
                "limit": max_docs * 2,
                "include_content": False  # Get metadata first
            }
        )
        
        # Sort by relevance score
        docs = sorted(
            search_result["documents"], 
            key=lambda d: d.get("score", 0), 
            reverse=True
        )
        
        # Add documents until token limit
        selected_docs = []
        total_tokens = 0
        
        for doc in docs:
            # Get full content
            full_doc = await self.client.call_tool(
                "get_document",
                {
                    "document_id": doc["uuid"],
                    "include_content": True
                }
            )
            
            doc_tokens = self.token_counter.count(full_doc["document"]["content"])
            if total_tokens + doc_tokens <= self.max_tokens:
                selected_docs.append(full_doc["document"])
                total_tokens += doc_tokens
            else:
                break
        
        return selected_docs
```

### 4. Streaming Results Pattern

For handling large result sets:

```python
async def stream_search_results(client: MCPHttpClient, query: str, batch_size: int = 100):
    """Stream search results in batches."""
    offset = 0
    
    while True:
        result = await client.call_tool(
            "search_documents",
            {
                "query": query,
                "limit": batch_size,
                "offset": offset
            }
        )
        
        documents = result.get("documents", [])
        if not documents:
            break
            
        for doc in documents:
            yield doc
            
        offset += batch_size
```

## Common Integration Scenarios

### 1. RAG Application Pattern

Complete RAG implementation with ContextFrame:

```python
class ContextFrameRAG:
    """RAG application using ContextFrame MCP."""
    
    def __init__(self, mcp_url: str, llm_client):
        self.mcp_client = MCPHttpClient(mcp_url)
        self.llm = llm_client
        self.context_manager = ContextWindowManager(self.mcp_client)
    
    async def initialize(self):
        await self.mcp_client.initialize({
            "name": "rag-application",
            "version": "1.0.0"
        })
    
    async def answer_question(self, question: str):
        # 1. Search for relevant documents
        relevant_docs = await self.context_manager.get_relevant_context(
            question, 
            max_docs=10
        )
        
        # 2. Build context
        context = "\n\n".join([
            f"Document {i+1} (ID: {doc['uuid']}):\n{doc['content']}"
            for i, doc in enumerate(relevant_docs)
        ])
        
        # 3. Generate answer
        prompt = f"""
        Based on the following documents, answer the question.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        response = await self.llm.generate(prompt)
        
        # 4. Track usage for analytics
        await self.mcp_client.call_tool(
            "track_usage",
            {
                "operation": "rag_query",
                "document_ids": [doc['uuid'] for doc in relevant_docs],
                "query": question
            }
        )
        
        return {
            "answer": response,
            "sources": [
                {
                    "id": doc['uuid'],
                    "title": doc['metadata'].get('title', 'Untitled'),
                    "excerpt": doc['content'][:200] + "..."
                }
                for doc in relevant_docs
            ]
        }
```

### 2. Document Processing Pipeline

Batch processing with progress tracking:

```python
class DocumentProcessingPipeline:
    """Process documents through multiple stages."""
    
    def __init__(self, mcp_url: str):
        self.client = MCPHttpClient(mcp_url)
    
    async def process_documents(self, file_paths: List[str]):
        # 1. Batch import documents
        import_result = await self.client.call_tool(
            "batch_import",
            {
                "file_paths": file_paths,
                "shared_settings": {
                    "generate_embeddings": False,  # We'll do this later
                    "metadata": {
                        "source": "batch_import",
                        "processed_date": datetime.now().isoformat()
                    }
                }
            }
        )
        
        operation_id = import_result.get("operation_id")
        if operation_id:
            # Track progress via SSE
            await self._track_operation(operation_id)
        
        document_ids = import_result.get("document_ids", [])
        
        # 2. Extract metadata
        extract_result = await self.client.call_tool(
            "batch_extract",
            {
                "document_ids": document_ids,
                "extraction_type": "metadata",
                "max_parallel": 5
            }
        )
        
        # 3. Enhance documents
        enhance_result = await self.client.call_tool(
            "batch_enhance",
            {
                "document_ids": document_ids,
                "enhancements": ["summary", "keywords", "entities"],
                "max_parallel": 3
            }
        )
        
        # 4. Generate embeddings
        embed_result = await self.client.call_tool(
            "batch_generate_embeddings",
            {
                "document_ids": document_ids,
                "model": "text-embedding-3-small",
                "batch_size": 100
            }
        )
        
        return {
            "total_processed": len(document_ids),
            "import": import_result,
            "extract": extract_result,
            "enhance": enhance_result,
            "embed": embed_result
        }
    
    async def _track_operation(self, operation_id: str):
        """Track long-running operation progress."""
        async for progress in self.client.track_operation_progress(operation_id):
            print(f"Progress: {progress['current']}/{progress['total']} - {progress.get('message', '')}")
            if progress.get("status") == "completed":
                break
```

### 3. Real-Time Monitoring Pattern

Monitor dataset changes with subscriptions:

```python
class DatasetMonitor:
    """Monitor dataset for changes."""
    
    def __init__(self, mcp_url: str):
        self.client = MCPHttpClient(mcp_url)
        self.handlers = {}
    
    async def monitor_changes(self, resource_type: str = "documents", filter: str = None):
        """Monitor dataset changes via SSE."""
        url = f"{self.client.base_url}/mcp/v1/sse/subscribe"
        params = {"resource_type": resource_type}
        if filter:
            params["filter"] = filter
        
        async with self.client.client.stream("GET", url, params=params) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    change = json.loads(line[6:])
                    await self._handle_change(change)
    
    async def _handle_change(self, change: dict):
        """Handle dataset change event."""
        change_type = change.get("type")
        handler = self.handlers.get(change_type)
        
        if handler:
            await handler(change)
        else:
            print(f"Unhandled change type: {change_type}")
    
    def on_document_added(self, handler):
        """Register handler for document additions."""
        self.handlers["document_added"] = handler
    
    def on_document_updated(self, handler):
        """Register handler for document updates."""
        self.handlers["document_updated"] = handler
```

### 4. Analytics Dashboard Pattern

Real-time analytics and monitoring:

```python
class AnalyticsDashboard:
    """Analytics dashboard for ContextFrame datasets."""
    
    def __init__(self, mcp_url: str):
        self.client = MCPHttpClient(mcp_url)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def get_dashboard_data(self):
        """Get comprehensive dashboard data."""
        # Use analytics tools
        tasks = [
            self._get_cached("stats", self._get_dataset_stats),
            self._get_cached("usage", self._get_usage_analysis),
            self._get_cached("performance", self._get_query_performance),
            self._get_cached("relationships", self._get_relationship_analysis)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "stats": results[0],
            "usage": results[1],
            "performance": results[2],
            "relationships": results[3],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_cached(self, key: str, fetcher):
        """Get cached data or fetch if expired."""
        cached = self._cache.get(key)
        if cached and (datetime.now() - cached["timestamp"]).seconds < self._cache_ttl:
            return cached["data"]
        
        data = await fetcher()
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        return data
    
    async def _get_dataset_stats(self):
        result = await self.client.call_tool(
            "get_dataset_stats",
            {"include_details": True}
        )
        return result["stats"]
    
    async def _get_usage_analysis(self):
        result = await self.client.call_tool(
            "analyze_usage",
            {"time_range": "7d", "include_patterns": True}
        )
        return result["analysis"]
```

## Best Practices

### 1. Connection Management

```python
class ManagedMCPClient:
    """MCP client with connection pooling and health checks."""
    
    def __init__(self, base_url: str, pool_size: int = 10):
        self.base_url = base_url
        limits = httpx.Limits(max_keepalive_connections=pool_size)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=limits,
            http2=True  # Enable HTTP/2 for better performance
        )
        self._initialized = False
    
    async def ensure_initialized(self):
        """Ensure client is initialized."""
        if not self._initialized:
            await self.initialize()
    
    async def initialize(self):
        """Initialize with retry logic."""
        for attempt in range(3):
            try:
                result = await self.request("initialize", {
                    "protocolVersion": "0.1.0",
                    "clientInfo": {"name": "managed-client"}
                })
                self._initialized = True
                return result
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
    
    async def health_check(self):
        """Perform health check."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
```

### 2. Authentication Patterns

```python
class AuthenticatedMCPClient(MCPHttpClient):
    """MCP client with authentication support."""
    
    def __init__(self, base_url: str, auth_token: str = None):
        super().__init__(base_url)
        self.auth_token = auth_token
    
    async def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send authenticated request."""
        headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._next_id()
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/v1/jsonrpc",
            json=payload,
            headers=headers
        )
        
        # Handle 401 and refresh token if needed
        if response.status_code == 401:
            await self._refresh_token()
            # Retry request
            return await self.request(method, params)
        
        response.raise_for_status()
        return response.json().get("result", {})
```

### 3. Error Recovery Patterns

```python
class ResilientMCPClient:
    """MCP client with circuit breaker and fallback."""
    
    def __init__(self, primary_url: str, fallback_url: str = None):
        self.primary_client = MCPHttpClient(primary_url)
        self.fallback_client = MCPHttpClient(fallback_url) if fallback_url else None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call tool with circuit breaker and fallback."""
        # Try primary
        if not self.circuit_breaker.is_open():
            try:
                result = await self.primary_client.call_tool(tool_name, arguments)
                self.circuit_breaker.record_success()
                return result
            except Exception as e:
                self.circuit_breaker.record_failure()
                if not self.fallback_client:
                    raise
        
        # Try fallback
        if self.fallback_client:
            return await self.fallback_client.call_tool(tool_name, arguments)
        
        raise Exception("Primary service unavailable and no fallback configured")
```

### 4. Performance Optimization

```python
class OptimizedMCPClient:
    """MCP client with caching and batching."""
    
    def __init__(self, base_url: str):
        self.client = MCPHttpClient(base_url)
        self.cache = TTLCache(maxsize=1000, ttl=300)
        self.batch_queue = []
        self.batch_lock = asyncio.Lock()
    
    async def get_document_cached(self, document_id: str):
        """Get document with caching."""
        cache_key = f"doc:{document_id}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.client.call_tool(
            "get_document",
            {"document_id": document_id, "include_content": True}
        )
        
        self.cache[cache_key] = result["document"]
        return result["document"]
    
    async def batch_get_documents(self, document_ids: List[str]):
        """Get multiple documents efficiently."""
        # Check cache first
        cached_docs = {}
        missing_ids = []
        
        for doc_id in document_ids:
            cache_key = f"doc:{doc_id}"
            if cache_key in self.cache:
                cached_docs[doc_id] = self.cache[cache_key]
            else:
                missing_ids.append(doc_id)
        
        # Batch fetch missing documents
        if missing_ids:
            result = await self.client.call_tool(
                "batch_get_documents",
                {"document_ids": missing_ids}
            )
            
            for doc in result["documents"]:
                doc_id = doc["uuid"]
                self.cache[f"doc:{doc_id}"] = doc
                cached_docs[doc_id] = doc
        
        # Return in requested order
        return [cached_docs[doc_id] for doc_id in document_ids if doc_id in cached_docs]
```

## Testing Patterns

### 1. Mock MCP Server

```python
class MockMCPServer:
    """Mock MCP server for testing."""
    
    def __init__(self):
        self.tools = {}
        self.documents = {}
        self.call_history = []
    
    async def handle_request(self, request: dict):
        """Handle mock request."""
        self.call_history.append(request)
        
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
                "protocolVersion": "0.1.0",
                "serverInfo": {"name": "mock-server"},
                "capabilities": {"tools": True}
            }
        
        elif method == "tools/list":
            return {"tools": list(self.tools.values())}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            if tool_name in self.tools:
                handler = self.tools[tool_name]["handler"]
                return await handler(params.get("arguments", {}))
        
        raise Exception(f"Unknown method: {method}")
    
    def register_mock_tool(self, name: str, handler, schema: dict):
        """Register a mock tool."""
        self.tools[name] = {
            "name": name,
            "inputSchema": schema,
            "handler": handler
        }
```

### 2. Integration Test Pattern

```python
@pytest.fixture
async def mcp_test_client(tmp_path):
    """Create test MCP client with temporary dataset."""
    # Create temporary dataset
    dataset_path = tmp_path / "test.lance"
    dataset = FrameDataset.create(str(dataset_path))
    
    # Add test data
    test_records = [
        FrameRecord(text_content=f"Test document {i}", metadata={"index": i})
        for i in range(10)
    ]
    dataset.add_many(test_records)
    
    # Start test server
    config = MCPConfig(transport="http", host="localhost", port=0)
    server = await create_http_server(str(dataset_path), config)
    
    # Start server in background
    server_task = asyncio.create_task(
        uvicorn.run(server.app, host="localhost", port=0)
    )
    
    # Create client
    client = MCPHttpClient(f"http://localhost:{server.port}")
    await client.initialize({"name": "test-client"})
    
    yield client
    
    # Cleanup
    server_task.cancel()
    await server_task
```

### 3. Tool Testing Strategy

```python
class TestSearchTool:
    """Test search tool functionality."""
    
    @pytest.mark.asyncio
    async def test_search_basic(self, mcp_test_client):
        """Test basic search functionality."""
        result = await mcp_test_client.call_tool(
            "search_documents",
            {"query": "test", "limit": 5}
        )
        
        assert "documents" in result
        assert len(result["documents"]) <= 5
        assert all("test" in doc["content"].lower() for doc in result["documents"])
    
    @pytest.mark.asyncio
    async def test_search_with_filter(self, mcp_test_client):
        """Test search with SQL filter."""
        result = await mcp_test_client.call_tool(
            "search_documents",
            {
                "query": "document",
                "filter": "metadata.index > 5",
                "limit": 10
            }
        )
        
        assert all(doc["metadata"]["index"] > 5 for doc in result["documents"])
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, mcp_test_client):
        """Test search error handling."""
        with pytest.raises(Exception) as exc_info:
            await mcp_test_client.call_tool(
                "search_documents",
                {"query": "test", "search_type": "invalid"}
            )
        
        assert "Invalid search type" in str(exc_info.value)
```

## Production Deployment

### 1. Load Balancing Pattern

```python
class LoadBalancedMCPClient:
    """Client with load balancing across multiple servers."""
    
    def __init__(self, server_urls: List[str], strategy: str = "round_robin"):
        self.clients = [MCPHttpClient(url) for url in server_urls]
        self.strategy = strategy
        self.current_index = 0
        self.health_checker = HealthChecker(self.clients)
    
    async def initialize(self):
        """Initialize all clients."""
        tasks = [client.initialize({"name": "lb-client"}) for client in self.clients]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Start health checking
        asyncio.create_task(self.health_checker.start())
    
    def _get_client(self) -> MCPHttpClient:
        """Get next healthy client based on strategy."""
        healthy_clients = self.health_checker.get_healthy_clients()
        
        if not healthy_clients:
            raise Exception("No healthy MCP servers available")
        
        if self.strategy == "round_robin":
            client = healthy_clients[self.current_index % len(healthy_clients)]
            self.current_index += 1
            return client
        
        elif self.strategy == "random":
            return random.choice(healthy_clients)
        
        elif self.strategy == "least_connections":
            # In production, track active connections per client
            return min(healthy_clients, key=lambda c: c.active_connections)
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call tool on load balanced server."""
        client = self._get_client()
        return await client.call_tool(tool_name, arguments)
```

### 2. Dataset Sharding Strategy

```python
class ShardedMCPClient:
    """Client for sharded dataset deployment."""
    
    def __init__(self, shard_config: Dict[str, str]):
        """
        shard_config: {
            "shard_1": "http://shard1.example.com",
            "shard_2": "http://shard2.example.com",
            ...
        }
        """
        self.shards = {
            name: MCPHttpClient(url) 
            for name, url in shard_config.items()
        }
        self.shard_router = ConsistentHashRouter(list(self.shards.keys()))
    
    async def initialize(self):
        """Initialize all shard clients."""
        tasks = [
            client.initialize({"name": f"sharded-client-{name}"})
            for name, client in self.shards.items()
        ]
        await asyncio.gather(*tasks)
    
    def _get_shard_for_document(self, document_id: str) -> MCPHttpClient:
        """Route document to appropriate shard."""
        shard_name = self.shard_router.get_node(document_id)
        return self.shards[shard_name]
    
    async def add_document(self, content: str, metadata: dict):
        """Add document to appropriate shard."""
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Route to shard
        client = self._get_shard_for_document(doc_id)
        
        return await client.call_tool(
            "add_document",
            {
                "content": content,
                "metadata": {**metadata, "shard": client.base_url},
                "uuid": doc_id
            }
        )
    
    async def search_all_shards(self, query: str, limit: int = 10):
        """Search across all shards and merge results."""
        # Query all shards in parallel
        tasks = [
            client.call_tool(
                "search_documents",
                {"query": query, "limit": limit}
            )
            for client in self.shards.values()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Merge and sort results
        all_documents = []
        for result in results:
            all_documents.extend(result.get("documents", []))
        
        # Sort by score and limit
        all_documents.sort(key=lambda d: d.get("score", 0), reverse=True)
        
        return {
            "documents": all_documents[:limit],
            "total_found": len(all_documents),
            "shards_queried": len(self.shards)
        }
```

### 3. Caching and CDN Integration

```python
class CachedMCPClient:
    """MCP client with multi-layer caching."""
    
    def __init__(self, base_url: str, redis_url: str = None):
        self.client = MCPHttpClient(base_url)
        self.local_cache = TTLCache(maxsize=1000, ttl=300)
        
        if redis_url:
            self.redis_client = aioredis.from_url(redis_url)
        else:
            self.redis_client = None
    
    async def get_document_with_cache(self, document_id: str):
        """Get document with multi-layer caching."""
        # Check local cache
        if document_id in self.local_cache:
            return self.local_cache[document_id]
        
        # Check Redis cache
        if self.redis_client:
            cached = await self.redis_client.get(f"doc:{document_id}")
            if cached:
                doc = json.loads(cached)
                self.local_cache[document_id] = doc
                return doc
        
        # Fetch from MCP server
        result = await self.client.call_tool(
            "get_document",
            {"document_id": document_id, "include_content": True}
        )
        
        doc = result["document"]
        
        # Update caches
        self.local_cache[document_id] = doc
        if self.redis_client:
            await self.redis_client.setex(
                f"doc:{document_id}",
                300,  # 5 minute TTL
                json.dumps(doc)
            )
        
        return doc
    
    async def invalidate_cache(self, document_id: str):
        """Invalidate cache entries for a document."""
        # Remove from local cache
        self.local_cache.pop(document_id, None)
        
        # Remove from Redis
        if self.redis_client:
            await self.redis_client.delete(f"doc:{document_id}")
```

### 4. Monitoring and Alerting

```python
class MonitoredMCPClient:
    """MCP client with comprehensive monitoring."""
    
    def __init__(self, base_url: str, metrics_collector):
        self.client = MCPHttpClient(base_url)
        self.metrics = metrics_collector
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call tool with monitoring."""
        start_time = time.time()
        error = None
        
        try:
            result = await self.client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            self.metrics.record_tool_call(
                tool_name=tool_name,
                duration=duration,
                success=error is None,
                error_type=type(error).__name__ if error else None
            )
            
            # Alert on slow operations
            if duration > 5.0:
                await self.metrics.send_alert(
                    f"Slow MCP operation: {tool_name} took {duration:.2f}s"
                )
            
            # Alert on errors
            if error and not isinstance(error, (InvalidParams, DocumentNotFound)):
                await self.metrics.send_alert(
                    f"MCP operation failed: {tool_name} - {error}"
                )
```

## Real-World Architecture Examples

### 1. Enterprise RAG System

```yaml
# Architecture Overview
components:
  load_balancer:
    type: nginx
    health_check: /health
    
  mcp_servers:
    - host: mcp1.internal
      dataset: primary_shard
    - host: mcp2.internal
      dataset: secondary_shard
      
  cache_layer:
    redis_cluster:
      nodes: 3
      memory: 16GB
      
  cdn:
    cloudflare:
      cache_rules:
        - path: /mcp/v1/resources/*
          ttl: 3600
          
  monitoring:
    prometheus:
      scrape_interval: 15s
    grafana:
      dashboards:
        - mcp_operations
        - dataset_health
        - query_performance
```

### 2. Multi-Tenant SaaS Platform

```python
class MultiTenantMCPClient:
    """MCP client for multi-tenant SaaS."""
    
    def __init__(self, tenant_router):
        self.tenant_router = tenant_router
        self.tenant_clients = {}
    
    async def get_client_for_tenant(self, tenant_id: str) -> MCPHttpClient:
        """Get or create client for tenant."""
        if tenant_id not in self.tenant_clients:
            # Get tenant configuration
            config = await self.tenant_router.get_tenant_config(tenant_id)
            
            # Create isolated client
            client = MCPHttpClient(config["mcp_url"])
            await client.initialize({
                "name": f"tenant-{tenant_id}",
                "tenant_id": tenant_id
            })
            
            self.tenant_clients[tenant_id] = client
        
        return self.tenant_clients[tenant_id]
    
    async def call_tool_for_tenant(
        self, 
        tenant_id: str, 
        tool_name: str, 
        arguments: dict
    ):
        """Call tool in tenant context."""
        client = await self.get_client_for_tenant(tenant_id)
        
        # Add tenant context to all operations
        arguments["_tenant_id"] = tenant_id
        
        return await client.call_tool(tool_name, arguments)
```

### 3. Real-Time Analytics Platform

```python
class RealTimeAnalyticsPlatform:
    """Real-time analytics using MCP subscriptions."""
    
    def __init__(self, mcp_urls: List[str]):
        self.clients = [MCPHttpClient(url) for url in mcp_urls]
        self.event_processor = EventProcessor()
        self.dashboard_manager = DashboardManager()
    
    async def start_monitoring(self):
        """Start monitoring all MCP servers."""
        # Initialize clients
        for client in self.clients:
            await client.initialize({"name": "analytics-platform"})
        
        # Start subscriptions
        tasks = []
        for i, client in enumerate(self.clients):
            task = asyncio.create_task(
                self._monitor_server(client, f"server_{i}")
            )
            tasks.append(task)
        
        # Start dashboard update loop
        asyncio.create_task(self._update_dashboards())
        
        await asyncio.gather(*tasks)
    
    async def _monitor_server(self, client: MCPHttpClient, server_id: str):
        """Monitor a single MCP server."""
        # Subscribe to all changes
        subscription_url = f"{client.base_url}/mcp/v1/sse/subscribe"
        
        async with client.client.stream("GET", subscription_url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    
                    # Process event
                    await self.event_processor.process({
                        **event,
                        "server_id": server_id,
                        "timestamp": datetime.now().isoformat()
                    })
    
    async def _update_dashboards(self):
        """Update dashboards periodically."""
        while True:
            # Collect metrics from all servers
            metrics = []
            for client in self.clients:
                try:
                    stats = await client.call_tool(
                        "get_dataset_stats",
                        {"include_details": False}
                    )
                    metrics.append(stats)
                except:
                    pass
            
            # Update dashboards
            await self.dashboard_manager.update({
                "servers": len(self.clients),
                "metrics": metrics,
                "events_per_second": self.event_processor.get_rate(),
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(10)  # Update every 10 seconds
```

## Summary

This guide covers comprehensive integration patterns for the ContextFrame MCP server, from basic client implementations to complex production architectures. Key takeaways:

1. **Use HTTP as Primary Transport**: HTTP provides reliability, scalability, and ease of integration
2. **Implement Robust Error Handling**: Use retries, circuit breakers, and fallbacks
3. **Optimize for Performance**: Cache aggressively, batch operations, use connection pooling
4. **Monitor Everything**: Track metrics, set up alerts, use distributed tracing
5. **Design for Scale**: Implement sharding, load balancing, and horizontal scaling
6. **Test Thoroughly**: Use mock servers, integration tests, and performance benchmarks

The MCP protocol's flexibility allows for various integration patterns, from simple scripts to enterprise-scale systems. Choose patterns that match your use case and scale requirements.