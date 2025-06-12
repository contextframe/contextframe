---
url: "https://docs.litellm.ai/docs/anthropic_unified"
title: "/v1/messages [BETA] | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/anthropic_unified#__docusaurus_skipToContent_fallback)

On this page

# /v1/messages \[BETA\]

Use LiteLLM to call all your LLM APIs in the Anthropic `v1/messages` format.

## Overview [​](https://docs.litellm.ai/docs/anthropic_unified\#overview "Direct link to Overview")

| Feature | Supported | Notes |
| --- | --- | --- |
| Cost Tracking | ✅ |  |
| Logging | ✅ | works across all integrations |
| End-user Tracking | ✅ |  |
| Streaming | ✅ |  |
| Fallbacks | ✅ | between supported models |
| Loadbalancing | ✅ | between supported models |
| Support llm providers | **All LiteLLM supported providers** | `openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai`, etc. |

## Usage [​](https://docs.litellm.ai/docs/anthropic_unified\#usage "Direct link to Usage")

* * *

### LiteLLM Python SDK [​](https://docs.litellm.ai/docs/anthropic_unified\#litellm-python-sdk "Direct link to LiteLLM Python SDK")

- Anthropic
- OpenAI
- Google AI Studio
- Vertex AI
- AWS Bedrock

#### Non-streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#non-streaming-example "Direct link to Non-streaming example")

Anthropic Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    api_key=api_key,
    model="anthropic/claude-3-haiku-20240307",
    max_tokens=100,
)

```

#### Streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#streaming-example "Direct link to Streaming example")

Anthropic Streaming Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    api_key=api_key,
    model="anthropic/claude-3-haiku-20240307",
    max_tokens=100,
    stream=True,
)
async for chunk in response:
    print(chunk)

```

#### Non-streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#non-streaming-example-1 "Direct link to Non-streaming example")

OpenAI Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="openai/gpt-4",
    max_tokens=100,
)

```

#### Streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#streaming-example-1 "Direct link to Streaming example")

OpenAI Streaming Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="openai/gpt-4",
    max_tokens=100,
    stream=True,
)
async for chunk in response:
    print(chunk)

```

#### Non-streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#non-streaming-example-2 "Direct link to Non-streaming example")

Google Gemini Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="gemini/gemini-2.0-flash-exp",
    max_tokens=100,
)

```

#### Streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#streaming-example-2 "Direct link to Streaming example")

Google Gemini Streaming Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="gemini/gemini-2.0-flash-exp",
    max_tokens=100,
    stream=True,
)
async for chunk in response:
    print(chunk)

```

#### Non-streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#non-streaming-example-3 "Direct link to Non-streaming example")

Vertex AI Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set credentials - Vertex AI uses application default credentials
# Run 'gcloud auth application-default login' to authenticate
os.environ["VERTEXAI_PROJECT"] = "your-gcp-project-id"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="vertex_ai/gemini-2.0-flash-exp",
    max_tokens=100,
)

```

#### Streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#streaming-example-3 "Direct link to Streaming example")

Vertex AI Streaming Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set credentials - Vertex AI uses application default credentials
# Run 'gcloud auth application-default login' to authenticate
os.environ["VERTEXAI_PROJECT"] = "your-gcp-project-id"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="vertex_ai/gemini-2.0-flash-exp",
    max_tokens=100,
    stream=True,
)
async for chunk in response:
    print(chunk)

```

#### Non-streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#non-streaming-example-4 "Direct link to Non-streaming example")

AWS Bedrock Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-access-key"
os.environ["AWS_REGION_NAME"] = "us-west-2"  # or your AWS region

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=100,
)

```

#### Streaming example [​](https://docs.litellm.ai/docs/anthropic_unified\#streaming-example-4 "Direct link to Streaming example")

AWS Bedrock Streaming Example using LiteLLM Python SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-access-key"
os.environ["AWS_REGION_NAME"] = "us-west-2"  # or your AWS region

response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=100,
    stream=True,
)
async for chunk in response:
    print(chunk)

```

Example response:

```codeBlockLines_e6Vv
{
  "content": [\
    {\
      "text": "Hi! this is a very short joke",\
      "type": "text"\
    }\
  ],
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "model": "claude-3-7-sonnet-20250219",
  "role": "assistant",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "type": "message",
  "usage": {
    "input_tokens": 2095,
    "output_tokens": 503,
    "cache_creation_input_tokens": 2095,
    "cache_read_input_tokens": 0
  }
}

```

