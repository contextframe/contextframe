---
url: "https://mirascope.com/docs/mirascope/learn/async"
title: "Async | Mirascope"
---

# Async [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#async)

Asynchronous programming is a crucial concept when building applications with LLMs (Large Language Models) using Mirascope. This feature allows for efficient handling of I/O-bound operations (e.g., API calls), improving application responsiveness and scalability. Mirascope utilizes the [asyncio](https://docs.python.org/3/library/asyncio.html) library to implement asynchronous processing.

Best Practices

- **Use asyncio for I/O-bound tasks**: Async is most beneficial for I/O-bound operations like API calls. It may not provide significant benefits for CPU-bound tasks.
- **Avoid blocking operations**: Ensure that you're not using blocking operations within async functions, as this can negate the benefits of asynchronous programming.
- **Consider using connection pools**: When making many async requests, consider using connection pools to manage and reuse connections efficiently.
- **Be mindful of rate limits**: While async allows for concurrent requests, be aware of API rate limits and implement appropriate throttling if necessary.
- **Use appropriate timeouts**: Implement timeouts for async operations to prevent hanging in case of network issues or unresponsive services.
- **Test thoroughly**: Async code can introduce subtle bugs. Ensure comprehensive testing of your async implementations.
- **Leverage async context managers**: Use async context managers (async with) for managing resources that require setup and cleanup in async contexts.

Diagram illustrating the flow of asynchronous processing

## Key Terms [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#key-terms)

- `async`: Keyword used to define a function as asynchronous
- `await`: Keyword used to wait for the completion of an asynchronous operation
- `asyncio`: Python library that supports asynchronous programming

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#basic-usage-and-syntax)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

To use async in Mirascope, simply define the function as async and use the `await` keyword when calling it. Here's a basic example:

ShorthandTemplate

```
import asyncio

from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

async def main():
    response = await recommend_book("fantasy")
    print(response.content)

asyncio.run(main())
```

In this example we:

1. Define `recommend_book` as an asynchronous function.
2. Create a `main` function that calls `recommend_book` and awaits it.
3. Use `asyncio.run(main())` to start the asynchronous event loop and run the main function.

## Parallel Async Calls [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#parallel-async-calls)

One of the main benefits of asynchronous programming is the ability to run multiple operations concurrently. Here's an example of making parallel async calls:

ShorthandTemplate

```
import asyncio

from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

async def main():
    genres = ["fantasy", "scifi", "mystery"]
    tasks = [recommend_book(genre) for genre in genres]
    results = await asyncio.gather(*tasks)

    for genre, response in zip(genres, results):
        print(f"({genre}):\n{response.content}\n")

asyncio.run(main())
```

We are using `asyncio.gather` to run and await multiple asynchronous tasks concurrently, printing the results for each task one all are completed.

## Async Streaming [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#async-streaming)

If you haven't already, we recommend first reading the section on [Streams](https://mirascope.com/docs/mirascope/learn/streams)

Streaming with async works similarly to synchronous streaming, but you use `async for` instead of a regular `for` loop:

ShorthandTemplate

```
import asyncio

from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

async def main():
    stream = await recommend_book("fantasy")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)

asyncio.run(main())
```

## Async Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#async-tools)

If you haven't already, we recommend first reading the section on [Tools](https://mirascope.com/docs/mirascope/learn/tools)

When using tools asynchronously, you can make the `call` method of a tool async:

ShorthandTemplate

```
import asyncio

from mirascope import BaseTool, llm

class FormatBook(BaseTool):
    title: str
    author: str

    async def call(self) -> str:
        # Simulating an async API call
        await asyncio.sleep(1)
        return f"{self.title} by {self.author}"

@llm.call(provider="openai", model="gpt-4o-mini", tools=[FormatBook])
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

async def main():
    response = await recommend_book("fantasy")
    if tool := response.tool:
        if isinstance(tool, FormatBook):
            output = await tool.call()
            print(output)
    else:
        print(response.content)

asyncio.run(main())
```

It's important to note that in this example we use `isinstance(tool, FormatBook)` to ensure the `call` method can be awaited safely. This also gives us proper type hints and editor support.

## Custom Client [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#custom-client)

When using custom clients with async calls, it's crucial to use the asynchronous version of the client. You can provide the async client either through the decorator or dynamic configuration:

### Decorator Parameter [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#decorator-parameter)

ShorthandTemplate

```
from mirascope.core import openai
from openai import AsyncOpenAI

@openai.call("gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
```

### Dynamic Configuration [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#dynamic-configuration)

ShorthandTemplate

```
from mirascope.core import openai, Messages
from openai import AsyncOpenAI

@openai.call("gpt-4o-mini")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncOpenAI(),
    }
```

Synchronous vs Asynchronous Clients

Make sure to use the appropriate asynchronous client class (e.g., `AsyncOpenAI` instead of `OpenAI`) when working with async functions. Using a synchronous client in an async context can lead to blocking operations that defeat the purpose of async programming.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/async\#next-steps)

By leveraging these async features in Mirascope, you can build more efficient and responsive applications, especially when working with multiple LLM calls or other I/O-bound operations.

This section concludes the core functionality Mirascope supports. If you haven't already, we recommend taking a look at any previous sections you've missed to learn about what you can do with Mirascope.

You can also check out the section on [Provider-Specific Features](https://mirascope.com/docs/mirascope/learn/provider-specific/openai) to learn about how to use features that only certain providers support, such as OpenAI's structured outputs.

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