---
url: "https://docs.litellm.ai/docs/text_to_speech"
title: "/audio/speech | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/text_to_speech#__docusaurus_skipToContent_fallback)

On this page

# /audio/speech

## **LiteLLM Python SDK Usage** [​](https://docs.litellm.ai/docs/text_to_speech\#litellm-python-sdk-usage "Direct link to litellm-python-sdk-usage")

### Quick Start [​](https://docs.litellm.ai/docs/text_to_speech\#quick-start "Direct link to Quick Start")

```codeBlockLines_e6Vv
from pathlib import Path
from litellm import speech
import os

os.environ["OPENAI_API_KEY"] = "sk-.."

speech_file_path = Path(__file__).parent / "speech.mp3"
response = speech(
        model="openai/tts-1",
        voice="alloy",
        input="the quick brown fox jumped over the lazy dogs",
    )
response.stream_to_file(speech_file_path)

```

### Async Usage [​](https://docs.litellm.ai/docs/text_to_speech\#async-usage "Direct link to Async Usage")

```codeBlockLines_e6Vv
from litellm import aspeech
from pathlib import Path
import os, asyncio

os.environ["OPENAI_API_KEY"] = "sk-.."

async def test_async_speech():
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = await litellm.aspeech(
            model="openai/tts-1",
            voice="alloy",
            input="the quick brown fox jumped over the lazy dogs",
            api_base=None,
            api_key=None,
            organization=None,
            project=None,
            max_retries=1,
            timeout=600,
            client=None,
            optional_params={},
        )
    response.stream_to_file(speech_file_path)

asyncio.run(test_async_speech())

```

## **LiteLLM Proxy Usage** [​](https://docs.litellm.ai/docs/text_to_speech\#litellm-proxy-usage "Direct link to litellm-proxy-usage")

LiteLLM provides an openai-compatible `/audio/speech` endpoint for Text-to-speech calls.

```codeBlockLines_e6Vv
curl http://0.0.0.0:4000/v1/audio/speech \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "The quick brown fox jumped over the lazy dog.",
    "voice": "alloy"
  }' \
  --output speech.mp3

```

**Setup**

```codeBlockLines_e6Vv
- model_name: tts
  litellm_params:
    model: openai/tts-1
    api_key: os.environ/OPENAI_API_KEY

```

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000

```

## **Supported Providers** [​](https://docs.litellm.ai/docs/text_to_speech\#supported-providers "Direct link to supported-providers")

| Provider | Link to Usage |
| --- | --- |
| OpenAI | [Usage](https://docs.litellm.ai/docs/text_to_speech#quick-start) |
| Azure OpenAI | [Usage](https://docs.litellm.ai/docs/providers/azure#azure-text-to-speech-tts) |
| Vertex AI | [Usage](https://docs.litellm.ai/docs/providers/vertex#text-to-speech-apis) |

## ✨ Enterprise LiteLLM Proxy - Set Max Request File Size [​](https://docs.litellm.ai/docs/text_to_speech\#-enterprise-litellm-proxy---set-max-request-file-size "Direct link to ✨ Enterprise LiteLLM Proxy - Set Max Request File Size")

Use this when you want to limit the file size for requests sent to `audio/transcriptions`

```codeBlockLines_e6Vv
- model_name: whisper
  litellm_params:
    model: whisper-1
    api_key: sk-*******
    max_file_size_mb: 0.00001 # 👈 max file size in MB  (Set this intentionally very small for testing)
  model_info:
    mode: audio_transcription

```

Make a test Request with a valid file

```codeBlockLines_e6Vv
curl --location 'http://localhost:4000/v1/audio/transcriptions' \
--header 'Authorization: Bearer sk-1234' \
--form 'file=@"/Users/ishaanjaffer/Github/litellm/tests/gettysburg.wav"' \
--form 'model="whisper"'

```

Expect to see the follow response

```codeBlockLines_e6Vv
{"error":{"message":"File size is too large. Please check your file size. Passed file size: 0.7392807006835938 MB. Max file size: 0.0001 MB","type":"bad_request","param":"file","code":500}}%

```

- [**LiteLLM Python SDK Usage**](https://docs.litellm.ai/docs/text_to_speech#litellm-python-sdk-usage)
  - [Quick Start](https://docs.litellm.ai/docs/text_to_speech#quick-start)
  - [Async Usage](https://docs.litellm.ai/docs/text_to_speech#async-usage)
- [**LiteLLM Proxy Usage**](https://docs.litellm.ai/docs/text_to_speech#litellm-proxy-usage)
- [**Supported Providers**](https://docs.litellm.ai/docs/text_to_speech#supported-providers)
- [✨ Enterprise LiteLLM Proxy - Set Max Request File Size](https://docs.litellm.ai/docs/text_to_speech#-enterprise-litellm-proxy---set-max-request-file-size)