### LiteLLM Proxy Server [​](https://docs.litellm.ai/docs/anthropic_unified\#litellm-proxy-server "Direct link to LiteLLM Proxy Server")

- Anthropic
- OpenAI
- Google AI Studio
- Vertex AI
- AWS Bedrock
- curl

1. Setup config.yaml

```codeBlockLines_e6Vv
model_list:
    - model_name: anthropic-claude
      litellm_params:
        model: claude-3-7-sonnet-latest
        api_key: os.environ/ANTHROPIC_API_KEY

```

2. Start proxy

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

```

3. Test it!

Anthropic Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import anthropic

# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-1234",
)

response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="anthropic-claude",
    max_tokens=100,
)

```

1. Setup config.yaml

```codeBlockLines_e6Vv
model_list:
    - model_name: openai-gpt4
      litellm_params:
        model: openai/gpt-4
        api_key: os.environ/OPENAI_API_KEY

```

2. Start proxy

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

```

3. Test it!

OpenAI Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import anthropic

# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-1234",
)

response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="openai-gpt4",
    max_tokens=100,
)

```

1. Setup config.yaml

```codeBlockLines_e6Vv
model_list:
    - model_name: gemini-2-flash
      litellm_params:
        model: gemini/gemini-2.0-flash-exp
        api_key: os.environ/GEMINI_API_KEY

```

2. Start proxy

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

```

3. Test it!

Google Gemini Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import anthropic

# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-1234",
)

response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="gemini-2-flash",
    max_tokens=100,
)

```

1. Setup config.yaml

```codeBlockLines_e6Vv
model_list:
    - model_name: vertex-gemini
      litellm_params:
        model: vertex_ai/gemini-2.0-flash-exp
        vertex_project: your-gcp-project-id
        vertex_location: us-central1

```

2. Start proxy

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

```

3. Test it!

Vertex AI Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import anthropic

# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-1234",
)

response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="vertex-gemini",
    max_tokens=100,
)

```

1. Setup config.yaml

```codeBlockLines_e6Vv
model_list:
    - model_name: bedrock-claude
      litellm_params:
        model: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
        aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
        aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
        aws_region_name: us-west-2

```

2. Start proxy

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

```

3. Test it!

AWS Bedrock Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import anthropic

# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-1234",
)

response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="bedrock-claude",
    max_tokens=100,
)

```

Example using LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
curl -L -X POST 'http://0.0.0.0:4000/v1/messages' \
-H 'content-type: application/json' \
-H 'x-api-key: $LITELLM_API_KEY' \
-H 'anthropic-version: 2023-06-01' \
-d '{
  "model": "anthropic-claude",
  "messages": [\
    {\
      "role": "user",\
      "content": "Hello, can you tell me a short joke?"\
    }\
  ],
  "max_tokens": 100
}'

```

## Request Format [​](https://docs.litellm.ai/docs/anthropic_unified\#request-format "Direct link to Request Format")

* * *

Request body will be in the Anthropic messages API format. **litellm follows the Anthropic messages specification for this endpoint.**

#### Example request body [​](https://docs.litellm.ai/docs/anthropic_unified\#example-request-body "Direct link to Example request body")

```codeBlockLines_e6Vv
{
  "model": "claude-3-7-sonnet-20250219",
  "max_tokens": 1024,
  "messages": [\
    {\
      "role": "user",\
      "content": "Hello, world"\
    }\
  ]
}

