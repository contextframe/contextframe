---
url: "https://mirascope.com/docs/mirascope/api/core/litellm/stream"
title: "mirascope.core.litellm.stream | Mirascope"
---

# mirascope.core.litellm.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/stream\#mirascope-core-litellm-stream)

The `LiteLLMStream` class for convenience around streaming LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class LiteLLMStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/stream\#litellmstream)

A simple wrapper around `OpenAIStream`.

Everything is the same except updates to the `construct_call_response` method and
the `cost` property so that cost is properly calculated using LiteLLM's cost
calculation method. This ensures cost calculation works for non-OpenAI models.

**Bases:**

[OpenAIStream](https://mirascope.com/docs/mirascope/api/core/openai/stream#openaistream)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns metadata needed for cost calculation. |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/stream\#construct-call-response)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [LiteLLMCallResponse](https://mirascope.com/docs/mirascope/api/core/litellm/call_response#litellmcallresponse) | - |

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