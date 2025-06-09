---
url: "https://mirascope.com/docs/mirascope/api/core/base/tool"
title: "mirascope.core.base.tool | Mirascope"
---

# mirascope.core.base.tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#mirascope-core-base-tool)

## Module tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#tool)

This module defines the base class for tools used in LLM calls.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools)

## Class ToolConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#toolconfig)

A base class for tool configurations.

**Bases:**

[TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)

## Class GenerateJsonSchemaNoTitles [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#generatejsonschemanotitles)

**Bases:**

GenerateJsonSchema

## Function generate [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#generate)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| schema | CoreSchema | - |
| mode= 'validation' | JsonSchemaMode | - |

### Returns

| Type | Description |
| --- | --- |
| JsonSchemaValue | - |

## Class BaseTool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#basetool)

A class for defining tools for LLM calls.

Example:

```
from mirascope.core import BaseTool
from pydantic import Field

class FormatBook(BaseTool):
    """Returns a nicely formatted book recommendation."""

    title: str = Field(..., description="The title of the book.")
    author: str = Field(..., description="The author of the book.")

    def call(self) -> str:
        return f"{self.title} by {self.author}"
```

**Bases:** [BaseModel](https://docs.pydantic.dev/latest/api/base_model/), ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| tool\_config | [ToolConfig](https://mirascope.com/docs/mirascope/api/core/base/tool#toolconfig) | - |
| model\_config | ConfigDict(arbitrary\_types\_allowed=True) | - |
| delta | [SkipJsonSchema](https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.SkipJsonSchema)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| args | [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | The arguments of the tool as a dictionary. |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#call)

The method to call the tool.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| args= () | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | - |
| kwargs= {} | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | - |

### Returns

| Type | Description |
| --- | --- |
| [Any](https://docs.python.org/3/library/typing.html#typing.Any) | - |

## Function type\_from\_fn [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#type-from-fn)

Returns this tool type converted from a function.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| fn | [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The function to convert into this tool type. |

### Returns

| Type | Description |
| --- | --- |
| [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

## Function type\_from\_base\_model\_type [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#type-from-base-model-type)

Returns this tool type converted from a given base tool type.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| tool\_type | [type](https://docs.python.org/3/library/functions.html#type)\[[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)\] | The tool type to convert into this tool type. This can be a<br>custom \`BaseTool\` or \`BaseModel\` definition. |

### Returns

| Type | Description |
| --- | --- |
| [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

## Function type\_from\_base\_type [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#type-from-base-type)

Returns this tool type converted from a base type.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| base\_type | [type](https://docs.python.org/3/library/functions.html#type)\[\_utils.BaseType\] | The base type (e.g. \`int\`) to convert into this tool type. |

### Returns

| Type | Description |
| --- | --- |
| [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

## Function tool\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#tool-schema)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [Any](https://docs.python.org/3/library/typing.html#typing.Any) | - |

## Function model\_json\_schema [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#model-json-schema)

Returns the generated JSON schema for the class.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| by\_alias= True | [bool](https://docs.python.org/3/library/functions.html#bool) | - |
| ref\_template= DEFAULT\_REF\_TEMPLATE | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| schema\_generator= GenerateJsonSchemaNoTitles | [type](https://docs.python.org/3/library/functions.html#type)\[GenerateJsonSchema\] | - |
| mode= 'validation' | JsonSchemaMode | - |

### Returns

| Type | Description |
| --- | --- |
| [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |

## Function warn\_for\_unsupported\_configurations [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/tool\#warn-for-unsupported-configurations)

Warns when a specific provider does not support provided config options.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [None](https://docs.python.org/3/library/constants.html#None) | - |

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