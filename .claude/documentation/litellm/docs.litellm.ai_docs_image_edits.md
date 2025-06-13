---
url: "https://docs.litellm.ai/docs/image_edits"
title: "/images/edits | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/image_edits#__docusaurus_skipToContent_fallback)

On this page

# /images/edits

LiteLLM provides image editing functionality that maps to OpenAI's `/images/edits` API endpoint.

| Feature | Supported | Notes |
| --- | --- | --- |
| Cost Tracking | ✅ | Works with all supported models |
| Logging | ✅ | Works across all integrations |
| End-user Tracking | ✅ |  |
| Fallbacks | ✅ | Works between supported models |
| Loadbalancing | ✅ | Works between supported models |
| Supported operations | Create image edits |  |
| Supported LiteLLM SDK Versions | 1.63.8+ |  |
| Supported LiteLLM Proxy Versions | 1.71.1+ |  |
| Supported LLM providers | **OpenAI** | Currently only `openai` is supported |

## Usage [​](https://docs.litellm.ai/docs/image_edits\#usage "Direct link to Usage")

### LiteLLM Python SDK [​](https://docs.litellm.ai/docs/image_edits\#litellm-python-sdk "Direct link to LiteLLM Python SDK")

- OpenAI

#### Basic Image Edit [​](https://docs.litellm.ai/docs/image_edits\#basic-image-edit "Direct link to Basic Image Edit")

OpenAI Image Edit

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Edit an image with a prompt
response = litellm.image_edit(
    model="gpt-image-1",
    image=open("original_image.png", "rb"),
    prompt="Add a red hat to the person in the image",
    n=1,
    size="1024x1024"
)

print(response)

```

#### Image Edit with Mask [​](https://docs.litellm.ai/docs/image_edits\#image-edit-with-mask "Direct link to Image Edit with Mask")

OpenAI Image Edit with Mask

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Edit an image with a mask to specify the area to edit
response = litellm.image_edit(
    model="gpt-image-1",
    image=open("original_image.png", "rb"),
    mask=open("mask_image.png", "rb"),  # Transparent areas will be edited
    prompt="Replace the background with a beach scene",
    n=2,
    size="512x512",
    response_format="url"
)

print(response)

```

#### Async Image Edit [​](https://docs.litellm.ai/docs/image_edits\#async-image-edit "Direct link to Async Image Edit")

Async OpenAI Image Edit

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm
import asyncio

async def edit_image():
    response = await litellm.aimage_edit(
        model="gpt-image-1",
        image=open("original_image.png", "rb"),
        prompt="Make the image look like a painting",
        n=1,
        size="1024x1024",
        response_format="b64_json"
    )
    return response

# Run the async function
response = asyncio.run(edit_image())
print(response)

```

#### Image Edit with Custom Parameters [​](https://docs.litellm.ai/docs/image_edits\#image-edit-with-custom-parameters "Direct link to Image Edit with Custom Parameters")

OpenAI Image Edit with Custom Parameters

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
import litellm

# Edit image with additional parameters
response = litellm.image_edit(
    model="gpt-image-1",
    image=open("portrait.png", "rb"),
    prompt="Add sunglasses and a smile",
    n=3,
    size="1024x1024",
    response_format="url",
    user="user-123",
    timeout=60,
    extra_headers={"Custom-Header": "value"}
)

print(f"Generated {len(response.data)} image variations")
for i, image_data in enumerate(response.data):
    print(f"Image {i+1}: {image_data.url}")

```

### LiteLLM Proxy with OpenAI SDK [​](https://docs.litellm.ai/docs/image_edits\#litellm-proxy-with-openai-sdk "Direct link to LiteLLM Proxy with OpenAI SDK")

- OpenAI

First, add this to your litellm proxy config.yaml:

OpenAI Proxy Configuration

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
model_list:
  - model_name: gpt-image-1
    litellm_params:
      model: gpt-image-1
      api_key: os.environ/OPENAI_API_KEY

```

Start the LiteLLM proxy server:

Start LiteLLM Proxy Server

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000

```

#### Basic Image Edit via Proxy [​](https://docs.litellm.ai/docs/image_edits\#basic-image-edit-via-proxy "Direct link to Basic Image Edit via Proxy")

OpenAI Proxy Image Edit

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:4000",  # Your proxy URL
    api_key="your-api-key"             # Your proxy API key
)

# Edit an image
response = client.images.edit(
    model="gpt-image-1",
    image=open("original_image.png", "rb"),
    prompt="Add a red hat to the person in the image",
    n=1,
    size="1024x1024"
)

print(response)

```

#### cURL Example [​](https://docs.litellm.ai/docs/image_edits\#curl-example "Direct link to cURL Example")

cURL Image Edit Request

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
curl -X POST "http://localhost:4000/v1/images/edits" \
  -H "Authorization: Bearer your-api-key" \
  -F "model=gpt-image-1" \
  -F "image=@original_image.png" \
  -F "mask=@mask_image.png" \
  -F "prompt=Add a beautiful sunset in the background" \
  -F "n=1" \
  -F "size=1024x1024" \
  -F "response_format=url"

```

## Supported Image Edit Parameters [​](https://docs.litellm.ai/docs/image_edits\#supported-image-edit-parameters "Direct link to Supported Image Edit Parameters")

| Parameter | Type | Description | Required |
| --- | --- | --- | --- |
| `image` | `FileTypes` | The image to edit. Must be a valid PNG file, less than 4MB, and square. | ✅ |
| `prompt` | `str` | A text description of the desired image edit. | ✅ |
| `model` | `str` | The model to use for image editing | Optional (defaults to `dall-e-2`) |
| `mask` | `str` | An additional image whose fully transparent areas indicate where the original image should be edited. Must be a valid PNG file, less than 4MB, and have the same dimensions as `image`. | Optional |
| `n` | `int` | The number of images to generate. Must be between 1 and 10. | Optional (defaults to 1) |
| `size` | `str` | The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`. | Optional (defaults to `1024x1024`) |
| `response_format` | `str` | The format in which the generated images are returned. Must be one of `url` or `b64_json`. | Optional (defaults to `url`) |
| `user` | `str` | A unique identifier representing your end-user. | Optional |

## Response Format [​](https://docs.litellm.ai/docs/image_edits\#response-format "Direct link to Response Format")

The response follows the OpenAI Images API format:

Image Edit Response Structure

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
{
    "created": 1677649800,
    "data": [\
        {\
            "url": "https://example.com/edited_image_1.png"\
        },\
        {\
            "url": "https://example.com/edited_image_2.png"\
        }\
    ]
}

```

For `b64_json` format:

Base64 Response Structure

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
{
    "created": 1677649800,
    "data": [\
        {\
            "b64_json": "iVBORw0KGgoAAAANSUhEUgAA..."\
        }\
    ]
}

```

- [Usage](https://docs.litellm.ai/docs/image_edits#usage)
  - [LiteLLM Python SDK](https://docs.litellm.ai/docs/image_edits#litellm-python-sdk)
  - [LiteLLM Proxy with OpenAI SDK](https://docs.litellm.ai/docs/image_edits#litellm-proxy-with-openai-sdk)
- [Supported Image Edit Parameters](https://docs.litellm.ai/docs/image_edits#supported-image-edit-parameters)
- [Response Format](https://docs.litellm.ai/docs/image_edits#response-format)