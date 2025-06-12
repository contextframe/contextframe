---
url: "https://docs.litellm.ai/docs/"
title: "LiteLLM - Getting Started | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/#__docusaurus_skipToContent_fallback)

On this page

# LiteLLM - Getting Started

[https://github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)

## **Call 100+ LLMs using the OpenAI Input/Output Format** [​](https://docs.litellm.ai/docs/\#call-100-llms-using-the-openai-inputoutput-format "Direct link to call-100-llms-using-the-openai-inputoutput-format")

- Translate inputs to provider's `completion`, `embedding`, and `image_generation` endpoints
- [Consistent output](https://docs.litellm.ai/docs/completion/output), text responses will always be available at `['choices'][0]['message']['content']`
- Retry/fallback logic across multiple deployments (e.g. Azure/OpenAI) - [Router](https://docs.litellm.ai/docs/routing)
- Track spend & set budgets per project [LiteLLM Proxy Server](https://docs.litellm.ai/docs/simple_proxy)

## How to use LiteLLM [​](https://docs.litellm.ai/docs/\#how-to-use-litellm "Direct link to How to use LiteLLM")

You can use litellm through either:

1. [LiteLLM Proxy Server](https://docs.litellm.ai/docs/#litellm-proxy-server-llm-gateway) \- Server (LLM Gateway) to call 100+ LLMs, load balance, cost tracking across projects
2. [LiteLLM python SDK](https://docs.litellm.ai/docs/#basic-usage) \- Python Client to call 100+ LLMs, load balance, cost tracking

### **When to use LiteLLM Proxy Server (LLM Gateway)** [​](https://docs.litellm.ai/docs/\#when-to-use-litellm-proxy-server-llm-gateway "Direct link to when-to-use-litellm-proxy-server-llm-gateway")

tip

Use LiteLLM Proxy Server if you want a **central service (LLM Gateway) to access multiple LLMs**

Typically used by Gen AI Enablement / ML PLatform Teams

- LiteLLM Proxy gives you a unified interface to access multiple LLMs (100+ LLMs)
- Track LLM Usage and setup guardrails
- Customize Logging, Guardrails, Caching per project

### **When to use LiteLLM Python SDK** [​](https://docs.litellm.ai/docs/\#when-to-use-litellm-python-sdk "Direct link to when-to-use-litellm-python-sdk")

tip

Use LiteLLM Python SDK if you want to use LiteLLM in your **python code**

Typically used by developers building llm projects

- LiteLLM SDK gives you a unified interface to access multiple LLMs (100+ LLMs)
- Retry/fallback logic across multiple deployments (e.g. Azure/OpenAI) - [Router](https://docs.litellm.ai/docs/routing)

## **LiteLLM Python SDK** [​](https://docs.litellm.ai/docs/\#litellm-python-sdk "Direct link to litellm-python-sdk")

### Basic usage [​](https://docs.litellm.ai/docs/\#basic-usage "Direct link to Basic usage")

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BerriAI/litellm/blob/main/cookbook/liteLLM_Getting_Started.ipynb)

```codeBlockLines_e6Vv
pip install litellm

```

- OpenAI
- Anthropic
- xAI
- VertexAI
- NVIDIA
- HuggingFace
- Azure OpenAI
- Ollama
- Openrouter
- Novita AI

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "your-api-key"

response = completion(
  model="openai/gpt-4o",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

response = completion(
  model="anthropic/claude-3-sonnet-20240229",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["XAI_API_KEY"] = "your-api-key"

response = completion(
  model="xai/grok-2-latest",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

# auth: run 'gcloud auth application-default'
os.environ["VERTEXAI_PROJECT"] = "hardy-device-386718"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

response = completion(
  model="vertex_ai/gemini-1.5-pro",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["NVIDIA_NIM_API_KEY"] = "nvidia_api_key"
os.environ["NVIDIA_NIM_API_BASE"] = "nvidia_nim_endpoint_url"

response = completion(
  model="nvidia_nim/<model_name>",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

os.environ["HUGGINGFACE_API_KEY"] = "huggingface_api_key"

# e.g. Call 'WizardLM/WizardCoder-Python-34B-V1.0' hosted on HF Inference endpoints
response = completion(
  model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  api_base="https://my-endpoint.huggingface.cloud"
)

print(response)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

# azure call
response = completion(
  "azure/<your_deployment_name>",
  messages = [{ "content": "Hello, how are you?","role": "user"}]
)

```

```codeBlockLines_e6Vv
from litellm import completion

response = completion(
            model="ollama/llama2",
            messages = [{ "content": "Hello, how are you?","role": "user"}],
            api_base="http://localhost:11434"
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["OPENROUTER_API_KEY"] = "openrouter_api_key"

response = completion(
  model="openrouter/google/palm-2-chat-bison",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables. Visit https://novita.ai/settings/key-management to get your API key
os.environ["NOVITA_API_KEY"] = "novita-api-key"

response = completion(
  model="novita/deepseek/deepseek-r1",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)

```

### Response Format (OpenAI Format) [​](https://docs.litellm.ai/docs/\#response-format-openai-format "Direct link to Response Format (OpenAI Format)")

```codeBlockLines_e6Vv
{
    "id": "chatcmpl-565d891b-a42e-4c39-8d14-82a1f5208885",
    "created": 1734366691,
    "model": "claude-3-sonnet-20240229",
    "object": "chat.completion",
    "system_fingerprint": null,
    "choices": [\
        {\
            "finish_reason": "stop",\
            "index": 0,\
            "message": {\
                "content": "Hello! As an AI language model, I don't have feelings, but I'm operating properly and ready to assist you with any questions or tasks you may have. How can I help you today?",\
                "role": "assistant",\
                "tool_calls": null,\
                "function_call": null\
            }\
        }\
    ],
    "usage": {
        "completion_tokens": 43,
        "prompt_tokens": 13,
        "total_tokens": 56,
        "completion_tokens_details": null,
        "prompt_tokens_details": {
            "audio_tokens": null,
            "cached_tokens": 0
        },
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0
    }
}

```

### Streaming [​](https://docs.litellm.ai/docs/\#streaming "Direct link to Streaming")

Set `stream=True` in the `completion` args.

- OpenAI
- Anthropic
- xAI
- VertexAI
- NVIDIA
- HuggingFace
- Azure OpenAI
- Ollama
- Openrouter
- Novita AI

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "your-api-key"

response = completion(
  model="openai/gpt-4o",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

response = completion(
  model="anthropic/claude-3-sonnet-20240229",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["XAI_API_KEY"] = "your-api-key"

response = completion(
  model="xai/grok-2-latest",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

# auth: run 'gcloud auth application-default'
os.environ["VERTEX_PROJECT"] = "hardy-device-386718"
os.environ["VERTEX_LOCATION"] = "us-central1"

response = completion(
  model="vertex_ai/gemini-1.5-pro",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["NVIDIA_NIM_API_KEY"] = "nvidia_api_key"
os.environ["NVIDIA_NIM_API_BASE"] = "nvidia_nim_endpoint_url"

response = completion(
  model="nvidia_nim/<model_name>",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

os.environ["HUGGINGFACE_API_KEY"] = "huggingface_api_key"

# e.g. Call 'WizardLM/WizardCoder-Python-34B-V1.0' hosted on HF Inference endpoints
response = completion(
  model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  api_base="https://my-endpoint.huggingface.cloud",
  stream=True,
)

print(response)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

# azure call
response = completion(
  "azure/<your_deployment_name>",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion

response = completion(
            model="ollama/llama2",
            messages = [{ "content": "Hello, how are you?","role": "user"}],
            api_base="http://localhost:11434",
            stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables
os.environ["OPENROUTER_API_KEY"] = "openrouter_api_key"

response = completion(
  model="openrouter/google/palm-2-chat-bison",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

```codeBlockLines_e6Vv
from litellm import completion
import os

## set ENV variables. Visit https://novita.ai/settings/key-management to get your API key
os.environ["NOVITA_API_KEY"] = "novita_api_key"

response = completion(
  model="novita/deepseek/deepseek-r1",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)

```

### Streaming Response Format (OpenAI Format) [​](https://docs.litellm.ai/docs/\#streaming-response-format-openai-format "Direct link to Streaming Response Format (OpenAI Format)")

```codeBlockLines_e6Vv
{
    "id": "chatcmpl-2be06597-eb60-4c70-9ec5-8cd2ab1b4697",
    "created": 1734366925,
    "model": "claude-3-sonnet-20240229",
    "object": "chat.completion.chunk",
    "system_fingerprint": null,
    "choices": [\
        {\
            "finish_reason": null,\
            "index": 0,\
            "delta": {\
                "content": "Hello",\
                "role": "assistant",\
                "function_call": null,\
                "tool_calls": null,\
                "audio": null\
            },\
            "logprobs": null\
        }\
    ]
}

```

### Exception handling [​](https://docs.litellm.ai/docs/\#exception-handling "Direct link to Exception handling")

LiteLLM maps exceptions across all supported providers to the OpenAI exceptions. All our exceptions inherit from OpenAI's exception types, so any error-handling you have for that, should work out of the box with LiteLLM.

```codeBlockLines_e6Vv
from openai.error import OpenAIError
from litellm import completion

os.environ["ANTHROPIC_API_KEY"] = "bad-key"
try:
    # some code
    completion(model="claude-instant-1", messages=[{"role": "user", "content": "Hey, how's it going?"}])
except OpenAIError as e:
    print(e)

```

### Logging Observability - Log LLM Input/Output ( [Docs](https://docs.litellm.ai/docs/observability/callbacks)) [​](https://docs.litellm.ai/docs/\#logging-observability---log-llm-inputoutput-docs "Direct link to logging-observability---log-llm-inputoutput-docs")

LiteLLM exposes pre defined callbacks to send data to Lunary, MLflow, Langfuse, Helicone, Promptlayer, Traceloop, Slack

```codeBlockLines_e6Vv
from litellm import completion

## set env variables for logging tools (API key set up is not required when using MLflow)
os.environ["LUNARY_PUBLIC_KEY"] = "your-lunary-public-key" # get your public key at https://app.lunary.ai/settings
os.environ["HELICONE_API_KEY"] = "your-helicone-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""

os.environ["OPENAI_API_KEY"]

# set callbacks
litellm.success_callback = ["lunary", "mlflow", "langfuse", "helicone"] # log input/output to lunary, mlflow, langfuse, helicone

#openai call
response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}])

```

### Track Costs, Usage, Latency for streaming [​](https://docs.litellm.ai/docs/\#track-costs-usage-latency-for-streaming "Direct link to Track Costs, Usage, Latency for streaming")

Use a callback function for this - more info on custom callbacks: [https://docs.litellm.ai/docs/observability/custom\_callback](https://docs.litellm.ai/docs/observability/custom_callback)

```codeBlockLines_e6Vv
import litellm

# track_cost_callback
def track_cost_callback(
    kwargs,                 # kwargs to completion
    completion_response,    # response from completion
    start_time, end_time    # start/end time
):
    try:
      response_cost = kwargs.get("response_cost", 0)
      print("streaming response_cost", response_cost)
    except:
        pass
# set callback
litellm.success_callback = [track_cost_callback] # set custom callback function

# litellm.completion() call
response = completion(
    model="gpt-3.5-turbo",
    messages=[\
        {\
            "role": "user",\
            "content": "Hi 👋 - i'm openai"\
        }\
    ],
    stream=True
)

```

## **LiteLLM Proxy Server (LLM Gateway)** [​](https://docs.litellm.ai/docs/\#litellm-proxy-server-llm-gateway "Direct link to litellm-proxy-server-llm-gateway")

Track spend across multiple projects/people

![ui_3](https://github.com/BerriAI/litellm/assets/29436595/47c97d5e-b9be-4839-b28c-43d7f4f10033)

The proxy provides:

1. [Hooks for auth](https://docs.litellm.ai/docs/proxy/virtual_keys#custom-auth)
2. [Hooks for logging](https://docs.litellm.ai/docs/proxy/logging#step-1---create-your-custom-litellm-callback-class)
3. [Cost tracking](https://docs.litellm.ai/docs/proxy/virtual_keys#tracking-spend)
4. [Rate Limiting](https://docs.litellm.ai/docs/proxy/users#set-rate-limits)

### 📖 Proxy Endpoints - [Swagger Docs](https://litellm-api.up.railway.app/) [​](https://docs.litellm.ai/docs/\#-proxy-endpoints---swagger-docs "Direct link to -proxy-endpoints---swagger-docs")

Go here for a complete tutorial with keys + rate limits - [**here**](https://docs.litellm.ai/docs/proxy/docker_quick_start)

### Quick Start Proxy - CLI [​](https://docs.litellm.ai/docs/\#quick-start-proxy---cli "Direct link to Quick Start Proxy - CLI")

```codeBlockLines_e6Vv
pip install 'litellm[proxy]'

```

#### Step 1: Start litellm proxy [​](https://docs.litellm.ai/docs/\#step-1-start-litellm-proxy "Direct link to Step 1: Start litellm proxy")

- pip package
- Docker container

```codeBlockLines_e6Vv
$ litellm --model huggingface/bigcode/starcoder

#INFO: Proxy running on http://0.0.0.0:4000

```

Step 1. CREATE config.yaml

Example `litellm_config.yaml`

```codeBlockLines_e6Vv
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: azure/<your-azure-model-deployment>
      api_base: os.environ/AZURE_API_BASE # runs os.getenv("AZURE_API_BASE")
      api_key: os.environ/AZURE_API_KEY # runs os.getenv("AZURE_API_KEY")
      api_version: "2023-07-01-preview"

```

Step 2. RUN Docker Image

```codeBlockLines_e6Vv
docker run \
    -v $(pwd)/litellm_config.yaml:/app/config.yaml \
    -e AZURE_API_KEY=d6*********** \
    -e AZURE_API_BASE=https://openai-***********/ \
    -p 4000:4000 \
    ghcr.io/berriai/litellm:main-latest \
    --config /app/config.yaml --detailed_debug

```

#### Step 2: Make ChatCompletions Request to Proxy [​](https://docs.litellm.ai/docs/\#step-2-make-chatcompletions-request-to-proxy "Direct link to Step 2: Make ChatCompletions Request to Proxy")

```codeBlockLines_e6Vv
import openai # openai v1.0.0+
client = openai.OpenAI(api_key="anything",base_url="http://0.0.0.0:4000") # set proxy to base_url
# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(model="gpt-3.5-turbo", messages = [\
    {\
        "role": "user",\
        "content": "this is a test request, write a short poem"\
    }\
])

print(response)

```

## More details [​](https://docs.litellm.ai/docs/\#more-details "Direct link to More details")

- [exception mapping](https://docs.litellm.ai/docs/exception_mapping)
- [retries + model fallbacks for completion()](https://docs.litellm.ai/docs/completion/reliable_completions)
- [proxy virtual keys & spend management](https://docs.litellm.ai/docs/proxy/virtual_keys)
- [E2E Tutorial for LiteLLM Proxy Server](https://docs.litellm.ai/docs/proxy/docker_quick_start)

- [**Call 100+ LLMs using the OpenAI Input/Output Format**](https://docs.litellm.ai/docs/#call-100-llms-using-the-openai-inputoutput-format)
- [How to use LiteLLM](https://docs.litellm.ai/docs/#how-to-use-litellm)
  - [**When to use LiteLLM Proxy Server (LLM Gateway)**](https://docs.litellm.ai/docs/#when-to-use-litellm-proxy-server-llm-gateway)
  - [**When to use LiteLLM Python SDK**](https://docs.litellm.ai/docs/#when-to-use-litellm-python-sdk)
- [**LiteLLM Python SDK**](https://docs.litellm.ai/docs/#litellm-python-sdk)
  - [Basic usage](https://docs.litellm.ai/docs/#basic-usage)
  - [Response Format (OpenAI Format)](https://docs.litellm.ai/docs/#response-format-openai-format)
  - [Streaming](https://docs.litellm.ai/docs/#streaming)
  - [Streaming Response Format (OpenAI Format)](https://docs.litellm.ai/docs/#streaming-response-format-openai-format)
  - [Exception handling](https://docs.litellm.ai/docs/#exception-handling)
  - [Logging Observability - Log LLM Input/Output (Docs)](https://docs.litellm.ai/docs/#logging-observability---log-llm-inputoutput-docs)
  - [Track Costs, Usage, Latency for streaming](https://docs.litellm.ai/docs/#track-costs-usage-latency-for-streaming)
- [**LiteLLM Proxy Server (LLM Gateway)**](https://docs.litellm.ai/docs/#litellm-proxy-server-llm-gateway)
  - [📖 Proxy Endpoints - Swagger Docs](https://docs.litellm.ai/docs/#-proxy-endpoints---swagger-docs)
  - [Quick Start Proxy - CLI](https://docs.litellm.ai/docs/#quick-start-proxy---cli)
- [More details](https://docs.litellm.ai/docs/#more-details)