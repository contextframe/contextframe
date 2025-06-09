---
url: "https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config"
title: "mirascope.core.groq.dynamic_config | Mirascope"
---

# mirascope.core.groq.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config\#mirascope-core-groq-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AsyncGroqDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config\#asyncgroqdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatCompletionMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [GroqCallParams](https://mirascope.com/docs/mirascope/api/core/groq/call_params#groqcallparams), AsyncGroq\]

## Attribute GroqDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/groq/dynamic_config\#groqdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ChatCompletionMessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [GroqCallParams](https://mirascope.com/docs/mirascope/api/core/groq/call_params#groqcallparams), Groq\]

The function return type for functions wrapped with the `groq_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.groq import GroqDynamicConfig, groq_call

@groq_call("llama-3.1-8b-instant")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GroqDynamicConfig:
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