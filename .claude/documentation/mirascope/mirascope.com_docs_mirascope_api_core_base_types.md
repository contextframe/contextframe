---
url: "https://mirascope.com/docs/mirascope/api/core/base/types"
title: "mirascope.core.base.types | Mirascope"
---

# mirascope.core.base.types [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#mirascope-core-base-types)

## Module types [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#types)

## Class Image [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#image)

## Class Image [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#image)

## Function tobytes [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#tobytes)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | - |

## Class AudioSegment [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#audiosegment)

## Function set\_frame\_rate [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#set-frame-rate)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| rate | [int](https://docs.python.org/3/library/functions.html#int) | - |

### Returns

| Type | Description |
| --- | --- |
| [AudioSegment](https://mirascope.com/docs/mirascope/api/core/base/types#audiosegment) | - |

## Function set\_channels [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#set-channels)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| channels | [int](https://docs.python.org/3/library/functions.html#int) | - |

### Returns

| Type | Description |
| --- | --- |
| [AudioSegment](https://mirascope.com/docs/mirascope/api/core/base/types#audiosegment) | - |

## Function set\_sample\_width [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#set-sample-width)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| sample\_width | [int](https://docs.python.org/3/library/functions.html#int) | - |

### Returns

| Type | Description |
| --- | --- |
| [AudioSegment](https://mirascope.com/docs/mirascope/api/core/base/types#audiosegment) | - |

## Function export [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#export)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |
| format | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

### Returns

| Type | Description |
| --- | --- |
| FileIO | - |

## Function read [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#read)

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | - |

## Attribute has\_pil\_module [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#has-pil-module)

**Type:** [bool](https://docs.python.org/3/library/functions.html#bool)

## Attribute has\_pydub\_module [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#has-pydub-module)

**Type:** [bool](https://docs.python.org/3/library/functions.html#bool)

## Attribute FinishReason [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#finishreason)

**Type:** TypeAlias

## Class Usage [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#usage)

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Number of tokens in the prompt. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Number of tokens used that were previously cached (and thus cheaper). |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Number of tokens in the generated output. |
| total\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Total number of tokens used in the request (prompt + completion). |

## Attribute JsonableType [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#jsonabletype)

**Type:** TypeAlias

## Class VideoMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#videometadata)

Metadata for a video for cost calculation

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| duration\_seconds | Annotated\[float, Field(description='Duration of the video in seconds')\] | - |
| with\_audio | Annotated\[bool \| None, Field(default=False, description='Whether the video includes audio that should be processed')\] | - |
| tokens | Annotated\[int \| None, Field(default=None, description='Precalculated token count for this video')\] | - |

## Class AudioMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#audiometadata)

Metadata for an audio file for cost calculation

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| duration\_seconds | Annotated\[float, Field(description='Duration of the audio in seconds')\] | - |
| with\_timestamps | Annotated\[bool \| None, Field(default=False, description='Whether timestamps should be included')\] | - |
| tokens | Annotated\[int \| None, Field(default=None, description='Precalculated token count for this audio')\] | - |

## Class ImageMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#imagemetadata)

Metadata for an image for cost calculation

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| width | Annotated\[int, Field(description='Width of the image in pixels')\] | - |
| height | Annotated\[int, Field(description='Height of the image in pixels')\] | - |
| tokens | Annotated\[int \| None, Field(default=None, description='Precalculated token count for this image')\] | - |
| detail | Annotated\[str \| None, Field(default=None, description='Detail level of the image')\] | - |

## Class GoogleMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#googlemetadata)

Google API specific metadata for cost calculation

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| use\_vertex\_ai | Annotated\[bool \| None, Field(default=False, description='Whether to use Vertex AI pricing (vs. direct Gemini API)')\] | - |
| grounding\_requests | Annotated\[int \| None, Field(default=None, description='Number of Google Search grounding requests')\] | - |

## Class PDFImageMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#pdfimagemetadata)

Metadata for an image extracted from a PDF page

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| width | Annotated\[int, Field(description='Width of the image in pixels')\] | - |
| height | Annotated\[int, Field(description='Height of the image in pixels')\] | - |
| tokens | Annotated\[int \| None, Field(default=None, description='Precalculated token count for this image')\] | - |

## Class PDFMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#pdfmetadata)

Metadata specific to PDF documents for cost calculation

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| page\_count | Annotated\[int \| None, Field(default=None, description='Number of pages in the PDF')\] | - |
| text\_tokens | Annotated\[int \| None, Field(default=None, description='Number of tokens from text content in the PDF')\] | - |
| images | Annotated\[list\[PDFImageMetadata\] \| None, Field(default=None, description='List of images extracted from PDF with width and height information')\] | - |
| cached | Annotated\[bool \| None, Field(default=None, description='Whether this PDF was cached for reduced token costs')\] | - |

## Class CostMetadata [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#costmetadata)

Metadata required for accurate LLM API cost calculation across all providers.

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| model\_config | ConfigDict(arbitrary\_types\_allowed=True) | - |
| input\_tokens | Annotated\[int \| float \| None, Field(default=None, description='Input tokens')\] | - |
| output\_tokens | Annotated\[int \| float \| None, Field(default=None, description='Output tokens')\] | - |
| cached\_tokens | Annotated\[int \| float \| None, Field(default=None, description='Cached tokens')\] | - |
| streaming\_mode | Annotated\[bool \| None, Field(default=None, description='Whether streaming API was used')\] | - |
| cached\_response | Annotated\[bool \| None, Field(default=None, description='Whether response was served from cache')\] | - |
| context\_length | Annotated\[int \| None, Field(default=None, description='Total context window length in tokens')\] | - |
| realtime\_mode | Annotated\[bool \| None, Field(default=None, description='Whether realtime processing was used')\] | - |
| region | Annotated\[str \| None, Field(default=None, description='Cloud region for request (affects pricing in some providers)')\] | - |
| tier | Annotated\[str \| None, Field(default=None, description='Service tier (e.g. standard, enterprise)')\] | - |
| batch\_mode | Annotated\[bool \| None, Field(default=False, description='Whether batch mode is used (discount usually applies)')\] | - |
| images | Annotated\[list\[ImageMetadata\] \| None, Field(default=None, description='List of images with their metadata')\] | - |
| videos | Annotated\[list\[VideoMetadata\] \| None, Field(default=None, description='List of videos with their metadata')\] | - |
| audio | Annotated\[list\[AudioMetadata\] \| None, Field(default=None, description='List of audio clips with their metadata')\] | - |
| audio\_output | Annotated\[list\[AudioMetadata\] \| None, Field(default=None, description='List of audio output clips with their metadata')\] | - |
| pdf | Annotated\[PDFMetadata \| None, Field(default=None, description='Metadata for PDF documents')\] | - |
| context\_cache\_tokens | Annotated\[int \| None, Field(default=None, description='Number of cached context tokens')\] | - |
| context\_cache\_hours | Annotated\[float \| None, Field(default=None, description='Number of hours to keep context in cache')\] | - |
| google | Annotated\[GoogleMetadata \| None, Field(default=None, description='Google/Gemini-specific metadata for cost calculation')\] | - |
| realtime\_tokens | Annotated\[int \| None, Field(default=None, description='\[OpenAI\] Number of realtime tokens in the request')\] | - |
| cache\_write | Annotated\[bool \| None, Field(default=None, description='\[Anthropic\] Whether cache write occurred')\] | - |
| tool\_use\_tokens | Annotated\[int \| None, Field(default=None, description='\[Anthropic\] Tokens used for tool calls')\] | - |
| cost | Annotated\[float \| None, Field(default=None, description='Cost provided by the API response')\] | - |

## Attribute Provider [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#provider)

**Type:** TypeAlias

## Attribute LocalProvider [Link to this heading](https://mirascope.com/docs/mirascope/api/core/base/types\#localprovider)

**Type:** TypeAlias

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