---
url: "https://mirascope.com/docs/mirascope/api/llm/call_response"
title: "mirascope.llm.call_response | Mirascope"
---

# mirascope.llm.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/call_response\#mirascope-llm-call-response)

The CallResponse class for the LLM provider.

## Class CallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/call_response\#callresponse)

A provider-agnostic CallResponse class.

We rely on \_response having `common_` methods or properties for normalization.

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any), [BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [Any](https://docs.python.org/3/library/typing.html#typing.Any), [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any), [Any](https://docs.python.org/3/library/typing.html#typing.Any), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\], [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), BaseMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| usage | [Usage](https://mirascope.com/docs/mirascope/api/core/base/types#usage) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_messages | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam)\] | - |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| tool | [Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam)\] | - |

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