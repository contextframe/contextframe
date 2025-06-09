---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/stream"
title: "mirascope.core.mistral.stream | Mirascope"
---

# mirascope.core.mistral.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/stream\#mirascope-core-mistral-stream)

The `MistralStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class MistralStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/stream\#mistralstream)

A class for convenience around streaming Mistral LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import mistral_call

@mistral_call("mistral-large-latest", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `MistralStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[MistralCallResponse](https://mirascope.com/docs/mirascope/api/core/mistral/call_response#mistralcallresponse), [MistralCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/mistral/call_response_chunk#mistralcallresponsechunk), UserMessage, AssistantMessage, ToolMessage, AssistantMessage \| SystemMessage \| ToolMessage \| UserMessage, [MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool), [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\], [MistralDynamicConfig](https://mirascope.com/docs/mirascope/api/core/mistral/dynamic_config#mistraldynamicconfig), [MistralCallParams](https://mirascope.com/docs/mirascope/api/core/mistral/call_params#mistralcallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/stream\#construct-call-response)

Constructs the call response from a consumed MistralStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [MistralCallResponse](https://mirascope.com/docs/mirascope/api/core/mistral/call_response#mistralcallresponse) | - |

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