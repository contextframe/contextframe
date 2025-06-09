---
url: "https://mirascope.com/docs/mirascope/api/core/base/toolkit"
title: "mirascope.core.base.toolkit | Mirascope"
---

# mirascope.core.base.toolkit [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#mirascope-core-base-toolkit)

## Module toolkit [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#toolkit)

The module for defining the toolkit class for LLM call tools.

Usage

[Tools](https://mirascope.com/docs/mirascope/learn/tools#toolkit)

## Attribute P [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#p)

**Type:** ParamSpec('P')

## Function is\_toolkit\_tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#is-toolkit-tool)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| method | () =\> [Any](https://docs.python.org/3/library/typing.html#typing.Any) \| [BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool) | - |

### Returns

| Type | Description |
| --- | --- |
| [bool](https://docs.python.org/3/library/functions.html#bool) | - |

## Class ToolKitToolMethod [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#toolkittoolmethod)

**Bases:**

NamedTuple

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| method | () =\> [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| template\_vars | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | - |
| template | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Class BaseToolKit [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#basetoolkit)

A class for defining tools for LLM call tools.

The class should have methods decorated with `@toolkit_tool` to create tools.

Example:

```
from mirascope.core.base import BaseToolKit, toolkit_tool
from mirascope.core import openai

class BookRecommendationToolKit(BaseToolKit):
    '''A toolkit for recommending books.'''

    __namespace__: ClassVar[str | None] = 'book_tools'
    reading_level: Literal["beginner", "advanced"]

    @toolkit_tool
    def format_book(self, title: str, author: str) -> str:
        '''Returns the title and author of a book nicely formatted.

        Reading level: {self.reading_level}
        '''
        return f"{title} by {author}"

@openai.call(model="gpt-4o")
def recommend_book(genre: str, reading_level: Literal["beginner", "advanced"]):
    '''Recommend a {genre} book.'''
    toolkit = BookRecommendationToolKit(reading_level=reading_level)
    return {"tools": toolkit.create_tools()}

response = recommend_book("fantasy", "beginner")
if tool := response.tool:
    output = tool.call()
    print(output)
    #> The Name of the Wind by Patrick Rothfuss
else:
    print(response.content)
    #> Sure! I would recommend...
```

**Bases:** [BaseModel](https://docs.pydantic.dev/latest/api/base_model/), ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| model\_config | ConfigDict(arbitrary\_types\_allowed=True) | - |

## Function create\_tools [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#create-tools)

The method to create the tools.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] | - |

## Function toolkit\_tool [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/toolkit\#toolkit-tool)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| method | ([\_BaseToolKitT](https://mirascope.com/docs/mirascope/api/core/base/toolkit#basetoolkit), [P](https://mirascope.com/docs/mirascope/api/core/base/toolkit#p)) =\> [str](https://docs.python.org/3/library/stdtypes.html#str) \| [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

### Returns

| Type | Description |
| --- | --- |
| ([\_BaseToolKitT](https://mirascope.com/docs/mirascope/api/core/base/toolkit#basetoolkit), [P](https://mirascope.com/docs/mirascope/api/core/base/toolkit#p)) =\> [str](https://docs.python.org/3/library/stdtypes.html#str) \| [type](https://docs.python.org/3/library/functions.html#type)\[[\_BaseToolT](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\] | - |

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