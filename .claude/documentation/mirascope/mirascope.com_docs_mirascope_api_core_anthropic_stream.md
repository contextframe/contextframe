---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/stream"
title: "mirascope.core.anthropic.stream | Mirascope"
---

# mirascope.core.anthropic.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/stream\#mirascope-core-anthropic-stream)

## Module stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/stream\#stream)

The `AnthropicStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/stream\#finishreason)

**Type:** Message.\_\_annotations\_\_\['stop\_reason'\]

## Class AnthropicStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/stream\#anthropicstream)

A class for convenience around streaming Anthropic LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import anthropic_call

@anthropic_call("claude-3-5-sonnet-20240620", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `AnthropicStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[AnthropicCallResponse](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response#anthropiccallresponse), [AnthropicCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response_chunk#anthropiccallresponsechunk), MessageParam, MessageParam, MessageParam, MessageParam, [AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool), ToolParam, [AsyncAnthropicDynamicConfig](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config#asyncanthropicdynamicconfig) \| [AnthropicDynamicConfig](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config#anthropicdynamicconfig), [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/stream\#construct-call-response)

Constructs the call response from a consumed AnthropicStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [AnthropicCallResponse](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response#anthropiccallresponse) | - |

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