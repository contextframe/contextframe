---
url: "https://mirascope.com/docs/mirascope/api/core/azure/stream"
title: "mirascope.core.azure.stream | Mirascope"
---

# mirascope.core.azure.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/stream\#mirascope-core-azure-stream)

The `AzureStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class AzureStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/stream\#azurestream)

A class for convenience around streaming Azure LLM calls.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.azure import azure_call

@azure_call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # returns `AzureStream` instance
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[AzureCallResponse](https://mirascope.com/docs/mirascope/api/core/azure/call_response#azurecallresponse), [AzureCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/azure/call_response_chunk#azurecallresponsechunk), UserMessage, AssistantMessage, ToolMessage, ChatRequestMessage, [AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool), ChatCompletionsToolDefinition, [AsyncAzureDynamicConfig](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config#asyncazuredynamicconfig) \| [AzureDynamicConfig](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config#azuredynamicconfig), [AzureCallParams](https://mirascope.com/docs/mirascope/api/core/azure/call_params#azurecallparams), CompletionsFinishReason\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/stream\#construct-call-response)

Constructs the call response from a consumed AzureStream.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [AzureCallResponse](https://mirascope.com/docs/mirascope/api/core/azure/call_response#azurecallresponse) | - |

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