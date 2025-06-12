---
url: "https://docs.litellm.ai/docs/response_api"
title: "/responses [Beta] | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/response_api#__docusaurus_skipToContent_fallback)

On this page

# /responses \[Beta\]

LiteLLM provides a BETA endpoint in the spec of [OpenAI's `/responses` API](https://platform.openai.com/docs/api-reference/responses)

| Feature | Supported | Notes |
| --- | --- | --- |
| Cost Tracking | ✅ | Works with all supported models |
| Logging | ✅ | Works across all integrations |
| End-user Tracking | ✅ |  |
| Streaming | ✅ |  |
| Fallbacks | ✅ | Works between supported models |
| Loadbalancing | ✅ | Works between supported models |
| Supported operations | Create a response, Get a response, Delete a response |  |
| Supported LiteLLM Versions | 1.63.8+ |  |
| Supported LLM providers | **All LiteLLM supported providers** | `openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai` etc. |

## Usage [​](https://docs.litellm.ai/docs/response_api\#usage "Direct link to Usage")

### LiteLLM Python SDK [​](https://docs.litellm.ai/docs/response_api\#litellm-python-sdk "Direct link to LiteLLM Python SDK")

- OpenAI
- Anthropic
- Vertex AI
- AWS Bedrock
- Google AI Studio

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming "Direct link to Non-streaming")

OpenAI Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Non-streaming response
response = litellm.responses(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming "Direct link to Streaming")

OpenAI Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Streaming response
response = litellm.responses(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

#### GET a Response [​](https://docs.litellm.ai/docs/response_api\#get-a-response "Direct link to GET a Response")

Get Response by ID

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# First, create a response
response = litellm.responses(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

# Get the response ID
response_id = response.id

# Retrieve the response by ID
retrieved_response = litellm.get_responses(
    response_id=response_id
)

print(retrieved_response)

# For async usage
# retrieved_response = await litellm.aget_responses(response_id=response_id)

```

#### DELETE a Response [​](https://docs.litellm.ai/docs/response_api\#delete-a-response "Direct link to DELETE a Response")

Delete Response by ID

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# First, create a response
response = litellm.responses(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

# Get the response ID
response_id = response.id

# Delete the response by ID
delete_response = litellm.delete_responses(
    response_id=response_id
)

print(delete_response)

# For async usage
# delete_response = await litellm.adelete_responses(response_id=response_id)

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-1 "Direct link to Non-streaming")

Anthropic Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Non-streaming response
response = litellm.responses(
    model="anthropic/claude-3-5-sonnet-20240620",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-1 "Direct link to Streaming")

Anthropic Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Streaming response
response = litellm.responses(
    model="anthropic/claude-3-5-sonnet-20240620",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-2 "Direct link to Non-streaming")

Vertex AI Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set credentials - Vertex AI uses application default credentials
# Run 'gcloud auth application-default login' to authenticate
os.environ["VERTEXAI_PROJECT"] = "your-gcp-project-id"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

# Non-streaming response
response = litellm.responses(
    model="vertex_ai/gemini-1.5-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-2 "Direct link to Streaming")

Vertex AI Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set credentials - Vertex AI uses application default credentials
# Run 'gcloud auth application-default login' to authenticate
os.environ["VERTEXAI_PROJECT"] = "your-gcp-project-id"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

# Streaming response
response = litellm.responses(
    model="vertex_ai/gemini-1.5-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-3 "Direct link to Non-streaming")

AWS Bedrock Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-access-key"
os.environ["AWS_REGION_NAME"] = "us-west-2"  # or your AWS region

# Non-streaming response
response = litellm.responses(
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-3 "Direct link to Streaming")

AWS Bedrock Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-access-key"
os.environ["AWS_REGION_NAME"] = "us-west-2"  # or your AWS region

# Streaming response
response = litellm.responses(
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-4 "Direct link to Non-streaming")

Google AI Studio Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key for Google AI Studio
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

# Non-streaming response
response = litellm.responses(
    model="gemini/gemini-1.5-flash",
    input="Tell me a three sentence bedtime story about a unicorn.",
    max_output_tokens=100
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-4 "Direct link to Streaming")

Google AI Studio Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import os

# Set API key for Google AI Studio
os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

# Streaming response
response = litellm.responses(
    model="gemini/gemini-1.5-flash",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

### LiteLLM Proxy with OpenAI SDK [​](https://docs.litellm.ai/docs/response_api\#litellm-proxy-with-openai-sdk "Direct link to LiteLLM Proxy with OpenAI SDK")

First, set up and start your LiteLLM proxy server.

Start LiteLLM Proxy Server

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000

```

- OpenAI
- Anthropic
- Vertex AI
- AWS Bedrock
- Google AI Studio

First, add this to your litellm proxy config.yaml:

OpenAI Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: openai/o1-pro
    litellm_params:
      model: openai/o1-pro
      api_key: os.environ/OPENAI_API_KEY

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-5 "Direct link to Non-streaming")

OpenAI Proxy Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Non-streaming response
response = client.responses.create(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-5 "Direct link to Streaming")

OpenAI Proxy Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

#### GET a Response [​](https://docs.litellm.ai/docs/response_api\#get-a-response-1 "Direct link to GET a Response")

Get Response by ID with OpenAI SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# First, create a response
response = client.responses.create(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn."
)

# Get the response ID
response_id = response.id

# Retrieve the response by ID
retrieved_response = client.responses.retrieve(response_id)

print(retrieved_response)

```

#### DELETE a Response [​](https://docs.litellm.ai/docs/response_api\#delete-a-response-1 "Direct link to DELETE a Response")

Delete Response by ID with OpenAI SDK

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# First, create a response
response = client.responses.create(
    model="openai/o1-pro",
    input="Tell me a three sentence bedtime story about a unicorn."
)

# Get the response ID
response_id = response.id

# Delete the response by ID
delete_response = client.responses.delete(response_id)

print(delete_response)

```

First, add this to your litellm proxy config.yaml:

Anthropic Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: anthropic/claude-3-5-sonnet-20240620
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20240620
      api_key: os.environ/ANTHROPIC_API_KEY

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-6 "Direct link to Non-streaming")

