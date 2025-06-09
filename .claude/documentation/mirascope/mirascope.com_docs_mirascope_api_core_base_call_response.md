---
url: "https://mirascope.com/docs/mirascope/api/core/base/call_response"
title: "mirascope.core.base.call_response | Mirascope"
---

# mirascope.core.base.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#mirascope-core-base-call-response)

## Module call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#call-response)

This module contains the base call response class.

## Function transform\_tool\_outputs [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#transform-tool-outputs)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| fn | ([type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\], Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\]) =\> [list](https://docs.python.org/3/library/stdtypes.html#list)\[\_ToolMessageParamT\] | - |

### Returns

| Type | Description |
| --- | --- |
| ([type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\], Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [JsonableType](https://mirascope.com/docs/mirascope/api/core/base/types#jsonabletype)\]\]) =\> [list](https://docs.python.org/3/library/stdtypes.html#list)\[\_ToolMessageParamT\] | - |

## Class BaseCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#basecallresponse)

A base abstract interface for LLM call responses.

**Bases:** [BaseModel](https://docs.pydantic.dev/latest/api/base_model/), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_ResponseT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), \_ToolSchemaT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_MessageParamT, \_CallParamsT, \_UserMessageParamT, \_BaseMessageParamConverterT\], ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| metadata | [Metadata](https://mirascope.com/docs/mirascope/api/core/base/metadata#metadata) | - |
| response | \_ResponseT | - |
| tool\_types | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| prompt\_template | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| fn\_args | [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |
| dynamic\_config | [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig) | - |
| messages | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[\_MessageParamT\]\] | - |
| call\_params | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[\_CallParamsT\] | - |
| call\_kwargs | BaseCallKwargs\[\_ToolSchemaT\] | - |
| user\_message\_param | \_UserMessageParamT \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| start\_time | [float](https://docs.python.org/3/library/functions.html#float) | - |
| end\_time | [float](https://docs.python.org/3/library/functions.html#float) | - |
| model\_config | ConfigDict(extra='allow', arbitrary\_types\_allowed=True) | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Should return the string content of the response.<br>If there are multiple choices in a response, this method should select the 0th<br>choice and return it's string content.<br>If there is no string content (e.g. when using tools), this method must return<br>the empty string. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the finish reasons of the response.<br>If there is no finish reason, this method must return None. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the id of the response. |
| usage | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | Should return the usage of the response.<br>If there is no usage, this method must return None. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of input tokens.<br>If there is no input\_tokens, this method must return None. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of cached tokens.<br>If there is no cached\_tokens, this method must return None. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Should return the number of output tokens.<br>If there is no output\_tokens, this method must return None. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |
| cost | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Calculate the cost of this API call using the unified calculate\_cost function. |
| provider | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) | Get the provider used for this API call. |
| message\_param | [Any](https://docs.python.org/3/library/typing.html#typing.Any) | Returns the assistant's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the tools for the 0th choice message. |
| tool | [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | Provider-agnostic assistant message param. |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic user message param. |
| common\_messages | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam)\] | Provider-agnostic list of messages. |
| common\_tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic tools. |
| common\_usage | [Usage](https://mirascope.com/docs/mirascope/api/core/base/types#usage) \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic usage info. |

## Function serialize\_tool\_types [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#serialize-tool-types)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| tool\_types | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| info | FieldSerializationInfo | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |

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