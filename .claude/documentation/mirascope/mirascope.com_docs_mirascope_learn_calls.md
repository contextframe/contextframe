---
url: "https://mirascope.com/docs/mirascope/learn/calls"
title: "Calls | Mirascope"
---

# Calls [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#calls)

If you haven't already, we recommend first reading the section on writing [Prompts](https://mirascope.com/docs/mirascope/learn/prompts)

When working with Large Language Model (LLM) APIs in Mirascope, a "call" refers to making a request to a LLM provider's API with a particular setting and prompt.

The `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various LLM providers. This powerful tool allows you to transform prompt templates written as Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.

We currently support [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Google (Gemini/Vertex)](https://ai.google.dev/), [Groq](https://groq.com/), [xAI](https://x.ai/api), [Mistral](https://mistral.ai/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Amazon Bedrock](https://aws.amazon.com/bedrock/).

If there are any providers we don't yet support that you'd like to see supported, let us know!

API Documentation

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#basic-usage-and-syntax)

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

![Mirascope Frog Logo](https://mirascope.com/assets/branding/mirascope-logo.svg)

Mirascope

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
```

Official provider SDKs typically require more boilerplate code:

Official SDK

```
from openai import OpenAI

client = OpenAI()

def recommend_book(genre: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return str(completion.choices[0].message.content)

output = recommend_book("fantasy")
print(output)
```

Notice how Mirascope makes calls more readable by reducing boilerplate and standardizing interactions with LLM providers.

The `llm.call` decorator accepts `provider` and `model` arguments and returns a provider-agnostic `CallResponse` instance that provides a consistent interface regardless of the underlying provider. You can find more information on `CallResponse` in the [section below](https://mirascope.com/docs/mirascope/learn/calls#handling-responses) on handling responses.

Note the `@prompt_template` decorator is optional unless you're using string templates.

### Runtime Provider Overrides [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#runtime-provider-overrides)

You can override provider settings at runtime using `llm.override`. This takes a function decorated with `llm.call` and lets you specify:

- `provider`: Change the provider being called
- `model`: Use a different model
- `call_params`: Override call parameters like temperature
- `client`: Use a different client instance

When overriding with a specific `provider`, you must specify the `model` parameter.

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response: llm.CallResponse = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider="anthropic",
    model="claude-3-5-sonnet-latest",
    call_params={"temperature": 0.7},
)("fantasy")

print(override_response.content)
```

## Handling Responses [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#handling-responses)

### Common Response Properties and Methods [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#common-response-properties-and-methods)

API Documentation

All [`BaseCallResponse`](https://mirascope.com/docs/mirascope/api) objects share these common properties:

- `content`: The main text content of the response. If no content is present, this will be the empty string.
- `finish_reasons`: A list of reasons why the generation finished (e.g., "stop", "length"). These will be typed specifically for the provider used. If no finish reasons are present, this will be `None`.
- `model`: The name of the model used for generation.
- `id`: A unique identifier for the response if available. Otherwise this will be `None`.
- `usage`: Information about token usage for the call if available. Otherwise this will be `None`.
- `input_tokens`: The number of input tokens used if available. Otherwise this will be `None`.
- `output_tokens`: The number of output tokens generated if available. Otherwise this will be `None`.
- `cost`: An estimated cost of the API call if available. Otherwise this will be `None`.
- `message_param`: The assistant's response formatted as a message parameter.
- `tools`: A list of provider-specific tools used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](https://mirascope.com/docs/mirascope/learn/tools) documentation for more details.
- `tool`: The first tool used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](https://mirascope.com/docs/mirascope/learn/tools) documentation for more details.
- `tool_types`: A list of tool types used in the call, if any. Otherwise this will be `None`.
- `prompt_template`: The prompt template used for the call.
- `fn_args`: The arguments passed to the function.
- `dynamic_config`: The dynamic configuration used for the call.
- `metadata`: Any metadata provided using the dynamic configuration.
- `messages`: The list of messages sent in the request.
- `call_params`: The call parameters provided to the `call` decorator.
- `call_kwargs`: The finalized keyword arguments used to make the API call.
- `user_message_param`: The most recent user message, if any. Otherwise this will be `None`.
- `start_time`: The timestamp when the call started.
- `end_time`: The timestamp when the call ended.

There are also two common methods:

- `__str__`: Returns the `content` property of the response for easy printing.
- `tool_message_params`: Creates message parameters for tool call results. Check out the [`Tools`](https://mirascope.com/docs/mirascope/learn/tools) documentation for more information.

## Multi-Modal Outputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#multi-modal-outputs)

While most LLM providers focus on text outputs, some providers support additional output modalities like audio. The availability of multi-modal outputs varies among providers:

| Provider | Text | Audio | Image |
| --- | --- | --- | --- |
| OpenAI | ✓ | ✓ | — |
| Anthropic | ✓ | — | — |
| Mistral | ✓ | — | — |
| Google Gemini | ✓ | — | — |
| Groq | ✓ | — | — |
| Cohere | ✓ | — | — |
| LiteLLM | ✓ | — | — |
| Azure AI | ✓ | — | — |

_Legend: ✓ (Supported), — (Not Supported)_

### Audio Outputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#audio-outputs)

- `audio`: Configuration for the audio output (voice, format, etc.)
- `modalities`: List of output modalities to receive (e.g. `["text", "audio"]`)

For providers that support audio outputs, you can receive both text and audio responses from your calls:

```
import io
import wave

from pydub.playback import play
from pydub import AudioSegment

from mirascope.core import openai

