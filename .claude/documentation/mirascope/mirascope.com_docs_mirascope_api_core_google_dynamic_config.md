---
url: "https://mirascope.com/docs/mirascope/api/core/google/dynamic_config"
title: "mirascope.core.google.dynamic_config | Mirascope"
---

# mirascope.core.google.dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/dynamic_config\#mirascope-core-google-dynamic-config)

This module defines the function return type for functions as LLM calls.

## Attribute GoogleDynamicConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/core/google/dynamic_config\#googledynamicconfig)

**Type:** [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\[ContentListUnion \| ContentListUnionDict \| [BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam), [GoogleCallParams](https://mirascope.com/docs/mirascope/api/core/google/call_params#googlecallparams), Client\]

The function return type for functions wrapped with the `google_call` decorator.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.google import GoogleDynamicConfig, google_call

@google_call("google-1.5-flash")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GoogleDynamicConfig:
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