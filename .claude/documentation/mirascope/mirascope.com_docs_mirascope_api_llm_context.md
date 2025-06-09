---
url: "https://mirascope.com/docs/mirascope/api/llm/context"
title: "mirascope.llm.context | Mirascope"
---

# mirascope.llm.context [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/context\#mirascope-llm-context)

## Alias context [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/context\#context)

Context manager for LLM API calls.

This method only allows setting overrides (provider, model, client, call\_params)
and does not allow structural overrides (stream, tools, response\_model, etc.).

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| provider | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) \| [LocalProvider](https://mirascope.com/docs/mirascope/api/core/base/types#localprovider) | The provider to use for the LLM API call. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The model to use for the LLM API call. |
| client= None | [Any](https://docs.python.org/3/library/typing.html#typing.Any) \| [None](https://docs.python.org/3/library/constants.html#None) | The client to use for the LLM API call. |
| call\_params= None | CommonCallParams \| [Any](https://docs.python.org/3/library/typing.html#typing.Any) \| [None](https://docs.python.org/3/library/constants.html#None) | The call parameters for the LLM API call. |

### Returns

| Type | Description |
| --- | --- |
| LLMContext | - |

**Alias to:** `mirascope.llm._context.context`

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