Anthropic Proxy Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Non-streaming response
response = client.responses.create(
    model="anthropic/claude-3-5-sonnet-20240620",
    input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-6 "Direct link to Streaming")

Anthropic Proxy Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="anthropic/claude-3-5-sonnet-20240620",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

First, add this to your litellm proxy config.yaml:

Vertex AI Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: vertex_ai/gemini-1.5-pro
    litellm_params:
      model: vertex_ai/gemini-1.5-pro
      vertex_project: your-gcp-project-id
      vertex_location: us-central1

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-7 "Direct link to Non-streaming")

Vertex AI Proxy Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Non-streaming response
response = client.responses.create(
    model="vertex_ai/gemini-1.5-pro",
    input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-7 "Direct link to Streaming")

Vertex AI Proxy Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="vertex_ai/gemini-1.5-pro",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

First, add this to your litellm proxy config.yaml:

AWS Bedrock Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
    litellm_params:
      model: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      aws_region_name: us-west-2

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-8 "Direct link to Non-streaming")

AWS Bedrock Proxy Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Non-streaming response
response = client.responses.create(
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-8 "Direct link to Streaming")

AWS Bedrock Proxy Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

First, add this to your litellm proxy config.yaml:

Google AI Studio Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: gemini/gemini-1.5-flash
    litellm_params:
      model: gemini/gemini-1.5-flash
      api_key: os.environ/GEMINI_API_KEY

```

#### Non-streaming [​](https://docs.litellm.ai/docs/response_api\#non-streaming-9 "Direct link to Non-streaming")

Google AI Studio Proxy Non-streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Non-streaming response
response = client.responses.create(
    model="gemini/gemini-1.5-flash",
    input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

```

#### Streaming [​](https://docs.litellm.ai/docs/response_api\#streaming-9 "Direct link to Streaming")

Google AI Studio Proxy Streaming Response

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="gemini/gemini-1.5-flash",
    input="Tell me a three sentence bedtime story about a unicorn.",
    stream=True
)

for event in response:
    print(event)

