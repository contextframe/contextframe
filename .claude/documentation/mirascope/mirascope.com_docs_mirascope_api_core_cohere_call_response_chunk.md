---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/call_response_chunk"
title: "mirascope.core.cohere.call_response_chunk | Mirascope"
---

# mirascope.core.cohere.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_response_chunk\#mirascope-core-cohere-call-response-chunk)

This module contains the `CohereCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class CohereCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_response_chunk\#coherecallresponsechunk)

A convenience wrapper around the Cohere `ChatCompletionChunk` streamed chunks.

When calling the Cohere API using a function decorated with `cohere_call` and
`stream` set to `True`, the stream will contain `CohereResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import cohere_call

@cohere_call("command-r-plus", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `CohereStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[[SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[StreamedChatResponse\], ChatStreamEndEventFinishReason\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content for the 0th choice delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[ChatStreamEndEventFinishReason\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the name of the response model.<br>Cohere does not return model, so we return None |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the id of the response. |
| usage | ApiMetaBilledUnits \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the response. |
| input\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns the cost metadata. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[types.FinishReason\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |

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