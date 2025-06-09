---
url: "https://mirascope.com/docs/mirascope/api/core/xai/stream"
title: "mirascope.core.xai.stream | Mirascope"
---

# mirascope.core.xai.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/xai/stream\#mirascope-core-xai-stream)

The `XAIStream` class for convenience around streaming xAI LLM calls.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams)

## Class XAIStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/xai/stream\#xaistream)

A simple wrapper around `OpenAIStream`.

Everything is the same except updates to the `construct_call_response` method and
the `cost` property so that cost is properly calculated using xAI's cost
calculation method. This ensures cost calculation works for non-OpenAI models.

**Bases:**

[OpenAIStream](https://mirascope.com/docs/mirascope/api/core/openai/stream#openaistream)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the cost of the call. |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/xai/stream\#construct-call-response)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [XAICallResponse](https://mirascope.com/docs/mirascope/api/core/xai/call_response#xaicallresponse) | - |

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