```

## Supported Responses API Parameters [​](https://docs.litellm.ai/docs/response_api\#supported-responses-api-parameters "Direct link to Supported Responses API Parameters")

| Provider | Supported Parameters |
| --- | --- |
| `openai` | [All Responses API parameters are supported](https://github.com/BerriAI/litellm/blob/7c3df984da8e4dff9201e4c5353fdc7a2b441831/litellm/llms/openai/responses/transformation.py#L23) |
| `azure` | [All Responses API parameters are supported](https://github.com/BerriAI/litellm/blob/7c3df984da8e4dff9201e4c5353fdc7a2b441831/litellm/llms/openai/responses/transformation.py#L23) |
| `anthropic` | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |
| `bedrock` | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |
| `gemini` | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |
| `vertex_ai` | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |
| `azure_ai` | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |
| All other llm api providers | [See supported parameters here](https://github.com/BerriAI/litellm/blob/f39d9178868662746f159d5ef642c7f34f9bfe5f/litellm/responses/litellm_completion_transformation/transformation.py#L57) |

## Load Balancing with Session Continuity. [​](https://docs.litellm.ai/docs/response_api\#load-balancing-with-session-continuity "Direct link to Load Balancing with Session Continuity.")

When using the Responses API with multiple deployments of the same model (e.g., multiple Azure OpenAI endpoints), LiteLLM provides session continuity. This ensures that follow-up requests using a `previous_response_id` are routed to the same deployment that generated the original response.

#### Example Usage [​](https://docs.litellm.ai/docs/response_api\#example-usage "Direct link to Example Usage")

- Python SDK
- Proxy Server

Python SDK with Session Continuity

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Set up router with multiple deployments of the same model
router = litellm.Router(
    model_list=[\
        {\
            "model_name": "azure-gpt4-turbo",\
            "litellm_params": {\
                "model": "azure/gpt-4-turbo",\
                "api_key": "your-api-key-1",\
                "api_version": "2024-06-01",\
                "api_base": "https://endpoint1.openai.azure.com",\
            },\
        },\
        {\
            "model_name": "azure-gpt4-turbo",\
            "litellm_params": {\
                "model": "azure/gpt-4-turbo",\
                "api_key": "your-api-key-2",\
                "api_version": "2024-06-01",\
                "api_base": "https://endpoint2.openai.azure.com",\
            },\
        },\
    ],
    optional_pre_call_checks=["responses_api_deployment_check"],
)

# Initial request
response = await router.aresponses(
    model="azure-gpt4-turbo",
    input="Hello, who are you?",
    truncation="auto",
)

# Store the response ID
response_id = response.id

# Follow-up request - will be automatically routed to the same deployment
follow_up = await router.aresponses(
    model="azure-gpt4-turbo",
    input="Tell me more about yourself",
    truncation="auto",
    previous_response_id=response_id  # This ensures routing to the same deployment
)

```

#### 1\. Setup session continuity on proxy config.yaml [​](https://docs.litellm.ai/docs/response_api\#1-setup-session-continuity-on-proxy-configyaml "Direct link to 1. Setup session continuity on proxy config.yaml")

To enable session continuity for Responses API in your LiteLLM proxy, set `optional_pre_call_checks: ["responses_api_deployment_check"]` in your proxy config.yaml.

config.yaml with Session Continuity

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: azure-gpt4-turbo
    litellm_params:
      model: azure/gpt-4-turbo
      api_key: your-api-key-1
      api_version: 2024-06-01
      api_base: https://endpoint1.openai.azure.com
  - model_name: azure-gpt4-turbo
    litellm_params:
      model: azure/gpt-4-turbo
      api_key: your-api-key-2
      api_version: 2024-06-01
      api_base: https://endpoint2.openai.azure.com

router_settings:
  optional_pre_call_checks: ["responses_api_deployment_check"]

```

#### 2\. Use the OpenAI Python SDK to make requests to LiteLLM Proxy [​](https://docs.litellm.ai/docs/response_api\#2-use-the-openai-python-sdk-to-make-requests-to-litellm-proxy "Direct link to 2. Use the OpenAI Python SDK to make requests to LiteLLM Proxy")

OpenAI Client with Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="your-api-key"
)

# Initial request
response = client.responses.create(
    model="azure-gpt4-turbo",
    input="Hello, who are you?"
)

response_id = response.id

# Follow-up request - will be automatically routed to the same deployment
follow_up = client.responses.create(
    model="azure-gpt4-turbo",
    input="Tell me more about yourself",
    previous_response_id=response_id  # This ensures routing to the same deployment
)

```

## Session Management - Non-OpenAI Models [​](https://docs.litellm.ai/docs/response_api\#session-management---non-openai-models "Direct link to Session Management - Non-OpenAI Models")

LiteLLM Proxy supports session management for non-OpenAI models. This allows you to store and fetch conversation history (state) in LiteLLM Proxy.

#### Usage [​](https://docs.litellm.ai/docs/response_api\#usage-1 "Direct link to Usage")

1. Enable storing request / response content in the database

