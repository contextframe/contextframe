---
url: "https://mirascope.com/docs/mirascope/learn/local_models"
title: "Local (Open-Source) Models | Mirascope"
---

# Local (Open-Source) Models [Link to this heading](https://mirascope.com/docs/mirascope/learn/local_models\#local-open-source-models)

You can use the [`llm.call`](https://mirascope.com/docs/mirascope/api) decorator to interact with models running with [Ollama](https://github.com/ollama/ollama) or [vLLM](https://github.com/vllm-project/vllm):

OllamavLLM

```
from mirascope import llm
from pydantic import BaseModel

@llm.call("ollama", "llama3.2")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

recommendation = recommend_book("fantasy")
print(recommendation)
# Output: Here are some popular and highly-recommended fantasy books...

class Book(BaseModel):
    title: str
    author: str

@llm.call("ollama", "llama3.2", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

Double Check Support

## OpenAI Compatibility [Link to this heading](https://mirascope.com/docs/mirascope/learn/local_models\#openai-compatibility)

When hosting (fine-tuned) open-source LLMs yourself locally or in your own cloud with tools that have OpenAI compatibility, you can use the [`openai.call`](https://mirascope.com/docs/mirascope/api) decorator with a [custom client](https://mirascope.com/docs/mirascope/learn/calls#custom-client) to interact with your model using all of Mirascope's various features.

OllamavLLM

```
from mirascope.core import openai
from openai import OpenAI
from pydantic import BaseModel

custom_client = OpenAI(
    base_url="http://localhost:11434/v1",  # your ollama endpoint
    api_key="ollama",  # required by openai, but unused
)

@openai.call("llama3.2", client=custom_client)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

recommendation = recommend_book("fantasy")
print(recommendation)
# Output: Here are some popular and highly-recommended fantasy books...

class Book(BaseModel):
    title: str
    author: str

@openai.call("llama3.2", response_model=Book, client=custom_client)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
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