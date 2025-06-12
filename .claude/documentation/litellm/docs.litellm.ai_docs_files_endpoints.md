---
url: "https://docs.litellm.ai/docs/files_endpoints"
title: "Provider Files Endpoints | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/files_endpoints#__docusaurus_skipToContent_fallback)

On this page

# Provider Files Endpoints

Files are used to upload documents that can be used with features like Assistants, Fine-tuning, and Batch API.

Use this to call the provider's `/files` endpoints directly, in the OpenAI format.

## Quick Start [​](https://docs.litellm.ai/docs/files_endpoints\#quick-start "Direct link to Quick Start")

- Upload a File
- List Files
- Retrieve File Information
- Delete File
- Get File Content

- LiteLLM PROXY Server
- SDK

1. Setup config.yaml

```codeBlockLines_e6Vv
# for /files endpoints
files_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: fake-key
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY

```

2. Start LiteLLM PROXY Server

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

## RUNNING on http://0.0.0.0:4000

```

3. Use OpenAI's /files endpoints

Upload a File

```codeBlockLines_e6Vv
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://0.0.0.0:4000/v1"
)

client.files.create(
    file=wav_data,
    purpose="user_data",
    extra_body={"custom_llm_provider": "openai"}
)

```

List Files

```codeBlockLines_e6Vv
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://0.0.0.0:4000/v1"
)

files = client.files.list(extra_body={"custom_llm_provider": "openai"})
print("files=", files)

```

Retrieve File Information

```codeBlockLines_e6Vv
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://0.0.0.0:4000/v1"
)

file = client.files.retrieve(file_id="file-abc123", extra_body={"custom_llm_provider": "openai"})
print("file=", file)

```

Delete File

```codeBlockLines_e6Vv
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://0.0.0.0:4000/v1"
)

response = client.files.delete(file_id="file-abc123", extra_body={"custom_llm_provider": "openai"})
print("delete response=", response)

```

Get File Content

```codeBlockLines_e6Vv
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://0.0.0.0:4000/v1"
)

content = client.files.content(file_id="file-abc123", extra_body={"custom_llm_provider": "openai"})
print("content=", content)

```

**Upload a File**

```codeBlockLines_e6Vv
from litellm
import os

os.environ["OPENAI_API_KEY"] = "sk-.."

file_obj = await litellm.acreate_file(
    file=open("mydata.jsonl", "rb"),
    purpose="fine-tune",
    custom_llm_provider="openai",
)
print("Response from creating file=", file_obj)

```

**List Files**

```codeBlockLines_e6Vv
files = await litellm.alist_files(
    custom_llm_provider="openai",
    limit=10
)
print("files=", files)

```

**Retrieve File Information**

```codeBlockLines_e6Vv
file = await litellm.aretrieve_file(
    file_id="file-abc123",
    custom_llm_provider="openai"
)
print("file=", file)

```

**Delete File**

```codeBlockLines_e6Vv
response = await litellm.adelete_file(
    file_id="file-abc123",
    custom_llm_provider="openai"
)
print("delete response=", response)

```

**Get File Content**

```codeBlockLines_e6Vv
content = await litellm.afile_content(
    file_id="file-abc123",
    custom_llm_provider="openai"
)
print("file content=", content)

```

## **Supported Providers**: [​](https://docs.litellm.ai/docs/files_endpoints\#supported-providers "Direct link to supported-providers")

### [OpenAI](https://docs.litellm.ai/docs/files_endpoints\#quick-start) [​](https://docs.litellm.ai/docs/files_endpoints\#openai "Direct link to openai")

### [Azure OpenAI](https://docs.litellm.ai/docs/providers/azure\#azure-batches-api) [​](https://docs.litellm.ai/docs/files_endpoints\#azure-openai "Direct link to azure-openai")

### [Vertex AI](https://docs.litellm.ai/docs/providers/vertex\#batch-apis) [​](https://docs.litellm.ai/docs/files_endpoints\#vertex-ai "Direct link to vertex-ai")

## [Swagger API Reference](https://litellm-api.up.railway.app/\#/files) [​](https://docs.litellm.ai/docs/files_endpoints\#swagger-api-reference "Direct link to swagger-api-reference")

- [Quick Start](https://docs.litellm.ai/docs/files_endpoints#quick-start)
- [**Supported Providers**:](https://docs.litellm.ai/docs/files_endpoints#supported-providers)
  - [OpenAI](https://docs.litellm.ai/docs/files_endpoints#openai)
  - [Azure OpenAI](https://docs.litellm.ai/docs/files_endpoints#azure-openai)
  - [Vertex AI](https://docs.litellm.ai/docs/files_endpoints#vertex-ai)
- [Swagger API Reference](https://docs.litellm.ai/docs/files_endpoints#swagger-api-reference)