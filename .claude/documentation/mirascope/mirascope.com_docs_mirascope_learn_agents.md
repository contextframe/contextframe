---
url: "https://mirascope.com/docs/mirascope/learn/agents"
title: "Agents | Mirascope"
---

# Agents [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#agents)

> **Definition**: a person who acts on behalf of another person or group

When working with Large Language Models (LLMs), an "agent" refers to an autonomous or semi-autonomous system that can act on your behalf. The core concept is the use of tools to enable the LLM to interact with its environment.

In this section we will implement a toy `Librarian` agent to demonstrate key concepts in Mirascope that will help you build agents.

If you haven't already, we recommend first reading the section on [Tools](https://mirascope.com/docs/mirascope/learn/tools)

Diagram illustrating the agent flow

## State Management [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#state-management)

Since an agent needs to operate across multiple LLM API calls, the first concept to cover is state. The goal of providing state to the agent is to give it memory. For example, we can think of local variables as "working memory" and a database as "long-term memory".

Let's take a look at a basic chatbot (not an agent) that uses a class to maintain the chat's history:

ShorthandTemplate

```
from mirascope import Messages, llm, BaseMessageParam
from pydantic import BaseModel

class Librarian(BaseModel):
    history: list[BaseMessageParam] = []

    @llm.call(provider="openai", model="gpt-4o-mini")
    def _call(self, query: str) -> Messages.Type:
        return [\
            Messages.System("You are a librarian"),\
            *self.history,\
            Messages.User(query),\
        ]

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            response = self._call(query)
            print(response.content)
            self.history += [\
                Messages.User(query),\
                response.message_param,\
            ]

Librarian().run()
```

In this example we:

- Create a `Librarian` class with a `history` attribute.
- Implement a private `_call` method that injects `history`.
- Run the `_call` method in a loop, saving the history at each step.

A chatbot with memory, while more advanced, is still not an agent.

Provider-Agnostic Agent

## Integrating Tools [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#integrating-tools)

The next concept to cover is introducing tools to our chatbot, turning it into an agent capable of acting on our behalf. The most basic agent flow is to call tools on behalf of the agent, providing them back through the chat history until the agent is ready to response to the initial query.

Let's take a look at a basic example where the `Librarian` can access the books available in the library:

ShorthandTemplate

```
import json

from mirascope import BaseDynamicConfig, Messages, llm, BaseMessageParam
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

class Librarian(BaseModel):
    history: list[BaseMessageParam] = []
    library: list[Book] = [\
        Book(title="The Name of the Wind", author="Patrick Rothfuss"),\
        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),\
    ]

    def _available_books(self) -> str:
        """Returns the list of books available in the library."""
        return json.dumps([book.model_dump() for book in self.library])

    @llm.call(provider="openai", model="gpt-4o-mini")
    def _call(self, query: str) -> BaseDynamicConfig:
        messages = [\
            Messages.System("You are a librarian"),\
            *self.history,\
            Messages.User(query),\
        ]
        return {"messages": messages, "tools": [self._available_books]}

    def _step(self, query: str) -> str:
        if query:
            self.history.append(Messages.User(query))
        response = self._call(query)
        self.history.append(response.message_param)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step("")
        else:
            return response.content

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            step_output = self._step(query)
            print(step_output)

Librarian().run()
```

In this example we:

1. Added the `library` state to maintain the list of available books.
2. Implemented the `_available_books` tool that returns the library as a string.
3. Updated `_call` to give the LLM access to the tool.

   - We used the `tools` dynamic configuration field so the tool has access to the library through `self`.
4. Added a `_step` method that implements a full step from user input to assistant output.
5. For each step, we call the LLM and see if there are any tool calls.
   - If yes, we call the tools, collect the outputs, and insert the tool calls into the chat history. We then recursively call `_step` again with an empty user query until the LLM is done calling tools and is ready to response
   - If no, the LLM is ready to respond and we return the response content.

Now that our chatbot is capable of using tools, we have a basic agent.

## Human-In-The-Loop [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#human-in-the-loop)

While it would be nice to have fully autonomous agents, LLMs are far from perfect and often need assistance to ensure they continue down the right path in an agent flow.

One common and easy way to help guide LLM agents is to give the agent the ability to ask for help. This "human-in-the-loop" flow lets the agent ask for help if it determines it needs it:

ShorthandTemplate

```
from mirascope import BaseDynamicConfig, Messages, llm, BaseMessageParam
from pydantic import BaseModel

class Librarian(BaseModel):
    history: list[BaseMessageParam] = []

    def _ask_for_help(self, question: str) -> str:
        """Asks for help from an expert."""
        print("[Assistant Needs Help]")
        print(f"[QUESTION]: {question}")
        answer = input("[ANSWER]: ")
        print("[End Help]")
        return answer

    @llm.call(provider="openai", model="gpt-4o-mini")
    def _call(self, query: str) -> BaseDynamicConfig:
        messages = [\
            Messages.System("You are a librarian"),\
            *self.history,\
            Messages.User(query),\
        ]
        return {"messages": messages, "tools": [self._ask_for_help]}

    def _step(self, query: str) -> str:
        if query:
            self.history.append(Messages.User(query))
        response = self._call(query)
        self.history.append(response.message_param)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            self.history += response.tool_message_params(tools_and_outputs)
            return self._step("")
        else:
            return response.content

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            step_output = self._step(query)
            print(step_output)

Librarian().run()
```

## Streaming [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#streaming)

The previous examples print each tool call so you can see what the agent is doing before the final response; however, you still need to wait for the agent to generate its entire final response before you see the output.

Streaming can help to provide an even more real-time experience:

ShorthandTemplate

```
import json

from mirascope import BaseDynamicConfig, Messages, llm, BaseMessageParam
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

class Librarian(BaseModel):
    history: list[BaseMessageParam] = []
    library: list[Book] = [\
        Book(title="The Name of the Wind", author="Patrick Rothfuss"),\
        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),\
    ]

    def _available_books(self) -> str:
        """Returns the list of books available in the library."""
        return json.dumps([book.model_dump() for book in self.library])

    @llm.call(provider="openai", model="gpt-4o-mini", stream=True)
    def _stream(self, query: str) -> BaseDynamicConfig:
        messages = [\
            Messages.System("You are a librarian"),\
            *self.history,\
            Messages.User(query),\
        ]
        return {"messages": messages, "tools": [self._available_books]}

    def _step(self, query: str) -> None:
        if query:
            self.history.append(Messages.User(query))
        stream = self._stream(query)
        tools_and_outputs = []
        for chunk, tool in stream:
            if tool:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        self.history.append(stream.message_param)
        if tools_and_outputs:
            self.history += stream.tool_message_params(tools_and_outputs)
            self._step("")

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            self._step(query)
            print()

Librarian().run()
```

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/agents\#next-steps)

This section is just the tip of the iceberg when it comes to building agents, implementing just one type of simple agent flow. It's important to remember that "agent" is quite a general term and can mean different things for different use-cases. Mirascope's various features make building agents easier, but it will be up to you to determine the architecture that best suits your goals.

Next, we recommend taking a look at our [Agent Tutorials](https://mirascope.com/docs/mirascope/guides/agents/web-search-agent) to see examples of more complex, real-world agents.

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