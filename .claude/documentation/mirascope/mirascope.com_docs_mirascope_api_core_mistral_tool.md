---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/tool"
title: "mirascope.core.mistral.tool | Mirascope"
---

# mirascope.core.mistral.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/tool\#mirascope-core-mistral-tool)

The `MistralTool` class for easy tool usage with Mistral LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class MistralTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/tool\#mistraltool)

A class for defining tools for Mistral LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import mistral_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@mistral_call("mistral-large-latest", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns a `MistralTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ToolCall\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.mistral import MistralTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = MistralTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Mistral-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/tool\#from-tool-call)

Constructs an `MistralTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ToolCall | The Mistral tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool) | - |

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