---
url: "https://docling-project.github.io/docling/examples/pictures_description/"
title: "Annotate picture with local VLM - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/pictures_description/#describe-pictures-with-granite-vision)

# Annotate picture with local VLM

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/pictures_description.ipynb)

In \[ \]:

Copied!

```
%pip install -q docling[vlm] ipython

```

%pip install -q docling\[vlm\] ipython

```
Note: you may need to restart the kernel to use updated packages.

```

In \[1\]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import PdfPipelineOptions
from docling.document\_converter import DocumentConverter, PdfFormatOption

In \[2\]:

Copied!

```
# The source document
DOC_SOURCE = "https://arxiv.org/pdf/2501.17887"

```

\# The source document
DOC\_SOURCE = "https://arxiv.org/pdf/2501.17887"

* * *

## Describe pictures with Granite Vision [¶](https://docling-project.github.io/docling/examples/pictures_description/\#describe-pictures-with-granite-vision)

This section will run locally the [ibm-granite/granite-vision-3.1-2b-preview](https://huggingface.co/ibm-granite/granite-vision-3.1-2b-preview) model to describe the pictures of the document.

In \[3\]:

Copied!

```
from docling.datamodel.pipeline_options import granite_picture_description

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = (
    granite_picture_description  # <-- the model choice
)
pipeline_options.picture_description_options.prompt = (
    "Describe the image in three sentences. Be consise and accurate."
)
pipeline_options.images_scale = 2.0
pipeline_options.generate_picture_images = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)
doc = converter.convert(DOC_SOURCE).document

```

from docling.datamodel.pipeline\_options import granite\_picture\_description

pipeline\_options = PdfPipelineOptions()
pipeline\_options.do\_picture\_description = True
pipeline\_options.picture\_description\_options = (
granite\_picture\_description # <-- the model choice
)
pipeline\_options.picture\_description\_options.prompt = (
"Describe the image in three sentences. Be consise and accurate."
)
pipeline\_options.images\_scale = 2.0
pipeline\_options.generate\_picture\_images = True

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)
doc = converter.convert(DOC\_SOURCE).document

```
Using a slow image processor as `use_fast` is unset and a slow processor was saved with this model. `use_fast=True` will be the default behavior in v4.48, even if the model was saved with a slow processor. This will result in minor differences in outputs. You'll still be able to use a slow processor with `use_fast=False`.

```

```
Loading checkpoint shards:   0%|          | 0/2 [00:00<?, ?it/s]
```

In \[4\]:

Copied!

```
from docling_core.types.doc.document import PictureDescriptionData
from IPython import display

html_buffer = []
# display the first 5 pictures and their captions and annotations:
for pic in doc.pictures[:5]:
    html_item = (
        f"<h3>Picture <code>{pic.self_ref}</code></h3>"
        f'<img src="{pic.image.uri!s}" /><br />'
        f"<h4>Caption</h4>{pic.caption_text(doc=doc)}<br />"
    )
    for annotation in pic.annotations:
        if not isinstance(annotation, PictureDescriptionData):
            continue
        html_item += (
            f"<h4>Annotations ({annotation.provenance})</h4>{annotation.text}<br />\n"
        )
    html_buffer.append(html_item)
display.HTML("<hr />".join(html_buffer))

```

from docling\_core.types.doc.document import PictureDescriptionData
from IPython import display

