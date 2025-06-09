---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/tool"
title: "mirascope.core.bedrock.tool | Mirascope"
---

# mirascope.core.bedrock.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#mirascope-core-bedrock-tool)

## Module tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#tool)

The `BedrockTool` class for easy tool usage with Bedrock LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class GenerateBedrockStrictToolJsonSchema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#generatebedrockstricttooljsonschema)

**Bases:**

[GenerateJsonSchemaNoTitles](https://mirascope.com/docs/mirascope/api/core/base/tool#generatejsonschemanotitles)

## Class BedrockToolConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#bedrocktoolconfig)

A tool configuration for Bedrock-specific features.

**Bases:**

[ToolConfig](https://mirascope.com/docs/mirascope/api/core/base/tool#toolconfig)

## Class BedrockTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#bedrocktool)

A class for defining tools for Bedrock LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.bedrock import bedrock_call

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

@bedrock_call("anthropic.claude-3-haiku-20240307-v1:0", tools=[format_book])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")
if tool := response.tool:  # returns an `BedrockTool` instance
    print(tool.call())
```

**Bases:**

[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_call | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[ToolUseBlockContentTypeDef\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#tool-schema)

Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

Example:

```
from mirascope.core.bedrock import BedrockTool

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

tool_type = BedrockTool.type_from_fn(format_book)
print(tool_type.tool_schema())  # prints the Bedrock-specific tool schema
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| ToolTypeDef | - |

## Function from\_tool\_call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/tool\#from-tool-call)

Constructs an `BedrockTool` instance from a `tool_call`.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tool\_call | ToolUseBlockContentTypeDef | The Bedrock tool call from which to construct this tool instance. |

### Returns

| Type | Description |
| --- | --- |
| [BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool) | - |

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