Set `store_prompts_in_spend_logs: true` in your proxy config.yaml. When this is enabled, LiteLLM will store the request and response content in the database.

```codeBlockLines_e6Vv
general_settings:
  store_prompts_in_spend_logs: true

```

2. Make request 1 with no `previous_response_id` (new session)

Start a new conversation by making a request without specifying a previous response ID.

- Curl
- OpenAI Python SDK

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "anthropic/claude-3-5-sonnet-latest",
    "input": "who is Michael Jordan"
  }'

```

```codeBlockLines_e6Vv
from openai import OpenAI

# Initialize the client with your LiteLLM proxy URL
client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

# Make initial request to start a new conversation
response = client.responses.create(
    model="anthropic/claude-3-5-sonnet-latest",
    input="who is Michael Jordan"
)

print(response.id)  # Store this ID for future requests in same session
print(response.output[0].content[0].text)

```

Response:

```codeBlockLines_e6Vv
{
  "id":"resp_123abc",
  "model":"claude-3-5-sonnet-20241022",
  "output":[{\
    "type":"message",\
    "content":[{\
      "type":"output_text",\
      "text":"Michael Jordan is widely considered one of the greatest basketball players of all time. He played for the Chicago Bulls (1984-1993, 1995-1998) and Washington Wizards (2001-2003), winning 6 NBA Championships with the Bulls."\
    }]\
  }]
}

```

3. Make request 2 with `previous_response_id` (same session)

Continue the conversation by referencing the previous response ID to maintain conversation context.

- Curl
- OpenAI Python SDK

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "anthropic/claude-3-5-sonnet-latest",
    "input": "can you tell me more about him",
    "previous_response_id": "resp_123abc"
  }'

```

```codeBlockLines_e6Vv
from openai import OpenAI

# Initialize the client with your LiteLLM proxy URL
client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

# Make follow-up request in the same conversation session
follow_up_response = client.responses.create(
    model="anthropic/claude-3-5-sonnet-latest",
    input="can you tell me more about him",
    previous_response_id="resp_123abc"  # ID from the previous response
)

print(follow_up_response.output[0].content[0].text)

```

Response:

```codeBlockLines_e6Vv
{
  "id":"resp_456def",
  "model":"claude-3-5-sonnet-20241022",
  "output":[{\
    "type":"message",\
    "content":[{\
      "type":"output_text",\
      "text":"Michael Jordan was born February 17, 1963. He attended University of North Carolina before being drafted 3rd overall by the Bulls in 1984. Beyond basketball, he built the Air Jordan brand with Nike and later became owner of the Charlotte Hornets."\
    }]\
  }]
}

```

4. Make request 3 with no `previous_response_id` (new session)

Start a brand new conversation without referencing previous context to demonstrate how context is not maintained between sessions.

- Curl
- OpenAI Python SDK

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "anthropic/claude-3-5-sonnet-latest",
    "input": "can you tell me more about him"
  }'

```

```codeBlockLines_e6Vv
from openai import OpenAI

# Initialize the client with your LiteLLM proxy URL
client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

# Make a new request without previous context
new_session_response = client.responses.create(
    model="anthropic/claude-3-5-sonnet-latest",
    input="can you tell me more about him"
    # No previous_response_id means this starts a new conversation
)

print(new_session_response.output[0].content[0].text)

```

Response:

```codeBlockLines_e6Vv
{
  "id":"resp_789ghi",
  "model":"claude-3-5-sonnet-20241022",
  "output":[{\
    "type":"message",\
    "content":[{\
      "type":"output_text",\
      "text":"I don't see who you're referring to in our conversation. Could you let me know which person you'd like to learn more about?"\
    }]\
  }]
}

```

- [Usage](https://docs.litellm.ai/docs/response_api#usage)
  - [LiteLLM Python SDK](https://docs.litellm.ai/docs/response_api#litellm-python-sdk)
  - [LiteLLM Proxy with OpenAI SDK](https://docs.litellm.ai/docs/response_api#litellm-proxy-with-openai-sdk)
- [Supported Responses API Parameters](https://docs.litellm.ai/docs/response_api#supported-responses-api-parameters)
- [Load Balancing with Session Continuity.](https://docs.litellm.ai/docs/response_api#load-balancing-with-session-continuity)
- [Session Management - Non-OpenAI Models](https://docs.litellm.ai/docs/response_api#session-management---non-openai-models)