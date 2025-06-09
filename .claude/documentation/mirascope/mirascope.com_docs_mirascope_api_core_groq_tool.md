---
url: "https://mirascope.com/docs/mirascope/api/core/groq/tool"
title: "mirascope.core.groq.tool | Mirascope"
---

# mirascope.core.groq.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/tool\#mirascope-core-groq-tool)

The `GroqTool` class for easy tool usage with Groq LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class GroqTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/tool\#groqtool)

A class for defining tools for Groq LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.groq import groq_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@groq_call("llama-3.1-8b-instant", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `GroqTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ChatCompletionMessageToolCall\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.groq import GroqTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = GroqTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Groq-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| ChatCompletionToolParam | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/tool\#from-tool-call)

Constructs an `GroqTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ChatCompletionMessageToolCall | The Groq tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool) | - |

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