---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/call_params"
title: "mirascope.core.anthropic.call_params | Mirascope"
---

# mirascope.core.anthropic.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params\#mirascope-core-anthropic-call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Class AnthropicCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params\#anthropiccallparams)

The parameters to use when calling the Anthropic API.

[Anthropic API Reference](https://docs.anthropic.com/en/api/messages)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| extra\_headers | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | - |
| tool\_choice | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ToolChoice \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| metadata | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[Metadata](https://mirascope.com/docs/mirascope/api/core/base/metadata#metadata) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| stop\_sequences | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| system | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| Iterable\[TextBlockParam\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| temperature | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| top\_k | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| top\_p | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| timeout | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| Timeout \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

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