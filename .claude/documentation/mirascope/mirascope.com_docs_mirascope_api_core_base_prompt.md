---
url: "https://mirascope.com/docs/mirascope/api/core/base/prompt"
title: "mirascope.core.base.prompt | Mirascope"
---

# mirascope.core.base.prompt [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#mirascope-core-base-prompt)

## Module prompt [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#prompt)

The `BasePrompt` class for better prompt engineering.

## Attribute SUPPORTED\_MESSAGE\_ROLES [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#supported-message-roles)

**Type:**\['system', 'user', 'assistant'\]

## Class BasePrompt [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#baseprompt)

The base class for engineering prompts.

This class is implemented as the base for all prompting needs. It is intended to
work across various providers by providing a common prompt interface.

Example:

```
from mirascope.core import BasePrompt, metadata, prompt_template

@prompt_template("Recommend a {genre} book")
@metadata({"tags": {"version:0001", "books"}})
class BookRecommendationPrompt(BasePrompt):
    genre: str

prompt = BookRecommendationPrompt(genre="fantasy")

print(prompt)
# > Recommend a fantasy book

print(prompt.message_params())
# > [BaseMessageParam(role="user", content="Recommend a fantasy book")]

print(prompt.dump()["metadata"])
# > {"metadata": {"version:0001", "books"}}
```

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| prompt\_template | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function message\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#message-params)

Returns the list of parsed message parameters.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[BaseMessageParam](https://mirascope.com/docs/mirascope/api/core/base/message_param#basemessageparam)\] | - |

## Function dynamic\_config [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#dynamic-config)

Returns the dynamic config of the prompt.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig) | - |

## Function dump [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#dump)

Dumps the contents of the prompt into a dictionary.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\] | - |

## Function run [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#run)

Returns the response of calling the API of the provided decorator.

Example:

```
from mirascope.core import BasePrompt, openai, prompt_template

@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str

prompt = BookRecommendationPrompt(genre="fantasy")
response = prompt.run(openai.call("gpt-4o-mini"))
print(response.content)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| call\_decorator | (() =\> [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)) =\> () =\> [\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse) \| (() =\> [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)) =\> () =\> [\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream) \| (() =\> [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)) =\> () =\> \_ResponseModelT \| (() =\> [BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)) =\> () =\> Iterable\[\_ResponseModelT\] | - |
| additional\_decorators= () | (\_T) =\> \_T | - |

### Returns

| Type | Description |
| --- | --- |
| [\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse) \| [\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream) \| \_ResponseModelT \| Iterable\[\_ResponseModelT\] | - |

## Function run\_async [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#run-async)

Returns the response of calling the API of the provided decorator.

Example:

```
import asyncio

from mirascope.core import BasePrompt, openai, prompt_template

@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str

async def run():
    prompt = BookRecommendationPrompt(genre="fantasy")
    response = await prompt.run_async(openai.call("gpt-4o-mini"))
    print(response.content)

asyncio.run(run())
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| call\_decorator | (() =\> Awaitable\[[BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\]) =\> () =\> Awaitable\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] \| (() =\> Awaitable\[[BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\]) =\> () =\> Awaitable\[[\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\] \| (() =\> Awaitable\[[BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\]) =\> () =\> Awaitable\[\_ResponseModelT\] \| (() =\> Awaitable\[[BaseDynamicConfig](https://mirascope.com/docs/mirascope/api/core/base/dynamic_config#basedynamicconfig)\]) =\> () =\> Awaitable\[AsyncIterable\[\_ResponseModelT\]\] | - |
| additional\_decorators= () | (\_T) =\> \_T | - |

### Returns

| Type | Description |
| --- | --- |
| Awaitable\[[\_BaseCallResponseT](https://mirascope.com/docs/mirascope/api/core/base/call_response#basecallresponse)\] \| Awaitable\[[\_BaseStreamT](https://mirascope.com/docs/mirascope/api/core/base/stream#basestream)\] \| Awaitable\[\_ResponseModelT\] \| Awaitable\[AsyncIterable\[\_ResponseModelT\]\] | - |

## Class PromptDecorator [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#promptdecorator)

**Bases:**

[Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)

## Function prompt\_template [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#prompt-template)

A decorator for setting the `prompt_template` of a `BasePrompt` or `call`.

Usage

[Prompts](https://mirascope.com/docs/mirascope/learn/prompts#prompt-templates-messages)

Example:

```
from mirascope.core import openai, prompt_template

@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

print(recommend_book("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| template= None | [str](https://docs.python.org/3/library/stdtypes.html#str) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator function that turns the decorated function<br>into a prompt template. |

## Class MetadataDecorator [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#metadatadecorator)

**Bases:**

[Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)

## Function metadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/prompt\#metadata)

A decorator for adding metadata to a `BasePrompt` or `call`.

Adding this decorator to a `BasePrompt` or `call` updates the `metadata` annotation
to the given value. This is useful for adding metadata to a `BasePrompt` or `call`
that can be used for logging or filtering.

Example:

```
from mirascope.core import metadata, openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
@metadata({"tags": {"version:0001", "books"}})
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")
print(response.metadata)
```

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| metadata | [Metadata](https://mirascope.com/docs/mirascope/api/core/base/metadata#metadata) | - |

### Returns

| Type | Description |
| --- | --- |
| [Callable](https://docs.python.org/3/library/typing.html#typing.Callable) | The decorator function that updates the \`\_metadata\`<br>attribute of the decorated input prompt or call. |

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