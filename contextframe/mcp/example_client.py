#!/usr/bin/env python
"""Example MCP client for testing the ContextFrame MCP server.

This script demonstrates how to interact with the MCP server
using JSON-RPC messages over stdio.

Usage:
    # Start the server and client together
    python -m contextframe.mcp /path/to/dataset.lance | python example_client.py
"""

import json
import sys
import asyncio
from typing import Any, Dict, Optional


class MCPClient:
    """Simple MCP client for testing."""

    def __init__(self):
        self._message_id = 0

    def _next_id(self) -> int:
        """Get next message ID."""
        self._message_id += 1
        return self._message_id

    async def send_message(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a JSON-RPC message to stdout."""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id()
        }
        if params:
            message["params"] = params
        
        print(json.dumps(message))
        sys.stdout.flush()

    async def read_response(self) -> Dict[str, Any]:
        """Read a JSON-RPC response from stdin."""
        line = sys.stdin.readline()
        if not line:
            raise EOFError("Connection closed")
        
        return json.loads(line.strip())

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an RPC call and wait for response."""
        await self.send_message(method, params)
        response = await self.read_response()
        
        if "error" in response:
            raise Exception(f"RPC Error: {response['error']}")
        
        return response.get("result", {})


async def main():
    """Example client interaction."""
    client = MCPClient()
    
    print("=== MCP Client Example ===")
    
    try:
        # 1. Initialize
        print("\n1. Initializing...")
        result = await client.call("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {}
        })
        print(f"Server: {result['serverInfo']['name']} v{result['serverInfo']['version']}")
        print(f"Capabilities: {result['capabilities']}")
        
        # 2. List tools
        print("\n2. Listing tools...")
        result = await client.call("tools/list")
        print(f"Available tools: {len(result['tools'])}")
        for tool in result['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 3. List resources
        print("\n3. Listing resources...")
        result = await client.call("resources/list")
        print(f"Available resources: {len(result['resources'])}")
        for resource in result['resources']:
            print(f"  - {resource['name']}: {resource['uri']}")
        
        # 4. Read dataset info
        print("\n4. Reading dataset info...")
        result = await client.call("resources/read", {
            "uri": "contextframe://dataset/info"
        })
        info = json.loads(result['contents'][0]['text'])
        print(f"Dataset path: {info['dataset_path']}")
        print(f"Total documents: {info.get('total_documents', 'Unknown')}")
        
        # 5. Search documents
        print("\n5. Searching documents...")
        result = await client.call("tools/call", {
            "name": "search_documents",
            "arguments": {
                "query": "test",
                "search_type": "text",
                "limit": 3
            }
        })
        print(f"Found {len(result['documents'])} documents")
        for doc in result['documents']:
            print(f"  - {doc['uuid']}: {doc['content'][:50]}...")
        
        # 6. Add a document
        print("\n6. Adding a document...")
        result = await client.call("tools/call", {
            "name": "add_document",
            "arguments": {
                "content": "This is a test document added via MCP",
                "metadata": {
                    "title": "MCP Test Document",
                    "source": "example_client.py"
                },
                "generate_embedding": False
            }
        })
        doc_id = result['document']['uuid']
        print(f"Added document: {doc_id}")
        
        # 7. Get the document back
        print("\n7. Retrieving document...")
        result = await client.call("tools/call", {
            "name": "get_document",
            "arguments": {
                "document_id": doc_id,
                "include_content": True,
                "include_metadata": True
            }
        })
        doc = result['document']
        print(f"Retrieved: {doc['content']}")
        print(f"Metadata: {doc['metadata']}")
        
        # 8. Shutdown
        print("\n8. Shutting down...")
        await client.send_message("shutdown")
        print("Client complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())