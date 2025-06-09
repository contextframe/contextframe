---
url: "https://mirascope.com/docs/mirascope/api/core/base/stream"
title: "mirascope.core.base.stream | Mirascope"
---

# mirascope.core.base.stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#mirascope-core-base-stream)

## Module stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#stream)

This module contains the base classes for streaming responses from LLMs.

## Class BaseStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#basestream)

A base class for streaming responses from LLMs.

**Bases:** [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse), [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), \_UserMessageParamT, \_AssistantMessageParamT, \_ToolMessageParamT, \_MessageParamT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), \_ToolSchemaT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), [\_FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\], ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| stream | Generator\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [None](https://docs.python.org/3/library/constants.html#None)\], [None](https://docs.python.org/3/library/constants.html#None), [None](https://docs.python.org/3/library/constants.html#None)\] \| AsyncGenerator\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) \| [None](https://docs.python.org/3/library/constants.html#None)\], [None](https://docs.python.org/3/library/constants.html#None)\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| metadata | [Metadata](https://mirascope.com/docs/mirascope/api/core/base/metadata#metadata) | - |
| tool\_types | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| call\_response\_type | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] | - |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| prompt\_template | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| fn\_args | [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| dynamic\_config | [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig) | - |
| messages | [list](https://docs.python.org/3/library/stdtypes.html#list)\[\_MessageParamT\] | - |
| call\_params | [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams) | - |
| call\_kwargs | BaseCallKwargs\[\_ToolSchemaT\] | - |
| user\_message\_param | \_UserMessageParamT \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| message\_param | \_AssistantMessageParamT | - |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[\_FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| start\_time | [float](https://docs.python.org/3/library/functions.html#float) | - |
| end\_time | [float](https://docs.python.org/3/library/functions.html#float) | - |
| provider | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns metadata needed for cost calculation. |
| cost | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Calculate the cost of this streaming API call. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| tools\_and\_outputs | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool), [JsonableType](https://mirascope.com/docs/mirascope/api/core/base/types#jsonabletype)\]\] | The list of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[\_ToolMessageParamT\] | - |

## Function construct\_call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#construct-call-response)

Constructs the call response.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse) | - |

## Function stream\_factory [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/stream\#stream-factory)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| TCallResponse | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] | - |
| TStream | [type](https://docs.python.org/3/library/functions.html#type)\[[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\] | - |
| setup\_call | SameSyncAndAsyncClientSetupCall\[\_SameSyncAndAsyncClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| SetupCall\[\_SyncBaseClientT, \_AsyncBaseClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| handle\_stream | HandleStream\[\_ResponseChunkT, [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| handle\_stream\_async | HandleStreamAsync\[\_AsyncResponseChunkT, [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

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