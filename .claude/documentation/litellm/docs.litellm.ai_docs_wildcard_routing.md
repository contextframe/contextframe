---
url: "https://docs.litellm.ai/docs/wildcard_routing"
title: "Provider specific Wildcard routing | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/wildcard_routing#__docusaurus_skipToContent_fallback)

On this page

# Provider specific Wildcard routing

**Proxy all models from a provider**

Use this if you want to **proxy all models from a specific provider without defining them on the config.yaml**

## Step 1. Define provider specific routing [​](https://docs.litellm.ai/docs/wildcard_routing\#step-1-define-provider-specific-routing "Direct link to Step 1. Define provider specific routing")

- SDK
- PROXY

```codeBlockLines_e6Vv
from litellm import Router

router = Router(
    model_list=[\
        {\
            "model_name": "anthropic/*",\
            "litellm_params": {\
                "model": "anthropic/*",\
                "api_key": os.environ["ANTHROPIC_API_KEY"]\
            }\
        },\
        {\
            "model_name": "groq/*",\
            "litellm_params": {\
                "model": "groq/*",\
                "api_key": os.environ["GROQ_API_KEY"]\
            }\
        },\
        {\
            "model_name": "fo::*:static::*", # all requests matching this pattern will be routed to this deployment, example: model="fo::hi::static::hi" will be routed to deployment: "openai/fo::*:static::*"\
            "litellm_params": {\
                "model": "openai/fo::*:static::*",\
                "api_key": os.environ["OPENAI_API_KEY"]\
            }\
        }\
    ]
)

```

**Step 1** \- define provider specific routing on config.yaml

```codeBlockLines_e6Vv
model_list:
  # provider specific wildcard routing
  - model_name: "anthropic/*"
    litellm_params:
      model: "anthropic/*"
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: "groq/*"
    litellm_params:
      model: "groq/*"
      api_key: os.environ/GROQ_API_KEY
  - model_name: "fo::*:static::*" # all requests matching this pattern will be routed to this deployment, example: model="fo::hi::static::hi" will be routed to deployment: "openai/fo::*:static::*"
    litellm_params:
      model: "openai/fo::*:static::*"
      api_key: os.environ/OPENAI_API_KEY

```

## \[PROXY-Only\] Step 2 - Run litellm proxy [​](https://docs.litellm.ai/docs/wildcard_routing\#proxy-only-step-2---run-litellm-proxy "Direct link to proxy-only-step-2---run-litellm-proxy")

```codeBlockLines_e6Vv
$ litellm --config /path/to/config.yaml

```

## Step 3 - Test it [​](https://docs.litellm.ai/docs/wildcard_routing\#step-3---test-it "Direct link to Step 3 - Test it")

- SDK
- PROXY

```codeBlockLines_e6Vv
from litellm import Router

router = Router(model_list=...)

# Test with `anthropic/` - all models with `anthropic/` prefix will get routed to `anthropic/*`
resp = completion(model="anthropic/claude-3-sonnet-20240229", messages=[{"role": "user", "content": "Hello, Claude!"}])
print(resp)

# Test with `groq/` - all models with `groq/` prefix will get routed to `groq/*`
resp = completion(model="groq/llama3-8b-8192", messages=[{"role": "user", "content": "Hello, Groq!"}])
print(resp)

# Test with `fo::*::static::*` - all requests matching this pattern will be routed to `openai/fo::*:static::*`
resp = completion(model="fo::hi::static::hi", messages=[{"role": "user", "content": "Hello, Claude!"}])
print(resp)

```

Test with `anthropic/` \- all models with `anthropic/` prefix will get routed to `anthropic/*`

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "anthropic/claude-3-sonnet-20240229",
    "messages": [\
      {"role": "user", "content": "Hello, Claude!"}\
    ]
  }'

```

Test with `groq/` \- all models with `groq/` prefix will get routed to `groq/*`

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "groq/llama3-8b-8192",
    "messages": [\
      {"role": "user", "content": "Hello, Claude!"}\
    ]
  }'

```

Test with `fo::*::static::*` \- all requests matching this pattern will be routed to `openai/fo::*:static::*`

```codeBlockLines_e6Vv
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "fo::hi::static::hi",
    "messages": [\
      {"role": "user", "content": "Hello, Claude!"}\
    ]
  }'

```

## [\[PROXY-Only\] Control Wildcard Model Access](https://docs.litellm.ai/docs/proxy/model_access\#-control-access-on-wildcard-models) [​](https://docs.litellm.ai/docs/wildcard_routing\#proxy-only-control-wildcard-model-access "Direct link to proxy-only-control-wildcard-model-access")

- [Step 1. Define provider specific routing](https://docs.litellm.ai/docs/wildcard_routing#step-1-define-provider-specific-routing)
- [PROXY-Only Step 2 - Run litellm proxy](https://docs.litellm.ai/docs/wildcard_routing#proxy-only-step-2---run-litellm-proxy)
- [Step 3 - Test it](https://docs.litellm.ai/docs/wildcard_routing#step-3---test-it)
- [\[PROXY-Only\] Control Wildcard Model Access](https://docs.litellm.ai/docs/wildcard_routing#proxy-only-control-wildcard-model-access)