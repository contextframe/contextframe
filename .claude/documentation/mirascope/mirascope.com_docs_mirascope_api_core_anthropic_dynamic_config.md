---
url: "https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config"
title: "mirascope.core.anthropic.dynamic_config | Mirascope"
---

# mirascope.core.anthropic.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config\#mirascope-core-anthropic-dynamic-config)

## Module dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config\#dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute AnthropicDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config\#anthropicdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[MessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams), Anthropic \| AnthropicBedrock \| AnthropicVertex\]

## Attribute AsyncAnthropicDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/anthropic/dynamic_config\#asyncanthropicdynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[MessageParam \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [AnthropicCallParams](https://mirascope.com/docs/mirascope/api/core/anthropic/call_params#anthropiccallparams), AsyncAnthropic \| AsyncAnthropicBedrock \| AsyncAnthropicVertex\]

The function return type for functions wrapped with the `anthropic_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.anthropic import AnthropicDynamicConfig, anthropic_call

@anthropic_call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> AnthropicDynamicConfig:
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