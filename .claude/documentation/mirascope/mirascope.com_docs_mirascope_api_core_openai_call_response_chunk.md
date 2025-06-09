---
url: "https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk"
title: "mirascope.core.openai.call_response_chunk | Mirascope"
---

# mirascope.core.openai.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk\#mirascope-core-openai-call-response-chunk)

## Module call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk\#call-response-chunk)

This module contains the `OpenAICallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk\#finishreason)

**Type:** Choice.\_\_annotations\_\_\['finish\_reason'\]

## Class OpenAICallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk\#openaicallresponsechunk)

A convenience wrapper around the OpenAI `ChatCompletionChunk` streamed chunks.

When calling the OpenAI API using a function decorated with `openai_call` and
`stream` set to `True`, the stream will contain `OpenAIResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.openai import openai_call

@openai_call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `OpenAIStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[ChatCompletionChunk, [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| chunk | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[ChatCompletionChunk\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content for the 0th choice delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| audio | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the audio data of the response. |
| audio\_transcript | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the transcript of the audio content. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns the cost metadata. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |

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