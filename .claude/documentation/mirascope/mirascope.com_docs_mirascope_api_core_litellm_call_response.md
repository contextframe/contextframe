---
url: "https://mirascope.com/docs/mirascope/api/core/litellm/call_response"
title: "mirascope.core.litellm.call_response | Mirascope"
---

# mirascope.core.litellm.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/call_response\#mirascope-core-litellm-call-response)

This module contains the `LiteLLMCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class LiteLLMCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/call_response\#litellmcallresponse)

A simpler wrapper around `OpenAICallResponse`.

Everything is the same except the `cost` property, which has been updated to use
LiteLLM's cost calculations so that cost tracking works for non-OpenAI models.

**Bases:**

[OpenAICallResponse](https://mirascope.com/docs/mirascope/api/core/openai/call_response#openaicallresponse)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

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