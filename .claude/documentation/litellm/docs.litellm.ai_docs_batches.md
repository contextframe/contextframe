---
url: "https://docs.litellm.ai/docs/batches"
title: "/batches | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/batches#__docusaurus_skipToContent_fallback)

On this page

# /batches

Covers Batches, Files

| Feature | Supported | Notes |
| --- | --- | --- |
| Supported Providers | OpenAI, Azure, Vertex | - |
| ✨ Cost Tracking | ✅ | LiteLLM Enterprise only |
| Logging | ✅ | Works across all logging integrations |

## Quick Start [​](https://docs.litellm.ai/docs/batches\#quick-start "Direct link to Quick Start")

- Create File for Batch Completion

- Create Batch Request

- List Batches

- Retrieve the Specific Batch and File Content


- LiteLLM PROXY Server
- SDK

```codeBlockLines_e6Vv
$ export OPENAI_API_KEY="sk-..."

$ litellm

# RUNNING on http://0.0.0.0:4000

```

**Create File for Batch Completion**

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/files \
    -H "Authorization: Bearer sk-1234" \
    -F purpose="batch" \
    -F file="@mydata.jsonl"

```

**Create Batch Request**

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/batches \
        -H "Authorization: Bearer sk-1234" \
        -H "Content-Type: application/json" \
        -d '{
            "input_file_id": "file-abc123",
            "endpoint": "/v1/chat/completions",
            "completion_window": "24h"
    }'

```

**Retrieve the Specific Batch**

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/batches/batch_abc123 \
    -H "Authorization: Bearer sk-1234" \
    -H "Content-Type: application/json" \

```

**List Batches**

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/batches \
    -H "Authorization: Bearer sk-1234" \
    -H "Content-Type: application/json" \

```

**Create File for Batch Completion**

```codeBlockLines_e6Vv
import litellm
import os
import asyncio

os.environ["OPENAI_API_KEY"] = "sk-.."

file_name = "openai_batch_completions.jsonl"
_current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(_current_dir, file_name)
file_obj = await litellm.acreate_file(
    file=open(file_path, "rb"),
    purpose="batch",
    custom_llm_provider="openai",
)
print("Response from creating file=", file_obj)

```

**Create Batch Request**

```codeBlockLines_e6Vv
import litellm
import os
import asyncio

create_batch_response = await litellm.acreate_batch(
    completion_window="24h",
    endpoint="/v1/chat/completions",
    input_file_id=batch_input_file_id,
    custom_llm_provider="openai",
    metadata={"key1": "value1", "key2": "value2"},
)

print("response from litellm.create_batch=", create_batch_response)

```

**Retrieve the Specific Batch and File Content**

```codeBlockLines_e6Vv
    # Maximum wait time before we give up
    MAX_WAIT_TIME = 300

    # Time to wait between each status check
    POLL_INTERVAL = 5

    #Time waited till now
    waited = 0

    # Wait for the batch to finish processing before trying to retrieve output
    # This loop checks the batch status every few seconds (polling)

    while True:
        retrieved_batch = await litellm.aretrieve_batch(
            batch_id=create_batch_response.id,
            custom_llm_provider="openai"
        )

        status = retrieved_batch.status
        print(f"⏳ Batch status: {status}")

        if status == "completed" and retrieved_batch.output_file_id:
            print("✅ Batch complete. Output file ID:", retrieved_batch.output_file_id)
            break
        elif status in ["failed", "cancelled", "expired"]:
            raise RuntimeError(f"❌ Batch failed with status: {status}")

        await asyncio.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL
        if waited > MAX_WAIT_TIME:
            raise TimeoutError("❌ Timed out waiting for batch to complete.")

print("retrieved batch=", retrieved_batch)
# just assert that we retrieved a non None batch

assert retrieved_batch.id == create_batch_response.id

# try to get file content for our original file

file_content = await litellm.afile_content(
    file_id=batch_input_file_id, custom_llm_provider="openai"
)

print("file content = ", file_content)

```

**List Batches**

```codeBlockLines_e6Vv
list_batches_response = litellm.list_batches(custom_llm_provider="openai", limit=2)
print("list_batches_response=", list_batches_response)

```

## **Supported Providers**: [​](https://docs.litellm.ai/docs/batches\#supported-providers "Direct link to supported-providers")

### [Azure OpenAI](https://docs.litellm.ai/docs/providers/azure\#azure-batches-api) [​](https://docs.litellm.ai/docs/batches\#azure-openai "Direct link to azure-openai")

### [OpenAI](https://docs.litellm.ai/docs/batches\#quick-start) [​](https://docs.litellm.ai/docs/batches\#openai "Direct link to openai")

### [Vertex AI](https://docs.litellm.ai/docs/providers/vertex\#batch-apis) [​](https://docs.litellm.ai/docs/batches\#vertex-ai "Direct link to vertex-ai")

## How Cost Tracking for Batches API Works [​](https://docs.litellm.ai/docs/batches\#how-cost-tracking-for-batches-api-works "Direct link to How Cost Tracking for Batches API Works")

LiteLLM tracks batch processing costs by logging two key events:

| Event Type | Description | When it's Logged |
| --- | --- | --- |
| `acreate_batch` | Initial batch creation | When batch request is submitted |
| `batch_success` | Final usage and cost | When batch processing completes |

Cost calculation:

- LiteLLM polls the batch status until completion
- Upon completion, it aggregates usage and costs from all responses in the output file
- Total `token` and `response_cost` reflect the combined metrics across all batch responses

## [Swagger API Reference](https://litellm-api.up.railway.app/\#/batch) [​](https://docs.litellm.ai/docs/batches\#swagger-api-reference "Direct link to swagger-api-reference")

- [Quick Start](https://docs.litellm.ai/docs/batches#quick-start)
- [**Supported Providers**:](https://docs.litellm.ai/docs/batches#supported-providers)
  - [Azure OpenAI](https://docs.litellm.ai/docs/batches#azure-openai)
  - [OpenAI](https://docs.litellm.ai/docs/batches#openai)
  - [Vertex AI](https://docs.litellm.ai/docs/batches#vertex-ai)
- [How Cost Tracking for Batches API Works](https://docs.litellm.ai/docs/batches#how-cost-tracking-for-batches-api-works)
- [Swagger API Reference](https://docs.litellm.ai/docs/batches#swagger-api-reference)