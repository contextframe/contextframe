---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/tool"
title: "mirascope.core.cohere.tool | Mirascope"
---

# mirascope.core.cohere.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/tool\#mirascope-core-cohere-tool)

The `CohereTool` class for easy tool usage with Cohere LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class CohereTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/tool\#coheretool)

A class for defining tools for Cohere LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import cohere_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@cohere_call("command-r-plus", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `CohereTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[[SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ToolCall\]\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.cohere import CohereTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = CohereTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Cohere-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool) | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/tool\#from-tool-call)

Constructs an `CohereTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ToolCall | The Cohere tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool) | - |

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