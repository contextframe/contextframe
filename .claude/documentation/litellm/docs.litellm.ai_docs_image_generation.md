---
url: "https://docs.litellm.ai/docs/image_generation"
title: "Image Generations | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/image_generation#__docusaurus_skipToContent_fallback)

On this page

# Image Generations

## Quick Start [​](https://docs.litellm.ai/docs/image_generation\#quick-start "Direct link to Quick Start")

### LiteLLM Python SDK [​](https://docs.litellm.ai/docs/image_generation\#litellm-python-sdk "Direct link to LiteLLM Python SDK")

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from litellm import image_generation
import os

# set api keys
os.environ["OPENAI_API_KEY"] = ""

response = image_generation(prompt="A cute baby sea otter", model="dall-e-3")

print(f"response: {response}")

```

### LiteLLM Proxy [​](https://docs.litellm.ai/docs/image_generation\#litellm-proxy "Direct link to LiteLLM Proxy")

### Setup config.yaml [​](https://docs.litellm.ai/docs/image_generation\#setup-configyaml "Direct link to Setup config.yaml")

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: gpt-image-1 ### RECEIVED MODEL NAME ###
    litellm_params: # all params accepted by litellm.image_generation()
      model: azure/gpt-image-1 ### MODEL NAME sent to `litellm.image_generation()` ###
      api_base: https://my-endpoint-europe-berri-992.openai.azure.com/
      api_key: "os.environ/AZURE_API_KEY_EU" # does os.getenv("AZURE_API_KEY_EU")

```

### Start proxy [​](https://docs.litellm.ai/docs/image_generation\#start-proxy "Direct link to Start proxy")

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000

```

### Test [​](https://docs.litellm.ai/docs/image_generation\#test "Direct link to Test")

- Curl
- OpenAI

```codeBlockLines_e6Vv
curl -X POST 'http://0.0.0.0:4000/v1/images/generations' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-1234' \
-D '{
    "model": "gpt-image-1",
    "prompt": "A cute baby sea otter",
    "n": 1,
    "size": "1024x1024"
}'

```

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI
client = openai.OpenAI(
    api_key="sk-1234",
    base_url="http://0.0.0.0:4000"
)

image = client.images.generate(
    prompt="A cute baby sea otter",
    model="dall-e-3",
)

print(image)

```

## Input Params for `litellm.image_generation()` [​](https://docs.litellm.ai/docs/image_generation\#input-params-for-litellmimage_generation "Direct link to input-params-for-litellmimage_generation")

info

Any non-openai params, will be treated as provider-specific params, and sent in the request body as kwargs to the provider.

