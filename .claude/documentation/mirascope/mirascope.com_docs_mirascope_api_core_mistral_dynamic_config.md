---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/dynamic_config"
title: "mirascope.core.mistral.dynamic_config | Mirascope"
---

# mirascope.core.mistral.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/dynamic_config\#mirascope-core-mistral-dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute MistralDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/dynamic_config\#mistraldynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[AssistantMessage \| SystemMessage \| ToolMessage \| UserMessage \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [MistralCallParams](https://mirascope.com/docs/mirascope/api/core/mistral/call_params#mistralcallparams), Mistral\]

The function return type for functions wrapped with the `mistral_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import MistralDynamicConfig, mistral_call

@mistral_call("mistral-large-latest")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> MistralDynamicConfig:
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