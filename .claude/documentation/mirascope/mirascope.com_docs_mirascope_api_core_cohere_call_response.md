---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/call_response"
title: "mirascope.core.cohere.call_response | Mirascope"
---

# mirascope.core.cohere.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_response\#mirascope-core-cohere-call-response)

This module contains the `CohereCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class CohereCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_response\#coherecallresponse)

A convenience wrapper around the Cohere `ChatCompletion` response.

When calling the Cohere API using a function decorated with `cohere_call`, the
response will be an `CohereCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import cohere_call

@cohere_call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `CohereCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[[SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[NonStreamedChatResponse\], [CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool), [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[[Tool](https://mirascope.com/docs/mirascope/api/llm/tool#tool)\], [AsyncCohereDynamicConfig](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config#asynccoheredynamicconfig) \| [CohereDynamicConfig](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config#coheredynamicconfig), [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[ChatMessage\], [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams), [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[ChatMessage\], CohereMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model.<br>Cohere does not return model, so we return the model provided by the user. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the id of the response. |
| usage | ApiMetaBilledUnits \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the response. |
| input\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | ChatMessage | Returns the assistant's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the tools for the 0th choice message. |
| tool | [CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[CohereTool](https://mirascope.com/docs/mirascope/api/core/cohere/tool#coheretool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ToolResult\] | The list of constructed \`ToolResult\` parameters. |

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