---
url: "https://mirascope.com/docs/mirascope/api/llm/call"
title: "mirascope.llm.call | Mirascope"
---

# mirascope.llm.call [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/call\#mirascope-llm-call)

## Alias call [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/call\#call)

A decorator for making provider-agnostic LLM API calls with a typed function.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls)

This decorator enables writing provider-agnostic code by wrapping a typed function
that can call any supported LLM provider's API. It parses the prompt template of
the wrapped function as messages and templates the input arguments into each message's
template.

Example:

```
from ..llm import call

@call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| provider | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) \| [LocalProvider](https://mirascope.com/docs/mirascope/api/core/base/types#localprovider) | The LLM provider to use<br>(e.g., "openai", "anthropic"). |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The model to use for the specified provider (e.g., "gpt-4o-mini"). |
| stream | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to stream the response from the API call. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] | The tools available for the LLM to use. |
| response\_model | [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) \| BaseType | The response model into which the response<br>should be structured. |
| output\_parser | ([CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse) \| ResponseModelT) =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) | A function for<br>parsing the call response whose value will be returned in place of the<br>original call response. |
| json\_mode | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to use JSON Mode. |
| client | [object](https://docs.python.org/3/library/functions.html#object) | An optional custom client to use in place of the default client. |
| call\_params | CommonCallParams | Provider-specific parameters to use in the API call. |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | A decorator that transforms a typed function into a<br>provider-agnostic LLM API call that returns standardized response types<br>regardless of the underlying provider used. |

**Alias to:** `mirascope.llm._call.call`

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