---
url: "https://docs.litellm.ai/docs/fine_tuning"
title: "/fine_tuning | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/fine_tuning#__docusaurus_skipToContent_fallback)

On this page

# /fine\_tuning

info

This is an Enterprise only endpoint [Get Started with Enterprise here](https://calendly.com/d/4mp-gd3-k5k/litellm-1-1-onboarding-chat)

| Feature | Supported | Notes |
| --- | --- | --- |
| Supported Providers | OpenAI, Azure OpenAI, Vertex AI | - |
| Cost Tracking | 🟡 | [Let us know if you need this](https://github.com/BerriAI/litellm/issues) |
| Logging | ✅ | Works across all logging integrations |

Add `finetune_settings` and `files_settings` to your litellm config.yaml to use the fine-tuning endpoints.

## Example config.yaml for `finetune_settings` and `files_settings` [​](https://docs.litellm.ai/docs/fine_tuning\#example-configyaml-for-finetune_settings-and-files_settings "Direct link to example-configyaml-for-finetune_settings-and-files_settings")

```codeBlockLines_e6Vv
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/fake
      api_key: fake-key
      api_base: https://exampleopenaiendpoint-production.up.railway.app/

# For /fine_tuning/jobs endpoints
finetune_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: os.environ/AZURE_API_KEY
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY
  - custom_llm_provider: "vertex_ai"
    vertex_project: "adroit-crow-413218"
    vertex_location: "us-central1"
    vertex_credentials: "/Users/ishaanjaffer/Downloads/adroit-crow-413218-a956eef1a2a8.json"

# for /files endpoints
files_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: fake-key
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY

```

## Create File for fine-tuning [​](https://docs.litellm.ai/docs/fine_tuning\#create-file-for-fine-tuning "Direct link to Create File for fine-tuning")

- OpenAI Python SDK
- curl

```codeBlockLines_e6Vv
client = AsyncOpenAI(api_key="sk-1234", base_url="http://0.0.0.0:4000") # base_url is your litellm proxy url

file_name = "openai_batch_completions.jsonl"
response = await client.files.create(
    extra_body={"custom_llm_provider": "azure"}, # tell litellm proxy which provider to use
    file=open(file_name, "rb"),
    purpose="fine-tune",
)

```

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/files \
    -H "Authorization: Bearer sk-1234" \
    -F purpose="batch" \
    -F custom_llm_provider="azure"\
    -F file="@mydata.jsonl"

```

## Create fine-tuning job [​](https://docs.litellm.ai/docs/fine_tuning\#create-fine-tuning-job "Direct link to Create fine-tuning job")

- Azure OpenAI

- OpenAI Python SDK
- curl

```codeBlockLines_e6Vv
ft_job = await client.fine_tuning.jobs.create(
    model="gpt-35-turbo-1106",                   # Azure OpenAI model you want to fine-tune
    training_file="file-abc123",                 # file_id from create file response
    extra_body={"custom_llm_provider": "azure"}, # tell litellm proxy which provider to use
)

```

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/fine_tuning/jobs \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer sk-1234" \
    -d '{
    "custom_llm_provider": "azure",
    "model": "gpt-35-turbo-1106",
    "training_file": "file-abc123"
    }'

```

### Request Body [​](https://docs.litellm.ai/docs/fine_tuning\#request-body "Direct link to Request Body")

- Supported Params
- Example Request Body

- `model`

**Type:** string

**Required:** Yes


The name of the model to fine-tune

- `custom_llm_provider`

**Type:** `Literal["azure", "openai", "vertex_ai"]`

**Required:** Yes
The name of the model to fine-tune. You can select one of the [**supported providers**](https://docs.litellm.ai/docs/fine_tuning#supported-providers)

- `training_file`

**Type:** string

**Required:** Yes


The ID of an uploaded file that contains training data.

  - See **upload file** for how to upload a file.
  - Your dataset must be formatted as a JSONL file.
- `hyperparameters`

**Type:** object

**Required:** No


The hyperparameters used for the fine-tuning job.


> #### Supported `hyperparameters` [​](https://docs.litellm.ai/docs/fine_tuning\#supported-hyperparameters "Direct link to supported-hyperparameters")
>
> #### batch\_size [​](https://docs.litellm.ai/docs/fine_tuning\#batch_size "Direct link to batch_size")
>
> **Type:** string or integer
>
> **Required:** No
>
> Number of examples in each batch. A larger batch size means that model parameters are updated less frequently, but with lower variance.
>
> #### learning\_rate\_multiplier [​](https://docs.litellm.ai/docs/fine_tuning\#learning_rate_multiplier "Direct link to learning_rate_multiplier")
>
> **Type:** string or number
>
> **Required:** No
>
> Scaling factor for the learning rate. A smaller learning rate may be useful to avoid overfitting.



> #### n\_epochs [​](https://docs.litellm.ai/docs/fine_tuning\#n_epochs "Direct link to n_epochs")
>
> **Type:** string or integer
>
> **Required:** No
>
> The number of epochs to train the model for. An epoch refers to one full cycle through the training dataset.

- `suffix` **Type:** string or null

**Required:** No

**Default:** null


A string of up to 18 characters that will be added to your fine-tuned model name.
Example: A `suffix` of "custom-model-name" would produce a model name like `ft:gpt-4o-mini:openai:custom-model-name:7p4lURel`.

- `validation_file` **Type:** string or null

**Required:** No


The ID of an uploaded file that contains validation data.

  - If provided, this data is used to generate validation metrics periodically during fine-tuning.

- `integrations` **Type:** array or null

**Required:** No


A list of integrations to enable for your fine-tuning job.

- `seed` **Type:** integer or null

**Required:** No


The seed controls the reproducibility of the job. Passing in the same seed and job parameters should produce the same results, but may differ in rare cases. If a seed is not specified, one will be generated for you.


```codeBlockLines_e6Vv
{
  "model": "gpt-4o-mini",
  "training_file": "file-abcde12345",
  "hyperparameters": {
    "batch_size": 4,
    "learning_rate_multiplier": 0.1,
    "n_epochs": 3
  },
  "suffix": "custom-model-v1",
  "validation_file": "file-fghij67890",
  "seed": 42
}

```

## Cancel fine-tuning job [​](https://docs.litellm.ai/docs/fine_tuning\#cancel-fine-tuning-job "Direct link to Cancel fine-tuning job")

- OpenAI Python SDK
- curl

```codeBlockLines_e6Vv
# cancel specific fine tuning job
cancel_ft_job = await client.fine_tuning.jobs.cancel(
    fine_tuning_job_id="123",                          # fine tuning job id
    extra_body={"custom_llm_provider": "azure"},       # tell litellm proxy which provider to use
)

print("response from cancel ft job={}".format(cancel_ft_job))

```

```codeBlockLines_e6Vv
curl -X POST http://localhost:4000/v1/fine_tuning/jobs/ftjob-abc123/cancel \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{"custom_llm_provider": "azure"}'

```

## List fine-tuning jobs [​](https://docs.litellm.ai/docs/fine_tuning\#list-fine-tuning-jobs "Direct link to List fine-tuning jobs")

- OpenAI Python SDK
- curl

```codeBlockLines_e6Vv
list_ft_jobs = await client.fine_tuning.jobs.list(
    extra_query={"custom_llm_provider": "azure"}   # tell litellm proxy which provider to use
)

print("list of ft jobs={}".format(list_ft_jobs))

```

```codeBlockLines_e6Vv
curl -X GET 'http://localhost:4000/v1/fine_tuning/jobs?custom_llm_provider=azure' \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer sk-1234"

```

## [👉 Proxy API Reference](https://litellm-api.up.railway.app/\#/fine-tuning) [​](https://docs.litellm.ai/docs/fine_tuning\#-proxy-api-reference "Direct link to -proxy-api-reference")

- [Example config.yaml for `finetune_settings` and `files_settings`](https://docs.litellm.ai/docs/fine_tuning#example-configyaml-for-finetune_settings-and-files_settings)
- [Create File for fine-tuning](https://docs.litellm.ai/docs/fine_tuning#create-file-for-fine-tuning)
- [Create fine-tuning job](https://docs.litellm.ai/docs/fine_tuning#create-fine-tuning-job)
  - [Request Body](https://docs.litellm.ai/docs/fine_tuning#request-body)
- [Cancel fine-tuning job](https://docs.litellm.ai/docs/fine_tuning#cancel-fine-tuning-job)
- [List fine-tuning jobs](https://docs.litellm.ai/docs/fine_tuning#list-fine-tuning-jobs)
- [👉 Proxy API Reference](https://docs.litellm.ai/docs/fine_tuning#-proxy-api-reference)