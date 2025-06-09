---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/call_response_chunk"
title: "mirascope.core.bedrock.call_response_chunk | Mirascope"
---

# mirascope.core.bedrock.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response_chunk\#mirascope-core-bedrock-call-response-chunk)

This module contains the `BedrockCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class BedrockCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response_chunk\#bedrockcallresponsechunk)

A convenience wrapper around the Bedrock `ChatCompletionChunk` streamed chunks.

When calling the Bedrock API using a function decorated with `bedrock_call` and
`stream` set to `True`, the stream will contain `BedrockResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.bedrock import bedrock_call

@bedrock_call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

stream = recommend_book("fantasy")  # response is an `BedrockStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[StreamOutputChunk \| AsyncStreamOutputChunk, [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| chunk | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[StreamOutputChunk \| AsyncStreamOutputChunk\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content for the 0th choice delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | TokenUsageTypeDef \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
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