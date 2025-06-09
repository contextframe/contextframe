---
url: "https://mirascope.com/docs/mirascope/learn/retries"
title: "Retries | Mirascope"
---

# Retries [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#retries)

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. This makes retrying calls extremely important when building robust systems.

Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed while maintaining end user transparency.

You can install the necessary packages directly or use the `tenacity` extras flag:

```
pip install "mirascope[tenacity]"
```

## Tenacity `retry` Decorator [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#tenacity-retry-decorator)

### Calls [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#calls)

Let's take a look at a basic Mirascope call that retries with exponential back-off:

ShorthandTemplate

```
from mirascope import llm
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

print(recommend_book("fantasy"))
```

Ideally the call to `recommend_book` will succeed on the first attempt, but now the API call will be made again after waiting should it fail.

The call will then throw a `RetryError` after 3 attempts if unsuccessful. This error should be caught and handled.

### Streams [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#streams)

When streaming, the generator is not actually run until you start iterating. This means the initial API call may be successful but fail during the actual iteration through the stream.

Instead, you need to wrap your call and add retries to this wrapper:

ShorthandTemplate

```
from mirascope import llm
from tenacity import retry, stop_after_attempt, wait_exponential

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def stream():
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)

stream()
```

### Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#tools)

When using tools, `ValidationError` errors won't happen until you attempt to construct the tool (either when calling `response.tools` or iterating through a stream with tools).

You need to handle retries in this case the same way as streams:

ShorthandTemplate

```
from mirascope import llm
from tenacity import retry, stop_after_attempt, wait_exponential

def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[get_book_author])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def run():
    response = identify_author("The Name of the Wind")
    if tool := response.tool:
        print(tool.call())
        print(f"Original tool call: {tool.tool_call}")
    else:
        print(response.content)

run()
```

### Error Reinsertion [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#error-reinsertion)

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls based on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, Mirascope provides a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

ShorthandTemplate

```
from typing import Annotated

from mirascope import llm
from mirascope.retries.tenacity import collect_errors
from pydantic import AfterValidator, ValidationError
from tenacity import retry, stop_after_attempt

def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v

@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
)
def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str:
    previous_errors = None
    if errors:
        print(previous_errors)
        return f"Previous Error: {errors}\n\nWho wrote {book}?"
    return f"Who wrote {book}?"

author = identify_author("The Name of the Wind")
print(author)
# Previous Errors: [1 validation error for str\
# value\
#   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]\
#     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
# PATRICK ROTHFUSS
```

In this example the first attempt fails because the identified author is not all uppercase. The `ValidationError` is then reinserted into the subsequent call, which enables the model to learn from it's mistake and correct its error.

Of course, we could always engineer a better prompt (i.e. ask for all caps), but even prompt engineering does not guarantee perfect results. The purpose of this example is to demonstrate the power of a feedback loop by reinserting errors to build more robust systems.

## Fallback [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#fallback)

When using the provider-agnostic `llm.call` decorator, you can use the `fallback` decorator to automatically catch certain errors and use a backup provider/model to attempt the call again.

For example, we may want to attempt the call with Anthropic in the event that we get a `RateLimitError` from OpenAI:

ShorthandTemplate

```
from anthropic import RateLimitError as AnthropicRateLimitError
from mirascope import llm
from mirascope.retries import FallbackError, fallback
from openai import RateLimitError as OpenAIRateLimitError

@fallback(
    OpenAIRateLimitError,
    [\
        {\
            "catch": AnthropicRateLimitError,\
            "provider": "anthropic",\
            "model": "claude-3-5-sonnet-latest",\
        }\
    ],
)
@llm.call("openai", "gpt-4o-mini")
def answer_question(question: str) -> str:
    return f"Answer this question: {question}"

try:
    response = answer_question("What is the meaning of life?")
    if caught := getattr(response, "_caught", None):
        print(f"Exception caught: {caught}")
    print("### Response ###")
    print(response.content)
except FallbackError as e:
    print(e)
```

Here, we first attempt to call OpenAI (the default setting). If we catch the `OpenAIRateLimitError`, then we'll attempt to call Anthropic. If we catch the `AnthropicRateLimitError`, then we'll receive a `FallbackError` since all attempts failed.

You can provide an `Exception` or tuple of multiple to catch, and you can stack the `fallback` decorator to handle different errors differently if desired.

### Fallback With Retries [Link to this heading](https://mirascope.com/docs/mirascope/learn/retries\#fallback-with-retries)

The decorator also works well with Tenacity's `retry` decorator. For example, we may want to first attempt to call OpenAI multiple times with exponential backoff, but if we fail 3 times fall back to Anthropic, which we'll also attempt to call 3 times:

ShorthandTemplate

```
from anthropic import RateLimitError as AnthropicRateLimitError
from mirascope import llm
from mirascope.retries import FallbackError, fallback
from openai import RateLimitError as OpenAIRateLimitError
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

@fallback(
    RetryError,
    [\
        {\
            "catch": RetryError,\
            "provider": "anthropic",\
            "model": "claude-3-5-sonnet-latest",\
        }\
    ],
)
@retry(
    retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@llm.call(provider="openai", model="gpt-4o-mini")
def answer_question(question: str) -> str:
    return f"Answer this question: {question}"

try:
    response = answer_question("What is the meaning of life?")
    if caught := getattr(response, "_caught", None):
        print(f"Exception caught: {caught}")
    print("### Response ###")
    print(response.content)
except FallbackError as e:
    print(e)
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