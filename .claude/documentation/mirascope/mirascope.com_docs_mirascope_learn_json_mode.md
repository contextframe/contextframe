---
url: "https://mirascope.com/docs/mirascope/learn/json_mode"
title: "JSON Mode | Mirascope"
---

# JSON Mode [Link to this heading](https://mirascope.com/docs/mirascope/learn/json_mode\#json-mode)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

JSON Mode is a feature in Mirascope that allows you to request structured JSON output from Large Language Models (LLMs). This mode is particularly useful when you need to extract structured information from the model's responses, making it easier to parse and use the data in your applications.

Not all providers have an official JSON Mode

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/json_mode\#basic-usage-and-syntax)

Let's take a look at a basic example using JSON Mode:

ShorthandTemplate

```
import json

from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", json_mode=True)
def get_book_info(book_title: str) -> str:
    return f"Provide the author and genre of {book_title}"

response = get_book_info("The Name of the Wind")
print(json.loads(response.content))
# Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
```

In this example we

1. Enable JSON Mode with `json_mode=True` in the `call` decorator
2. Instruct the model what fields to include in our prompt
3. Load the JSON string response into a Python object and print it

## Error Handling and Validation [Link to this heading](https://mirascope.com/docs/mirascope/learn/json_mode\#error-handling-and-validation)

While JSON Mode can significantly improve the structure of model outputs, it's important to note that it's far from infallible. LLMs often produce invalid JSON or deviate from the expected structure, so it's crucial to implement proper error handling and validation in your code:

ShorthandTemplate

```
import json

from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", json_mode=True)
def get_book_info(book_title: str) -> str:
    return f"Provide the author and genre of {book_title}"

try:
    response = get_book_info("The Name of the Wind")
    print(json.loads(response.content))
except json.JSONDecodeError:
    print("The model produced invalid JSON")
```

Beyond JSON Validation

While this example catches errors for invalid JSON, there's always a chance that the LLM returns valid JSON that doesn't conform to your expected schema (such as missing fields or incorrect types).

For more robust validation, we recommend using [Response Models](https://mirascope.com/docs/mirascope/learn/response_models) for easier structuring and validation of LLM outputs.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/json_mode\#next-steps)

By leveraging JSON Mode, you can create more robust and data-driven applications that efficiently process and utilize LLM outputs. This approach allows for easy integration with databases, APIs, or user interfaces, demonstrating the power of JSON Mode in creating robust, data-driven applications.

Next, we recommend reading the section on [Output Parsers](https://mirascope.com/docs/mirascope/learn/output_parsers) to see how to engineer prompts with specific output structures and parse the outputs automatically on every call.

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