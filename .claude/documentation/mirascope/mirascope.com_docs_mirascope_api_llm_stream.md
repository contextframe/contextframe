---
url: "https://mirascope.com/docs/mirascope/api/llm/stream"
title: "mirascope.llm.stream | Mirascope"
---

# mirascope.llm.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/stream\#mirascope-llm-stream)

This module contains the Stream class that inherits from BaseStream.

## Class Stream [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/stream\#stream)

A non-pydantic class that inherits from BaseStream.

**Bases:**

[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\[[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse), [BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [Any](https://docs.python.org/3/library/typing.html#typing.Any), [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), [BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| cost | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/stream\#construct-call-response)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [CallResponse](https://mirascope.com/docs/mirascope/api/llm/call_response#callresponse) | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/llm/stream\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool), [JsonableType](https://mirascope.com/docs/mirascope/api/core/base/types#jsonabletype)\]\] | The list of tools and their outputs from which the tool<br>message parameters should be constructed. |

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