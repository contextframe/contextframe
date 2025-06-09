---
url: "https://mirascope.com/docs/mirascope/api/core/openai/call_params"
title: "mirascope.core.openai.call_params | Mirascope"
---

# mirascope.core.openai.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#mirascope-core-openai-call-params)

## Module call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Class ChatCompletionAudioParam [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#chatcompletionaudioparam)

## Class ChatCompletionModality [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#chatcompletionmodality)

## Class ChatCompletionReasoningEffort [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#chatcompletionreasoningeffort)

## Class OpenAICallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_params\#openaicallparams)

The parameters to use when calling the OpenAI API.

[OpenAI API Reference](https://platform.openai.com/docs/api-reference/chat/create)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| audio | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[ChatCompletionAudioParam](https://mirascope.com/docs/mirascope/api/core/openai/call_params#chatcompletionaudioparam) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| extra\_headers | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| frequency\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| logit\_bias | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [int](https://docs.python.org/3/library/functions.html#int)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| logprobs | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| max\_tokens | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| metadata | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| modalities | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[ChatCompletionModality](https://mirascope.com/docs/mirascope/api/core/openai/call_params#chatcompletionmodality)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| n | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| parallel\_tool\_calls | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[bool](https://docs.python.org/3/library/functions.html#bool)\] | - |
| presence\_penalty | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| reasoning\_effort | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[ChatCompletionReasoningEffort](https://mirascope.com/docs/mirascope/api/core/openai/call_params#chatcompletionreasoningeffort) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| response\_format | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ResponseFormat\] | - |
| seed | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| stop | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str) \| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| stream\_options | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ChatCompletionStreamOptionsParam \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| temperature | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| tool\_choice | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ChatCompletionToolChoiceOptionParam\] | - |
| top\_logprobs | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| top\_p | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| user | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | - |

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