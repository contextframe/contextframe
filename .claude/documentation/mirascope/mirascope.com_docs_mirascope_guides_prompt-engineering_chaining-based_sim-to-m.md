---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/sim-to-m"
title: "Sim to M: Enhancing LLM Reasoning with Perspective-Taking | Mirascope"
---

# Sim to M: Enhancing LLM Reasoning with Perspective-Taking [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/sim-to-m\#sim-to-m-enhancing-llm-reasoning-with-perspective-taking)

This recipe demonstrates how to implement the Sim to M (Simulation Theory of Mind) technique using Large Language Models (LLMs) with Mirascope. Sim to M is a prompt engineering method that enhances an LLM's ability to reason about complex situations involving multiple perspectives.

Mirascope Concepts Used

Background

[Sim to M](https://arxiv.org/pdf/2311.10227) is a prompt engineering technique for dealing with complex situations which involve multiple perspectives. First ask the LLM to establish the facts from one person's perspective, then answer the question based only on that perspective. This approach can significantly improve the LLM's ability to reason about situations involving different viewpoints or limited information.

## Implementation [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/sim-to-m\#implementation)

Let's implement the Sim to M technique using Mirascope:

```
from mirascope.core import openai
from mirascope.core.base.prompt import prompt_template

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    The following is a sequence of events:
    {story}
    What events does {name} know about?
    """
)
def get_one_perspective(story: str, name: str):
    """Gets one person's perspective of a story."""

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {story_from_perspective}
    Based on the above information, answer the following question:
    {query}
    """
)
def sim_to_m(story: str, query: str, name: str) -> openai.OpenAIDynamicConfig:
    """Executes the flow of the Sim to M technique."""
    story_from_perspective = get_one_perspective(story=story, name=name)
    return {"computed_fields": {"story_from_perspective": story_from_perspective}}

story = """Jim put the ball in the box. While Jim wasn't looking, Avi moved the \
ball to the basket."""
query = "Where does Jim think the ball is?"

print(sim_to_m(story=story, query=query, name="Jim"))
```

Based on the information provided, Jim believes the ball is in the box, as he is only aware of his own action of putting the ball there. He is unaware of Avi's action of moving the ball to the basket. Therefore, Jim thinks the ball is still in the box.

This implementation consists of two main functions:

1. `get_one_perspective`: This function takes a story and a person's name as input, and returns the events known to that person.
2. `sim_to_m`: This function orchestrates the Sim to M technique. It first calls `get_one_perspective` to establish the facts from one person's viewpoint, then uses this perspective to answer the given query.

## Benefits and Considerations [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/sim-to-m\#benefits-and-considerations)

The Sim to M implementation offers several advantages:

1. Improved reasoning about situations involving multiple perspectives or limited information.
2. Enhanced ability to model and simulate different viewpoints in complex scenarios.
3. Potential for more accurate responses in tasks involving theory of mind or perspective-taking.

When implementing this technique, consider:

- Carefully crafting the initial story to include relevant information about different perspectives.
- Ensuring that the query is specific to a particular perspective or viewpoint.
- Experimenting with different prompts for the `get_one_perspective` function to optimize perspective extraction.

Additional Real-World Applications

- **Character Analysis in Literature**: Use Sim to M to analyze characters' motivations and beliefs in complex narratives.
- **Conflict Resolution**: Apply the technique to understand different stakeholders' viewpoints in disputes.
- **User Experience Design**: Simulate how different user groups might perceive and interact with a product or service.
- **Historical Analysis**: Model historical figures' decision-making based on their known information at the time.
- **Psychological Assessments**: Enhance AI-assisted psychological evaluations by better modeling individual perspectives.

When adapting this recipe to your specific use-case, consider:

- Tailoring the story and query formats to your domain for better performance.
- Implementing a mechanism to handle multiple perspectives in more complex scenarios.
- Combining Sim to M with other techniques like Chain of Thought for even more nuanced reasoning.
- Developing a feedback loop to refine the perspective extraction process based on the accuracy of final answers.

By leveraging Mirascope's `call` decorator and dynamic configuration, you can easily implement and customize the Sim to M technique to enhance your LLM's ability to reason about complex, multi-perspective situations across a wide range of applications.

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