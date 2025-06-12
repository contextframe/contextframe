---
url: "https://docs.litellm.ai/docs/rerank"
title: "/rerank | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/rerank#__docusaurus_skipToContent_fallback)

On this page

# /rerank

tip

LiteLLM Follows the [cohere api request / response for the rerank api](https://cohere.com/rerank)

## **LiteLLM Python SDK Usage** [​](https://docs.litellm.ai/docs/rerank\#litellm-python-sdk-usage "Direct link to litellm-python-sdk-usage")

### Quick Start [​](https://docs.litellm.ai/docs/rerank\#quick-start "Direct link to Quick Start")

```codeBlockLines_e6Vv
from litellm import rerank
import os

os.environ["COHERE_API_KEY"] = "sk-.."

query = "What is the capital of the United States?"
documents = [\
    "Carson City is the capital city of the American state of Nevada.",\
    "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",\
    "Washington, D.C. is the capital of the United States.",\
    "Capital punishment has existed in the United States since before it was a country.",\
]

response = rerank(
    model="cohere/rerank-english-v3.0",
    query=query,
    documents=documents,
    top_n=3,
)
print(response)

```

### Async Usage [​](https://docs.litellm.ai/docs/rerank\#async-usage "Direct link to Async Usage")

```codeBlockLines_e6Vv
from litellm import arerank
import os, asyncio

os.environ["COHERE_API_KEY"] = "sk-.."

async def test_async_rerank():
    query = "What is the capital of the United States?"
    documents = [\
        "Carson City is the capital city of the American state of Nevada.",\
        "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",\
        "Washington, D.C. is the capital of the United States.",\
        "Capital punishment has existed in the United States since before it was a country.",\
    ]

    response = await arerank(
        model="cohere/rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=3,
    )
    print(response)

asyncio.run(test_async_rerank())

```

## **LiteLLM Proxy Usage** [​](https://docs.litellm.ai/docs/rerank\#litellm-proxy-usage "Direct link to litellm-proxy-usage")

LiteLLM provides an cohere api compatible `/rerank` endpoint for Rerank calls.

**Setup**

Add this to your litellm proxy config.yaml

```codeBlockLines_e6Vv
model_list:
  - model_name: Salesforce/Llama-Rank-V1
    litellm_params:
      model: together_ai/Salesforce/Llama-Rank-V1
      api_key: os.environ/TOGETHERAI_API_KEY
  - model_name: rerank-english-v3.0
    litellm_params:
      model: cohere/rerank-english-v3.0
      api_key: os.environ/COHERE_API_KEY

```

Start litellm

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000

```

Test request

```codeBlockLines_e6Vv
curl http://0.0.0.0:4000/rerank \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rerank-english-v3.0",
    "query": "What is the capital of the United States?",
    "documents": [\
        "Carson City is the capital city of the American state of Nevada.",\
        "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",\
        "Washington, D.C. is the capital of the United States.",\
        "Capital punishment has existed in the United States since before it was a country."\
    ],
    "top_n": 3
  }'

```

## **Supported Providers** [​](https://docs.litellm.ai/docs/rerank\#supported-providers "Direct link to supported-providers")

| Provider | Link to Usage |
| --- | --- |
| Cohere (v1 + v2 clients) | [Usage](https://docs.litellm.ai/docs/rerank#quick-start) |
| Together AI | [Usage](https://docs.litellm.ai/docs/providers/togetherai) |
| Azure AI | [Usage](https://docs.litellm.ai/docs/providers/azure_ai) |
| Jina AI | [Usage](https://docs.litellm.ai/docs/providers/jina_ai) |
| AWS Bedrock | [Usage](https://docs.litellm.ai/docs/providers/bedrock#rerank-api) |
| HuggingFace | [Usage](https://docs.litellm.ai/docs/providers/huggingface_rerank) |
| Infinity | [Usage](https://docs.litellm.ai/docs/providers/infinity) |

- [**LiteLLM Python SDK Usage**](https://docs.litellm.ai/docs/rerank#litellm-python-sdk-usage)
  - [Quick Start](https://docs.litellm.ai/docs/rerank#quick-start)
  - [Async Usage](https://docs.litellm.ai/docs/rerank#async-usage)
- [**LiteLLM Proxy Usage**](https://docs.litellm.ai/docs/rerank#litellm-proxy-usage)
- [**Supported Providers**](https://docs.litellm.ai/docs/rerank#supported-providers)