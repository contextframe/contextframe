---
url: "https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo"
title: "mirascope.tools.web._duckduckgo | Mirascope"
---

# mirascope.tools.web.\_duckduckgo [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#mirascope-tools-web-duckduckgo)

## Module \_duckduckgo [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#duckduckgo)

## Class DuckDuckGoSearchConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#duckduckgosearchconfig)

Configuration for DuckDuckGo search

**Bases:**

\_ConfigurableToolConfig

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| max\_results\_per\_query | [int](https://docs.python.org/3/library/functions.html#int) | - |

## Class DuckDuckGoSearch [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#duckduckgosearch)

Tool for performing web searches using DuckDuckGo.

Takes search queries and returns relevant search results(Title, URL, Snippet).

**Bases:**

\_BaseDuckDuckGoSearch

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#call)

Perform a web search using DuckDuckGo and return formatted results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Formatted search results if successful, error message if search fails |

## Class AsyncDuckDuckGoSearch [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#asyncduckduckgosearch)

Tool for performing web searches using DuckDuckGo.

Takes search queries and returns relevant search results(Title, URL, Snippet).

**Bases:**

\_BaseDuckDuckGoSearch

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/duckduckgo\#call)

Perform an asynchronous web search using DuckDuckGo and return formatted results.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Formatted search results if successful, error message if search fails |

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