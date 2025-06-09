---
url: "https://mirascope.com/docs/mirascope/api/core/google/stream"
title: "mirascope.core.google.stream | Mirascope"
---

# mirascope.core.google.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/stream\#mirascope-core-google-stream)

The `GoogleStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class GoogleStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/stream\#googlestream)

A class for convenience around streaming Google LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.google import google_call

@google_call("google-1.5-flash", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `GoogleStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[GoogleCallResponse](https://mirascope.com/docs/mirascope/api/core/google/call_response#googlecallresponse), [GoogleCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/google/call_response_chunk#googlecallresponsechunk), ContentDict, ContentDict, ContentDict, ContentListUnion \| ContentListUnionDict, [GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool), [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool), [GoogleDynamicConfig](https://mirascope.com/docs/mirascope/api/core/google/dynamic_config#googledynamicconfig), [GoogleCallParams](https://mirascope.com/docs/mirascope/api/core/google/call_params#googlecallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/stream\#construct-call-response)

Constructs the call response from a consumed GoogleStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [GoogleCallResponse](https://mirascope.com/docs/mirascope/api/core/google/call_response#googlecallresponse) | - |

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