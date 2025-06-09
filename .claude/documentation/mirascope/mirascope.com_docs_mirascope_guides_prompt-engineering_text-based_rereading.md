---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rereading"
title: "Rereading | Mirascope"
---

# Rereading [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rereading\#rereading)

Note

Our experiences indicate that re-reading is not as effective for newer, more powerful models such as Anthropic's 3.5 Sonnet or OpenAI's GPT-4o, although it remains effective in older models.

[Rereading](https://arxiv.org/pdf/2309.06275) is a prompt engineering technique that simply asks the LLM to reread a question and repeats it. When working with older, less capable LLM models, rereading has shown improvements for all types of reasoning tasks (arithmetic, symbolic, commonsense).

Mirascope Concepts Used

```
from mirascope.core import openai, prompt_template

@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {reread}")
def call(query: str, reread_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "reread": f"Read the question again: {query}" if reread_prompt else "",
        }
    }

prompt = """A coin is heads up. aluino flips the coin. arthor flips the coin.
Is the coin still heads up? Flip means reverse."""

print(call(query=prompt, reread_prompt=True))
```

To analyze the situation:

1. The coin starts heads up.
2. Aluino flips the coin, which reverses it to tails up.
3. Arthor then flips the coin again, which reverses it back to heads up.

So, after both flips, the coin is heads up again. The final answer is yes, the coin is still heads up.

This example demonstrates how to implement the Rereading technique using Mirascope. The `reread` computed field is added to the prompt when `reread_prompt` is set to `True`, instructing the LLM to read the question again.

## Benefits of Rereading [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/rereading\#benefits-of-rereading)

1. **Improved Comprehension**: Rereading can help the LLM better understand complex or nuanced questions.
2. **Enhanced Accuracy**: For older models, rereading has shown to improve accuracy across various reasoning tasks.
3. **Reinforcement**: Repeating the question can reinforce key details that might be overlooked in a single pass.
4. **Reduced Errors**: Rereading can help minimize errors that might occur due to misreading or misinterpreting the initial question.

Effective Rereading

- **Use with Older Models**: Rereading is most effective with older, less capable LLM models.
- **Apply to Complex Questions**: Consider using rereading for questions that involve multiple steps or complex reasoning.
- **Combine with Other Techniques**: Rereading can be used in conjunction with other prompt engineering techniques for potentially better results.
- **Monitor Performance**: Keep track of how rereading affects your model's performance, as its effectiveness may vary depending on the specific task and model used.
- **Consider Model Capabilities**: For newer, more advanced models, rereading might not provide significant benefits and could potentially be redundant.

By leveraging the Rereading technique, particularly with older LLM models, you may be able to improve the model's understanding and accuracy across various types of reasoning tasks. However, always consider the capabilities of your specific model when deciding whether to apply this technique.

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