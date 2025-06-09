---
url: "https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config"
title: "mirascope.core.azure.dynamic_config | Mirascope"
---

# mirascope.core.azure.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config\#mirascope-core-azure-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AsyncAzureDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config\#asyncazuredynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatRequestMessage \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [AzureCallParams](https://mirascope.com/docs/mirascope/api/core/azure/call_params#azurecallparams), AsyncChatCompletionsClient\]

## Attribute AzureDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/azure/dynamic_config\#azuredynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatRequestMessage \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [AzureCallParams](https://mirascope.com/docs/mirascope/api/core/azure/call_params#azurecallparams), ChatCompletionsClient\]

The function return type for functions wrapped with the `azure_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.azure import AzureDynamicConfig, azure_call

@azure_call("gpt-4o-mini")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> AzureDynamicConfig:
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