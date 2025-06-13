---
url: "https://docs.litellm.ai/docs/image_variations"
title: "[BETA] Image Variations | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/image_variations#__docusaurus_skipToContent_fallback)

On this page

# \[BETA\] Image Variations

OpenAI's `/image/variations` endpoint is now supported.

## Quick Start [​](https://docs.litellm.ai/docs/image_variations\#quick-start "Direct link to Quick Start")

```codeBlockLines_e6Vv
from litellm import image_variation
import os

# set env vars
os.environ["OPENAI_API_KEY"] = ""
os.environ["TOPAZ_API_KEY"] = ""

# openai call
response = image_variation(
    model="dall-e-2", image=image_url
)

# topaz call
response = image_variation(
    model="topaz/Standard V2", image=image_url
)

print(response)

```

## Supported Providers [​](https://docs.litellm.ai/docs/image_variations\#supported-providers "Direct link to Supported Providers")

- OpenAI
- Topaz

- [Quick Start](https://docs.litellm.ai/docs/image_variations#quick-start)
- [Supported Providers](https://docs.litellm.ai/docs/image_variations#supported-providers)