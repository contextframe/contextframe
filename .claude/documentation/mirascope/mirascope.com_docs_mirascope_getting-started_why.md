---
url: "https://mirascope.com/docs/mirascope/getting-started/why"
title: "Why Mirascope? | Mirascope"
---

# Why Mirascope? [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#why-mirascope)

Trusted by founders and engineers building the next generation of AI-native applications:

Jake Duth

Co-Founder & CTO / Reddy

"Mirascope's simplicity made it the natural next step from OpenAI's API — all without fighting the unnecessary complexity of tools like LangChain. We have all the bells and whistles we need for production while maintaining exceptional ease of use."

Vince Trost

Co-Founder / Plastic Labs

"The Pydantic inspired LLM toolkit the space has been missing. Simple, modular, extensible...helps where you need it, stays out of your way when you don't."

Skylar Payne

VP of Engineering & DS / Health Rhythms

"Mirascope's 'abstractions that aren't obstructions' tagline rings true – I was up and running in minutes, with seamless switching between AI providers. The type system catches any schema issues while I iterate, letting me focus entirely on crafting the perfect prompts."

Off Sornsoontorn

Senior AI & ML Engineer / Six Atomic

"LangChain required learning many concepts and its rigid abstractions made LLM behavior hard to customize. Mirascope lets us easily adapt LLM behaviors to any UI/UX design, so we can focus on innovation rather than working around limitations."

William Profit

Co-Founder / Callisto

"After trying many alternatives, we chose Mirascope for our large project and haven't looked back. It's simple, lean, and gets the job done without getting in the way. The team & community are super responsive, making building even easier."

Rami Awar

Founder / DataLine

"Migrating DataLine to Mirascope feels like I was rid of a pebble in my shoe that I never knew existed. This is what good design should feel like. Well done."

## Abstractions That Aren't Obstructions [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#abstractions-that-aren-t-obstructions)

Mirascope provides powerful abstractions that simplify LLM interactions without hiding the underlying mechanics. This approach gives you the convenience of high-level APIs while maintaining full control and transparency.

### Everything Beyond The Prompt Is Boilerplate [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#everything-beyond-the-prompt-is-boilerplate)

By eliminating boilerplate, Mirascope allows you to focus on what matters most: your prompt.

Let's compare structured outputs using Mirascope vs. the official SDKs:

#### Mirascope API [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#mirascope-api)

![Mirascope Frog Logo](https://mirascope.com/assets/branding/mirascope-logo.svg)

Mirascope

MessagesTemplate

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

book: Book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

#### Provider SDK Equivalent [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#provider-sdk-equivalent)

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

Reducing this boilerplate becomes increasingly important as the number and complexity of your calls grows beyond a single basic example. Furthermore, the Mirascope interface works across all of our various supported providers, so you don't need to learn the intricacies of each provider to use them the same way.

### Functional, Modular Design [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#functional-modular-design)

Mirascope's functional approach promotes modularity and reusability. You can easily compose and chain LLM calls, creating complex workflows with simple, readable code.

Separate CallsNested Calls

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"

@llm.call(provider="openai", model="gpt-4o-mini")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"

summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
```

The goal of our design approach is to remain **Pythonic** so you can **build your way**.

### Provider-Agnostic When Wanted, Specific When Needed [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#provider-agnostic-when-wanted-specific-when-needed)

We understand the desire for easily switching between various LLM providers. We also understand the (common) need to engineer a prompt for a specific provider (and model).

By implementing our LLM API call functionality as decorators, Mirascope makes implementing any and all of these paths straightforward and easy:

Provider SpecificProvider Agnostic

```
from mirascope.core import anthropic, openai

@openai.call("gpt-4o-mini")
def openai_recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

@anthropic.call("claude-3-5-sonnet-latest")
def anthropic_recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
```

### Type Hints & Editor Support [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#type-hints-editor-support)

🛡️ Type Safety

Catch errors before runtime during lint

💡 Editor Support

Rich autocomplete and inline documentation

## Who Should Use Mirascope? [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#who-should-use-mirascope)

Mirascope is **designed for everyone** to use!

However, we believe that the value of Mirascope will shine in particular for:

- **Professional Developers**: Who need fine-grained control and transparency in their LLM interactions.
- **AI Application Builders**: Looking for a tool that can grow with their project from prototype to production.
- **Teams**: Who value clean, maintainable code and want to avoid the "black box" problem of many AI frameworks.
- **Researchers and Experimenters**: Who need the flexibility to quickly try out new ideas without fighting their tools.

## Getting Started [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/why\#getting-started)

[Quick Start](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart) [Learn More](https://mirascope.com/docs/mirascope/learn) [Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA)

By choosing Mirascope, you're opting for a tool that respects your expertise as a developer while providing the conveniences you need to work efficiently and effectively with LLMs.

We believe the best tools get out of your way and let you focus on building great applications.

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