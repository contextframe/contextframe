"""HTTP-first client example for MCP server.

This example demonstrates the recommended approach for interacting with
the MCP server using HTTP as the primary transport protocol.
"""

import asyncio
import httpx
import json
from typing import Any, Dict, Optional


class MCPHttpClient:
    """Simple HTTP client for MCP server - recommended approach."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._request_id = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _next_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id
    
    async def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request using standard HTTP.
        
        This is the primary way to interact with the MCP server.
        """
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
    
    # Convenience methods for common operations
    
    async def initialize(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize MCP session."""
        return await self.request("initialize", {
            "protocolVersion": "0.1.0",
            "clientInfo": client_info,
            "capabilities": {}
        })
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.request("tools/list")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with arguments."""
        return await self.request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return await self.request("resources/list")
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI."""
        return await self.request("resources/read", {"uri": uri})
    
    # Optional SSE support for specific streaming use cases
    
    async def track_operation_progress(self, operation_id: str):
        """Track operation progress using SSE (optional feature).
        
        Note: This is only needed for long-running operations.
        Most operations complete synchronously via HTTP.
        """
        url = f"{self.base_url}/mcp/v1/sse/progress/{operation_id}"
        
        async with self.client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data


async def main():
    """Example usage of HTTP-first MCP client."""
    
    # Initialize client - uses standard HTTP
    async with MCPHttpClient() as client:
        
        # 1. Initialize session
        print("Initializing MCP session...")
        init_result = await client.initialize({
            "name": "example-client",
            "version": "1.0.0"
        })
        print(f"Server: {init_result['serverInfo']}")
        
        # 2. List available tools
        print("\nListing tools...")
        tools = await client.list_tools()
        for tool in tools.get("tools", []):
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
        # 3. Call a tool (example: search)
        print("\nSearching for documents...")
        search_result = await client.call_tool(
            "search_contextframe",
            {
                "query": "example",
                "limit": 5
            }
        )
        print(f"Found {len(search_result.get('documents', []))} documents")
        
        # 4. List resources
        print("\nListing resources...")
        resources = await client.list_resources()
        for resource in resources.get("resources", [])[:3]:
            print(f"  - {resource['uri']}: {resource.get('name', 'Unnamed')}")
        
        # 5. Read a resource
        if resources.get("resources"):
            print("\nReading first resource...")
            first_uri = resources["resources"][0]["uri"]
            content = await client.read_resource(first_uri)
            print(f"Content preview: {content.get('contents', [{}])[0].get('text', '')[:100]}...")
        
        # 6. Optional: Use SSE only for long-running operations
        # This is NOT the primary communication method
        print("\nExample of optional SSE usage for progress tracking:")
        print("(Note: SSE is only used for specific streaming scenarios)")
        
        # Simulate a batch operation that returns an operation_id
        batch_result = await client.call_tool(
            "batch_extract_metadata",
            {"document_ids": ["doc1", "doc2", "doc3"]}
        )
        
        if "operation_id" in batch_result:
            print(f"Tracking operation {batch_result['operation_id']}...")
            async for progress in client.track_operation_progress(batch_result["operation_id"]):
                print(f"  Progress: {progress['current']}/{progress['total']}")
                if progress.get("status") == "completed":
                    break


if __name__ == "__main__":
    # Run the HTTP-first example
    asyncio.run(main())