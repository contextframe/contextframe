---
url: "https://docs.litellm.ai/docs/set_keys"
title: "Setting API Keys, Base, Version | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/set_keys#__docusaurus_skipToContent_fallback)

On this page

# Setting API Keys, Base, Version

LiteLLM allows you to specify the following:

- API Key
- API Base
- API Version
- API Type
- Project
- Location
- Token

Useful Helper functions:

- [`check_valid_key()`](https://docs.litellm.ai/docs/set_keys#check_valid_key)
- [`get_valid_models()`](https://docs.litellm.ai/docs/set_keys#get_valid_models)

You can set the API configs using:

- Environment Variables
- litellm variables `litellm.api_key`
- Passing args to `completion()`

## Environment Variables [​](https://docs.litellm.ai/docs/set_keys\#environment-variables "Direct link to Environment Variables")

### Setting API Keys [​](https://docs.litellm.ai/docs/set_keys\#setting-api-keys "Direct link to Setting API Keys")

Set the liteLLM API key or specific provider key:

```codeBlockLines_e6Vv
import os

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "Your API Key"
os.environ["ANTHROPIC_API_KEY"] = "Your API Key"
os.environ["XAI_API_KEY"] = "Your API Key"
os.environ["REPLICATE_API_KEY"] = "Your API Key"
os.environ["TOGETHERAI_API_KEY"] = "Your API Key"

```

### Setting API Base, API Version, API Type [​](https://docs.litellm.ai/docs/set_keys\#setting-api-base-api-version-api-type "Direct link to Setting API Base, API Version, API Type")

```codeBlockLines_e6Vv
# for azure openai
os.environ['AZURE_API_BASE'] = "https://openai-gpt-4-test2-v-12.openai.azure.com/"
os.environ['AZURE_API_VERSION'] = "2023-05-15" # [OPTIONAL]
os.environ['AZURE_API_TYPE'] = "azure" # [OPTIONAL]

# for openai
os.environ['OPENAI_BASE_URL'] = "https://your_host/v1"

```

### Setting Project, Location, Token [​](https://docs.litellm.ai/docs/set_keys\#setting-project-location-token "Direct link to Setting Project, Location, Token")

For cloud providers:

- Azure
- Bedrock
- GCP
- Watson AI

you might need to set additional parameters. LiteLLM provides a common set of params, that we map across all providers.

|  | LiteLLM param | Watson | Vertex AI | Azure | Bedrock |
| --- | --- | --- | --- | --- | --- |
| Project | project | watsonx\_project | vertex\_project | n/a | n/a |
| Region | region\_name | watsonx\_region\_name | vertex\_location | n/a | aws\_region\_name |
| Token | token | watsonx\_token or token | n/a | azure\_ad\_token | n/a |

If you want, you can call them by their provider-specific params as well.

## litellm variables [​](https://docs.litellm.ai/docs/set_keys\#litellm-variables "Direct link to litellm variables")

### litellm.api\_key [​](https://docs.litellm.ai/docs/set_keys\#litellmapi_key "Direct link to litellm.api_key")

This variable is checked for all providers

```codeBlockLines_e6Vv
import litellm
# openai call
litellm.api_key = "sk-OpenAIKey"
response = litellm.completion(messages=messages, model="gpt-3.5-turbo")

# anthropic call
litellm.api_key = "sk-AnthropicKey"
response = litellm.completion(messages=messages, model="claude-2")

```

### litellm.provider\_key (example litellm.openai\_key) [​](https://docs.litellm.ai/docs/set_keys\#litellmprovider_key-example-litellmopenai_key "Direct link to litellm.provider_key (example litellm.openai_key)")

```codeBlockLines_e6Vv
litellm.openai_key = "sk-OpenAIKey"
response = litellm.completion(messages=messages, model="gpt-3.5-turbo")

# anthropic call
litellm.anthropic_key = "sk-AnthropicKey"
response = litellm.completion(messages=messages, model="claude-2")

```

### litellm.api\_base [​](https://docs.litellm.ai/docs/set_keys\#litellmapi_base "Direct link to litellm.api_base")

```codeBlockLines_e6Vv
import litellm
litellm.api_base = "https://hosted-llm-api.co"
response = litellm.completion(messages=messages, model="gpt-3.5-turbo")

```

### litellm.api\_version [​](https://docs.litellm.ai/docs/set_keys\#litellmapi_version "Direct link to litellm.api_version")

```codeBlockLines_e6Vv
import litellm
litellm.api_version = "2023-05-15"
response = litellm.completion(messages=messages, model="gpt-3.5-turbo")

```

### litellm.organization [​](https://docs.litellm.ai/docs/set_keys\#litellmorganization "Direct link to litellm.organization")

```codeBlockLines_e6Vv
import litellm
litellm.organization = "LiteLlmOrg"
response = litellm.completion(messages=messages, model="gpt-3.5-turbo")

```

## Passing Args to completion() (or any litellm endpoint - `transcription`, `embedding`, `text_completion`, etc) [​](https://docs.litellm.ai/docs/set_keys\#passing-args-to-completion-or-any-litellm-endpoint---transcription-embedding-text_completion-etc "Direct link to passing-args-to-completion-or-any-litellm-endpoint---transcription-embedding-text_completion-etc")

You can pass the API key within `completion()` call:

### api\_key [​](https://docs.litellm.ai/docs/set_keys\#api_key "Direct link to api_key")

```codeBlockLines_e6Vv
from litellm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_key="Your-Api-Key")

```

### api\_base [​](https://docs.litellm.ai/docs/set_keys\#api_base "Direct link to api_base")

```codeBlockLines_e6Vv
from litellm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_base="https://hosted-llm-api.co")

```

### api\_version [​](https://docs.litellm.ai/docs/set_keys\#api_version "Direct link to api_version")

```codeBlockLines_e6Vv
from litellm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_version="2023-02-15")

```

## Helper Functions [​](https://docs.litellm.ai/docs/set_keys\#helper-functions "Direct link to Helper Functions")

### `check_valid_key()` [​](https://docs.litellm.ai/docs/set_keys\#check_valid_key "Direct link to check_valid_key")

Check if a user submitted a valid key for the model they're trying to call.

```codeBlockLines_e6Vv
key = "bad-key"
response = check_valid_key(model="gpt-3.5-turbo", api_key=key)
assert(response == False)

```

### `get_valid_models()` [​](https://docs.litellm.ai/docs/set_keys\#get_valid_models "Direct link to get_valid_models")

This helper reads the .env and returns a list of supported llms for user

```codeBlockLines_e6Vv
old_environ = os.environ
os.environ = {'OPENAI_API_KEY': 'temp'} # mock set only openai key in environ

valid_models = get_valid_models()
print(valid_models)

# list of openai supported llms on litellm
expected_models = litellm.open_ai_chat_completion_models + litellm.open_ai_text_completion_models

assert(valid_models == expected_models)

# reset replicate env key
os.environ = old_environ

```

### `get_valid_models(check_provider_endpoint: True)` [​](https://docs.litellm.ai/docs/set_keys\#get_valid_modelscheck_provider_endpoint-true "Direct link to get_valid_modelscheck_provider_endpoint-true")

This helper will check the provider's endpoint for valid models.

Currently implemented for:

- OpenAI (if OPENAI\_API\_KEY is set)
- Fireworks AI (if FIREWORKS\_AI\_API\_KEY is set)
- LiteLLM Proxy (if LITELLM\_PROXY\_API\_KEY is set)
- Gemini (if GEMINI\_API\_KEY is set)
- XAI (if XAI\_API\_KEY is set)
- Anthropic (if ANTHROPIC\_API\_KEY is set)

You can also specify a custom provider to check:

**All providers**:

```codeBlockLines_e6Vv
from litellm import get_valid_models

valid_models = get_valid_models(check_provider_endpoint=True)
print(valid_models)

```

**Specific provider**:

```codeBlockLines_e6Vv
from litellm import get_valid_models

valid_models = get_valid_models(check_provider_endpoint=True, custom_llm_provider="openai")
print(valid_models)

```

### `validate_environment(model: str)` [​](https://docs.litellm.ai/docs/set_keys\#validate_environmentmodel-str "Direct link to validate_environmentmodel-str")

This helper tells you if you have all the required environment variables for a model, and if not - what's missing.

```codeBlockLines_e6Vv
from litellm import validate_environment

print(validate_environment("openai/gpt-3.5-turbo"))

```

- [Environment Variables](https://docs.litellm.ai/docs/set_keys#environment-variables)
  - [Setting API Keys](https://docs.litellm.ai/docs/set_keys#setting-api-keys)
  - [Setting API Base, API Version, API Type](https://docs.litellm.ai/docs/set_keys#setting-api-base-api-version-api-type)
  - [Setting Project, Location, Token](https://docs.litellm.ai/docs/set_keys#setting-project-location-token)
- [litellm variables](https://docs.litellm.ai/docs/set_keys#litellm-variables)
  - [litellm.api\_key](https://docs.litellm.ai/docs/set_keys#litellmapi_key)
  - [litellm.provider\_key (example litellm.openai\_key)](https://docs.litellm.ai/docs/set_keys#litellmprovider_key-example-litellmopenai_key)
  - [litellm.api\_base](https://docs.litellm.ai/docs/set_keys#litellmapi_base)
  - [litellm.api\_version](https://docs.litellm.ai/docs/set_keys#litellmapi_version)
  - [litellm.organization](https://docs.litellm.ai/docs/set_keys#litellmorganization)
- [Passing Args to completion() (or any litellm endpoint - `transcription`, `embedding`, `text_completion`, etc)](https://docs.litellm.ai/docs/set_keys#passing-args-to-completion-or-any-litellm-endpoint---transcription-embedding-text_completion-etc)
  - [api\_key](https://docs.litellm.ai/docs/set_keys#api_key)
  - [api\_base](https://docs.litellm.ai/docs/set_keys#api_base)
  - [api\_version](https://docs.litellm.ai/docs/set_keys#api_version)
- [Helper Functions](https://docs.litellm.ai/docs/set_keys#helper-functions)
  - [`check_valid_key()`](https://docs.litellm.ai/docs/set_keys#check_valid_key)
  - [`get_valid_models()`](https://docs.litellm.ai/docs/set_keys#get_valid_models)
  - [`get_valid_models(check_provider_endpoint: True)`](https://docs.litellm.ai/docs/set_keys#get_valid_modelscheck_provider_endpoint-true)
  - [`validate_environment(model: str)`](https://docs.litellm.ai/docs/set_keys#validate_environmentmodel-str)