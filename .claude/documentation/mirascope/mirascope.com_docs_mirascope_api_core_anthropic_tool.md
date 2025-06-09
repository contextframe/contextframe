---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/tool"
title: "mirascope.core.anthropic.tool | Mirascope"
---

# mirascope.core.anthropic.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#mirascope-core-anthropic-tool)

## Module tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#tool)

The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class AnthropicToolConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#anthropictoolconfig)

A tool configuration for Anthropic-specific features.

**Bases:**

[ToolConfig](https://mirascope.com/docs/mirascope/api/core/base/tool#toolconfig)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cache\_control | \_CacheControl | - |

## Class AnthropicTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#anthropictool)

A class for defining tools for Anthropic LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import anthropic_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@anthropic_call("claude-3-5-sonnet-20240620", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `AnthropicTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ToolUseBlock\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#tool-schema)

Constructs a `ToolParam` tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.anthropic import AnthropicTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = AnthropicTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Anthropic-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| ToolParam | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/tool\#from-tool-call)

Constructs an `AnthropicTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ToolUseBlock | The Anthropic tool call from which to construct this tool<br>instance. |
| allow\_partial= False | [bool](https://docs.python.org/3/library/functions.html#bool) | - |

### Returns

| Type | Description |
| --- | --- |
| [AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool) | - |

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