---
url: "https://mirascope.com/docs/mirascope/api/core/azure/call_response"
title: "mirascope.core.azure.call_response | Mirascope"
---

# mirascope.core.azure.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_response\#mirascope-core-azure-call-response)

This module contains the `AzureCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class AzureCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_response\#azurecallresponse)

A convenience wrapper around the Azure `ChatCompletion` response.

When calling the Azure API using a function decorated with `azure_call`, the
response will be an `AzureCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.azure import azure_call

@azure_call("gpt-4o")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")  # response is an `AzureCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[ChatCompletions, [AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool), ChatCompletionsToolDefinition, [AsyncAzureDynamicConfig](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config#asyncazuredynamicconfig) \| [AzureDynamicConfig](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config#azuredynamicconfig), ChatRequestMessage, [AzureCallParams](https://mirascope.com/docs/mirascope/api/core/azure/call_params#azurecallparams), UserMessage, AzureMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| response | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[ChatCompletions\] | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | CompletionsUsage \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | SerializeAsAny\[AssistantMessage\] | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns any available tool calls as their \`AzureTool\` definition. |
| tool | [AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Provider-agnostic finish reasons. |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[AzureTool](https://mirascope.com/docs/mirascope/api/core/azure/tool#azuretool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ToolMessage\] | The list of constructed \`ChatCompletionToolMessageParam\` parameters. |

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