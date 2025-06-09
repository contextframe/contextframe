---
url: "https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config"
title: "mirascope.core.openai.dynamic_config | Mirascope"
---

# mirascope.core.openai.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config\#mirascope-core-openai-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AsyncOpenAIDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config\#asyncopenaidynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatCompletionMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams), AsyncOpenAI \| AsyncAzureOpenAI\]

## Attribute OpenAIDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/openai/dynamic_config\#openaidynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatCompletionMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [OpenAICallParams](https://mirascope.com/docs/mirascope/api/core/openai/call_params#openaicallparams), OpenAI \| AzureOpenAI\]

The function return type for functions wrapped with the `openai_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.openai import OpenAIDynamicConfig, openai_call

@openai_call("gpt-4o-mini")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> OpenAIDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept