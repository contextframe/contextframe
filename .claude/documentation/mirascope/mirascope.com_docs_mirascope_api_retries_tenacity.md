---
url: "https://mirascope.com/docs/mirascope/api/retries/tenacity"
title: "mirascope.retries.tenacity | Mirascope"
---

# mirascope.retries.tenacity [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/tenacity\#mirascope-retries-tenacity)

Utitlies for more easily using Tenacity to reinsert errors on failed API calls.

## Function collect\_errors [Link to this heading](https://mirascope.com/docs/mirascope/api/retries/tenacity\#collect-errors)

Collects specified errors into an `errors` keyword argument.

Example:

```
from mirascope.integrations.tenacity import collect_errors
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3), after=collect_errors(ValueError))
def throw_value_error(*, errors: list[ValueError] | None = None):
    if errors:
        print(errors[-1])
    raise ValueError("Throwing Error")

try:
    throw_value_error()
    # > Throwing Error
    # > Throwing Error
except RetryError:
    ...
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| args= () | [type](https://docs.python.org/3/library/functions.html#type)\[Exception\] | - |

### Returns

| Type | Description |
| --- | --- |
| (RetryCallState) =\> [None](https://docs.python.org/3/library/constants.html#None) | - |

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