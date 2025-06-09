---
url: "https://mirascope.com/docs/mirascope/api/core/google/call_response_chunk"
title: "mirascope.core.google.call_response_chunk | Mirascope"
---

# mirascope.core.google.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/call_response_chunk\#mirascope-core-google-call-response-chunk)

This module contains the `GoogleCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class GoogleCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/call_response_chunk\#googlecallresponsechunk)

A convenience wrapper around the Google API streamed response chunks.

When calling the Google API using a function decorated with `google_call` and
`stream` set to `True`, the stream will contain `GoogleCallResponseChunk` instances

Example:

```
from mirascope.core import prompt_template
from mirascope.core.google import google_call

@google_call("google-1.5-flash", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `GoogleStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[GenerateContentResponse, GoogleFinishReason\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the chunk content for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[GoogleFinishReason\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the model name.<br>google.generativeai does not return model, so we return None |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the id of the response.<br>google.generativeai does not return an id |
| usage | GenerateContentResponseUsageMetadata \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion.<br>google.generativeai does not have Usage, so we return None |
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