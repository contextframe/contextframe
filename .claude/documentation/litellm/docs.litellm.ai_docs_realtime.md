---
url: "https://docs.litellm.ai/docs/realtime"
title: "/realtime | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/realtime#__docusaurus_skipToContent_fallback)

On this page

# /realtime

Use this to loadbalance across Azure + OpenAI.

## Proxy Usage [​](https://docs.litellm.ai/docs/realtime\#proxy-usage "Direct link to Proxy Usage")

### Add model to config [​](https://docs.litellm.ai/docs/realtime\#add-model-to-config "Direct link to Add model to config")

- OpenAI
- OpenAI + Azure

```codeBlockLines_e6Vv
model_list:
  - model_name: openai-gpt-4o-realtime-audio
    litellm_params:
      model: openai/gpt-4o-realtime-preview-2024-10-01
      api_key: os.environ/OPENAI_API_KEY
    model_info:
      mode: realtime

```

```codeBlockLines_e6Vv
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o-realtime-preview
      api_key: os.environ/AZURE_SWEDEN_API_KEY
      api_base: os.environ/AZURE_SWEDEN_API_BASE

  - model_name: openai-gpt-4o-realtime-audio
    litellm_params:
      model: openai/gpt-4o-realtime-preview-2024-10-01
      api_key: os.environ/OPENAI_API_KEY

```

### Start proxy [​](https://docs.litellm.ai/docs/realtime\#start-proxy "Direct link to Start proxy")

```codeBlockLines_e6Vv
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:8000

```

### Test [​](https://docs.litellm.ai/docs/realtime\#test "Direct link to Test")

Run this script using node - `node test.js`

```codeBlockLines_e6Vv
// test.js
const WebSocket = require("ws");

const url = "ws://0.0.0.0:4000/v1/realtime?model=openai-gpt-4o-realtime-audio";
// const url = "wss://my-endpoint-sweden-berri992.openai.azure.com/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-4o-realtime-preview";
const ws = new WebSocket(url, {
    headers: {
        "api-key": `f28ab7b695af4154bc53498e5bdccb07`,
        "OpenAI-Beta": "realtime=v1",
    },
});

ws.on("open", function open() {
    console.log("Connected to server.");
    ws.send(JSON.stringify({
        type: "response.create",
        response: {
            modalities: ["text"],
            instructions: "Please assist the user.",
        }
    }));
});

ws.on("message", function incoming(message) {
    console.log(JSON.parse(message.toString()));
});

ws.on("error", function handleError(error) {
    console.error("Error: ", error);
});

```

## Logging [​](https://docs.litellm.ai/docs/realtime\#logging "Direct link to Logging")

To prevent requests from being dropped, by default LiteLLM just logs these event types:

- `session.created`
- `response.create`
- `response.done`

You can override this by setting the `logged_real_time_event_types` parameter in the config. For example:

```codeBlockLines_e6Vv
litellm_settings:
  logged_real_time_event_types: "*" # Log all events
  ## OR ##
  logged_real_time_event_types: ["session.created", "response.create", "response.done"] # Log only these event types

```

- [Proxy Usage](https://docs.litellm.ai/docs/realtime#proxy-usage)
  - [Add model to config](https://docs.litellm.ai/docs/realtime#add-model-to-config)
  - [Start proxy](https://docs.litellm.ai/docs/realtime#start-proxy)
  - [Test](https://docs.litellm.ai/docs/realtime#test)
- [Logging](https://docs.litellm.ai/docs/realtime#logging)