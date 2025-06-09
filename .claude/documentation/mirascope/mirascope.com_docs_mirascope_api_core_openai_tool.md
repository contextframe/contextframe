---
url: "https://mirascope.com/docs/mirascope/api/core/openai/tool"
title: "mirascope.core.openai.tool | Mirascope"
---

# mirascope.core.openai.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#mirascope-core-openai-tool)

## Module tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#tool)

The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class GenerateOpenAIStrictToolJsonSchema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#generateopenaistricttooljsonschema)

**Bases:**

[GenerateJsonSchemaNoTitles](https://mirascope.com/docs/mirascope/api/core/base/tool#generatejsonschemanotitles)

## Class OpenAIToolConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#openaitoolconfig)

A tool configuration for OpenAI-specific features.

**Bases:**

[ToolConfig](https://mirascope.com/docs/mirascope/api/core/base/tool#toolconfig)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| strict | [bool](https://docs.python.org/3/library/functions.html#bool) | - |

## Class OpenAITool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#openaitool)

A class for defining tools for OpenAI LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.openai import openai_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@openai_call("gpt-4o-mini", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `OpenAITool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ChatCompletionMessageToolCall\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.openai import OpenAITool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = OpenAITool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the OpenAI-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| ChatCompletionToolParam | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/tool\#from-tool-call)

Constructs an `OpenAITool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ChatCompletionMessageToolCall | The OpenAI tool call from which to construct this tool instance. |
| allow\_partial= False | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to allow partial JSON data. |

### Returns

| Type | Description |
| --- | --- |
| [OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool) | - |

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