---
url: "https://mirascope.com/docs/mirascope/learn/chaining"
title: "Chaining | Mirascope"
---

# Chaining [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#chaining)

If you haven't already, we recommend first reading the section on [Calls](https://mirascope.com/docs/mirascope/learn/calls)

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. This approach is particularly useful for breaking down complex problems into smaller, manageable steps.

Before diving into Mirascope's implementation, let's understand what chaining means in the context of LLM applications:

1. **Problem Decomposition**: Breaking a complex task into smaller, manageable steps.
2. **Sequential Processing**: Executing these steps in a specific order, where the output of one step becomes the input for the next.
3. **Data Flow**: Passing information between steps to build up a final result.

## Basic Usage and Syntax [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#basic-usage-and-syntax)

### Function Chaining [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#function-chaining)

Mirascope is designed to be Pythonic. Since calls are defined as functions, chaining them together is as simple as chaining the function calls as you would normally:

ShorthandTemplate

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

One benefit of this approach is that you can chain your calls together any which way since they are just functions. You can then always wrap these functional chains in a parent function that operates as the single call to the chain.

### Nested Chains [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#nested-chains)

In some cases you'll want to prompt engineer an entire chain rather than just chaining together individual calls. You can do this simply by calling the subchain inside the function body of the parent:

ShorthandTemplate

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"

@llm.call(provider="openai", model="gpt-4o-mini")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary.content}"

response = summarize_and_translate("Long English text here...", "french")
print(response.content)
```

We recommend using nested chains for better observability when using tracing tools or applications.

Improved tracing through computed fields

## Advanced Chaining Techniques [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#advanced-chaining-techniques)

There are many different ways to chain calls together, often resulting in breakdowns and flows that are specific to your task.

Here are a few examples:

ConditionalParallelIterative

```
from enum import Enum

from mirascope import BaseDynamicConfig, llm, prompt_template

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Sentiment)
def sentiment_classifier(review: str) -> str:
    return f"Is the following review positive or negative? {review}"

@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Your task is to respond to a review.
    The review has been identified as {sentiment}.
    Please write a {conditional_review_prompt}.

    USER: Write a response for the following review: {review}
    """
)
def review_responder(review: str) -> BaseDynamicConfig:
    sentiment = sentiment_classifier(review=review)
    conditional_review_prompt = (
        "thank you response for the review."
        if sentiment == Sentiment.POSITIVE
        else "response addressing the review."
    )
    return {
        "computed_fields": {
            "conditional_review_prompt": conditional_review_prompt,
            "sentiment": sentiment,
        }
    }

positive_review = "This tool is awesome because it's so flexible!"
response = review_responder(review=positive_review)
print(response)
print(response.dynamic_config)
```

[Response Models](https://mirascope.com/docs/mirascope/learn/response_models) are a great way to add more structure to your chains, and [parallel async calls](https://mirascope.com/docs/mirascope/learn/async#parallel-async-calls) can be particularly powerful for making your chains more efficient.

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/learn/chaining\#next-steps)

By mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and observability.

Next, we recommend taking a look at the [Response Models](https://mirascope.com/docs/mirascope/learn/response_models) documentation, which shows you how to generate structured outputs.

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