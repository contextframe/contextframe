---
url: "https://docs.litellm.ai/docs/scheduler"
title: "[BETA] Request Prioritization | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/scheduler#__docusaurus_skipToContent_fallback)

On this page

# \[BETA\] Request Prioritization

info

Beta feature. Use for testing only.

[Help us improve this](https://github.com/BerriAI/litellm/issues)

Prioritize LLM API requests in high-traffic.

- Add request to priority queue
- Poll queue, to check if request can be made. Returns 'True':
  - if there's healthy deployments
  - OR if request is at top of queue
- Priority - The lower the number, the higher the priority:
  - e.g. `priority=0` \> `priority=2000`

Supported Router endpoints:

- `acompletion` ( `/v1/chat/completions` on Proxy)
- `atext_completion` ( `/v1/completions` on Proxy)

## Quick Start [​](https://docs.litellm.ai/docs/scheduler\#quick-start "Direct link to Quick Start")

```codeBlockLines_e6Vv
from litellm import Router

router = Router(
    model_list=[\
        {\
            "model_name": "gpt-3.5-turbo",\
            "litellm_params": {\
                "model": "gpt-3.5-turbo",\
                "mock_response": "Hello world this is Macintosh!", # fakes the LLM API call\
                "rpm": 1,\
            },\
        },\
    ],
    timeout=2, # timeout request if takes > 2s
    routing_strategy="usage-based-routing-v2",
    polling_interval=0.03 # poll queue every 3ms if no healthy deployments
)

try:
    _response = await router.acompletion( # 👈 ADDS TO QUEUE + POLLS + MAKES CALL
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hey!"}],
        priority=0, # 👈 LOWER IS BETTER
    )
except Exception as e:
    print("didn't make request")

```

## LiteLLM Proxy [​](https://docs.litellm.ai/docs/scheduler\#litellm-proxy "Direct link to LiteLLM Proxy")

To prioritize requests on LiteLLM Proxy add `priority` to the request.

- curl
- OpenAI SDK

```codeBlockLines_e6Vv
curl -X POST 'http://localhost:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-1234' \
-D '{
    "model": "gpt-3.5-turbo-fake-model",
    "messages": [\
        {\
        "role": "user",\
        "content": "what is the meaning of the universe? 1234"\
        }],
    "priority": 0 👈 SET VALUE HERE
}'

```

```codeBlockLines_e6Vv
import openai
client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages = [\
        {\
            "role": "user",\
            "content": "this is a test request, write a short poem"\
        }\
    ],
    extra_body={
        "priority": 0 👈 SET VALUE HERE
    }
)

print(response)

```

## Advanced - Redis Caching [​](https://docs.litellm.ai/docs/scheduler\#advanced---redis-caching "Direct link to Advanced - Redis Caching")

Use redis caching to do request prioritization across multiple instances of LiteLLM.

### SDK [​](https://docs.litellm.ai/docs/scheduler\#sdk "Direct link to SDK")

```codeBlockLines_e6Vv
from litellm import Router

router = Router(
    model_list=[\
        {\
            "model_name": "gpt-3.5-turbo",\
            "litellm_params": {\
                "model": "gpt-3.5-turbo",\
                "mock_response": "Hello world this is Macintosh!", # fakes the LLM API call\
                "rpm": 1,\
            },\
        },\
    ],
    ### REDIS PARAMS ###
    redis_host=os.environ["REDIS_HOST"],
    redis_password=os.environ["REDIS_PASSWORD"],
    redis_port=os.environ["REDIS_PORT"],
)

try:
    _response = await router.acompletion( # 👈 ADDS TO QUEUE + POLLS + MAKES CALL
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hey!"}],
        priority=0, # 👈 LOWER IS BETTER
    )
except Exception as e:
    print("didn't make request")

```

### PROXY [​](https://docs.litellm.ai/docs/scheduler\#proxy "Direct link to PROXY")

```codeBlockLines_e6Vv
model_list:
    - model_name: gpt-3.5-turbo-fake-model
      litellm_params:
        model: gpt-3.5-turbo
        mock_response: "hello world!"
        api_key: my-good-key

litellm_settings:
    request_timeout: 600 # 👈 Will keep retrying until timeout occurs

router_settings:
    redis_host; os.environ/REDIS_HOST
    redis_password: os.environ/REDIS_PASSWORD
    redis_port: os.environ/REDIS_PORT

```

```codeBlockLines_e6Vv
$ litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000s

```

```codeBlockLines_e6Vv
curl -X POST 'http://localhost:4000/queue/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-1234' \
-D '{
    "model": "gpt-3.5-turbo-fake-model",
    "messages": [\
        {\
        "role": "user",\
        "content": "what is the meaning of the universe? 1234"\
        }],
    "priority": 0 👈 SET VALUE HERE
}'

```

- [Quick Start](https://docs.litellm.ai/docs/scheduler#quick-start)
- [LiteLLM Proxy](https://docs.litellm.ai/docs/scheduler#litellm-proxy)
- [Advanced - Redis Caching](https://docs.litellm.ai/docs/scheduler#advanced---redis-caching)
  - [SDK](https://docs.litellm.ai/docs/scheduler#sdk)
  - [PROXY](https://docs.litellm.ai/docs/scheduler#proxy)