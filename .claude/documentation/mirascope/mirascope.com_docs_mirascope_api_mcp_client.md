---
url: "https://mirascope.com/docs/mirascope/api/mcp/client"
title: "mirascope.mcp.client | Mirascope"
---

# mirascope.mcp.client [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#mirascope-mcp-client)

## Module client [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#client)

The `MCPServer` Class and context managers.

## Class MCPClient [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#mcpclient)

The SSE client session that connects to the MCP server.

All of the results from the server are converted into Mirascope-friendly types.

**Bases:**

ClientSession

## Function list\_resources [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#list-resources)

List all resources available on the MCP server.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[Resource\] | A list of Resource objects |

## Function read\_resource [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#read-resource)

Read a resource from the MCP server.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| uri | [str](https://docs.python.org/3/library/stdtypes.html#str) \| AnyUrl | URI of the resource to read |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[TextPart](https://mirascope.com/docs/mirascope/api/core/base/message_param#textpart) \| BlobResourceContents\] | Contents of the resource, either as string or BlobResourceContents |

## Function list\_prompts [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#list-prompts)

List all prompts available on the MCP server.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | A list of Prompt objects |

## Function get\_prompt\_template [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#get-prompt-template)

Get a prompt template from the MCP server.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the prompt template |

### Returns

| Type | Description |
| --- | --- |
| () =\> Awaitable\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam)\]\] | A callable that accepts keyword arguments and returns a list of BaseMessageParam |

## Function list\_tools [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#list-tools)

List all tools available on the MCP server.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] | A list of dynamically created \`BaseTool\` types. |

## Function sse\_client [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#sse-client)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| url | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| list\_roots\_callback= None | ListRootsFnT \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| read\_timeout\_seconds= None | timedelta \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| sampling\_callback= None | SamplingFnT \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| session= None | ClientSession \| [None](https://docs.python.org/3/library/constants.html#None) | - |

### Returns

| Type | Description |
| --- | --- |
| AsyncIterator\[[MCPClient](https://mirascope.com/docs/mirascope/api/mcp/client#mcpclient)\] | - |

## Function stdio\_client [Link to this heading](https://mirascope.com/docs/mirascope/api/mcp/client\#stdio-client)

Create a MCPClient instance with the given server parameters and exception handler.

Returns:

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| server\_parameters | StdioServerParameters | - |
| read\_stream\_exception\_handler= None | (Exception) =\> [None](https://docs.python.org/3/library/constants.html#None) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

### Returns

| Type | Description |
| --- | --- |
| AsyncIterator\[[MCPClient](https://mirascope.com/docs/mirascope/api/mcp/client#mcpclient)\] | - |

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