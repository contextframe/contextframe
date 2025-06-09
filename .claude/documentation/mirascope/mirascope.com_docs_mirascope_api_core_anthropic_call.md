---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/call"
title: "mirascope.core.anthropic.call | Mirascope"
---

# mirascope.core.anthropic.call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call\#mirascope-core-anthropic-call)

## Alias call [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call\#call)

A decorator for calling the Anthropic API with a typed function.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls)

This decorator is used to wrap a typed function that calls the Anthropic API. It
parses the prompt template of the wrapped function as the messages array and templates
the input arguments for the function into each message's template.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import anthropic_call

@anthropic_call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The Anthropic model to use in the API call. |
| stream | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to stream the response from the API call. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\] | The tools to use in the Anthropic API call. |
| response\_model | [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) \| BaseType | The response model into which the response<br>should be structured. |
| output\_parser | ([AnthropicCallResponse](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response#anthropiccallresponse) \| ResponseModelT) =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) | A function<br>for parsing the call response whose value will be returned in place of the<br>original call response. |
| json\_mode | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to use JSON Mode. |
| client | [object](https://docs.python.org/3/library/functions.html#object) | An optional custom client to use in place of the default client. |
| call\_params | [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams) | The \`AnthropicCallParams\` call parameters to use<br>in the API call. |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator for turning a typed function into an Anthropic<br>API call. |

**Alias to:** `mirascope.core.anthropic._call.anthropic_call`

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