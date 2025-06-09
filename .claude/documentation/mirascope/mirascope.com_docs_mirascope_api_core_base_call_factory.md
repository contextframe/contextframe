---
url: "https://mirascope.com/docs/mirascope/api/core/base/call_factory"
title: "mirascope.core.base.call_factory | Mirascope"
---

# mirascope.core.base.call\_factory [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_factory\#mirascope-core-base-call-factory)

## `call_factory` [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_factory\#call-factory)

## Function call\_factory [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/call_factory\#call-factory)

A factory method for creating provider-specific call decorators.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| TCallResponse | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] | The provider-specific \`BaseCallResponse\` type. |
| TCallResponseChunk | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\] | The provider-specific \`BaseCallResponseChunk\` type. |
| TToolType | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | The provider-specific \`BaseTool\` type. |
| TStream | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\] | The provider-specific \`BaseStream\` type. |
| default\_call\_params | [BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams) | The default call parameters to use, which must match the<br>\`TCallParams\` type if provided. |
| setup\_call | SameSyncAndAsyncClientSetupCall\[\_SameSyncAndAsyncClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| SetupCall\[\_SyncBaseClientT, \_AsyncBaseClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | The helper method for setting up a call, which returns the<br>configured create function, the prompt template, the list of<br>provider-specific messages, the list of provider-specific tool types, and<br>the finalized \`call\_kwargs\` with which to make the API call with the create<br>function. |
| get\_json\_output | GetJsonOutput\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse) \| [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\] | The helper method for getting JSON output from a call response. |
| handle\_stream | HandleStream\[\_ResponseChunkT, [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | The helper method for converting a provider's original stream<br>generator into a generator that returns tuples of \`(chunk, tool)\` where<br>\`chunk\` and \`tool\` are provider-specific \`BaseCallResponseChunk\` and<br>\`BaseTool\` instances, respectively. |
| handle\_stream\_async | HandleStreamAsync\[\_AsyncResponseChunkT, [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | The same helper method as \`handle\_stream\` except for<br>handling asynchronous streaming. |

### Returns

| Type | Description |
| --- | --- |
| CallDecorator\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse), [\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk), [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), [\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream), \_SyncBaseClientT, \_AsyncBaseClientT, \_SameSyncAndAsyncClientT\] | - |

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