@openai.call(
    "gpt-4o-audio-preview",
    call_params={
        "audio": {"voice": "alloy", "format": "wav"},
        "modalities": ["text", "audio"],
    },
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book(genre="fantasy")

print(response.audio_transcript)

if audio := response.audio:
    audio_io = io.BytesIO(audio)

    with wave.open(audio_io, "rb") as f:
        audio_segment = AudioSegment.from_raw(
            audio_io,
            sample_width=f.getsampwidth(),
            frame_rate=f.getframerate(),
            channels=f.getnchannels(),
        )

    play(audio_segment)
```

When using models that support audio outputs, you'll have access to:

- `content`: The text content of the response
- `audio`: The raw audio bytes of the response
- `audio_transcript`: The transcript of the audio response

Audio Playback Requirements

Voice Options

## Common Parameters Across Providers [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#common-parameters-across-providers)

There are several common parameters that you'll find across all providers when using the `call` decorator. These parameters allow you to control various aspects of the LLM call:

- `model`: The only required parameter for all providers, which may be passed in as a standard argument (whereas all others are optional and must be provided as keyword arguments). It specifies which language model to use for the generation. Each provider has its own set of available models.
- `stream`: A boolean that determines whether the response should be streamed or returned as a complete response. We cover this in more detail in the [`Streams`](https://mirascope.com/docs/mirascope/learn/streams) documentation.
- `response_model`: A Pydantic `BaseModel` type that defines how to structure the response. We cover this in more detail in the [`Response Models`](https://mirascope.com/docs/mirascope/learn/response_models) documentation.
- `output_parser`: A function for parsing the response output. We cover this in more detail in the [`Output Parsers`](https://mirascope.com/docs/mirascope/learn/output_parsers) documentation.
- `json_mode`: A boolean that deterines whether to use JSON mode or not. We cover this in more detail in the [`JSON Mode`](https://mirascope.com/docs/mirascope/learn/json_mode) documentation.
- `tools`: A list of tools that the model may request to use in its response. We cover this in more detail in the [`Tools`](https://mirascope.com/docs/mirascope/learn/tools) documentation.
- `client`: A custom client to use when making the call to the LLM. We cover this in more detail in the [`Custom Client`](https://mirascope.com/docs/mirascope/learn/calls#custom-client) section below.
- `call_params`: The provider-specific parameters to use when making the call to that provider's API. We cover this in more detail in the [`Provider-Specific Usage`](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-usage) section below.

These common parameters provide a consistent way to control the behavior of LLM calls across different providers. Keep in mind that while these parameters are widely supported, there might be slight variations in how they're implemented or their exact effects across different providers (and the documentation should cover any such differences).

Since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior). This presents one way to pass provider-specific parameters (or deprecated parameters) while still using the general interface.

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
```

## Dynamic Configuration [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#dynamic-configuration)

Often you will want (or need) to configure your calls dynamically at runtime. Mirascope supports returning a `BaseDynamicConfig` from your prompt template, which will then be used to dynamically update the settings of the call.

In all cases, you will need to return your prompt messages through the `messages` keyword of the dynamic config unless you're using string templates.

### Call Params [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#call-params)

ShorthandTemplate

```
from mirascope import BaseDynamicConfig, Messages, llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }

response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
```

### Metadata [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#metadata)

ShorthandTemplate

```
from mirascope import BaseDynamicConfig, Messages, llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }

response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
```

## Provider-Specific Usage [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#provider-specific-usage)

API Documentation

While Mirascope provides a consistent interface across different LLM providers, you can also use provider-specific modules with refined typing for an individual provider.

When using the provider modules, you'll receive a provider-specific `BaseCallResponse` object, which may have extra properties. Regardless, you can always access the full, provider-specific response object as `response.response`.

ShorthandTemplate

```
from mirascope.core import openai

@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
```

Reasoning For Provider-Specific BaseCallResponse Objects

### Custom Messages [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#custom-messages)

When using provider-specific calls, you can also always return the original message types for that provider. To do so, simply return the provider-specific dynamic config:

```
from mirascope.core import openai

@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}

response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
```

Support for provider-specific messages ensures that you can still access newly released provider-specific features that Mirascope may not yet support natively.

### Custom Client [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#custom-client)

Mirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.

**Decorator Parameter:**

You can pass a client to the `call` decorator using the `client` parameter:

ShorthandTemplate

```
from mirascope.core import openai
from openai import OpenAI

@openai.call("gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
```

**Dynamic Configuration:**

You can also configure the client dynamically at runtime through the dynamic configuration:

ShorthandTemplate

```
from mirascope.core import openai, Messages
from openai import OpenAI

@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": OpenAI(),
    }
```

Make sure to use the correct client!

## Error Handling [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#error-handling)

When making LLM calls, it's important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

try:
    response: llm.CallResponse = recommend_book("fantasy")
    print(response.content)
except Exception as e:
    print(f"Error: {str(e)}")
```

These examples catch the base Exception class; however, you can (and should) catch provider-specific exceptions instead when using provider-specific modules.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/calls\#next-steps)

By mastering calls in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend choosing one of:

- [Streams](https://mirascope.com/docs/mirascope/learn/streams) to see how to stream call responses for a more real-time interaction.
- [Chaining](https://mirascope.com/docs/mirascope/learn/chaining) to see how to chain calls together.
- [Response Models](https://mirascope.com/docs/mirascope/learn/response_models) to see how to generate structured outputs.
- [Tools](https://mirascope.com/docs/mirascope/learn/tools) to see how to give LLMs access to custom tools to extend their capabilities.
- [Async](https://mirascope.com/docs/mirascope/learn/async) to see how to better take advantage of asynchronous programming and parallelization for improved performance.

Pick whichever path aligns best with what you're hoping to get from Mirascope.

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