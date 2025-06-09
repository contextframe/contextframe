---
url: "https://mirascope.com/docs/mirascope/learn/tools"
title: "Tools | Mirascope"
---

# Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#tools)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

Tools are user-defined functions that an LLM (Large Language Model) can ask the user to invoke on its behalf. This greatly enhances the capabilities of LLMs by enabling them to perform specific tasks, access external data, interact with other systems, and more.

Mirascope enables defining tools in a provider-agnostic way, which can be used across all supported LLM providers without modification.

Diagram illustrating how tools are called

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#basic-usage-and-syntax)

API Documentation

There are two ways of defining tools in Mirascope: `BaseTool` and functions.

You can consider the functional definitions a shorthand form of writing the `BaseTool` version of the same tool. Under the hood, tools defined as functions will get converted automatically into their corresponding `BaseTool`.

Let's take a look at a basic example of each:

![Mirascope Frog Logo](https://mirascope.com/assets/branding/mirascope-logo.svg)

Mirascope

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
    # Output: Patrick Rothfuss
else:
    print(response.content)
```

Official SDK

```
import json

from openai import OpenAI

client = OpenAI()

def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"

def identify_author(book: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Who wrote {book}"}],
        tools=[\
            {\
                "function": {\
                    "name": "get_book_author",\
                    "description": "Returns the author of the book with the given title.",\
                    "parameters": {\
                        "properties": {"title": {"type": "string"}},\
                        "required": ["title"],\
                        "type": "object",\
                    },\
                },\
                "type": "function",\
            }\
        ],
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        if tool_calls[0].function.name == "get_book_author":
            return get_book_author(**json.loads(tool_calls[0].function.arguments))
    return str(completion.choices[0].message.content)

author = identify_author("The Name of the Wind")
print(author)
```

In this example we:

1. Define the `GetBookAuthor`/ `get_book_author` tool (a dummy method for the example)
2. Set the `tools` argument in the `call` decorator to give the LLM access to the tool.
3. We call `identify_author`, which automatically generates the corresponding provider-specific tool schema under the hood.
4. Check if the response from `identify_author` contains a tool, which is the `BaseTool` instance constructed from the underlying tool call

   - If yes, we call the constructed tool's `call` method and print its output. This calls the tool with the arguments provided by the LLM.
   - If no, we print the content of the response (assuming no tool was called).

The core idea to understand here is that the LLM is asking us to call the tool on its behalf with arguments that it has provided. In the above example, the LLM chooses to call the tool to get the author rather than relying on its world knowledge.

This is particularly important for buildling applications with access to live information and external systems.

For the purposes of this example we are showing just a single tool call. Generally, you would then give the tool call's output back to the LLM and make another call so the LLM can generate a response based on the output of the tool. We cover this in more detail in the section on [Agents](https://mirascope.com/docs/mirascope/learn/agents)

### Accessing Original Tool Call [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#accessing-original-tool-call)

The `BaseTool` instances have a `tool_call` property for accessing the original LLM tool call.

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
    # Output: Patrick Rothfuss
    print(f"Original tool call: {tool.tool_call}")
else:
    print(response.content)
```

## Supported Field Types [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#supported-field-types)

While Mirascope provides a consistent interface, type support varies among providers:

| Type | OpenAI | Anthropic | Google | Groq | xAI | Mistral | Cohere |
| --- | --- | --- | --- | --- | --- | --- | --- |
| str | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| int | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| float | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| bool | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| bytes | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| list | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| set | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| tuple | — | ✓ | — | ✓ | — | ✓ | ✓ |
| dict | — | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| Literal/Enum | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| BaseModel | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Nested ($def) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |

_Legend: ✓ (Supported), — (Not Supported)_

Consider provider-specific capabilities when working with advanced type structures. Even for supported types, LLM outputs may sometimes be incorrect or of the wrong type. In such cases, prompt engineering or error handling (like [retries](https://mirascope.com/docs/mirascope/learn/retries) and [reinserting validation errors](https://mirascope.com/docs/mirascope/learn/retries#error-reinsertion)) may be necessary.

## Parallel Tool Calls [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#parallel-tool-calls)

In certain cases the LLM will ask to call multiple tools in the same response. Mirascope makes calling all such tools simple:

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_authors(books: list[str]) -> str:
    return f"Who wrote {books}?"

response = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
if tools := response.tools:
    for tool in tools:
        print(tool.call())
else:
    print(response.content)
```

If your tool calls are I/O-bound, it's often worth writing [async tools](https://mirascope.com/docs/mirascope/learn/async#async-tools) so that you can run all of the tools calls [in parallel](https://mirascope.com/docs/mirascope/learn/async#parallel-async-calls) for better efficiency.

## Streaming Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#streaming-tools)

Mirascope supports streaming responses with tools, which is useful for long-running tasks or real-time updates:

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor], stream=True)
def identify_authors(books: list[str]) -> str:
    return f"Who wrote {books}?"

stream = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
for chunk, tool in stream:
    if tool:
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
```

When are tools returned?

When we identify that a tool is being streamed, we will internally reconstruct the tool from the streamed response. This means that the tool won't be returned until the full tool has been streamed and reconstructed on your behalf.

Not all providers support streaming tools

Currently only OpenAI, Anthropic, Mistral, and Groq support streaming tools. All other providers will always return `None` for tools.

If you think we're missing any, let us know!

### Streaming Partial Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#streaming-partial-tools)

You can also stream intermediate partial tools and their deltas (rather than just the fully constructed tool) by setting `stream={"partial_tools": True}`:

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[GetBookAuthor],
    stream={"partial_tools": True},
)
def identify_authors(books: list[str]) -> str:
    return f"Who wrote {books}?"

stream = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
for chunk, tool in stream:
    if tool:
        if tool.delta is not None:  # partial tool
            print(tool.delta)
        else:
            print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
```

## Tool Message Parameters [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#tool-message-parameters)

Calling tools and inserting their outputs into subsequent LLM API calls in a loop in the most basic form of an agent. While we cover this briefly here, we recommend reading the section on [Agents](https://mirascope.com/docs/mirascope/learn/agents) for more details and examples.

Generally the next step after the LLM returns a tool call is for you to call the tool on its behalf and supply the output in a subsequent call.

Let's take a look at a basic example of this:

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseMessageParam, BaseTool, Messages, llm

class GetBookAuthor(BaseTool):
    title: str

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_author(book: str, history: list[BaseMessageParam]) -> Messages.Type:
    messages = [*history]
    if book:
        messages.append(Messages.User(f"Who wrote {book}?"))
    return messages

history = []
response = identify_author("The Name of the Wind", history)
history += [response.user_message_param, response.message_param]
while tool := response.tool:
    tools_and_outputs = [(tool, tool.call())]
    history += response.tool_message_params(tools_and_outputs)
    response = identify_author("", history)
    history.append(response.message_param)
print(response.content)
# Output: The Name of the Wind was written by Patrick Rothfuss.
```

In this example we:

1. Add `history` to maintain the messages across multiple calls to the LLM.
2. Loop until the response no longer has tools calls.
3. While there are tool calls, call the tools, append their corresponding message parameters to the history, and make a subsequent call with an empty query and updated history. We use an empty query because the original user message is already included in the history.
4. Print the final response content once the LLM is done calling tools.

## Validation and Error Handling [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#validation-and-error-handling)

Since `BaseTool` is a subclass of Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), they are validated on construction, so it's important that you handle potential `ValidationError`'s for building more robust applications:

BaseToolFunction

ShorthandTemplate

```
from typing import Annotated

from mirascope import BaseTool, llm
from pydantic import AfterValidator, Field, ValidationError

def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: Annotated[str, AfterValidator(is_upper)] = Field(
        ..., description="The title of the book."
    )

    def call(self) -> str:
        if self.title == "THE NAME OF THE WIND":
            return "Patrick Rothfuss"
        elif self.title == "MISTBORN: THE FINAL EMPIRE":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

response = identify_author("The Name of the Wind")
try:
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)
except ValidationError as e:
    print(e)
    # > 1 validation error for GetBookAuthor
    #   title
    #     Assertion failed, Must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.8/v/assertion_error
```

In this example we've added additional validation, but it's important that you still handle `ValidationError`'s even with standard tools since they are still `BaseModel` instances and will validate the field types regardless.

## Few-Shot Examples [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#few-shot-examples)

Just like with [Response Models](https://mirascope.com/docs/mirascope/learn/response_models#few-shot-examples), you can add few-shot examples to your tools:

BaseToolFunction

ShorthandTemplate

```
from mirascope import BaseTool, llm
from pydantic import ConfigDict, Field

class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(
        ...,
        description="The title of the book.",
        examples=["The Name of the Wind"],
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"title": "The Name of the Wind"}]}
    )

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[GetBookAuthor])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
else:
    print(response.content)
```

Both approaches will result in the same tool schema with examples included. The function approach gets automatically converted to use Pydantic fields internally, making both methods equivalent in terms of functionality.

Field level examples in both styles

## ToolKit [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#toolkit)

API Documentation

The `BaseToolKit` class enables:

- Organiziation of a group of tools under a single namespace.
  - This can be useful for making it clear to the LLM when to use certain tools over others. For example, you could namespace a set of tools under "file\_system" to indicate that those tools are specifically for interacting with the file system.
- Dynamic tool definitions.
  - This can be useful for generating tool definitions that are dependent on some input or state. For example, you may want to update the description of tools based on an argument of the call being made.

ShorthandTemplate

```
from mirascope import (
    BaseDynamicConfig,
    BaseToolKit,
    Messages,
    llm,
)
from mirascope.core import toolkit_tool

class BookTools(BaseToolKit):
    __namespace__ = "book_tools"

    reading_level: str

    @toolkit_tool
    def suggest_author(self, author: str) -> str:
        """Suggests an author for the user to read based on their reading level.

        User reading level: {self.reading_level} # [!code highlight]
        Author you suggest must be appropriate for the user's reading level.
        """
        return f"I would suggest you read some books by {author}"

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_author(genre: str, reading_level: str) -> BaseDynamicConfig:
    toolkit = BookTools(reading_level=reading_level)
    return {
        "tools": toolkit.create_tools(),
        "messages": [Messages.User(f"What {genre} author should I read?")],
    }

response = recommend_author("fantasy", "beginner")
if tool := response.tool:
    print(tool.call())
    # Output: I would suggest you read some books by J.K. Rowling

response = recommend_author("fantasy", "advanced")
if tool := response.tool:
    print(tool.call())
    # Output: I would suggest you read some books by Brandon Sanderson
```

In this example we:

1. Create a `BookTools` toolkit
2. We set `__namespace__` equal to "book\_tools"
3. We define the `reading_level` state of the toolkit
4. We define the `suggest_author` tool and mark it with `@toolkit_tool` to identify the method as a tool of the toolkit
5. We use the `{self.reading_level}` template variable in the description of the tool.
6. We create the toolkit with the `reading_level` argument.
7. We call `create_tools` to generate the toolkit's tools. This will generate the tools on every call, ensuring that the description correctly includes the provided reading level.
8. We call `recommend_author` with a "beginner" reading level, and the LLM calls the `suggest_author` tool with its suggested author.
9. We call `recommend_author` again but with "advanced" reading level, and again the LLM calls the `suggest_author` tool with its suggested author.

The core concept to understand here is that the `suggest_author` tool's description is dynamically generated on each call to `recommend_author` through the toolkit.

This is why the "beginner" recommendation and "advanced" recommendations call the `suggest_author` tool with authors befitting the reading level of each call.

## Pre-Made Tools and ToolKits [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#pre-made-tools-and-toolkits)

Mirascope provides several pre-made tools and toolkits to help you get started quickly:

Pre-made tools and toolkits require installing the dependencies listed in the "Dependencies" column for each tool/toolkit.

For example:

```
pip install httpx  # For HTTPX tool
pip install requests  # For Requests tool
```

### Pre-Made Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#pre-made-tools)

API Documentation

| Tool | Primary Use | Dependencies | Key Features | Characteristics |
| --- | --- | --- | --- | --- |
| [`DuckDuckGoSearch`](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo) | Web Searching | [`duckduckgo-search`](https://pypi.org/project/duckduckgo-search/) | • Multiple query support<br>• Title/URL/snippet extraction<br>• Result count control<br>• Automated formatting | • Privacy-focused search<br>• Async support (AsyncDuckDuckGoSearch)<br>• Automatic filtering<br>• Structured results |
| [`HTTPX`](https://mirascope.com/docs/mirascope/api/tools/web/httpx) | Advanced HTTP Requests | [`httpx`](https://pypi.org/project/httpx/) | • Full HTTP method support (GET/POST/PUT/DELETE)<br>• Custom header support<br>• File upload/download<br>• Form data handling | • Async support (AsyncHTTPX)<br>• Configurable timeouts<br>• Comprehensive error handling<br>• Redirect control |
| [`ParseURLContent`](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content) | Web Content Extraction | [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/), [`httpx`](https://pypi.org/project/httpx/) | • HTML content fetching<br>• Main content extraction<br>• Element filtering<br>• Text normalization | • Automatic cleaning<br>• Configurable parser<br>• Timeout settings<br>• Error handling |
| [`Requests`](https://mirascope.com/docs/mirascope/api/tools/web/requests) | Simple HTTP Requests | [`requests`](https://pypi.org/project/requests/) | • Basic HTTP methods<br>• Simple API<br>• Response text retrieval<br>• Basic authentication | • Minimal configuration<br>• Intuitive interface<br>• Basic error handling<br>• Lightweight implementation |

Example using DuckDuckGoSearch:

Basic UsageCustom Config

ShorthandTemplate

```
from mirascope import llm
from mirascope.tools import DuckDuckGoSearch

@llm.call(provider="openai", model="gpt-4o-mini", tools=[DuckDuckGoSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"

response = research("fantasy")
if tool := response.tool:
    print(tool.call())
```

### Pre-Made ToolKits [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#pre-made-toolkits)

API Documentation

| ToolKit | Primary Use | Dependencies | Tools and Features | Characteristics |
| --- | --- | --- | --- | --- |
| [`FileSystemToolKit`](https://mirascope.com/docs/mirascope/api/tools/system/file_system) | File System Operations | None | • ReadFile: File content reading<br>• WriteFile: Content writing<br>• ListDirectory: Directory listing<br>• CreateDirectory: Directory creation<br>• DeleteFile: File deletion | • Path traversal protection<br>• File size limits<br>• Extension validation<br>• Robust error handling<br>• Base directory isolation |
| [`DockerOperationToolKit`](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation) | Code & Command Execution | [`docker`](https://pypi.org/project/docker/), [`docker engine`](https://docs.docker.com/engine/install/) | • ExecutePython: Python code execution with optional package installation<br>• ExecuteShell: Shell command execution | • Docker container isolation<br>• Memory limits<br>• Network control<br>• Security restrictions<br>• Resource cleanup |

Example using FileSystemToolKit:

ShorthandTemplate

```
from pathlib import Path

from mirascope import BaseDynamicConfig, Messages, llm
from mirascope.tools import FileSystemToolKit

@llm.call(provider="openai", model="gpt-4o-mini")
def write_blog_post(topic: str, output_file: Path) -> BaseDynamicConfig:
    toolkit = FileSystemToolKit(base_directory=output_file.parent)
    return {
        "messages": [\
            Messages.User(\
                content=f"Write a blog post about '{topic}' as a '{output_file.name}'."\
            )\
        ],
        "tools": toolkit.create_tools(),
    }

response = write_blog_post("machine learning", Path("introduction.html"))
if tool := response.tool:
    result = tool.call()
    print(result)
```

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/tools\#next-steps)

Tools can significantly extend LLM capabilities, enabling more interactive and dynamic applications. We encourage you to explore and experiment with tools to enhance your projects and the find the best fit for your specific needs.

Mirascope hopes to provide a simple and clean interface that is both easy to learn and easy to use; however, we understand that LLM tools can be a difficult concept regardless of the supporting tooling.

Next, we recommend learning about how to build [Agents](https://mirascope.com/docs/mirascope/learn/agents) that take advantage of these tools.

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