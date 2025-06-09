---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/call_response"
title: "mirascope.core.mistral.call_response | Mirascope"
---

# mirascope.core.mistral.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_response\#mirascope-core-mistral-call-response)

This module contains the `MistralCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class MistralCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_response\#mistralcallresponse)

A convenience wrapper around the Mistral `ChatCompletion` response.

When calling the Mistral API using a function decorated with `mistral_call`, the
response will be an `MistralCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import mistral_call

@mistral_call("mistral-largel-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `MistralCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[ChatCompletionResponse, [MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool), [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\], [MistralDynamicConfig](https://mirascope.com/docs/mirascope/api/core/mistral/dynamic_config#mistraldynamicconfig), AssistantMessage \| SystemMessage \| ToolMessage \| UserMessage, [MistralCallParams](https://mirascope.com/docs/mirascope/api/core/mistral/call_params#mistralcallparams), UserMessage, MistralMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | The content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | UsageInfo | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | AssistantMessage | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the tools for the 0th choice message. |
| tool | [MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[MistralTool](https://mirascope.com/docs/mirascope/api/core/mistral/tool#mistraltool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ToolMessage\] | The list of constructed \`ChatMessage\` parameters. |

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