---
url: "https://mirascope.com/docs/mirascope/api/core/litellm/call_response_chunk"
title: "mirascope.core.litellm.call_response_chunk | Mirascope"
---

# mirascope.core.litellm.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/call_response_chunk\#mirascope-core-litellm-call-response-chunk)

This module contains the `LiteLLMCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class LiteLLMCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/litellm/call_response_chunk\#litellmcallresponsechunk)

A simpler wrapper around `OpenAICallResponse`.

Everything is the same except the `cost` property, which has been updated to use
LiteLLM's cost calculations so that cost tracking works for non-OpenAI models.

**Bases:**

[OpenAICallResponseChunk](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#openaicallresponsechunk)

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