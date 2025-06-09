---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk"
title: "mirascope.core.anthropic.call_response_chunk | Mirascope"
---

# mirascope.core.anthropic.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk\#mirascope-core-anthropic-call-response-chunk)

## Module call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk\#call-response-chunk)

This module contains the `AnthropicCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk\#finishreason)

**Type:** Message.\_\_annotations\_\_\['stop\_reason'\]

## Class AnthropicCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk\#anthropiccallresponsechunk)

A convenience wrapper around the Anthropic `ChatCompletionChunk` streamed chunks.

When calling the Anthropic API using a function decorated with `anthropic_call` and
`stream` set to `True`, the stream will contain `AnthropicResponseChunk` instances
with properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import anthropic_call

@anthropic_call("claude-3-5-sonnet-20240620", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `AnthropicStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[MessageStreamEvent, [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the string content of the 0th message. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the finish reason of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the id of the response. |
| usage | [Usage](https://mirascope.com/docs/mirascope/api/core/base/types#usage) \| MessageDeltaUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the message. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns the cost metadata. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[types.FinishReason\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |

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