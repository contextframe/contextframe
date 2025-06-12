---
url: "https://docs.litellm.ai/docs/migration"
title: "Migration Guide - LiteLLM v1.0.0+ | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/migration#__docusaurus_skipToContent_fallback)

On this page

# Migration Guide - LiteLLM v1.0.0+

When we have breaking changes (i.e. going from 1.x.x to 2.x.x), we will document those changes here.

## `1.0.0` [​](https://docs.litellm.ai/docs/migration\#100 "Direct link to 100")

**Last Release before breaking change**: 0.14.0

**What changed?**

- Requires `openai>=1.0.0`
- `openai.InvalidRequestError` → `openai.BadRequestError`
- `openai.ServiceUnavailableError` → `openai.APIStatusError`
- _NEW_ litellm client, allow users to pass api\_key
  - `litellm.Litellm(api_key="sk-123")`
- response objects now inherit from `BaseModel` (prev. `OpenAIObject`)
- _NEW_ default exception - `APIConnectionError` (prev. `APIError`)
- litellm.get\_max\_tokens() now returns an int not a dict




```codeBlockLines_e6Vv
max_tokens = litellm.get_max_tokens("gpt-3.5-turbo") # returns an int not a dict
assert max_tokens==4097

```

- Streaming - OpenAI Chunks now return `None` for empty stream chunks. This is how to process stream chunks with content




```codeBlockLines_e6Vv
response = litellm.completion(model="gpt-3.5-turbo", messages=messages, stream=True)
for part in response:
      print(part.choices[0].delta.content or "")

```


**How can we communicate changes better?**
Tell us

- [Discord](https://discord.com/invite/wuPM9dRgDw)
- Email ( [krrish@berri.ai](mailto:krrish@berri.ai)/ [ishaan@berri.ai](mailto:ishaan@berri.ai))
- Text us (+17708783106)

- [`1.0.0`](https://docs.litellm.ai/docs/migration#100)