---
url: "https://mirascope.com/docs/mirascope/learn/output_parsers"
title: "Output Parsers | Mirascope"
---

# Output Parsers [Link to this heading](https://mirascope.com/docs/mirascope/learn/output_parsers\#output-parsers)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

Output Parsers in Mirascope provide a flexible way to process and structure the raw output from Large Language Models (LLMs). They allow you to transform the LLM's response into a more usable format, enabling easier integration with your application logic and improving the overall reliability of your LLM-powered features.

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/output_parsers\#basic-usage-and-syntax)

API Documentation

Output Parsers are functions that take the call response object as input and return an output of a specified type. When you supply an output parser to a `call` decorator, it modifies the return type of the decorated function to match the output type of the parser.

Let's take a look at a basic example:

ShorthandTemplate

```
from mirascope import llm

def parse_recommendation(response: llm.CallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)

@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_recommendation)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book. Output only Title by Author"

print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
```

## Additional Examples [Link to this heading](https://mirascope.com/docs/mirascope/learn/output_parsers\#additional-examples)

There are many different ways to structure and parse LLM outputs, ranging from XML parsing to using regular expressions.

Here are a few examples:

Regular ExpressionXMLJSON Mode

```
import re

from mirascope import llm, prompt_template

def parse_cot(response: llm.CallResponse) -> str:
    pattern = r"<thinking>.*?</thinking>.*?<o>(.*?)</o>"
    match = re.search(pattern, response.content, re.DOTALL)
    if not match:
        return response.content
    return match.group(1).strip()

@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_cot)
@prompt_template(
    """
    First, output your thought process in <thinking> tags. # [!code highlight]
    Then, provide your final output in <o> tags. # [!code highlight]

    Question: {question}
    """
)
def chain_of_thought(question: str): ...

question = "Roger has 5 tennis balls. He buys 2 cans of 3. How many does he have now?"
output = chain_of_thought(question)
print(output)
```

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/output_parsers\#next-steps)

By leveraging Output Parsers effectively, you can create more robust and reliable LLM-powered applications, ensuring that the raw model outputs are transformed into structured data that's easy to work with in your application logic.

Next, we recommend taking a look at the section on [Tools](https://mirascope.com/docs/mirascope/learn/tools) to learn how to extend the capabilities of LLMs with custom functions.

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