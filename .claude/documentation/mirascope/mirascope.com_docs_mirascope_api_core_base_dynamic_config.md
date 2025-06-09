---
url: "https://mirascope.com/docs/mirascope/api/core/base/dynamic_config"
title: "mirascope.core.base.dynamic_config | Mirascope"
---

# mirascope.core.base.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#mirascope-core-base-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamic-config)

The base type in a function as an LLM call to return for dynamic configuration.

## Class DynamicConfigBase [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigbase)

**Bases:**

[TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| metadata | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[Metadata](https://mirascope.com/docs/mirascope/api/core/base/metadata#metadata)\] | - |
| computed\_fields | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any) \| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any)\] \| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any)\]\]\]\] | - |
| tools | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[[type](https://docs.python.org/3/library/functions.html#type)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] \| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)\]\] | - |

## Class DynamicConfigMessages [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigmessages)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_MessageParamT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| messages | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[\_MessageParamT\]\] | - |

## Class DynamicConfigCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigcallparams)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_CallParamsT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| call\_params | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_CallParamsT\] | - |

## Class DynamicConfigClient [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigclient)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_ClientT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| client | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_ClientT \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

## Class DynamicConfigMessagesCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigmessagescallparams)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_MessageParamT, \_CallParamsT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| messages | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[\_MessageParamT\]\] | - |
| call\_params | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_CallParamsT\] | - |

## Class DynamicConfigMessagesClient [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigmessagesclient)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_MessageParamT, \_ClientT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| messages | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[\_MessageParamT\]\] | - |
| client | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_ClientT \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

## Class DynamicConfigCallParamsClient [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigcallparamsclient)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_CallParamsT, \_ClientT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| call\_params | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_CallParamsT\] | - |
| client | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_ClientT \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

## Class DynamicConfigFull [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#dynamicconfigfull)

**Bases:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase), [Generic](https://docs.python.org/3/library/typing.html#typing.Generic)\[\_MessageParamT, \_CallParamsT, \_ClientT\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| messages | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Sequence\[\_MessageParamT\]\] | - |
| call\_params | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_CallParamsT\] | - |
| client | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[\_ClientT \| [None](https://docs.python.org/3/library/constants.html#None)\] | - |

## Attribute BaseDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config\#basedynamicconfig)

**Type:** [DynamicConfigBase](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigbase) \| [DynamicConfigMessages](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigmessages)\[\_MessageParamT\] \| [DynamicConfigCallParams](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigcallparams)\[\_CallParamsT\] \| [DynamicConfigClient](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigclient)\[\_ClientT\] \| [DynamicConfigMessagesCallParams](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigmessagescallparams)\[\_MessageParamT, \_CallParamsT\] \| [DynamicConfigMessagesClient](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigmessagesclient)\[\_MessageParamT, \_ClientT\] \| [DynamicConfigCallParamsClient](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigcallparamsclient)\[\_CallParamsT, \_ClientT\] \| [DynamicConfigFull](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#dynamicconfigfull)\[\_MessageParamT, \_CallParamsT, \_ClientT\] \| [None](https://docs.python.org/3/library/constants.html#None)

The base type in a function as an LLM call to return for dynamic configuration.

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