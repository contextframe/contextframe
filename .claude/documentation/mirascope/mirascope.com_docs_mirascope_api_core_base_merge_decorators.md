---
url: "https://mirascope.com/docs/mirascope/api/core/base/merge_decorators"
title: "mirascope.core.base.merge_decorators | Mirascope"
---

# mirascope.core.base.merge\_decorators [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/merge_decorators\#mirascope-core-base-merge-decorators)

## Function merge\_decorators [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/merge_decorators\#merge-decorators)

Combines multiple decorators into a single decorator factory.

This function allows you to merge multiple decorators into a single decorator factory.
The decorators are applied in the order they are passed to the function.
All function metadata (e.g. docstrings, function name) is preserved through the decoration chain.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| decorator | (() =\> \_R) =\> () =\> \_WR | The base decorator that determines the type signature of the decorated function. |
| additional\_decorators= () | ([Callable](https://docs.python.org/3/library/typing.html#typing.Callable)) =\> [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | - |

### Returns

| Type | Description |
| --- | --- |
| () =\> (() =\> \_R) =\> () =\> \_WR | A decorator factory function that applies all decorators in the specified order. |

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