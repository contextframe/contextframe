---
url: "https://mirascope.com/docs/mirascope/api/core/xai/call"
title: "mirascope.core.xai.call | Mirascope"
---

# mirascope.core.xai.call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/xai/call\#mirascope-core-xai-call)

## Alias call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/xai/call\#call)

A decorator for calling the xAI API with a typed function.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls)

This decorator is used to wrap a typed function that calls the xAI API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.xai import xai_call

@xai_call("grok-2-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The model to use in the API call. |
| stream | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to stream the response from the API call. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] | The tools to use in the API call. |
| response\_model | [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) \| BaseType | The response model into which the response<br>should be structured. |
| output\_parser | ([OpenAICallResponse](https://mirascope.com/docs/mirascope/api/core/openai/call_response#openaicallresponse) \| ResponseModelT) =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) | A function for<br>parsing the call response whose value will be returned in place of the original<br>call response. |
| json\_mode | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to use JSON Mode. |
| client | [None](https://docs.python.org/3/library/constants.html#None) | xAI does not support a custom client. |
| call\_params | [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams) | The \`OpenAICallParams\` call parameters to use in the<br>API call. |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator for turning a typed function into a xAI<br>routed LLM API call. |

**Alias to:** `mirascope.core.xai._call.xai_call`

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