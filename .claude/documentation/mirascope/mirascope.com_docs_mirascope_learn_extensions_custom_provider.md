---
url: "https://mirascope.com/docs/mirascope/learn/extensions/custom_provider"
title: "Custom LLM Provider | Mirascope"
---

# Implementing a Custom Provider [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#implementing-a-custom-provider)

This guide explains how to implement a custom provider for Mirascope using the `call_factory` method. Before proceeding, ensure you're familiar with Mirascope's core concepts as covered in the [Learn section](https://mirascope.com/docs/mirascope/learn) of the documentation.

## Overview [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#overview)

To implement a custom provider, you'll need to create several components:

1. Provider-specific `BaseCallParams` class
2. Provider-specific `BaseCallResponse` class
3. Provider-specific `BaseCallResponseChunk` class
4. Provider-specific `BaseDynamicConfig` class
5. Provider-specific `BaseStream` class
6. Provider-specific `BaseTool` class
7. Utility functions for setup, JSON output, and stream handling
8. The main call factory implementation

Let's go through each of these components.

In this documentation, we are only going to cover the basic general outline of how to implement a custom provider, such as class and function signatures. For a full view into how to implement a decorator for a custom provider, we recommend taking a look at how we implement support for existing providers.

## `BaseCallParams` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basecallparams-class)

Define a class that inherits from `BaseCallParams` to specify the parameters for your custom provider's API calls.

```
from typing_extensions import NotRequired

from mirascope.core.base import BaseCallParams

class CustomProviderCallParams(BaseCallParams):
    # Add parameters specific to your provider, such as:
    max_tokens: NotRequired[int | None]
    temperature: NotRequired[float | None]
```

## `BaseCallResponse` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basecallresponse-class)

Create a class that inherits from `BaseCallResponse` to handle the response from your custom provider's API.

```
from mirascope.core.base import BaseCallResponse, BaseMessageParam

class CustomProviderCallResponse(BaseCallResponse[...]):  # provide types for generics
    # Implement abstract properties and methods
    @property
    def content(self) -> str:
        # Return the main content of the response

    @property
    def finish_reasons(self) -> list[str] | None:
        # Return the finish reasons of the response

    # Implement other abstract properties and methods
```

## `BaseCallResponseChunk` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basecallresponsechunk-class)

For streaming support, create a class that inherits from `BaseCallResponseChunk`.

```
from mirascope.core.base import BaseCallResponseChunk

class CustomProviderCallResponseChunk(BaseCallResponseChunk[...]):  # provide types for generics
    # Implement abstract properties
    @property
    def content(self) -> str:
        # Return the content of the chunk

    @property
    def finish_reasons(self) -> list[str] | None:
        # Return the finish reasons for the chunk

    # Implement other abstract properties
```

## `BaseDynamicConfig` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basedynamicconfig-class)

Define a type for dynamic configuration using `BaseDynamicConfig`.

```
from mirascope.core.base import BaseDynamicConfig
from .call_params import CustomProviderCallParams

CustomProviderDynamicConfig = BaseDynamicConfig[BaseMessageParam, CustomProviderCallParams]
```

## `BaseStream` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basestream-class)

Implement a stream class that inherits from `BaseStream` for handling streaming responses.

```
from mirascope.core.base import BaseStream

class CustomProviderStream(BaseStream):
    # Implement abstract methods and properties
    @property
    def cost(self) -> float | None:
        # Calculate and return the cost of the stream

    def _construct_message_param(self, tool_calls: list | None = None, content: str | None = None):
        # Construct and return the message parameter

    def construct_call_response(self) -> CustomProviderCallResponse:
        # Construct and return the call response
```

## `BaseTool` class [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#basetool-class)

Create a tool class that inherits from `BaseTool` for defining custom tools.

```
from mirascope.core.base import BaseTool

class CustomProviderTool(BaseTool):
    # Implement custom tool functionality
    @classmethod
    def tool_schema(cls) -> ProviderToolSchemaType:
        # Return the tool schema

    @classmethod
    def from_tool_call(cls, tool_call: Any) -> "CustomProviderTool":
        # Construct a tool instance from a tool call
```

## Utility Functions [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#utility-functions)

Implement utility functions for setup, JSON output handling, and stream handling.

```
from typing import Any, Callable, Awaitable

def setup_call(
    *,
    model: str,
    client: Any,
    fn: Callable[..., CustomProviderDynamicConfig | Awaitable[CustomProviderDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: CustomProviderDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: CustomProviderCallParams,
    extract: bool,
) -> tuple[\
    Callable[..., Any] | Callable[..., Awaitable[Any]],\
    str,\
    list[Any],\
    list[type[CustomProviderTool]] | None,\
    dict[str, Any],\
]:
    # Implement setup logic
    ...

def get_json_output(
    response: CustomProviderCallResponse | CustomProviderCallResponseChunk,
    json_mode: bool
) -> str:
    # Implement JSON output extraction
    ...

def handle_stream(
    stream: Any,
    tool_types: list[type[CustomProviderTool]] | None,
) -> Generator[tuple[CustomProviderCallResponseChunk, CustomProviderTool | None], None, None]:
    # Implement stream handling
    ...

async def handle_stream_async(
    stream: Any,
    tool_types: list[type[CustomProviderTool]] | None,
) -> AsyncGenerator[tuple[CustomProviderCallResponseChunk, CustomProviderTool | None], None]:
    # Implement asynchronous stream handling
    ...
```

## Call Factory Implementation [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#call-factory-implementation)

Finally, use the `call_factory` to create your custom provider's call decorator.

```
from mirascope.core.base import call_factory

custom_provider_call = call_factory(
    TCallResponse=CustomProviderCallResponse,
    TCallResponseChunk=CustomProviderCallResponseChunk,
    TDynamicConfig=CustomProviderDynamicConfig,
    TStream=CustomProviderStream,
    TToolType=CustomProviderTool,
    TCallParams=CustomProviderCallParams,
    default_call_params=CustomProviderCallParams(),
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
)
```

## Usage [Link to this heading](https://mirascope.com/docs/mirascope/learn/extensions/custom_provider\#usage)

After implementing your custom provider, you can use it like any other Mirascope provider:

```
from mirascope.core import prompt_template

@custom_provider_call(model="your-custom-model")
@prompt_template("Your prompt template here")
def your_function(param: str):
    ...

result = your_function("example parameter")
```

By following this guide, you can implement a custom provider that integrates seamlessly with Mirascope's existing functionality. Remember to thoroughly test your implementation and handle any provider-specific quirks or requirements.

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