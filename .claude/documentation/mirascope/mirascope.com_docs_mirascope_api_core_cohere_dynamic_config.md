---
url: "https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config"
title: "mirascope.core.cohere.dynamic_config | Mirascope"
---

# mirascope.core.cohere.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config\#mirascope-core-cohere-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AsyncCohereDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config\#asynccoheredynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatMessage \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams), AsyncClient\]

## Attribute CohereDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/cohere/dynamic_config\#coheredynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatMessage \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [CohereCallParams](https://mirascope.com/docs/mirascope/api/core/cohere/call_params#coherecallparams), Client\]

The function return type for functions wrapped with the `cohere_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.cohere import CohereDynamicConfig, cohere_call

@cohere_call("command-r-plus")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> CohereDynamicConfig:
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