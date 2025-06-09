---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/mixture-of-reasoning"
title: "Mixture of Reasoning: Enhancing LLM Performance with Multiple Techniques | Mirascope"
---

# Mixture of Reasoning: Enhancing LLM Performance with Multiple Techniques [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/mixture-of-reasoning\#mixture-of-reasoning-enhancing-llm-performance-with-multiple-techniques)

Mixture of Reasoning is a prompt engineering technique where you set up multiple calls, each utilizing a different prompt engineering technique. This approach is best when you want to be able to handle a wide variety of responses, or have a variety of techniques that you have found to be successful for responding to a type of prompt.

Mirascope Concepts Used

Background

In the [original paper](https://users.umiacs.umd.edu/~jbg/docs/2023_findings_more.pdf), a trained classifier is used to determine the best answer, but since we do not have access to that, we will use an LLM to evaluate the best answer instead. To get a clean separation between the reasoning and the actual output, we'll use `response_model` in our final evaluation call.

## Implementation [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/mixture-of-reasoning\#implementation)

Let's implement the Mixture of Reasoning technique using Mirascope:

```
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Answer this question, thinking step by step.
    {query}
    """
)
def cot_call(query: str): ...

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {query}
    It's very important to my career.
    """
)
def emotion_prompting_call(query: str): ...

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {query}
    Rephrase and expand the question, and respond.
    """
)
def rar_call(query: str): ...

class BestResponse(BaseModel):
    best_response: str = Field(
        ..., description="The best response of the options given, verbatim"
    )
    reasoning: str = Field(
        ...,
        description="""A short description of why this is the best response to
        the query, along with reasons why the other answers were worse.""",
    )

@openai.call(model="gpt-4o-mini", response_model=BestResponse)
@prompt_template(
    """
    Here is a query: {query}

    Evaluate the following responses from LLMs and decide which one
    is the best based on correctness, fulfillment of the query, and clarity:

    Response 1:
    {cot_response}

    Response 2:
    {emotion_prompting_response}

    Response 3:
    {rar_response}
    """
)
def mixture_of_reasoning(query: str) -> openai.OpenAIDynamicConfig:
    cot_response = cot_call(query=query)
    emotion_prompting_response = emotion_prompting_call(query=query)
    rar_response = rar_call(query=query)

    return {
        "computed_fields": {
            "cot_response": cot_response,
            "emotion_prompting_response": emotion_prompting_response,
            "rar_response": rar_response,
        }
    }

prompt = "What are the side lengths of a rectangle with area 8 and perimeter 12?"

best_response = mixture_of_reasoning(prompt)
print(best_response.best_response)
print(best_response.reasoning)
```

This implementation consists of several key components:

1. Three different prompt engineering techniques:
   - `cot_call`: [Chain of Thought reasoning](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/chain-of-thought)
   - `emotion_prompting_call`: [Emotion prompting](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/emotion-prompting)
   - `rar_call`: [Rephrase and Respond](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond)
2. A `BestResponse` model to structure the output of the final evaluation.

3. The `mixture_of_reasoning` function, which:
   - Calls each of the three prompt engineering techniques
   - Uses dynamic configuration to pass the responses to the final evaluation
   - Returns the best response and reasoning using the `BestResponse` model

## Benefits and Considerations [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/mixture-of-reasoning\#benefits-and-considerations)

The Mixture of Reasoning implementation offers several advantages:

1. Improved ability to handle a wide variety of queries by leveraging multiple prompt engineering techniques.
2. Enhanced performance by selecting the best response from multiple approaches.
3. Flexibility to add or modify prompt engineering techniques as needed.

When implementing this technique, consider:

- Carefully selecting the prompt engineering techniques to include based on your specific use case.
- Balancing the number of techniques with computational cost and time constraints.
- Fine-tuning the evaluation criteria in the final step to best suit your needs.

Additional Real-World Applications

- **Complex Problem Solving**: Use Mixture of Reasoning for multi-step problems in fields like mathematics, physics, or engineering.
- **Customer Support**: Implement different response strategies to handle various types of customer queries effectively.
- **Content Generation**: Generate diverse content ideas by applying multiple creative thinking techniques.
- **Decision Making**: Analyze complex scenarios from different perspectives to make more informed decisions.
- **Educational Tutoring**: Provide explanations using various teaching methods to cater to different learning styles.

When adapting this recipe to your specific use-case, consider:

- Experimenting with different combinations of prompt engineering techniques.
- Implementing a feedback loop to continuously improve the selection of the best response.
- Tailoring the evaluation criteria to your specific domain or task requirements.
- Combining Mixture of Reasoning with other techniques like Self-Consistency for even more robust reasoning capabilities.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Mixture of Reasoning technique to enhance your LLM's performance across a wide range of applications.

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