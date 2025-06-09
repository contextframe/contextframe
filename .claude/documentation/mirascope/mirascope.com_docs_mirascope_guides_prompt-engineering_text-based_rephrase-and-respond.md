---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond"
title: "Rephrase and Respond | Mirascope"
---

# Rephrase and Respond [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond\#rephrase-and-respond)

[Rephrase and respond](https://arxiv.org/pdf/2311.04205) (RaR) is a prompt engineering technique which involves asking the LLM to rephrase and expand upon the question before responding. RaR has shown improvements across all types of prompts, but we have personally found that RaR is most effective for shorter and vaguer prompts.

Mirascope Concepts Used

```
from mirascope.core import openai, prompt_template

rar_augment = "\nRephrase and expand the question, and respond."

@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {rar_augment}")
def call(query: str, rar_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "rar_augment": rar_augment if rar_prompt else "",
        }
    }

prompt = """A coin is heads up. aluino flips the coin. arthor flips the coin.
Is the coin still heads up? Flip means reverse."""

print(call(query=prompt, rar_prompt=True))
```

### Rephrased and Expanded Question: [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond\#rephrased-and-expanded-question)

A coin starts with the heads side facing up. If Aluino flips the coin, it will land with the tails side facing up. Then Arthur flips the coin again. After these two sequences of flips, can we say that the coin is still heads up?

### Response: [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond\#response)

To analyze the scenario, let's break down the actions step by step:

1. **Initial State**: The coin starts with the heads side facing up.

2. **Aluino Flips the Coin**: When Aluino flips the coin, it reverses its position. Since the coin initially was heads up, after Aluino's flip, the coin will now be tails up.

3. **Arthur Flips the Coin**: Next, Arthur takes his turn to flip the coin. Given that the current state of the coin is tails up, flipping it will reverse it again, resulting in the coin now being heads up.


At the end of these actions, after both Aluino and Arthur have flipped the coin, the final state of the coin is heads up once more. Thus, the answer to the question is:

**No, after Aluino flips it, the coin is tails up; however, after Arthur flips it again, the coin is heads up once more.**

This example demonstrates how to implement the Rephrase and Respond technique using Mirascope. The `rar_augment` variable contains the instruction for the LLM to rephrase and expand the question before responding. This instruction is added to the end of the prompt when `rar_prompt` is set to `True`.

## Benefits of Rephrase and Respond [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rephrase-and-respond\#benefits-of-rephrase-and-respond)

1. **Improved Understanding**: By rephrasing the question, the LLM demonstrates and often improves its understanding of the query.
2. **Clarity**: The rephrasing can help clarify ambiguous or vague queries.
3. **Context Expansion**: The expansion part of RaR allows the LLM to consider additional relevant context.
4. **Better Responses**: The combination of rephrasing and expanding often leads to more comprehensive and accurate responses.

Effective Rephrase and Respond

- **Use with Shorter Prompts**: RaR is particularly effective with shorter or vaguer prompts that benefit from expansion.
- **Allow for Flexibility**: The rephrasing may interpret the question slightly differently, which can lead to new insights.
- **Review the Rephrasing**: Pay attention to how the LLM rephrases the question, as it can provide insights into the model's understanding.
- **Iterative Refinement**: If the rephrasing misses key points, consider refining your original prompt.
- **Combine with Other Techniques**: RaR can be used in conjunction with other prompt engineering techniques for even better results.

By leveraging the Rephrase and Respond technique, you can often obtain more thorough and accurate responses from the LLM, especially for queries that benefit from additional context or clarification.

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