```

#### Required Fields [​](https://docs.litellm.ai/docs/anthropic_unified\#required-fields "Direct link to Required Fields")

- **model** (string):

The model identifier (e.g., `"claude-3-7-sonnet-20250219"`).
- **max\_tokens** (integer):

The maximum number of tokens to generate before stopping.

_Note: The model may stop before reaching this limit; value must be greater than 1._
- **messages** (array of objects):

An ordered list of conversational turns.

Each message object must include:
  - **role** (enum: `"user"` or `"assistant"`):

    Specifies the speaker of the message.
  - **content** (string or array of content blocks):

    The text or content blocks (e.g., an array containing objects with a `type` such as `"text"`) that form the message.

    _Example equivalence:_




    ```codeBlockLines_e6Vv
    {"role": "user", "content": "Hello, Claude"}

    ```








    is equivalent to:




    ```codeBlockLines_e6Vv
    {"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}

    ```

#### Optional Fields [​](https://docs.litellm.ai/docs/anthropic_unified\#optional-fields "Direct link to Optional Fields")

- **metadata** (object):

Contains additional metadata about the request (e.g., `user_id` as an opaque identifier).
- **stop\_sequences** (array of strings):

Custom sequences that, when encountered in the generated text, cause the model to stop.
- **stream** (boolean):

Indicates whether to stream the response using server-sent events.
- **system** (string or array):

A system prompt providing context or specific instructions to the model.
- **temperature** (number):

Controls randomness in the model's responses. Valid range: `0 < temperature < 1`.
- **thinking** (object):

Configuration for enabling extended thinking. If enabled, it includes:
  - **budget\_tokens** (integer):

    Minimum of 1024 tokens (and less than `max_tokens`).
  - **type** (enum):

    E.g., `"enabled"`.
- **tool\_choice** (object):

Instructs how the model should utilize any provided tools.
- **tools** (array of objects):

Definitions for tools available to the model. Each tool includes:
  - **name** (string):

    The tool's name.
  - **description** (string):

    A detailed description of the tool.
  - **input\_schema** (object):

    A JSON schema describing the expected input format for the tool.
- **top\_k** (integer):

Limits sampling to the top K options.
- **top\_p** (number):

Enables nucleus sampling with a cumulative probability cutoff. Valid range: `0 < top_p < 1`.

## Response Format [​](https://docs.litellm.ai/docs/anthropic_unified\#response-format "Direct link to Response Format")

* * *

Responses will be in the Anthropic messages API format.

#### Example Response [​](https://docs.litellm.ai/docs/anthropic_unified\#example-response "Direct link to Example Response")

```codeBlockLines_e6Vv
{
  "content": [\
    {\
      "text": "Hi! My name is Claude.",\
      "type": "text"\
    }\
  ],
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "model": "claude-3-7-sonnet-20250219",
  "role": "assistant",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "type": "message",
  "usage": {
    "input_tokens": 2095,
    "output_tokens": 503,
    "cache_creation_input_tokens": 2095,
    "cache_read_input_tokens": 0
  }
}

```

#### Response fields [​](https://docs.litellm.ai/docs/anthropic_unified\#response-fields "Direct link to Response fields")

- **content** (array of objects):

Contains the generated content blocks from the model. Each block includes:

  - **type** (string):

    Indicates the type of content (e.g., `"text"`, `"tool_use"`, `"thinking"`, or `"redacted_thinking"`).
  - **text** (string):

    The generated text from the model.

    _Note: Maximum length is 5,000,000 characters._
  - **citations** (array of objects or `null`):

    Optional field providing citation details. Each citation includes:
    - **cited\_text** (string):

      The excerpt being cited.
    - **document\_index** (integer):

      An index referencing the cited document.
    - **document\_title** (string or `null`):

      The title of the cited document.
    - **start\_char\_index** (integer):

      The starting character index for the citation.
    - **end\_char\_index** (integer):

      The ending character index for the citation.
    - **type** (string):

      Typically `"char_location"`.
- **id** (string):

A unique identifier for the response message.

_Note: The format and length of IDs may change over time._

- **model** (string):

Specifies the model that generated the response.

- **role** (string):

Indicates the role of the generated message. For responses, this is always `"assistant"`.

- **stop\_reason** (string):

Explains why the model stopped generating text. Possible values include:

  - `"end_turn"`: The model reached a natural stopping point.
  - `"max_tokens"`: The generation stopped because the maximum token limit was reached.
  - `"stop_sequence"`: A custom stop sequence was encountered.
  - `"tool_use"`: The model invoked one or more tools.
- **stop\_sequence** (string or `null`):

Contains the specific stop sequence that caused the generation to halt, if applicable; otherwise, it is `null`.

- **type** (string):

Denotes the type of response object, which is always `"message"`.

- **usage** (object):

Provides details on token usage for billing and rate limiting. This includes:

  - **input\_tokens** (integer):

    Total number of input tokens processed.
  - **output\_tokens** (integer):

    Total number of output tokens generated.
  - **cache\_creation\_input\_tokens** (integer or `null`):

    Number of tokens used to create a cache entry.
  - **cache\_read\_input\_tokens** (integer or `null`):

    Number of tokens read from the cache.

- [Overview](https://docs.litellm.ai/docs/anthropic_unified#overview)
- [Usage](https://docs.litellm.ai/docs/anthropic_unified#usage)
  - [LiteLLM Python SDK](https://docs.litellm.ai/docs/anthropic_unified#litellm-python-sdk)
  - [LiteLLM Proxy Server](https://docs.litellm.ai/docs/anthropic_unified#litellm-proxy-server)
- [Request Format](https://docs.litellm.ai/docs/anthropic_unified#request-format)
- [Response Format](https://docs.litellm.ai/docs/anthropic_unified#response-format)