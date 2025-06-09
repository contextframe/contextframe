---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/call_params"
title: "mirascope.core.cohere.call_params | Mirascope"
---

# mirascope.core.cohere.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_params\#mirascope-core-cohere-call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Class CohereCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_params\#coherecallparams)

The parameters to use when calling the Cohere API.

[Cohere API Reference](https://docs.cohere.com/reference/chat)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| chat\_history | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[ChatMessage\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| connectors | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[ChatConnector\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| conversation\_id | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| documents | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[ChatDocument\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| frequency\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| k | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_input\_tokens | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_tokens | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| p | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| preamble | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| presence\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| prompt\_truncation | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ChatRequestPromptTruncation \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| raw\_prompting | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| search\_queries\_only | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| seed | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| stop\_sequences | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| temperature | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| tool\_results | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[ToolResult\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

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