---
url: "https://mirascope.com/docs/mirascope/learn/prompts"
title: "Prompts | Mirascope"
---

# Prompts [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#prompts)

API Documentation

When working with Large Language Model (LLM) APIs, the "prompt" is generally a list of messages where each message has a particular role. These prompts are the foundation of effectively working with LLMs, so Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions.

Let's look at how we can write prompts using Mirascope in a reusable, modular, and provider-agnostic way.

Calls will come later

For the following explanations we will be talking _only_ about the messages aspect of prompt engineering and will discuss calling the API later in the [Calls](https://mirascope.com/docs/mirascope/learn/calls) documentation.

In that section we will show how to use these provider-agnostic prompts to actually call a provider's API as well as how to engineer and tie a prompt to a specific call.

## Prompt Templates (Messages) [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#prompt-templates-messages)

First, let's look at a basic example:

ShorthandTemplate

```
from mirascope import prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> str:
    return f"Recommend a {genre} book"

print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

In this example:

1. The `recommend_book_prompt` method's signature defines the prompt's template variables.
2. Calling the method with `genre="fantasy"` returns a list with the corresponding `BaseMessageParam` instance with role `user` and content "Recommend a fantasy book".

The core concept to understand here is `BaseMessageParam`. This class operates as the base class for message parameters that Mirascope can handle and use across all supported providers.

In Mirascope, we use the `@prompt_template` decorator to write prompt templates as reusable methods that return the corresponding list of `BaseMessageParam` instances.

There are two common ways of writing Mirascope prompt functions:

1. _(Shorthand)_ Returning the `str` or `list` content for a single user message, or returning `Messages.{Role}` (individually or a list) when specific roles are needed.
2. _(String Template)_ Passing a string template to `@prompt_template` that gets parsed and then formatted like a normal Python formatted string.

Which method you use is mostly up to your preference, so feel free to select which one you prefer in the following sections.

## Message Roles [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#message-roles)

We can also define additional messages with different roles, such as a system message:

ShorthandTemplate

```
from mirascope import Messages, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return [\
        Messages.System("You are a librarian"),\
        Messages.User(f"Recommend a {genre} book"),\
    ]

print(recommend_book_prompt("fantasy"))
# Output: [\
#   BaseMessageParam(role='system', content='You are a librarian'),\
#   BaseMessageParam(role='user', content='Recommend a fantasy book'),\
# ]
```

Messages.Type

The return type `Messages.Type` accepts all shorthand methods as well as `BaseMessageParam` types. Since the message methods (e.g. `Messages.User`) return `BaseMessageParam` instances, we generally recommend always typing your prompt templates with the `Messages.Type` return type since it covers all prompt template writing methods.

Supported Roles

Mirascope prompt templates currently support the `system`, `user`, and `assistant` roles. When using string templates, the roles are parsed by their corresponding all caps keyword (e.g. SYSTEM).

For messages with the `tool` role, see how Mirascope automatically generates these messages for you in the [Tools](https://mirascope.com/docs/mirascope/learn/tools) and [Agents](https://mirascope.com/docs/mirascope/learn/agents) sections.

## Multi-Line Prompts [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#multi-line-prompts)

When writing prompts that span multiple lines, it's important to ensure you don't accidentally include additional, unnecessary tokens (namely `\t` tokens):

ShorthandTemplate

```
import inspect
from mirascope import prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> str:
    return inspect.cleandoc(
        f"""
        Recommend a {genre} book.
        Output in the format Title by Author.
        """
    )

print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
```

In this example, we use `inspect.cleandoc` to remove unnecessary tokens while maintaining proper formatting in our codebase.

Multi-Line String Templates

## Multi-Modal Inputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#multi-modal-inputs)

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. Mirascope treats these input types as first-class and supports them natively.

While Mirascope provides a consistent interface, support varies among providers:

| Type | Anthropic | Cohere | Google | Groq | Mistral | OpenAI |
| --- | --- | --- | --- | --- | --- | --- |
| text | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| image | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| audio | — | — | ✓ | — | — | ✓ |
| video | — | — | ✓ | — | — | — |
| document | ✓ | — | ✓ | — | — | — |

_Legend: ✓ (Supported), — (Not Supported)_

### Image Inputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#image-inputs)

ShorthandTemplate

```
from mirascope import prompt_template
from PIL import Image

@prompt_template()
def recommend_book_prompt(previous_book: Image.Image) -> list:
    return ["I just read this book:", previous_book, "What should I read next?"]

with Image.open("path/to/image.jpg") as image:
    print(recommend_book_prompt(image))
# Output: [\
#   BaseMessageParam(\
#     role='user',\
#     content=[\
#       ContentPartParam(type='text', text='I just read this book:'),\
#       ContentPartParam(type='image', image=<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1000x1000>),\
#       ContentPartParam(type='text', text='What should I read next?')\
#     ]\
#   )\
# ]
```

Additional String Template Image Functionality

### Audio Inputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#audio-inputs)

pydubwave

ShorthandTemplate

```
from mirascope import Messages, prompt_template
from pydub import AudioSegment

@prompt_template()
def identify_book_prompt(audio_wave: AudioSegment) -> Messages.Type:
    return ["Here's an audio book snippet:", audio_wave, "What book is this?"]

with open("....", "rb") as audio:
    print(identify_book_prompt(AudioSegment.from_mp3(audio)))
# Output: [\
#     BaseMessageParam(\
#         role="user",\
#         content=[\
#             TextPart(type="text", text="Here's an audio book snippet:"),\
#             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),\
#             TextPart(type="text", text="What book is this?"),\
#         ],\
#     )\
# ]
```

Additional String Template Audio Functionality

### Document Inputs [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#document-inputs)

ShorthandTemplate

```
from mirascope import DocumentPart, Messages, prompt_template

@prompt_template()
def recommend_book_prompt(previous_book_pdf: bytes) -> Messages.Type:
    return Messages.User(
        [\
            "I just read this book:",\
            DocumentPart(\
                type="document",\
                media_type="application/pdf",\
                document=previous_book_pdf,\
            ),\
            "What should I read next?",\
        ]
    )

print(recommend_book_prompt(b"..."))
# Output: [\
#     BaseMessageParam(\
#         role="user",\
#         content=[\
#             TextPart(type="text", text="I just read this book:"),\
#             DocumentPart(type='document', media_type='application/pdf', document=b'...'),\
#             TextPart(type="text", text="What should I read next?"),\
#         ],\
#     )\
# ]
```

Supported Document Types

Additional String Template Document Functionality

## Chat History [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#chat-history)

Often you'll want to inject messages (such as previous chat messages) into the prompt. Generally you can just unroll the messages into the return value of your prompt template. When using string templates, we provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

ShorthandTemplate

```
from mirascope import BaseMessageParam, Messages, prompt_template

@prompt_template()
def chatbot(query: str, history: list[BaseMessageParam]) -> list[BaseMessageParam]:
    return [Messages.System("You are a librarian"), *history, Messages.User(query)]

history = [\
    Messages.User("Recommend a book"),\
    Messages.Assistant("What genre do you like?"),\
]
print(chatbot("fantasy", history))
# Output: [\
#     BaseMessageParam(role="system", content="You are a librarian"),\
#     BaseMessageParam(role="user", content="Recommend a book"),\
#     BaseMessageParam(role="assistant", content="What genre do you like?"),\
#     BaseMessageParam(role="user", content="fantasy"),\
# ]
```

## Object Attribute Access [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#object-attribute-access)

When using template variables that have attributes, you can easily inject these attributes directly even when using string templates:

ShorthandTemplate

```
from mirascope import prompt_template
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

@prompt_template()
def recommend_book_prompt(book: Book) -> str:
    return f"I read {book.title} by {book.author}. What should I read next?"

book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
print(recommend_book_prompt(book))
# Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]
```

It's worth noting that this also works with `self` when using prompt templates inside of a class, which is particularly important when building [Agents](https://mirascope.com/docs/mirascope/learn/agents).

## Format Specifiers [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#format-specifiers)

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

ShorthandTemplate

```
from mirascope import prompt_template

@prompt_template()
def recommend_book(genre: str, price: float) -> str:
    return f"Recommend a {genre} book under ${price:.2f}"

print(recommend_book("fantasy", 12.3456))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
```

When writing string templates, we also offer additional format specifiers for convenience around formatting more dynamic content:

### Lists [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#lists)

String templates support the `:list` format specifier for formatting lists:

List(s)Text(s)Part(s)

```
from mirascope import prompt_template

@prompt_template(
    """
    Book themes:
    {themes:list}

    Character analysis:
    {characters:lists}
    """
)
def analyze_book(themes: list[str], characters: list[list[str]]): ...

prompt = analyze_book(
    themes=["redemption", "power", "friendship"],
    characters=[\
        ["Name: Frodo", "Role: Protagonist"],\
        ["Name: Gandalf", "Role: Mentor"],\
    ],
)

print(prompt[0].content)
# Output:
# Book themes:
# redemption
# power
# friendship

# Character analysis:
# Name: Frodo
# Role: Protagonist

# Name: Gandalf
# Role: Mentor
```

## Computed Fields (Dynamic Configuration) [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#computed-fields-dynamic-configuration)

In Mirascope, we write prompt templates as functions, which enables dynamically configuring our prompts at runtime depending on the values of the template variables. We use the term "computed fields" to talk about variables that are computed and formatted at runtime.

ShorthandTemplate

```
from mirascope import BaseDynamicConfig, Messages, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
    uppercase_genre = genre.upper()
    messages = [Messages.User(f"Recommend a {uppercase_genre} book")]
    return {
        "messages": messages,
        "computed_fields": {"uppercase_genre": uppercase_genre},
    }

print(recommend_book_prompt("fantasy"))
# Output: {
#     "messages": [BaseMessageParam(role="user", content="Recommend a FANTASY book")],
#     "computed_fields": {"uppercase_genre": "FANTASY"},
# }
```

There are various other parts of an LLM API call that we may want to configure dynamically as well, such as call parameters, tools, and more. We cover such cases in each of their respective sections.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/prompts\#next-steps)

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Calls](https://mirascope.com/docs/mirascope/learn/calls) documentation, which shows you how to use your prompt templates to actually call LLM APIs and generate a response.

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