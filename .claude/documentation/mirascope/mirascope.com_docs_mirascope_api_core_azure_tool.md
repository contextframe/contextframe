---
url: "https://mirascope.com/docs/mirascope/api/core/azure/tool"
title: "mirascope.core.azure.tool | Mirascope"
---

# mirascope.core.azure.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#mirascope-core-azure-tool)

## Module tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#tool)

The `AzureTool` class for easy tool usage with Azure LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class GenerateAzureStrictToolJsonSchema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#generateazurestricttooljsonschema)

**Bases:**

[GenerateJsonSchemaNoTitles](https://mirascope.com/docs/mirascope/api/core/base/tool#generatejsonschemanotitles)

## Class AzureToolConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#azuretoolconfig)

A tool configuration for Azure-specific features.

**Bases:**

[ToolConfig](https://mirascope.com/docs/mirascope/api/core/base/tool#toolconfig)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| strict | [bool](https://docs.python.org/3/library/functions.html#bool) | - |

## Class AzureTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#azuretool)

A class for defining tools for Azure LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.azure import azure_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@azure_call("gpt-4o-mini", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `AzureTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ChatCompletionsToolCall\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.azure import AzureTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = AzureTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Azure-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| ChatCompletionsToolDefinition | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/tool\#from-tool-call)

Constructs an `AzureTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ChatCompletionsToolCall | The Azure tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool) | - |

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