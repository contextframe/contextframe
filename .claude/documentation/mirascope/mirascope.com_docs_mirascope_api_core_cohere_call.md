---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/call"
title: "mirascope.core.cohere.call | Mirascope"
---

# mirascope.core.cohere.call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call\#mirascope-core-cohere-call)

## Alias call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call\#call)

A decorator for calling the Cohere API with a typed function.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls)

This decorator is used to wrap a typed function that calls the Cohere API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import cohere_call

@cohere_call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The Cohere model to use in the API call. |
| stream | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to stream the response from the API call. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] | The tools to use in the Cohere API call. |
| response\_model | [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) \| BaseType | The response model into which the response<br>should be structured. |
| output\_parser | ([CohereCallResponse](https://mirascope.com/docs/mirascope/api/core/cohere/call_response#coherecallresponse) \| ResponseModelT) =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) | A function for<br>parsing the call response whose value will be returned in place of the original<br>call response. |
| json\_mode | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to use JSON Mode. |
| client | [object](https://docs.python.org/3/library/functions.html#object) | An optional custom client to use in place of the default client. |
| call\_params | [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams) | The \`CohereCallParams\` call parameters to use in the<br>API call. |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator for turning a typed function into a Cohere API<br>call. |

**Alias to:** `mirascope.core.cohere._call.cohere_call`

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