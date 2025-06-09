---
url: "https://mirascope.com/docs/mirascope"
title: "Welcome | Mirascope"
---

# Welcome to Mirascope [Link to this heading](https://mirascope.com/docs/mirascope\#welcome-to-mirascope)

[![Tests](https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Mirascope/mirascope/actions/workflows/tests.yml)[![Coverage](https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9)](https://app.codecov.io/github/Mirascope/mirascope)[![PyPI Version](https://img.shields.io/pypi/v/mirascope.svg)](https://pypi.org/project/mirascope/)[![Stars](https://img.shields.io/pypi/pyversions/mirascope.svg)](https://pypi.org/project/mirascope/)[![License](https://img.shields.io/github/license/Mirascope/mirascope.svg)](https://github.com/Mirascope/mirascope/blob/main/LICENSE)

Mirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs through a unified interface that works across various supported providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Google (Gemini/Vertex)](https://googleapis.github.io/python-genai/), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Bedrock](https://aws.amazon.com/bedrock/).

Whether you're generating text, extracting structured information, or developing complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.

[Why Use Mirascope](https://mirascope.com/docs/mirascope/getting-started/why) [Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) [Star the Repo](https://github.com/Mirascope/mirascope)

## Getting Started [Link to this heading](https://mirascope.com/docs/mirascope\#getting-started)

Install Mirascope, specifying the provider you intend to use, and set your API key:

MacOS / LinuxWindows

```
pip install "mirascope[openai]"
export OPENAI_API_KEY=XXXX
```

## Mirascope API [Link to this heading](https://mirascope.com/docs/mirascope\#mirascope-api)

Mirascope provides a consistent, easy-to-use API across all providers:

![Mirascope Frog Logo](https://mirascope.com/assets/branding/mirascope-logo.svg)

Mirascope

ShorthandTemplate

```
from mirascope import llm
from pydantic import BaseModel

class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str

@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=Book
)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book: Book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

## Provider SDK Equivalent [Link to this heading](https://mirascope.com/docs/mirascope\#provider-sdk-equivalent)

For comparison, here's how you would achieve the same result using the provider's native SDK:

Official SDK

```
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str

def extract_book(text: str) -> Book:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Extract {text}"}],
        tools=[\
            {\
                "function": {\
                    "name": "Book",\
                    "description": "An extracted book.",\
                    "parameters": {\
                        "properties": {\
                            "title": {"type": "string"},\
                            "author": {"type": "string"},\
                        },\
                        "required": ["title", "author"],\
                        "type": "object",\
                    },\
                },\
                "type": "function",\
            }\
        ],
        tool_choice="required",
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        return Book.model_validate_json(tool_calls[0].function.arguments)
    raise ValueError("No tool call found")

book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

If you'd like a more in-depth guide to getting started with Mirascope, check out our [quickstart guide](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart)

We're excited to see what you'll build with Mirascope, and we're here to help! Don't hesitate to reach out :)

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