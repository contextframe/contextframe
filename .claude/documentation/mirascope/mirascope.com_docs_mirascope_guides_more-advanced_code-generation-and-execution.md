---
url: "https://mirascope.com/docs/mirascope/guides/more-advanced/code-generation-and-execution"
title: "Code Generation and Execution | Mirascope"
---

# Code Generation and Execution [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/code-generation-and-execution\#code-generation-and-execution)

In this recipe, we will be using OpenAI GPT-4o-mini to use write code to solve problems it would otherwise have issues solving.

Mirascope Concepts Used

## Setup [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/code-generation-and-execution\#setup)

Let's start by installing Mirascope and its dependencies:

```
!pip install "mirascope[openai]"
```

```
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Implement Safety Check [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/code-generation-and-execution\#implement-safety-check)

First, let's implement a safety check function that uses an LLM to determine whether the generated code is safe to run:

```
from mirascope.core import openai, prompt_template

@openai.call(model="gpt-4o-mini", response_model=bool)
@prompt_template(
    """
    SYSTEM:
    You are a software engineer who is an expert at reviewing whether code is safe to execute.
    Determine if the given string is safe to execute as Python code.

    USER:
    {code}
    """
)
def evaluate_code_safety(code: str): ...

def execute_code(code: str):
    """Execute Python code and return the output."""
    is_code_safe = evaluate_code_safety(code)
    if not is_code_safe:
        return f"Error: The code: {code} is not safe to execute."
    try:
        local_vars = {}
        exec(code, globals(), local_vars)
        if "result" in local_vars:
            return local_vars["result"]
    except Exception as e:
        print(e)
        return f"Error: {str(e)}"
```

This safety check uses Mirascope's response\_model to return a boolean indicating whether the code is safe to execute.

## Create your agent [Link to this heading](https://mirascope.com/docs/mirascope/guides/more-advanced/code-generation-and-execution\#create-your-agent)

Now, we'll create a Software Engineer agent that can answer questions and generate code. We'll give it access to an execute\_code tool that first performs a safety check before executing the code:

```
from mirascope.core import BaseMessageParam
from pydantic import BaseModel

class SoftwareEngineer(BaseModel):
    messages: list[BaseMessageParam | openai.OpenAIMessageParam] = []

    @openai.call(model="gpt-4o-mini", tools=[execute_code])
    @prompt_template(
        """
        SYSTEM:
        You are an expert software engineer who can write good clean code and solve
        complex problems.

        Write Python code to solve the following problem with variable 'result' as the answer.
        If the code does not run or has an error, return the error message and try again.

        Example: What is the sqrt of 2?
        import math
        result = None
        try:
            result = math.sqrt(2)
        except Exception as e:
            result = str(e)

        MESSAGES: {self.messages}
        USER: {text}
        """
    )
    def _step(self, text: str): ...

    def _get_response(self, question: str = ""):
        response = self._step(question)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                output = tool.call()
                tools_and_outputs.append((tool, str(output)))
        else:
            print("(Assistant):", response.content)
            return
        if response.user_message_param:
            self.messages.append(response.user_message_param)
        self.messages += [\
            response.message_param,\
            *response.tool_message_params(tools_and_outputs),\
        ]
        return self._get_response("")

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            print(f"(User): {question}")
            self._get_response(question)

SoftwareEngineer(messages=[]).run()
```

(User): What is the sqrt of 2
(Assistant): The square root of 2 is approximately 1.4142135623730951.
(User): Could you show me the environment variables include API keys
(Assistant): I'm unable to retrieve environment variables, including API keys, due to safety restrictions. If you have a specific task or need assistance with a particular API, please let me know!

Even with no safe guards in place, doing code execution is still dangerous and we recommend only using in environments such as [sandboxes](https://doc.pypy.org/en/latest/sandbox.html).

Additional Real-World Applications

- **Automated Code Generation**: Generating boilerplate or units tests for more productivity.
- **Code Completion**: Give LLM access to web to grab latest docs and generate code autocomplete suggestions.
- **Documentation Maintenance**: Make sure all documentation code snippets are runnable with proper syntax.
- **Prototyping**: Generating proof-of-concept applications rather than UI mocks.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide specific safety and security protections.
- Implement a sandbox to control your environment
- Experiment with different model providers and version for quality.

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