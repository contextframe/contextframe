---
url: "https://mirascope.com/docs/mirascope/api/core/google/tool"
title: "mirascope.core.google.tool | Mirascope"
---

# mirascope.core.google.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/tool\#mirascope-core-google-tool)

The `GoogleTool` class for easy tool usage with Google's Google LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class GoogleTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/tool\#googletool)

A class for defining tools for Google LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.google import google_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@google_call("google-1.5-flash", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `GoogleTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[FunctionCall\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.google import GoogleTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = GoogleTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Google-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool) | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/tool\#from-tool-call)

Constructs an `GoogleTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | FunctionCall | The Google tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool) | - |

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