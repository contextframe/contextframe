---
url: "https://mirascope.com/docs/mirascope/api/core/openai/call_response"
title: "mirascope.core.openai.call_response | Mirascope"
---

# mirascope.core.openai.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response\#mirascope-core-openai-call-response)

## Module call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response\#call-response)

This module contains the `OpenAICallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class ChatCompletionAudio [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response\#chatcompletionaudio)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| data | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| transcript | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Class OpenAICallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response\#openaicallresponse)

A convenience wrapper around the OpenAI `ChatCompletion` response.

When calling the OpenAI API using a function decorated with `openai_call`, the
response will be an `OpenAICallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.openai import openai_call

@openai_call("gpt-4o")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `OpenAICallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[ChatCompletion, [OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool), ChatCompletionToolParam, [OpenAIDynamicConfig](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config#openaidynamicconfig), ChatCompletionMessageParam, [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams), ChatCompletionUserMessageParam, OpenAIMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| response | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[ChatCompletion\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | SerializeAsAny\[ChatCompletionAssistantMessageParam\] | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns any available tool calls as their \`OpenAITool\` definition. |
| tool | [OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| audio | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the audio data of the response. |
| audio\_transcript | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the transcript of the audio content. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[OpenAITool](https://mirascope.com/docs/mirascope/api/core/openai/tool#openaitool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ChatCompletionToolMessageParam\] | The list of constructed \`ChatCompletionToolMessageParam\` parameters. |

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