---
url: "https://mirascope.com/docs/mirascope/api/llm/override"
title: "mirascope.llm.override | Mirascope"
---

# mirascope.llm.override [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/override\#mirascope-llm-override)

## Alias override [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/override\#override)

Overrides the provider-specific call with the specified provider.

This function creates a new function that wraps the original function
and temporarily sets a context with the specified overrides when called.
It supports both setting overrides (provider, model, client, call\_params)
and structural overrides (stream, tools, response\_model, output\_parser).

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| provider\_agnostic\_call | () =\> Awaitable\[\_R\] \| () =\> \_R | The provider-agnostic call to override. |
| provider= None | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) \| [LocalProvider](https://mirascope.com/docs/mirascope/api/core/base/types#localprovider) \| [None](https://docs.python.org/3/library/constants.html#None) | The provider to override with. |
| model= None | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | The model to override with. |
| stream= None | [bool](https://docs.python.org/3/library/functions.html#bool) \| StreamConfig \| [None](https://docs.python.org/3/library/constants.html#None) | Whether to stream the response. |
| tools= None | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] \| [None](https://docs.python.org/3/library/constants.html#None) | The tools to use for the LLM API call. |
| response\_model= None | [type](https://docs.python.org/3/library/functions.html#type)\[\_ResponseModelT\] \| [None](https://docs.python.org/3/library/constants.html#None) | The response model to structure the response into. |
| output\_parser= None | ([Any](https://docs.python.org/3/library/typing.html#typing.Any)) =\> \_ParsedOutputT \| [None](https://docs.python.org/3/library/constants.html#None) | A function to parse the response. |
| json\_mode= None | [bool](https://docs.python.org/3/library/functions.html#bool) \| [None](https://docs.python.org/3/library/constants.html#None) | Whether to use JSON mode. |
| client= None | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | The client to override with. |
| call\_params= None | CommonCallParams \| [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams) \| [AzureCallParams](https://mirascope.com/docs/mirascope/api/core/azure/call_params#azurecallparams) \| [BedrockCallParams](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params#bedrockcallparams) \| [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams) \| GeminiCallParams \| [GoogleCallParams](https://mirascope.com/docs/mirascope/api/core/google/call_params#googlecallparams) \| [GroqCallParams](https://mirascope.com/docs/mirascope/api/core/groq/call_params#groqcallparams) \| [MistralCallParams](https://mirascope.com/docs/mirascope/api/core/mistral/call_params#mistralcallparams) \| [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams) \| VertexCallParams \| [XAICallParams](https://mirascope.com/docs/mirascope/api/core/xai/call_params#xaicallparams) \| [None](https://docs.python.org/3/library/constants.html#None) | The call params to override with. |

### Returns

| Type | Description |
| --- | --- |
| () =\> Awaitable\[\_R\] \| Awaitable\[[CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse)\] \| Awaitable\[[Stream](https://mirascope.com/docs/mirascope/api/llm/stream#stream)\] \| Awaitable\[\_ResponseModelT\] \| Awaitable\[\_ParsedOutputT\] \| Awaitable\[AsyncIterable\[\_ResponseModelT\]\] \| Awaitable\[\_ResponseModelT \| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse)\] \| Awaitable\[\_ParsedOutputT \| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse)\] \| \_R \| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse) \| [Stream](https://mirascope.com/docs/mirascope/api/llm/stream#stream) \| \_ResponseModelT \| \_ParsedOutputT \| Iterable\[\_ResponseModelT\] \| \_ResponseModelT \| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse) \| \_ParsedOutputT \| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse) | The overridden function with appropriate return type. |

**Alias to:** `mirascope.llm._override.override`

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