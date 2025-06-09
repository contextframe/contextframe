---
url: "https://mirascope.com/docs/mirascope/api/core/groq/call_response"
title: "mirascope.core.groq.call_response | Mirascope"
---

# mirascope.core.groq.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response\#mirascope-core-groq-call-response)

This module contains the `GroqCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class GroqCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response\#groqcallresponse)

A convenience wrapper around the Groq `ChatCompletion` response.

When calling the Groq API using a function decorated with `groq_call`, the
response will be an `GroqCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.groq import groq_call

@groq_call("llama-3.1-8b-instant")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `GroqCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[ChatCompletion, [GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool), ChatCompletionToolParam, [AsyncGroqDynamicConfig](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config#asyncgroqdynamicconfig) \| [GroqDynamicConfig](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config#groqdynamicconfig), ChatCompletionMessageParam, [GroqCallParams](https://mirascope.com/docs/mirascope/api/core/groq/call_params#groqcallparams), ChatCompletionUserMessageParam, GroqMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | SerializeAsAny\[ChatCompletionAssistantMessageParam\] | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns any available tool calls as their \`GroqTool\` definition. |
| tool | [GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | - |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[GroqTool](https://mirascope.com/docs/mirascope/api/core/groq/tool#groqtool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

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