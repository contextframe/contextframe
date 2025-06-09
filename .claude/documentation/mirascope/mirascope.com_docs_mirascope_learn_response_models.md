---
url: "https://mirascope.com/docs/mirascope/learn/response_models"
title: "Response Models | Mirascope"
---

# Response Models [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#response-models)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

Response Models in Mirascope provide a powerful way to structure and validate the output from Large Language Models (LLMs). By leveraging Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), Response Models offer type safety, automatic validation, and easier data manipulation for your LLM responses. While we cover some details in this documentation, we highly recommend reading through Pydantic's documentation for a deeper, comprehensive dive into everything you can do with Pydantic's `BaseModel`.

## Why Use Response Models? [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#why-use-response-models)

1. **Structured Output**: Define exactly what you expect from the LLM, ensuring consistency in responses.
2. **Automatic Validation**: Pydantic handles type checking and validation, reducing errors in your application.
3. **Improved Type Hinting**: Better IDE support and clearer code structure.
4. **Easier Data Manipulation**: Work with Python objects instead of raw strings or dictionaries.

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#basic-usage-and-syntax)

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

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

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

Official SDK

Notice how Mirascope makes generating structured outputs significantly simpler than the official SDKs. It also greatly reduces boilerplate and standardizes the interaction across all supported LLM providers.

Tools By Default

### Accessing Original Call Response [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#accessing-original-call-response)

Every `response_model` that uses a Pydantic `BaseModel` will automatically have the original `BaseCallResponse` instance accessible through the `_response` property:

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

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'

response = book._response  # pyright: ignore[reportAttributeAccessIssue]
print(response.model_dump())
# > {'metadata': {}, 'response': {'id': ...}, ...}
```

### Built-In Types [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#built-in-types)

For cases where you want to extract just a single built-in type, Mirascope provides a shorthand:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", response_model=list[str])
def extract_book(texts: list[str]) -> str:
    return f"Extract book titles from {texts}"

book = extract_book(
    [\
        "The Name of the Wind by Patrick Rothfuss",\
        "Mistborn: The Final Empire by Brandon Sanderson",\
    ]
)
print(book)
# Output: ["The Name of the Wind", "Mistborn: The Final Empire"]
```

Here, we are using `list[str]` as the `response_model`, which Mirascope handles without needing to define a full `BaseModel`. You could of course set `response_model=list[Book]` as well.

Note that we have no way of attaching `BaseCallResponse` to built-in types, so using a Pydantic `BaseModel` is recommended if you anticipate needing access to the original call response.

## Supported Field Types [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#supported-field-types)

While Mirascope provides a consistent interface, type support varies among providers:

