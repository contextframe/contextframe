---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/call_params"
title: "mirascope.core.mistral.call_params | Mirascope"
---

# mirascope.core.mistral.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_params\#mirascope-core-mistral-call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Class MistralCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_params\#mistralcallparams)

The parameters to use when calling the Mistral API.

[Mistral API Reference](https://docs.mistral.ai/api/)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| endpoint | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_tokens | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| random\_seed | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| response\_format | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ResponseFormat \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| safe\_mode | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| safe\_prompt | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| temperature | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| tool\_choice | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ToolChoice \| ToolChoiceEnum \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
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