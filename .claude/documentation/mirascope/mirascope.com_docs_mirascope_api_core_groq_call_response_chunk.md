---
url: "https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk"
title: "mirascope.core.groq.call_response_chunk | Mirascope"
---

# mirascope.core.groq.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk\#mirascope-core-groq-call-response-chunk)

## Module call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk\#call-response-chunk)

This module contains the `GroqCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk\#finishreason)

**Type:** Choice.\_\_annotations\_\_\['finish\_reason'\]

## Class GroqCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk\#groqcallresponsechunk)

A convenience wrapper around the Groq `ChatCompletionChunk` streamed chunks.

When calling the Groq API using a function decorated with `groq_call` and
`stream` set to `True`, the stream will contain `GroqResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.groq import groq_call

@groq_call("llama-3.1-8b-instant", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `GroqStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[ChatCompletionChunk, [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content for the 0th choice delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns the cost metadata. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |

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