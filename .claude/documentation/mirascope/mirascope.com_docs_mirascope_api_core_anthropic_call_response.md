---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/call_response"
title: "mirascope.core.anthropic.call_response | Mirascope"
---

# mirascope.core.anthropic.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response\#mirascope-core-anthropic-call-response)

This module contains the `AnthropicCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class AnthropicCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response\#anthropiccallresponse)

A convenience wrapper around the Anthropic `Message` response.

When calling the Anthropic API using a function decorated with `anthropic_call`, the
response will be an `AnthropicCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import anthropic_call

@anthropic_call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `AnthropicCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[Message, [AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool), ToolParam, [AsyncAnthropicDynamicConfig](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config#asyncanthropicdynamicconfig) \| [AnthropicDynamicConfig](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config#anthropicdynamicconfig), MessageParam, [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams), MessageParam, AnthropicMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the string text of the 0th text block. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | [Usage](https://mirascope.com/docs/mirascope/api/core/base/types#usage) | Returns the usage of the message. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of output tokens. |
| message\_param | SerializeAsAny\[MessageParam\] | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns any available tool calls as their \`AnthropicTool\` definition. |
| tool | [AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[types.FinishReason\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[AnthropicTool](https://mirascope.com/docs/mirascope/api/core/anthropic/tool#anthropictool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[MessageParam\] | The list of constructed \`MessageParam\` parameters. |

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