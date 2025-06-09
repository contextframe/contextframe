---
url: "https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk"
title: "mirascope.core.base.call_response_chunk | Mirascope"
---

# mirascope.core.base.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk\#mirascope-core-base-call-response-chunk)

This module contains the `BaseCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class BaseCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk\#basecallresponsechunk)

A base abstract interface for LLM streaming response chunks.

**Bases:** [BaseModel](https://docs.pydantic.dev/latest/api/base_model/), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_ChunkT, [\_FinishReasonT](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\], ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| chunk | \_ChunkT | - |
| model\_config | ConfigDict(extra='allow', arbitrary\_types\_allowed=True) | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Should return the string content of the response chunk.<br>If there are multiple choices in a chunk, this method should select the 0th<br>choice and return it's string content.<br>If there is no string content (e.g. when using tools), this method must return<br>the empty string. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[\_FinishReasonT](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the finish reasons of the response.<br>If there is no finish reason, this method must return None. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the id of the response. |
| usage | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | Should return the usage of the response.<br>If there is no usage, this method must return None. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of input tokens.<br>If there is no input\_tokens, this method must return None. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of cached tokens.<br>If there is no cached\_tokens, this method must return None. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of output tokens.<br>If there is no output\_tokens, this method must return None. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |
| common\_usage | [Usage](https://mirascope.com/docs/mirascope/api/core/base/types#usage) \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic usage info. |

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