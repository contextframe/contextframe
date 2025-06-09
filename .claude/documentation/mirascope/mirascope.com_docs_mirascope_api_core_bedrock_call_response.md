---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/call_response"
title: "mirascope.core.bedrock.call_response | Mirascope"
---

# mirascope.core.bedrock.call\_response [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response\#mirascope-core-bedrock-call-response)

This module contains the `BedrockCallResponse` class.

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#handling-responses)

## Class BedrockCallResponse [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response\#bedrockcallresponse)

A convenience wrapper around the Bedrock `ChatCompletion` response.

When calling the Bedrock API using a function decorated with `bedrock_call`, the
response will be an `BedrockCallResponse` instance with properties that allow for
more convenience access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.bedrock import bedrock_call

@bedrock_call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")  # response is an `BedrockCallResponse` instance
print(response.content)
```

**Bases:**

[BaseCallResponse](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\[SyncConverseResponseTypeDef \| AsyncConverseResponseTypeDef, [BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool), ToolTypeDef, [AsyncBedrockDynamicConfig](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config#asyncbedrockdynamicconfig) \| [BedrockDynamicConfig](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config#bedrockdynamicconfig), InternalBedrockMessageParam, [BedrockCallParams](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params#bedrockcallparams), UserMessageTypeDef, BedrockMessageParamConverter\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| response | [SkipValidation](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.SkipValidation)\[SyncConverseResponseTypeDef \| AsyncConverseResponseTypeDef\] | - |
| message | SyncMessageTypeDef \| AsyncMessageTypeDef \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the message of the response. |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the chat completion for the 0th choice. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | TokenUsageTypeDef | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| message\_param | SerializeAsAny\[AssistantMessageTypeDef\] | Returns the assistants's response as a message parameter. |
| tools | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool)\] \| [None](https://docs.python.org/3/library/constants.html#None) | Returns any available tool calls as their \`BedrockTool\` definition. |
| tool | [BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the 0th tool for the 0th choice message. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| common\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) | - |
| common\_user\_message\_param | [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Get metadata required for cost calculation. |

## Function tool\_message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_response\#tool-message-params)

Returns the tool message parameters for tool call results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| tools\_and\_outputs | Sequence\[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[BedrockTool](https://mirascope.com/docs/mirascope/api/core/bedrock/tool#bedrocktool), [str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | The sequence of tools and their outputs from which the tool<br>message parameters should be constructed. |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[ToolResultBlockMessageTypeDef\] | The list of constructed \`ChatCompletionToolMessageParam\` parameters. |

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