html\_buffer = \[\]
\# display the first 5 pictures and their captions and annotations:
for pic in doc.pictures\[:5\]:
html\_item = (
f"

### Picture `{pic.self_ref}`

"
f'![No description has been provided for this image](https://docling-project.github.io/docling/examples/pictures_description/%7Bpic.image.uri!s%7D)

'
f"

#### Caption

{pic.caption\_text(doc=doc)}

"
)
for annotation in pic.annotations:
if not isinstance(annotation, PictureDescriptionData):
continue
html\_item += (
f"

#### Annotations ({annotation.provenance})

{annotation.text}

\\n"
)
html\_buffer.append(html\_item)
display.HTML("

* * *

".join(html\_buffer))

Out\[4\]:

### Picture `\#/pictures/0`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 1: Sketch of Docling's pipelines and usage model. Both PDF pipeline and simple pipeline build up a DoclingDocument representation, which can be further enriched. Downstream applications can utilize Docling's API to inspect, export, or chunk the document for various purposes.

#### Annotations (ibm-granite/granite-vision-3.1-2b-preview)

In this image we can see a poster with some text and images.

* * *

### Picture `\#/pictures/1`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 2: Dataset categories and sample counts for documents and pages.

#### Annotations (ibm-granite/granite-vision-3.1-2b-preview)

In this image we can see a pie chart. In the pie chart we can see the categories and the number of documents in each category.

* * *

### Picture `\#/pictures/2`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 3: Distribution of conversion times for all documents, ordered by number of pages in a document, on all system configurations. Every dot represents one document. Log/log scale is used to even the spacing, since both number of pages and conversion times have long-tail distributions.

#### Annotations (ibm-granite/granite-vision-3.1-2b-preview)

In this image we can see a graph. On the x-axis we can see the number of pages. On the y-axis we can see the seconds.

* * *

### Picture `\#/pictures/3`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 4: Contributions of PDF backend and AI models to the conversion time of a page (in seconds per page). Lower is better. Left: Ranges of time contributions for each model to pages it was applied on (i.e., OCR was applied only on pages with bitmaps, table structure was applied only on pages with tables). Right: Average time contribution to a page in the benchmark dataset (factoring in zero-time contribution for OCR and table structure models on pages without bitmaps or tables) .

#### Annotations (ibm-granite/granite-vision-3.1-2b-preview)

In this image we can see a bar chart and a line chart. In the bar chart we can see the values of Pdf Parse, OCR, Layout, Table Structure, Page Total and Page. In the line chart we can see the values of Pdf Parse, OCR, Layout, Table Structure, Page Total and Page.

* * *

### Picture `\#/pictures/4`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 5: Conversion time in seconds per page on our dataset in three scenarios, across all assets and system configurations. Lower bars are better. The configuration includes OCR and table structure recognition ( fast table option on Docling and MinerU, hi res in unstructured, as shown in table 1).

#### Annotations (ibm-granite/granite-vision-3.1-2b-preview)

In this image we can see a bar chart. In the chart we can see the CPU, Max, GPU, and sec/page.

* * *

## Describe pictures with SmolVLM [¶](https://docling-project.github.io/docling/examples/pictures_description/\#describe-pictures-with-smolvlm)

This section will run locally the [HuggingFaceTB/SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) model to describe the pictures of the document.

In \[7\]:

Copied!

```
from docling.datamodel.pipeline_options import smolvlm_picture_description

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = (
    smolvlm_picture_description  # <-- the model choice
)
pipeline_options.picture_description_options.prompt = (
    "Describe the image in three sentences. Be consise and accurate."
)
pipeline_options.images_scale = 2.0
pipeline_options.generate_picture_images = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)
doc = converter.convert(DOC_SOURCE).document

```

from docling.datamodel.pipeline\_options import smolvlm\_picture\_description

pipeline\_options = PdfPipelineOptions()
pipeline\_options.do\_picture\_description = True
pipeline\_options.picture\_description\_options = (
smolvlm\_picture\_description # <-- the model choice
)
pipeline\_options.picture\_description\_options.prompt = (
"Describe the image in three sentences. Be consise and accurate."
)
pipeline\_options.images\_scale = 2.0
pipeline\_options.generate\_picture\_images = True

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)
doc = converter.convert(DOC\_SOURCE).document

In \[6\]:

Copied!

```
from docling_core.types.doc.document import PictureDescriptionData
from IPython import display

html_buffer = []
# display the first 5 pictures and their captions and annotations:
for pic in doc.pictures[:5]:
    html_item = (
        f"<h3>Picture <code>{pic.self_ref}</code></h3>"
        f'<img src="{pic.image.uri!s}" /><br />'
        f"<h4>Caption</h4>{pic.caption_text(doc=doc)}<br />"
    )
    for annotation in pic.annotations:
        if not isinstance(annotation, PictureDescriptionData):
            continue
        html_item += (
            f"<h4>Annotations ({annotation.provenance})</h4>{annotation.text}<br />\n"
        )
    html_buffer.append(html_item)
display.HTML("<hr />".join(html_buffer))

```

from docling\_core.types.doc.document import PictureDescriptionData
from IPython import display

