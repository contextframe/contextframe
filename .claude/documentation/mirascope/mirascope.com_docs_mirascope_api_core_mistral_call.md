---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/call"
title: "mirascope.core.mistral.call | Mirascope"
---

# mirascope.core.mistral.call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call\#mirascope-core-mistral-call)

## Alias call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call\#call)

A decorator for calling the Mistral API with a typed function.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls)

This decorator is used to wrap a typed function that calls the Mistral API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import mistral_call

@mistral_call("mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The Mistral model to use in the API call. |
| stream | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to stream the response from the API call. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] | The tools to use in the Mistral API call. |
| response\_model | [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) \| BaseType | The response model into which the response should be structured. |
| output\_parser | ([MistralCallResponse](https://mirascope.com/docs/mirascope/api/core/mistral/call_response#mistralcallresponse) \| ResponseModelT) =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) | A function for<br>parsing the call response whose value will be returned in place of the original call response. |
| json\_mode | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to use JSON Mode. |
| client | [object](https://docs.python.org/3/library/functions.html#object) | An optional custom client to use in place of the default client. |
| call\_params | [MistralCallParams](https://mirascope.com/docs/mirascope/api/core/mistral/call_params#mistralcallparams) | The \`MistralCallParams\` call parameters to use in<br>the API call. |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator for turning a typed function into a Mistral API<br>call. |

**Alias to:** `mirascope.core.mistral._call.mistral_call`

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