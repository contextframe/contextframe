---
url: "https://mirascope.com/docs/mirascope/api/core/azure/call_params"
title: "mirascope.core.azure.call_params | Mirascope"
---

# mirascope.core.azure.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_params\#mirascope-core-azure-call-params)

## Module call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_params\#call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Attribute ResponseFormatJSON [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_params\#responseformatjson)

**Type:** TypeAlias

## Class AzureCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_params\#azurecallparams)

The parameters to use when calling the Azure API.

[Azure API Reference](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| frequency\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_tokens | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| model\_extras | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| presence\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| response\_format | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[ResponseFormatJSON](https://mirascope.com/docs/mirascope/api/core/azure/call_params#responseformatjson) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| seed | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| stop | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| temperature | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| tool\_choice | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| ChatCompletionsToolChoicePreset \| ChatCompletionsNamedToolChoice \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| top\_p | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

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