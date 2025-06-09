---
url: "https://mirascope.com/docs/mirascope/api/core/openai/stream"
title: "mirascope.core.openai.stream | Mirascope"
---

# mirascope.core.openai.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/stream\#mirascope-core-openai-stream)

## Module stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/stream\#stream)

The `OpenAIStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/stream\#finishreason)

**Type:** Choice.\_\_annotations\_\_\['finish\_reason'\]

## Class OpenAIStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/stream\#openaistream)

A class for convenience around streaming OpenAI LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.openai import openai_call

@openai_call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `OpenAIStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[OpenAICallResponse](https://mirascope.com/docs/mirascope/api/core/openai/call_response#openaicallresponse), [OpenAICallResponseChunk](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#openaicallresponsechunk), ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam, ChatCompletionMessageParam, [OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool), ChatCompletionToolParam, [OpenAIDynamicConfig](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config#openaidynamicconfig), [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| audio\_id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/stream\#construct-call-response)

Constructs the call response from a consumed OpenAIStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [OpenAICallResponse](https://mirascope.com/docs/mirascope/api/core/openai/call_response#openaicallresponse) | - |

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