html\_buffer = \[\]
\# display the first 5 pictures and their captions and annotations:
for pic in doc.pictures\[:5\]:
html\_item = (
f"

### Picture `{pic.self_ref}`

"
f'![No description has been provided for this image](https://docling-project.github.io/docling/examples/pictures_description/%7Bpic.image.uri!s%7D)

'
f"

#### Caption

{pic.caption\_text(doc=doc)}

"
)
for annotation in pic.annotations:
if not isinstance(annotation, PictureDescriptionData):
continue
html\_item += (
f"

#### Annotations ({annotation.provenance})

{annotation.text}

\\n"
)
html\_buffer.append(html\_item)
display.HTML("

* * *

".join(html\_buffer))

Out\[6\]:

### Picture `\#/pictures/0`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 1: Sketch of Docling's pipelines and usage model. Both PDF pipeline and simple pipeline build up a DoclingDocument representation, which can be further enriched. Downstream applications can utilize Docling's API to inspect, export, or chunk the document for various purposes.

#### Annotations (HuggingFaceTB/SmolVLM-256M-Instruct)

This is a page that has different types of documents on it.

* * *

### Picture `\#/pictures/1`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 2: Dataset categories and sample counts for documents and pages.

#### Annotations (HuggingFaceTB/SmolVLM-256M-Instruct)

Here is a page-by-page list of documents per category:
\- Science
\- Articles
\- Law and Regulations
\- Articles
\- Misc.

* * *

### Picture `\#/pictures/2`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 3: Distribution of conversion times for all documents, ordered by number of pages in a document, on all system configurations. Every dot represents one document. Log/log scale is used to even the spacing, since both number of pages and conversion times have long-tail distributions.

#### Annotations (HuggingFaceTB/SmolVLM-256M-Instruct)

The image is a bar chart that shows the number of pages of a website as a function of the number of pages of the website. The x-axis represents the number of pages, ranging from 100 to 10,000. The y-axis represents the number of pages, ranging from 100 to 10,000. The chart is labeled "Number of pages" and has a legend at the top of the chart that indicates the number of pages.

The chart shows a clear trend: as the number of pages increases, the number of pages decreases. This is evident from the following points:

\- The number of pages increases from 100 to 1000.
\- The number of pages decreases from 1000 to 10,000.
\- The number of pages increases from 10,000 to 10,000.

* * *

### Picture `\#/pictures/3`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 4: Contributions of PDF backend and AI models to the conversion time of a page (in seconds per page). Lower is better. Left: Ranges of time contributions for each model to pages it was applied on (i.e., OCR was applied only on pages with bitmaps, table structure was applied only on pages with tables). Right: Average time contribution to a page in the benchmark dataset (factoring in zero-time contribution for OCR and table structure models on pages without bitmaps or tables) .

#### Annotations (HuggingFaceTB/SmolVLM-256M-Instruct)

bar chart with different colored bars representing different data points.

* * *

### Picture `\#/pictures/4`

![No description has been provided for this image](<Base64-Image-Removed>)

#### Caption

Figure 5: Conversion time in seconds per page on our dataset in three scenarios, across all assets and system configurations. Lower bars are better. The configuration includes OCR and table structure recognition ( fast table option on Docling and MinerU, hi res in unstructured, as shown in table 1).

#### Annotations (HuggingFaceTB/SmolVLM-256M-Instruct)

A bar chart with the following information:

\- The x-axis represents the number of pages, ranging from 0 to 14.
\- The y-axis represents the page count, ranging from 0 to 14.
\- The chart has three categories: Marker, Unstructured, and Detailed.
\- The x-axis is labeled "see/page."
\- The y-axis is labeled "Page Count."
\- The chart shows that the Marker category has the highest number of pages, followed by the Unstructured category, and then the Detailed category.

* * *

## Use other vision models [¶](https://docling-project.github.io/docling/examples/pictures_description/\#use-other-vision-models)

The examples above can also be reproduced using other vision model.
The Docling options `PictureDescriptionVlmOptions` allows to specify your favorite vision model from the Hugging Face Hub.

In \[8\]:

Copied!

```
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="",  # <-- add here the Hugging Face repo_id of your favorite VLM
    prompt="Describe the image in three sentences. Be consise and accurate.",
)
pipeline_options.images_scale = 2.0
pipeline_options.generate_picture_images = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

# Uncomment to run:
# doc = converter.convert(DOC_SOURCE).document

```

from docling.datamodel.pipeline\_options import PictureDescriptionVlmOptions

pipeline\_options = PdfPipelineOptions()
pipeline\_options.do\_picture\_description = True
pipeline\_options.picture\_description\_options = PictureDescriptionVlmOptions(
repo\_id="", # <-- add here the Hugging Face repo\_id of your favorite VLM
prompt="Describe the image in three sentences. Be consise and accurate.",
)
pipeline\_options.images\_scale = 2.0
pipeline\_options.generate\_picture\_images = True

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)

\# Uncomment to run:
\# doc = converter.convert(DOC\_SOURCE).document

In \[ \]:

Copied!

```

```

Back to top