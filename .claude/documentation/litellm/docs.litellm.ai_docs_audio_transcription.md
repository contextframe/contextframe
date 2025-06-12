---
url: "https://docs.litellm.ai/docs/audio_transcription"
title: "/audio/transcriptions | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/audio_transcription#__docusaurus_skipToContent_fallback)

On this page

# /audio/transcriptions

Use this to loadbalance across Azure + OpenAI.

## Quick Start [​](https://docs.litellm.ai/docs/audio_transcription\#quick-start "Direct link to Quick Start")

### LiteLLM Python SDK [​](https://docs.litellm.ai/docs/audio_transcription\#litellm-python-sdk "Direct link to LiteLLM Python SDK")

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from litellm import transcription
import os

# set api keys
os.environ["OPENAI_API_KEY"] = ""
audio_file = open("/path/to/audio.mp3", "rb")

response = transcription(model="whisper", file=audio_file)

print(f"response: {response}")

```

### LiteLLM Proxy [​](https://docs.litellm.ai/docs/audio_transcription\#litellm-proxy "Direct link to LiteLLM Proxy")

### Add model to config [​](https://docs.litellm.ai/docs/audio_transcription\#add-model-to-config "Direct link to Add model to config")

- OpenAI
- OpenAI + Azure

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
- model_name: whisper
  litellm_params:
    model: whisper-1
    api_key: os.environ/OPENAI_API_KEY
  model_info:
    mode: audio_transcription

general_settings:
  master_key: sk-1234

```

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
- model_name: whisper
  litellm_params:
    model: whisper-1
    api_key: os.environ/OPENAI_API_KEY
  model_info:
    mode: audio_transcription
- model_name: whisper
  litellm_params:
    model: azure/azure-whisper
    api_version: 2024-02-15-preview
    api_base: os.environ/AZURE_EUROPE_API_BASE
    api_key: os.environ/AZURE_EUROPE_API_KEY
  model_info:
    mode: audio_transcription

general_settings:
  master_key: sk-1234

```

### Start proxy [​](https://docs.litellm.ai/docs/audio_transcription\#start-proxy "Direct link to Start proxy")

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:8000

```

### Test [​](https://docs.litellm.ai/docs/audio_transcription\#test "Direct link to Test")

- Curl
- OpenAI Python SDK

```codeBlockLines_e6Vv
curl --location 'http://0.0.0.0:8000/v1/audio/transcriptions' \
--header 'Authorization: Bearer sk-1234' \
--form 'file=@"/Users/krrishdholakia/Downloads/gettysburg.wav"' \
--form 'model="whisper"'

```

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI
client = openai.OpenAI(
    api_key="sk-1234",
    base_url="http://0.0.0.0:8000"
)

audio_file = open("speech.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper",
  file=audio_file
)

```

## Supported Providers [​](https://docs.litellm.ai/docs/audio_transcription\#supported-providers "Direct link to Supported Providers")

- OpenAI
- Azure
- [Fireworks AI](https://docs.litellm.ai/docs/providers/fireworks_ai#audio-transcription)
- [Groq](https://docs.litellm.ai/docs/providers/groq#speech-to-text---whisper)
- [Deepgram](https://docs.litellm.ai/docs/providers/deepgram)

- [Quick Start](https://docs.litellm.ai/docs/audio_transcription#quick-start)
  - [LiteLLM Python SDK](https://docs.litellm.ai/docs/audio_transcription#litellm-python-sdk)
  - [LiteLLM Proxy](https://docs.litellm.ai/docs/audio_transcription#litellm-proxy)
  - [Add model to config](https://docs.litellm.ai/docs/audio_transcription#add-model-to-config)
  - [Start proxy](https://docs.litellm.ai/docs/audio_transcription#start-proxy)
  - [Test](https://docs.litellm.ai/docs/audio_transcription#test)
- [Supported Providers](https://docs.litellm.ai/docs/audio_transcription#supported-providers)