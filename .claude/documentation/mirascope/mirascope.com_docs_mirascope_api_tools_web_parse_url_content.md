---
url: "https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content"
title: "mirascope.tools.web._parse_url_content | Mirascope"
---

# mirascope.tools.web.\_parse\_url\_content [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content\#mirascope-tools-web-parse-url-content)

## Module \_parse\_url\_content [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content\#parse-url-content)

## Class ParseURLConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content\#parseurlconfig)

Configuration for URL content parsing

**Bases:**

\_ConfigurableToolConfig

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| parser | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| timeout | [int](https://docs.python.org/3/library/functions.html#int) | - |

## Class ParseURLContent [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content\#parseurlcontent)

Tool for parsing and extracting main content from URLs.

Fetches content from URL, removes unnecessary elements like scripts, styles, navigation, etc.,
and returns clean text content from the webpage's main body.

**Bases:**

ConfigurableTool\[[ParseURLConfig](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content#parseurlconfig)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| url | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/web/parse_url_content\#call)

Fetch and parse content from the URL.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Cleaned text content from the URL if successful, error message if parsing fails |

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