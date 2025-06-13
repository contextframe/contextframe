---
url: "https://docs.litellm.ai/docs/rules"
title: "Rules | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/rules#__docusaurus_skipToContent_fallback)

On this page

# Rules

Use this to fail a request based on the input or output of an llm api call.

```codeBlockLines_e6Vv
import litellm
import os

# set env vars
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENROUTER_API_KEY"] = "your-api-key"

def my_custom_rule(input): # receives the model response
    if "i don't think i can answer" in input: # trigger fallback if the model refuses to answer
        return False
    return True

litellm.post_call_rules = [my_custom_rule] # have these be functions that can be called to fail a call

response = litellm.completion(model="gpt-3.5-turbo", messages=[{"role": "user",\
"content": "Hey, how's it going?"}], fallbacks=["openrouter/gryphe/mythomax-l2-13b"])

```

## Available Endpoints [​](https://docs.litellm.ai/docs/rules\#available-endpoints "Direct link to Available Endpoints")

- `litellm.pre_call_rules = []` \- A list of functions to iterate over before making the api call. Each function is expected to return either True (allow call) or False (fail call).

- `litellm.post_call_rules = []` \- List of functions to iterate over before making the api call. Each function is expected to return either True (allow call) or False (fail call).


## Expected format of rule [​](https://docs.litellm.ai/docs/rules\#expected-format-of-rule "Direct link to Expected format of rule")

```codeBlockLines_e6Vv
def my_custom_rule(input: str) -> bool: # receives the model response
    if "i don't think i can answer" in input: # trigger fallback if the model refuses to answer
        return False
    return True

```

#### Inputs [​](https://docs.litellm.ai/docs/rules\#inputs "Direct link to Inputs")

- `input`: _str_: The user input or llm response.

#### Outputs [​](https://docs.litellm.ai/docs/rules\#outputs "Direct link to Outputs")

- `bool`: Return True (allow call) or False (fail call)

## Example Rules [​](https://docs.litellm.ai/docs/rules\#example-rules "Direct link to Example Rules")

### Example 1: Fail if user input is too long [​](https://docs.litellm.ai/docs/rules\#example-1-fail-if-user-input-is-too-long "Direct link to Example 1: Fail if user input is too long")

```codeBlockLines_e6Vv
import litellm
import os

# set env vars
os.environ["OPENAI_API_KEY"] = "your-api-key"

def my_custom_rule(input): # receives the model response
    if len(input) > 10: # fail call if too long
        return False
    return True

litellm.pre_call_rules = [my_custom_rule] # have these be functions that can be called to fail a call

response = litellm.completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hey, how's it going?"}])

```

### Example 2: Fallback to uncensored model if llm refuses to answer [​](https://docs.litellm.ai/docs/rules\#example-2-fallback-to-uncensored-model-if-llm-refuses-to-answer "Direct link to Example 2: Fallback to uncensored model if llm refuses to answer")

```codeBlockLines_e6Vv
import litellm
import os

# set env vars
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENROUTER_API_KEY"] = "your-api-key"

def my_custom_rule(input): # receives the model response
    if "i don't think i can answer" in input: # trigger fallback if the model refuses to answer
        return False
    return True

litellm.post_call_rules = [my_custom_rule] # have these be functions that can be called to fail a call

response = litellm.completion(model="gpt-3.5-turbo", messages=[{"role": "user",\
"content": "Hey, how's it going?"}], fallbacks=["openrouter/gryphe/mythomax-l2-13b"])

```

- [Available Endpoints](https://docs.litellm.ai/docs/rules#available-endpoints)
- [Expected format of rule](https://docs.litellm.ai/docs/rules#expected-format-of-rule)
- [Example Rules](https://docs.litellm.ai/docs/rules#example-rules)
  - [Example 1: Fail if user input is too long](https://docs.litellm.ai/docs/rules#example-1-fail-if-user-input-is-too-long)
  - [Example 2: Fallback to uncensored model if llm refuses to answer](https://docs.litellm.ai/docs/rules#example-2-fallback-to-uncensored-model-if-llm-refuses-to-answer)