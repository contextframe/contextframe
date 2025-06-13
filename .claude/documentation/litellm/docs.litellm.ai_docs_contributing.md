---
url: "https://docs.litellm.ai/docs/contributing"
title: "Contributing - UI | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/contributing#__docusaurus_skipToContent_fallback)

On this page

# Contributing - UI

Here's how to run the LiteLLM UI locally for making changes:

## 1\. Clone the repo [​](https://docs.litellm.ai/docs/contributing\#1-clone-the-repo "Direct link to 1. Clone the repo")

```codeBlockLines_e6Vv
git clone https://github.com/BerriAI/litellm.git

```

## 2\. Start the UI + Proxy [​](https://docs.litellm.ai/docs/contributing\#2-start-the-ui--proxy "Direct link to 2. Start the UI + Proxy")

**2.1 Start the proxy on port 4000**

Tell the proxy where the UI is located

```codeBlockLines_e6Vv
export PROXY_BASE_URL="http://localhost:3000/"

```

```codeBlockLines_e6Vv
cd litellm/litellm/proxy
python3 proxy_cli.py --config /path/to/config.yaml --port 4000

```

**2.2 Start the UI**

Set the mode as development (this will assume the proxy is running on localhost:4000)

```codeBlockLines_e6Vv
export NODE_ENV="development"

```

```codeBlockLines_e6Vv
cd litellm/ui/litellm-dashboard

npm run dev

# starts on http://0.0.0.0:3000

```

## 3\. Go to local UI [​](https://docs.litellm.ai/docs/contributing\#3-go-to-local-ui "Direct link to 3. Go to local UI")

```codeBlockLines_e6Vv
http://0.0.0.0:3000

```

- [1\. Clone the repo](https://docs.litellm.ai/docs/contributing#1-clone-the-repo)
- [2\. Start the UI + Proxy](https://docs.litellm.ai/docs/contributing#2-start-the-ui--proxy)
- [3\. Go to local UI](https://docs.litellm.ai/docs/contributing#3-go-to-local-ui)