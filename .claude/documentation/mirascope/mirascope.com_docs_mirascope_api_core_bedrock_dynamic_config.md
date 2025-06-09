---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config"
title: "mirascope.core.bedrock.dynamic_config | Mirascope"
---

# mirascope.core.bedrock.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config\#mirascope-core-bedrock-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AsyncBedrockDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config\#asyncbedrockdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[InternalBedrockMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BedrockCallParams](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params#bedrockcallparams), AsyncBedrockRuntimeClient\]

## Attribute BedrockDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/dynamic_config\#bedrockdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[InternalBedrockMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [BedrockCallParams](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params#bedrockcallparams), BedrockRuntimeClient\]

The function return type for functions wrapped with the `bedrock_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.bedrock import BedrockDynamicConfig, bedrock_call

@bedrock_call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> BedrockDynamicConfig:
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