---
url: "https://mirascope.com/docs/mirascope/api/core/google/call_response"
title: "mirascope.core.google.call_response | Mirascope"
---

# mirascope.core.google.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/call_response\#mirascope-core-google-call-response)

This module contains the `GoogleCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class GoogleCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/call_response\#googlecallresponse)

A convenience wrapper around the Google API response.

When calling the Google API using a function decorated with `google_call`, the
response will be a `GoogleCallResponse` instance with properties that allow for
more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.google import google_call

@google_call("google-1.5-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `GoogleCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[GenerateContentResponse, [GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool), [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool), [GoogleDynamicConfig](https://mirascope.com/docs/mirascope/api/core/google/dynamic_config#googledynamicconfig), ContentListUnion \| ContentListUnionDict, [GoogleCallParams](https://mirascope.com/docs/mirascope/api/core/google/call_params#googlecallparams), ContentDict, GoogleMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the contained string content for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the model name.<br>google.generativeai does not return model, so we return the model provided by<br>the user. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the id of the response.<br>google.generativeai does not return an id |
| usage | GenerateContentResponseUsageMetadata \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion.<br>google.generativeai does not have Usage, so we return None |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | ContentDict | Returns the models's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the list of tools for the response. |
| tool | [GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th candidate's 0th content part. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[GoogleTool](https://mirascope.com/docs/mirascope/api/core/google/tool#googletool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ContentDict\] | The list of constructed \`FunctionResponse\` parameters. |

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