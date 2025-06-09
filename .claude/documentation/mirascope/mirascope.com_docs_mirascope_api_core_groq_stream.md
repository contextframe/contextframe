---
url: "https://mirascope.com/docs/mirascope/api/core/groq/stream"
title: "mirascope.core.groq.stream | Mirascope"
---

# mirascope.core.groq.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/stream\#mirascope-core-groq-stream)

## Module stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/stream\#stream)

The `GroqStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/stream\#finishreason)

**Type:** Choice.\_\_annotations\_\_\['finish\_reason'\]

## Class GroqStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/stream\#groqstream)

A class for convenience around streaming Groq LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.groq import groq_call

@groq_call("llama-3.1-8b-instant", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `GroqStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[GroqCallResponse](https://mirascope.com/docs/mirascope/api/core/groq/call_response#groqcallresponse), [GroqCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/groq/call_response_chunk#groqcallresponsechunk), ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam, ChatCompletionMessageParam, [GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool), ChatCompletionToolParam, [AsyncGroqDynamicConfig](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config#asyncgroqdynamicconfig) \| [GroqDynamicConfig](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config#groqdynamicconfig), [GroqCallParams](https://mirascope.com/docs/mirascope/api/core/groq/call_params#groqcallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/stream\#construct-call-response)

Constructs the call response from a consumed GroqStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [GroqCallResponse](https://mirascope.com/docs/mirascope/api/core/groq/call_response#groqcallresponse) | - |

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