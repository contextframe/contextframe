---
url: "https://mirascope.com/docs/mirascope/api/core/base/structured_stream"
title: "mirascope.core.base.structured_stream | Mirascope"
---

# mirascope.core.base.structured\_stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/structured_stream\#mirascope-core-base-structured-stream)

## Module structured\_stream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/structured_stream\#structured-stream)

This module defines the base class for structured streams.

## Class BaseStructuredStream [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/structured_stream\#basestructuredstream)

A base class for streaming structured outputs from LLMs.

**Bases:**

[Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_ResponseModelT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| stream | [BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream) | - |
| response\_model | [type](https://docs.python.org/3/library/functions.html#type)\[\_ResponseModelT\] | - |
| constructed\_response\_model | \_ResponseModelT | - |
| fields\_from\_call\_args | fields\_from\_call\_args | - |

## Function structured\_stream\_factory [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/structured_stream\#structured-stream-factory)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| TCallResponse | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] | - |
| TCallResponseChunk | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\] | - |
| TStream | [type](https://docs.python.org/3/library/functions.html#type)\[[BaseStream](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\] | - |
| TToolType | [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| setup\_call | SameSyncAndAsyncClientSetupCall\[\_SameSyncAndAsyncClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| SetupCall\[\_SyncBaseClientT, \_AsyncBaseClientT, [\_BaseDynamicConfigT](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig), \_AsyncBaseDynamicConfigT, [\_BaseCallParamsT](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams), \_ResponseT, \_ResponseChunkT, \_AsyncResponseT, \_AsyncResponseChunkT, [\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |
| get\_json\_output | GetJsonOutput\[[\_BaseCallResponseChunkT](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\] | - |

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