---
url: "https://mirascope.com/docs/mirascope/api/core/azure/call_response_chunk"
title: "mirascope.core.azure.call_response_chunk | Mirascope"
---

# mirascope.core.azure.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_response_chunk\#mirascope-core-azure-call-response-chunk)

This module contains the `AzureCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class AzureCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_response_chunk\#azurecallresponsechunk)

A convenience wrapper around the Azure `ChatCompletionChunk` streamed chunks.

When calling the Azure API using a function decorated with `azure_call` and
`stream` set to `True`, the stream will contain `AzureResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.azure import azure_call

@azure_call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `AzureStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[StreamingChatCompletionsUpdate, CompletionsFinishReason\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| chunk | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[StreamingChatCompletionsUpdate\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content for the 0th choice delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[CompletionsFinishReason\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionsUsage | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of output tokens. |
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