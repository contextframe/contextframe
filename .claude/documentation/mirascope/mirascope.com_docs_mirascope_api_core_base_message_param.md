---
url: "https://mirascope.com/docs/mirascope/api/core/base/message_param"
title: "mirascope.core.base.message_param | Mirascope"
---

# mirascope.core.base.message\_param [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#mirascope-core-base-message-param)

## `BaseMessageParam` [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#basemessageparam)

## Class BaseMessageParam [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#basemessageparam)

A base class for message parameters.

Usage

[Prompts](https://mirascope.com/docs/mirascope/learn/prompts#prompt-templates-messages)

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| role | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) \| Sequence\[[TextPart](https://mirascope.com/docs/mirascope/api/core/base/message_param#textpart) \| [ImagePart](https://mirascope.com/docs/mirascope/api/core/base/message_param#imagepart) \| ImageURLPart \| [AudioPart](https://mirascope.com/docs/mirascope/api/core/base/message_param#audiopart) \| AudioURLPart \| CacheControlPart \| DocumentPart \| ToolCallPart \| ToolResultPart\] | - |

## `TextPart` [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#textpart)

## Class TextPart [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#textpart)

A content part for text.

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| type | [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)\['text'\] | - |
| text | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## `ImagePart` [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#imagepart)

## Class ImagePart [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#imagepart)

A content part for images.

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| type | [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)\['image'\] | - |
| media\_type | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| image | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | - |
| detail | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

## `AudioPart` [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#audiopart)

## Class AudioPart [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/message_param\#audiopart)

A content part for audio.

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| type | [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)\['audio'\] | - |
| media\_type | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| audio | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) \| [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

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