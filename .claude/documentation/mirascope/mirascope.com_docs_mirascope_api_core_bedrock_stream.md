---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/stream"
title: "mirascope.core.bedrock.stream | Mirascope"
---

# mirascope.core.bedrock.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/stream\#mirascope-core-bedrock-stream)

The `BedrockStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class BedrockStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/stream\#bedrockstream)

A class for convenience around streaming Bedrock LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.bedrock import bedrock_call

@bedrock_call("gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

stream = recommend_book("fantasy")  # returns `BedrockStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[BedrockCallResponse](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response#bedrockcallresponse), [BedrockCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response_chunk#bedrockcallresponsechunk), UserMessageTypeDef, AssistantMessageTypeDef, ToolUseBlockMessageTypeDef, InternalBedrockMessageParam, [BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool), ToolTypeDef, [AsyncBedrockDynamicConfig](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config#asyncbedrockdynamicconfig) \| [BedrockDynamicConfig](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config#bedrockdynamicconfig), [BedrockCallParams](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params#bedrockcallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/stream\#construct-call-response)

Constructs the call response from a consumed BedrockStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [BedrockCallResponse](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response#bedrockcallresponse) | - |

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