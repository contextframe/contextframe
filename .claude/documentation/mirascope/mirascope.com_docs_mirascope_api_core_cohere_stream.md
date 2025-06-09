---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/stream"
title: "mirascope.core.cohere.stream | Mirascope"
---

# mirascope.core.cohere.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/stream\#mirascope-core-cohere-stream)

The `CohereStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class CohereStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/stream\#coherestream)

A class for convenience around streaming Cohere LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import cohere_call

@cohere_call("command-r-plus", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `CohereStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[CohereCallResponse](https://mirascope.com/docs/mirascope/api/core/cohere/call_response#coherecallresponse), [CohereCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/cohere/call_response_chunk#coherecallresponsechunk), ChatMessage, ChatMessage, ChatMessage, ChatMessage, [CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool), [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool), [AsyncCohereDynamicConfig](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config#asynccoheredynamicconfig) \| [CohereDynamicConfig](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config#coheredynamicconfig), [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams), ChatStreamEndEventFinishReason\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/stream\#construct-call-response)

Constructs the call response from a consumed CohereStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [CohereCallResponse](https://mirascope.com/docs/mirascope/api/core/cohere/call_response#coherecallresponse) | - |

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