---
url: "https://mirascope.com/docs/mirascope/learn/streams"
title: "Streams | Mirascope"
---

# Streams [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#streams)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

Streaming is a powerful feature when using LLMs that allows you to process chunks of an LLM response in real-time as they are generated. This can be particularly useful for long-running tasks, providing immediate feedback to users, or implementing more responsive applications.

Diagram illustrating standard vs. streaming responses

This approach offers several benefits:

1. **Immediate feedback**: Users can see responses as they're being generated, creating a more interactive experience.
2. **Reduced latency**: For long responses, users don't have to wait for the entire generation to complete before seeing results.
3. **Incremental processing**: Applications can process and act on partial results as they arrive.
4. **Efficient resource use**: Memory usage can be optimized by processing chunks instead of storing the entire response.
5. **Early termination**: If the desired information is found early in the response, processing can be stopped without waiting for the full generation.

API Documentation

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#basic-usage-and-syntax)

To use streaming, simply set the `stream` parameter to `True` in your [`call`](https://mirascope.com/docs/mirascope/learn/calls) decorator:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

In this example:

1. We use the `call` decorator with `stream=True` to enable streaming.
2. The `recommend_book` function now returns a generator that yields `(chunk, tool)` tuples of the response.
3. We iterate over the chunks, printing each one as it's received.
4. We use `end=""` and `flush=True` parameters in the print function to ensure that the output is displayed in real-time without line breaks.

## Handling Streamed Responses [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#handling-streamed-responses)

API Documentation

When streaming, the initial response will be a provider-specific [`BaseStream`](https://mirascope.com/docs/mirascope/api) instance (e.g. `OpenAIStream`), which is a generator that yields tuples `(chunk, tool)` where `chunk` is a provider-specific [`BaseCallResponseChunk`](https://mirascope.com/docs/mirascope/api) (e.g. `OpenAICallResponseChunk`) that wraps the original chunk in the provider's response. These objects provide a consistent interface across providers while still allowing access to provider-specific details.

Streaming Tools

You'll notice in the above example that we ignore the `tool` in each tuple. If no tools are set in the call, then `tool` will always be `None` and can be safely ignored. For more details, check out the documentation on [streaming tools](https://mirascope.com/docs/mirascope/learn/tools#streaming-tools)

### Common Chunk Properties and Methods [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#common-chunk-properties-and-methods)

All `BaseCallResponseChunk` objects share these common properties:

- `content`: The main text content of the response. If no content is present, this will be the empty string.
- `finish_reasons`: A list of reasons why the generation finished (e.g., "stop", "length"). These will be typed specifically for the provider used. If no finish reasons are present, this will be `None`.
- `model`: The name of the model used for generation.
- `id`: A unique identifier for the response if available. Otherwise this will be `None`.
- `usage`: Information about token usage for the call if available. Otherwise this will be `None`.
- `input_tokens`: The number of input tokens used if available. Otherwise this will be `None`.
- `output_tokens`: The number of output tokens generated if available. Otherwise this will be `None`.

### Common Stream Properties and Methods [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#common-stream-properties-and-methods)

Must Exhaust Stream

To access these properties, you must first exhaust the stream by iterating through it.

Once exhausted, all `BaseStream` objects share the [same common properties and methods as `BaseCallResponse`](https://mirascope.com/docs/mirascope/learn/calls#common-response-properties-and-methods), except for `usage`, `tools`, `tool`, and `__str__`.

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)

print(f"Content: {stream.content}")
```

You can access the additional missing properties by using the method `construct_call_response` to reconstruct a provider-specific `BaseCallResponse` instance:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)

print(f"Content: {stream.content}")

call_response = stream.construct_call_response()
print(f"Usage: {call_response.usage}")
```

Reconstructed Response Limitations

While we try our best to reconstruct the `BaseCallResponse` instance from the stream, there's always a chance that some information present in a standard call might be missing from the stream.

### Provider-Specific Response Details [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#provider-specific-response-details)

While Mirascope provides a consistent interface, you can always access the full, provider-specific response object if needed. This is available through the `chunk` property of the `BaseCallResponseChunk` object:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(f"Original chunk: {chunk.chunk}")
    print(chunk.content, end="", flush=True)
```

Reasoning For Provider-Specific BaseCallResponseChunk Objects

The reason that we have provider-specific response objects (e.g. `OpenAICallResponseChunk`) is to provide proper type hints and safety when accessing the original response chunk.

## Multi-Modal Outputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#multi-modal-outputs)

While most LLM providers focus on text streaming, some providers support streaming additional output modalities like audio. The availability of multi-modal streaming varies among providers:

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

### Audio Streaming [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#audio-streaming)

For providers that support audio outputs, you can stream both text and audio responses simultaneously:

```
import io

from pydub.playback import play
from pydub import AudioSegment

from mirascope.core import openai, Messages

SAMPLE_WIDTH = 2
FRAME_RATE = 24000
CHANNELS = 1

@openai.call(
    "gpt-4o-audio-preview",
    call_params={
        "audio": {"voice": "alloy", "format": "pcm16"},
        "modalities": ["text", "audio"],
    },
    stream=True,
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")

audio_chunk = b""
audio_transcript_chunk = ""

stream = recommend_book("fantasy")
for chunk, _ in stream:
    if chunk.audio:
        audio_chunk += chunk.audio
    if chunk.audio_transcript:
        audio_transcript_chunk += chunk.audio_transcript

print(audio_transcript_chunk)

audio_segment = AudioSegment.from_raw(
    io.BytesIO(audio_chunk),
    sample_width=SAMPLE_WIDTH,
    frame_rate=FRAME_RATE,
    channels=CHANNELS,
)
play(audio_segment)
```

Each stream chunk provides access to:

- `chunk.audio`: Raw audio data in bytes format
- `chunk.audio_transcript`: The transcript of the audio

This allows you to process both text and audio streams concurrently. Since audio data is received in chunks, you could technically begin playback before receiving the complete response.

Audio Playback Requirements

The example above uses `pydub` and `ffmpeg` for audio playback, but you can use any audio processing libraries or media players that can handle WAV format audio data. Choose the tools that best fit your needs and environment.

If you decide to use pydub:

- Install [pydub](https://github.com/jiaaro/pydub): `pip install pydub`
- Install ffmpeg: Available from [ffmpeg.org](https://www.ffmpeg.org/) or through system package managers

Voice Options

For providers that support audio outputs, refer to their documentation for available voice options and configurations:

- OpenAI: [Text to Speech Guide](https://platform.openai.com/docs/guides/text-to-speech)

## Error Handling [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#error-handling)

Error handling in streams is similar to standard non-streaming calls. However, it's important to note that errors may occur during iteration rather than at the initial function call:

```
from mirascope.core import Messages, openai
from openai import OpenAIError

@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")

try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except OpenAIError as e:
    print(f"Error: {str(e)}")
```

In these examples we show provider-specific error handling, though you can also catch generic exceptions.

Note how we wrap the iteration loop in a try/except block to catch any errors that might occur during streaming.

When Errors Occur

The initial response when calling an LLM function with `stream=True` will return a generator. Any errors that may occur during streaming will not happen until you actually iterate through the generator. This is why we wrap the generation loop in the try/except block and not just the call to `recommend_book`.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/streams\#next-steps)

By leveraging streaming effectively, you can create more responsive and efficient LLM-powered applications with Mirascope's streaming capabilities.

Next, we recommend taking a look at the [Chaining](https://mirascope.com/docs/mirascope/learn/chaining) documentation, which shows you how to break tasks down into smaller, more directed calls and chain them together.

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