| Type | OpenAI | Anthropic | Google | Groq | xAI | Mistral | Cohere |
| --- | --- | --- | --- | --- | --- | --- | --- |
| str | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| int | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| float | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| bool | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| bytes | ✓✓ | ✓✓ | -✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| list | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| set | ✓✓ | ✓✓ | -- | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| tuple | -✓ | ✓✓ | -✓ | ✓✓ | -✓ | ✓✓ | ✓✓ |
| dict | -✓ | ✓✓ | ✓✓ | ✓✓ | -✓ | ✓✓ | ✓✓ |
| Literal/Enum | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| BaseModel | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | -✓ |
| Nested ($def) | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | -- |

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Validation and Error Handling [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#validation-and-error-handling)

While `response_model` significantly improves output structure and validation, it's important to handle potential errors.

Let's take a look at an example where we want to validate that all fields are uppercase:

ShorthandTemplate

```
from typing import Annotated

from mirascope import llm
from pydantic import AfterValidator, BaseModel, ValidationError

def validate_upper(v: str) -> str:
    assert v.isupper(), "Field must be uppercase"
    return v

class Book(BaseModel):
    """An extracted book."""

    title: Annotated[str, AfterValidator(validate_upper)]
    author: Annotated[str, AfterValidator(validate_upper)]

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

try:
    book = extract_book("The Name of the Wind by Patrick Rothfuss")
    print(book)
    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
except ValidationError as e:
    print(f"Error: {str(e)}")
    # Error: 2 validation errors for Book
    # title
    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
    # author
    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
```

Without additional prompt engineering, this call will fail every single time. It's important to engineer your prompts to reduce errors, but LLMs are far from perfect, so always remember to catch and handle validation errors gracefully.

We highly recommend taking a look at our section on [retries](https://mirascope.com/docs/mirascope/learn/retries) to learn more about automatically retrying and re-inserting validation errors, which enables retrying the call such that the LLM can learn from its previous mistakes.

### Accessing Original Call Response On Error [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#accessing-original-call-response-on-error)

In case of a `ValidationError`, you can access the original response for debugging:

ShorthandTemplate

```
from typing import Annotated

from mirascope import llm
from pydantic import AfterValidator, BaseModel, ValidationError

def validate_upper(v: str) -> str:
    assert v.isupper(), "Field must be uppercase"
    return v

class Book(BaseModel):
    """An extracted book."""

    title: Annotated[str, AfterValidator(validate_upper)]
    author: Annotated[str, AfterValidator(validate_upper)]

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

try:
    book = extract_book("The Name of the Wind by Patrick Rothfuss")
    print(book)
except ValidationError as e:
    response = e._response  # pyright: ignore[reportAttributeAccessIssue]
    print(response.model_dump())
    # > {'metadata': {}, 'response': {'id': ...}, ...}
```

This allows you to gracefully handle errors as well as inspect the original LLM response when validation fails.

## JSON Mode [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#json-mode)

By default, `response_model` uses [Tools](https://mirascope.com/docs/mirascope/learn/tools) under the hood. You can instead use [JSON Mode](https://mirascope.com/docs/mirascope/learn/json_mode) in conjunction with `response_model` by setting `json_mode=True`:

ShorthandTemplate

```
from mirascope import llm
from pydantic import BaseModel

class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book, json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

## Few-Shot Examples [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#few-shot-examples)

Adding few-shot examples to your response model can improve results by demonstrating exactly how to adhere to your desired output.

We take advantage of Pydantic's [`Field`](https://docs.pydantic.dev/latest/concepts/fields/) and [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) to add these examples to response models:

ShorthandTemplate

```
from mirascope import llm
from pydantic import BaseModel, ConfigDict, Field

class Book(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [\
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}\
            ]
        }
    )

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book, json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract {text}. Match example format EXCLUDING 'examples' key."

book = extract_book("The Way of Kings by Brandon Sanderson")
print(book)
# Output: title='THE WAY OF KINGS' author='Sanderson, Brandon'
```

## Streaming Response Models [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#streaming-response-models)

If you set `stream=True` when `response_model` is set, your LLM call will return an `Iterable` where each item will be a partial version of your response model representing the current state of the streamed information. The final model returned by the iterator will be the full response model.

ShorthandTemplate

```
from mirascope import llm
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book, stream=True)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
for partial_book in book_stream:
    print(partial_book)
# Output:
# title=None author=None
# title='' author=None
# title='The' author=None
# title='The Name' author=None
# title='The Name of' author=None
# title='The Name of the' author=None
# title='The Name of the Wind' author=None
# title='The Name of the Wind' author=''
# title='The Name of the Wind' author='Patrick'
# title='The Name of the Wind' author='Patrick Roth'
# title='The Name of the Wind' author='Patrick Rothf'
# title='The Name of the Wind' author='Patrick Rothfuss'
```

Once exhausted, you can access the final, full response model through the `constructed_response_model` property of the structured stream. Note that this will also give you access to the [`._response` property](https://mirascope.com/docs/mirascope/learn/response_models#accessing-original-call-response) that every `BaseModel` receives.

You can also use the `stream` property to access the `BaseStream` instance and [all of it's properties](https://mirascope.com/docs/mirascope/learn/streams#common-stream-properties-and-methods).

## FromCallArgs [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#fromcallargs)

Fields annotated with `FromCallArgs` will be populated with the corresponding argument from the function call rather than expecting it from the LLM's response. This enables seamless validation of LLM outputs against function inputs:

ShorthandTemplate

```
from typing import Annotated

from mirascope import llm
from mirascope.core import FromCallArgs
from pydantic import BaseModel, model_validator
from typing_extensions import Self

class Book(BaseModel):
    title: str
    author: str

class Books(BaseModel):
    texts: Annotated[list[str], FromCallArgs()]
    books: list[Book]

    @model_validator(mode="after")
    def validate_output_length(self) -> Self:
        if len(self.texts) != len(self.books):
            raise ValueError("length mismatch...")
        return self

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Books)
def extract_books(texts: list[str]) -> str:
    return f"Extract the books from these texts: {texts}"

texts = [\
    "The Name of the Wind by Patrick Rothfuss",\
    "Mistborn: The Final Empire by Brandon Sanderson",\
]
print(extract_books(texts))
# Output:
# texts=[\
#     'The Name of the Wind by Patrick Rothfuss',\
#     'Mistborn: The Final Empire by Brandon Sanderson'\
# ]
# books=[\
#     Book(title='The Name of the Wind', author='Patrick Rothfuss'),\
#     Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')\
# ]
```

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/response_models\#next-steps)

By following these best practices and leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.

Next, we recommend taking a look at one of:

- [JSON Mode](https://mirascope.com/docs/mirascope/learn/json_mode) to see an alternate way to generate structured outputs where using Pydantic to validate outputs is optional.
- [Evals](https://mirascope.com/docs/mirascope/learn/evals) to see how to use `response_model` to evaluate your prompts.

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