[**See Reserved Params**](https://github.com/BerriAI/litellm/blob/2f5f85cb52f36448d1f8bbfbd3b8af8167d0c4c8/litellm/main.py#L4082)

### Required Fields [​](https://docs.litellm.ai/docs/image_generation\#required-fields "Direct link to Required Fields")

- `prompt`: _string_ \- A text description of the desired image(s).

### Optional LiteLLM Fields [​](https://docs.litellm.ai/docs/image_generation\#optional-litellm-fields "Direct link to Optional LiteLLM Fields")

```codeBlockLines_e6Vv
model: Optional[str] = None,
n: Optional[int] = None,
quality: Optional[str] = None,
response_format: Optional[str] = None,
size: Optional[str] = None,
style: Optional[str] = None,
user: Optional[str] = None,
timeout=600,  # default to 10 minutes
api_key: Optional[str] = None,
api_base: Optional[str] = None,
api_version: Optional[str] = None,
litellm_logging_obj=None,
custom_llm_provider=None,

```

- `model`: _string (optional)_ The model to use for image generation. Defaults to openai/gpt-image-1

- `n`: _int (optional)_ The number of images to generate. Must be between 1 and 10. For dall-e-3, only n=1 is supported.

- `quality`: _string (optional)_ The quality of the image that will be generated.

  - `auto` (default value) will automatically select the best quality for the given model.
  - `high`, `medium` and `low` are supported for `gpt-image-1`.
  - `hd` and `standard` are supported for `dall-e-3`.
  - `standard` is the only option for `dall-e-2`.
- `response_format`: _string (optional)_ The format in which the generated images are returned. Must be one of url or b64\_json.

- `size`: _string (optional)_ The size of the generated images. Must be one of `1024x1024`, `1536x1024` (landscape), `1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.

- `timeout`: _integer_ \- The maximum time, in seconds, to wait for the API to respond. Defaults to 600 seconds (10 minutes).

- `user`: _string (optional)_ A unique identifier representing your end-user,

- `api_base`: _string (optional)_ \- The api endpoint you want to call the model with

- `api_version`: _string (optional)_ \- (Azure-specific) the api version for the call; required for dall-e-3 on Azure

- `api_key`: _string (optional)_ \- The API key to authenticate and authorize requests. If not provided, the default API key is used.

- `api_type`: _string (optional)_ \- The type of API to use.


### Output from `litellm.image_generation()` [​](https://docs.litellm.ai/docs/image_generation\#output-from-litellmimage_generation "Direct link to output-from-litellmimage_generation")

```codeBlockLines_e6Vv

{
    "created": 1703658209,
    "data": [{\
        'b64_json': None,\
        'revised_prompt': 'Adorable baby sea otter with a coat of thick brown fur, playfully swimming in blue ocean waters. Its curious, bright eyes gleam as it is surfaced above water, tiny paws held close to its chest, as it playfully spins in the gentle waves under the soft rays of a setting sun.',\
        'url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-ikDc4ex8NB5ZzfTf8m5WYVB7/user-JpwZsbIXubBZvan3Y3GchiiB/img-dpa3g5LmkTrotY6M93dMYrdE.png?st=2023-12-27T05%3A23%3A29Z&se=2023-12-27T07%3A23%3A29Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-26T13%3A22%3A56Z&ske=2023-12-27T13%3A22%3A56Z&sks=b&skv=2021-08-06&sig=hUuQjYLS%2BvtsDdffEAp2gwewjC8b3ilggvkd9hgY6Uw%3D'\
    }],
    "usage": {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
}

```

## OpenAI Image Generation Models [​](https://docs.litellm.ai/docs/image_generation\#openai-image-generation-models "Direct link to OpenAI Image Generation Models")

### Usage [​](https://docs.litellm.ai/docs/image_generation\#usage "Direct link to Usage")

```codeBlockLines_e6Vv
from litellm import image_generation
import os
os.environ['OPENAI_API_KEY'] = ""
response = image_generation(model='gpt-image-1', prompt="cute baby otter")

```

| Model Name | Function Call | Required OS Variables |
| --- | --- | --- |
| gpt-image-1 | `image_generation(model='gpt-image-1', prompt="cute baby otter")` | `os.environ['OPENAI_API_KEY']` |
| dall-e-3 | `image_generation(model='dall-e-3', prompt="cute baby otter")` | `os.environ['OPENAI_API_KEY']` |
| dall-e-2 | `image_generation(model='dall-e-2', prompt="cute baby otter")` | `os.environ['OPENAI_API_KEY']` |

## Azure OpenAI Image Generation Models [​](https://docs.litellm.ai/docs/image_generation\#azure-openai-image-generation-models "Direct link to Azure OpenAI Image Generation Models")

### API keys [​](https://docs.litellm.ai/docs/image_generation\#api-keys "Direct link to API keys")

This can be set as env variables or passed as **params to litellm.image\_generation()**

```codeBlockLines_e6Vv
import os
os.environ['AZURE_API_KEY'] =
os.environ['AZURE_API_BASE'] =
os.environ['AZURE_API_VERSION'] =

```

### Usage [​](https://docs.litellm.ai/docs/image_generation\#usage-1 "Direct link to Usage")

```codeBlockLines_e6Vv
from litellm import embedding
response = embedding(
    model="azure/<your deployment name>",
    prompt="cute baby otter",
    api_key=api_key,
    api_base=api_base,
    api_version=api_version,
)
print(response)

```

| Model Name | Function Call |
| --- | --- |
| gpt-image-1 | `image_generation(model="azure/<your deployment name>", prompt="cute baby otter")` |
| dall-e-3 | `image_generation(model="azure/<your deployment name>", prompt="cute baby otter")` |
| dall-e-2 | `image_generation(model="azure/<your deployment name>", prompt="cute baby otter")` |

## OpenAI Compatible Image Generation Models [​](https://docs.litellm.ai/docs/image_generation\#openai-compatible-image-generation-models "Direct link to OpenAI Compatible Image Generation Models")

Use this for calling `/image_generation` endpoints on OpenAI Compatible Servers, example [https://github.com/xorbitsai/inference](https://github.com/xorbitsai/inference)

**Note add `openai/` prefix to model so litellm knows to route to OpenAI**

### Usage [​](https://docs.litellm.ai/docs/image_generation\#usage-2 "Direct link to Usage")

```codeBlockLines_e6Vv
from litellm import image_generation
response = image_generation(
  model = "openai/<your-llm-name>",     # add `openai/` prefix to model so litellm knows to route to OpenAI
  api_base="http://0.0.0.0:8000/"       # set API Base of your Custom OpenAI Endpoint
  prompt="cute baby otter"
)

```

## Bedrock - Stable Diffusion [​](https://docs.litellm.ai/docs/image_generation\#bedrock---stable-diffusion "Direct link to Bedrock - Stable Diffusion")

Use this for stable diffusion on bedrock

### Usage [​](https://docs.litellm.ai/docs/image_generation\#usage-3 "Direct link to Usage")

```codeBlockLines_e6Vv
import os
from litellm import image_generation

os.environ["AWS_ACCESS_KEY_ID"] = ""
os.environ["AWS_SECRET_ACCESS_KEY"] = ""
os.environ["AWS_REGION_NAME"] = ""

response = image_generation(
            prompt="A cute baby sea otter",
            model="bedrock/stability.stable-diffusion-xl-v0",
        )
print(f"response: {response}")

```

## VertexAI - Image Generation Models [​](https://docs.litellm.ai/docs/image_generation\#vertexai---image-generation-models "Direct link to VertexAI - Image Generation Models")

### Usage [​](https://docs.litellm.ai/docs/image_generation\#usage-4 "Direct link to Usage")

Use this for image generation models on VertexAI

```codeBlockLines_e6Vv
response = litellm.image_generation(
    prompt="An olympic size swimming pool",
    model="vertex_ai/imagegeneration@006",
    vertex_ai_project="adroit-crow-413218",
    vertex_ai_location="us-central1",
)
print(f"response: {response}")

```

- [Quick Start](https://docs.litellm.ai/docs/image_generation#quick-start)
  - [LiteLLM Python SDK](https://docs.litellm.ai/docs/image_generation#litellm-python-sdk)
  - [LiteLLM Proxy](https://docs.litellm.ai/docs/image_generation#litellm-proxy)
  - [Setup config.yaml](https://docs.litellm.ai/docs/image_generation#setup-configyaml)
  - [Start proxy](https://docs.litellm.ai/docs/image_generation#start-proxy)
  - [Test](https://docs.litellm.ai/docs/image_generation#test)
- [Input Params for `litellm.image_generation()`](https://docs.litellm.ai/docs/image_generation#input-params-for-litellmimage_generation)
  - [Required Fields](https://docs.litellm.ai/docs/image_generation#required-fields)
  - [Optional LiteLLM Fields](https://docs.litellm.ai/docs/image_generation#optional-litellm-fields)
  - [Output from `litellm.image_generation()`](https://docs.litellm.ai/docs/image_generation#output-from-litellmimage_generation)
- [OpenAI Image Generation Models](https://docs.litellm.ai/docs/image_generation#openai-image-generation-models)
  - [Usage](https://docs.litellm.ai/docs/image_generation#usage)
- [Azure OpenAI Image Generation Models](https://docs.litellm.ai/docs/image_generation#azure-openai-image-generation-models)
  - [API keys](https://docs.litellm.ai/docs/image_generation#api-keys)
  - [Usage](https://docs.litellm.ai/docs/image_generation#usage-1)
- [OpenAI Compatible Image Generation Models](https://docs.litellm.ai/docs/image_generation#openai-compatible-image-generation-models)
  - [Usage](https://docs.litellm.ai/docs/image_generation#usage-2)
- [Bedrock - Stable Diffusion](https://docs.litellm.ai/docs/image_generation#bedrock---stable-diffusion)
  - [Usage](https://docs.litellm.ai/docs/image_generation#usage-3)
- [VertexAI - Image Generation Models](https://docs.litellm.ai/docs/image_generation#vertexai---image-generation-models)
  - [Usage](https://docs.litellm.ai/docs/image_generation#usage-4)