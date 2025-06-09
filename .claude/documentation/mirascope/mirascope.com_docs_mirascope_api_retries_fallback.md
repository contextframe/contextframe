---
url: "https://mirascope.com/docs/mirascope/api/retries/fallback"
title: "mirascope.retries.fallback | Mirascope"
---

# mirascope.retries.fallback [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#mirascope-retries-fallback)

## Module fallback [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#fallback)

The `fallback` module provides a fallback retry strategy.

## Class FallbackDecorator [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#fallbackdecorator)

**Bases:**

[Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)

## Class Fallback [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#fallback)

The override arguments to use for this fallback attempt.

**Bases:**

[TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| catch | [Required](https://docs.python.org/3/library/typing.html#typing.Required)\[[type](https://docs.python.org/3/library/functions.html#type)\[Exception\] \| [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[type](https://docs.python.org/3/library/functions.html#type)\[Exception\]\]\] | - |
| provider | [Required](https://docs.python.org/3/library/typing.html#typing.Required)\[[Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider)\] | - |
| model | [Required](https://docs.python.org/3/library/typing.html#typing.Required)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | - |
| call\_params | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[CommonCallParams\] | - |
| client | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |

## Class FallbackError [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#fallbackerror)

An error raised when all fallbacks fail.

**Bases:**

Exception

## Function fallback [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/fallback\#fallback)

A decorator that retries the function call with a fallback strategy.

This must use the provider-agnostic `llm.call` decorator.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| catch | [type](https://docs.python.org/3/library/functions.html#type)\[Exception\] \| [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)\[[type](https://docs.python.org/3/library/functions.html#type)\[Exception\]\] | The exception(s) to catch for the original call. |
| fallbacks | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[Fallback](https://mirascope.com/docs/mirascope/api/retries/fallback#fallback)\] | - |

### Returns

| Type | Description |
| --- | --- |
| [FallbackDecorator](https://mirascope.com/docs/mirascope/api/retries/fallback#fallbackdecorator) | The decorated function. |

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