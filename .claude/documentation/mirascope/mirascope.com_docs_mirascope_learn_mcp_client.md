---
url: "https://mirascope.com/docs/mirascope/learn/mcp/client"
title: "Client | Mirascope"
---

# MCP Client [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#mcp-client)

If you haven't already, we recommend first reading and learning about [Model Context Protocol](https://github.com/modelcontextprotocol)

MCP Client in Mirascope enables you to interact with MCP servers through a standardized protocol. The client provides methods to access resources, tools, and prompts exposed by MCP servers.

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#basic-usage-and-syntax)

Let's connect to our book recommendation server using the MCP client:

```
import asyncio
from pathlib import Path

from mcp.client.stdio import StdioServerParameters
from mirascope.mcp import stdio_client

server_file = Path(__file__).parent / "server.py"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", str(server_file)],
    env=None,
)

async def main() -> None:
    async with stdio_client(server_params) as client:
        prompts = await client.list_prompts()
        print(prompts[0])

asyncio.run(main())
```

This example demonstrates:

1. Creating server parameters with `StdioServerParameters`
2. Using the `stdio_client` context manager to connect to the server
3. Accessing the list of available prompts

## Client Components [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#client-components)

### Standard In/Out (stdio) Server Connection [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#standard-in-out-stdio-server-connection)

To connect to an MCP server, use the `stdio_client` context manager with appropriate server parameters:

```
server_file = Path(__file__).parent / "server.py"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", str(server_file)],
    env=None,
)

async def main() -> None:
    async with stdio_client(server_params) as client:
        prompts = await client.list_prompts()
        print(prompts[0])
```

The `StdioServerParameters` specify how to launch and connect to the server process.

### Server Side Events (sse) Server Connection [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#server-side-events-sse-server-connection)

You can also use the `sse_client` instead to connect to an MCP server side event endpoint:

```
from mirascope.mcp import sse_client

async with sse_client("http://localhost:8000") as client:
    prompts = await client.list_prompts()
    print(prompts[0])
```

### Prompts [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#prompts)

You can list available prompts and get prompt templates from the server:

```
prompts = await client.list_prompts()
        print(prompts[0])
        # name='recommend_book' description='Get book recommendations by genre.' arguments=[PromptArgument(name='genre', description='Genre of book to recommend (fantasy, mystery, sci-fi, etc.)', required=True)]
        prompt_template = await client.get_prompt_template(prompts[0].name)
        prompt = await prompt_template(genre="fantasy")
        print(prompt)
        # [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

The client automatically converts server prompts into Mirascope-compatible prompt templates that return `BaseMessageParam` instances. This makes it easy to consume these prompts downstream in your Mirascope code.

### Resources [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#resources)

Resources can be listed and read from the server:

```
resources = await client.list_resources()
        resource = await client.read_resource(resources[0].uri)
        print(resources[0])
        # uri=AnyUrl('file://books.txt/') name='Books Database' description='Read the books database file.' mimeType='text/plain'
        print(resource)
        # ['The Name of the Wind by Patrick Rothfuss\nThe Silent Patient by Alex Michaelides']
```

The client provides methods to:

- `list_resources()`: Get available resources
- `read_resource(uri)`: Read resource content by URI

If the resource is text, it will be converted into a `TextPart` instance. Otherwise it will be the MCP `BlobResourceContents` type where the data contained is the original bytes encoded as a base64 string.

### Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#tools)

Tools from the server can be used with Mirascope's standard call decorators:

```
tools = await client.list_tools()

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
            tools=tools,
        )
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        if tool := recommend_book("fantasy").tool:
            call_result = await tool.call()
            print(call_result)
            # ['The Name of the Wind by Patrick Rothfuss']
```

The client automatically converts server tools into Mirascope-compatible tool types that can be used with any provider's call decorator.

## Type Safety [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#type-safety)

The MCP client preserves type information from the server:

1. **Prompts**: Arguments and return types from server prompt definitions
2. **Resources**: MIME types and content types for resources
3. **Tools**: Input schemas and return types for tools

This enables full editor support and type checking when using server components.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/mcp/client\#next-steps)

By using the MCP client with Mirascope's standard features like [Calls](https://mirascope.com/docs/mirascope/learn/calls), [Tools](https://mirascope.com/docs/mirascope/learn/tools), and [Prompts](https://mirascope.com/docs/mirascope/learn/prompts), you can build powerful applications that leverage local services through MCP servers.

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept