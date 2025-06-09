---
url: "https://mirascope.com/docs/mirascope/api/tools/web/requests"
title: "mirascope.tools.web._requests | Mirascope"
---

# mirascope.tools.web.\_requests [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/requests\#mirascope-tools-web-requests)

## Module \_requests [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/requests\#requests)

## Class RequestsConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/requests\#requestsconfig)

Configuration for HTTP requests

**Bases:**

\_ConfigurableToolConfig

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| timeout | [int](https://docs.python.org/3/library/functions.html#int) | - |

## Class Requests [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/requests\#requests)

Tool for making HTTP requests with built-in requests library.

**Bases:**

ConfigurableTool

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| url | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| method | [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)\['GET', 'POST', 'PUT', 'DELETE'\] | - |
| data | [dict](https://docs.python.org/3/library/stdtypes.html#dict) \| [None](https://docs.python.org/3/library/constants.html#None) | - |
| headers | [dict](https://docs.python.org/3/library/stdtypes.html#dict) \| [None](https://docs.python.org/3/library/constants.html#None) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/requests\#call)

Make an HTTP request to the given URL.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Response text content if successful, error message if request fails |

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