---
url: "https://docling-project.github.io/docling/examples/serialization/"
title: "Serialization - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/serialization/#serialization)

# Serialization [¶](https://docling-project.github.io/docling/examples/serialization/\#serialization)

## Overview [¶](https://docling-project.github.io/docling/examples/serialization/\#overview)

In this notebook we showcase the usage of Docling [serializers](https://docling-project.github.io/docling/concepts/serialization).

## Setup [¶](https://docling-project.github.io/docling/examples/serialization/\#setup)

In \[1\]:

Copied!

```
%pip install -qU pip docling docling-core~=2.29 rich

```

%pip install -qU pip docling docling-core~=2.29 rich

```
Note: you may need to restart the kernel to use updated packages.

```

In \[2\]:

Copied!

```
DOC_SOURCE = "https://arxiv.org/pdf/2311.18481"

# we set some start-stop cues for defining an excerpt to print
start_cue = "Copyright © 2024"
stop_cue = "Application of NLP to ESG"

```

DOC\_SOURCE = "https://arxiv.org/pdf/2311.18481"

\# we set some start-stop cues for defining an excerpt to print
start\_cue = "Copyright © 2024"
stop\_cue = "Application of NLP to ESG"

In \[3\]:

Copied!

```
from rich.console import Console
from rich.panel import Panel

console = Console(width=210)  # for preventing Markdown table wrapped rendering

def print_in_console(text):
    console.print(Panel(text))

```

from rich.console import Console
from rich.panel import Panel

console = Console(width=210) # for preventing Markdown table wrapped rendering

def print\_in\_console(text):
console.print(Panel(text))

## Basic usage [¶](https://docling-project.github.io/docling/examples/serialization/\#basic-usage)

We first convert the document:

In \[4\]:

Copied!

```
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
doc = converter.convert(source=DOC_SOURCE).document

```

from docling.document\_converter import DocumentConverter

converter = DocumentConverter()
doc = converter.convert(source=DOC\_SOURCE).document

```
/Users/pva/work/github.com/DS4SD/docling/.venv/lib/python3.13/site-packages/torch/utils/data/dataloader.py:683: UserWarning: 'pin_memory' argument is set as true but not supported on MPS now, then device pinned memory won't be used.
  warnings.warn(warn_msg)

```

We can now apply any `BaseDocSerializer` on the produced document.

👉 Note that, to keep the shown output brief, we only print an excerpt.

E.g. below we apply an `HTMLDocSerializer`:

In \[5\]:

Copied!

```
from docling_core.transforms.serializer.html import HTMLDocSerializer

serializer = HTMLDocSerializer(doc=doc)
ser_result = serializer.serialize()
ser_text = ser_result.text

# we here only print an excerpt to keep the output brief:
print_in_console(ser_text[ser_text.find(start_cue) : ser_text.find(stop_cue)])

```

from docling\_core.transforms.serializer.html import HTMLDocSerializer

serializer = HTMLDocSerializer(doc=doc)
ser\_result = serializer.serialize()
ser\_text = ser\_result.text

\# we here only print an excerpt to keep the output brief:
print\_in\_console(ser\_text\[ser\_text.find(start\_cue) : ser\_text.find(stop\_cue)\])

```
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Copyright © 2024, Association for the Advancement of Artificial Intelligence (www.aaai.org). All rights reserved.</p>                                                                                          │
│ <table><tbody><tr><th>Report</th><th>Question</th><th>Answer</th></tr><tr><td>IBM 2022</td><td>How many hours were spent on employee learning in 2021?</td><td>22.5 million hours</td></tr><tr><td>IBM         │
│ 2022</td><td>What was the rate of fatalities in 2021?</td><td>The rate of fatalities in 2021 was 0.0016.</td></tr><tr><td>IBM 2022</td><td>How many full audits were con- ducted in 2022 in                    │
│ India?</td><td>2</td></tr><tr><td>Starbucks 2022</td><td>What is the percentage of women in the Board of Directors?</td><td>25%</td></tr><tr><td>Starbucks 2022</td><td>What was the total energy con-         │
│ sumption in 2021?</td><td>According to the table, the total energy consumption in 2021 was 2,491,543 MWh.</td></tr><tr><td>Starbucks 2022</td><td>How much packaging material was made from renewable mate-    │
│ rials?</td><td>According to the given data, 31% of packaging materials were made from recycled or renewable materials in FY22.</td></tr></tbody></table>                                                       │
│ <p>Table 1: Example question answers from the ESG reports of IBM and Starbucks using Deep Search DocQA system.</p>                                                                                             │
│ <p>ESG report in our library via our QA conversational assistant. Our assistant generates answers and also presents the information (paragraph or table), in the ESG report, from which it has generated the   │
│ response.</p>                                                                                                                                                                                                  │
│ <h2>Related Work</h2>                                                                                                                                                                                          │
│ <p>The DocQA integrates multiple AI technologies, namely:</p>                                                                                                                                                  │
│ <p>Document Conversion: Converting unstructured documents, such as PDF files, into a machine-readable format is a challenging task in AI. Early strategies for document conversion were based on geometric     │
│ layout analysis (Cattoni et al. 2000; Breuel 2002). Thanks to the availability of large annotated datasets (PubLayNet (Zhong et al. 2019), DocBank (Li et al. 2020), DocLayNet (Pfitzmann et al. 2022; Auer et │
│ al. 2023), deep learning-based methods are routinely used. Modern approaches for recovering the structure of a document can be broadly divided into two categories: image-based or PDF representation-based .  │
│ Imagebased methods usually employ Transformer or CNN architectures on the images of pages (Zhang et al. 2023; Li et al. 2022; Huang et al. 2022). On the other hand, deep learning-</p>                        │
│ <figure><figcaption>Figure 1: System architecture: Simplified sketch of document question-answering pipeline.</figcaption></figure>                                                                            │
│ <p>based language processing methods are applied on the native PDF content (generated by a single PDF printing command) (Auer et al. 2022; Livathinos et al. 2021; Staar et al. 2018).</p>                     │
│ <p>                                                                                                                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

In the following example, we use a `MarkdownDocSerializer`:

In \[6\]:

Copied!

```
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer

serializer = MarkdownDocSerializer(doc=doc)
ser_result = serializer.serialize()
ser_text = ser_result.text

print_in_console(ser_text[ser_text.find(start_cue) : ser_text.find(stop_cue)])

```

from docling\_core.transforms.serializer.markdown import MarkdownDocSerializer

serializer = MarkdownDocSerializer(doc=doc)
ser\_result = serializer.serialize()
ser\_text = ser\_result.text

print\_in\_console(ser\_text\[ser\_text.find(start\_cue) : ser\_text.find(stop\_cue)\])

```
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Copyright © 2024, Association for the Advancement of Artificial Intelligence (www.aaai.org). All rights reserved.                                                                                              │
│                                                                                                                                                                                                                │
│ | Report         | Question                                                         | Answer                                                                                                          |        │
│ |----------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|        │
│ | IBM 2022       | How many hours were spent on employee learning in 2021?          | 22.5 million hours                                                                                              |        │
│ | IBM 2022       | What was the rate of fatalities in 2021?                         | The rate of fatalities in 2021 was 0.0016.                                                                      |        │
│ | IBM 2022       | How many full audits were con- ducted in 2022 in India?          | 2                                                                                                               |        │
│ | Starbucks 2022 | What is the percentage of women in the Board of Directors?       | 25%                                                                                                             |        │
│ | Starbucks 2022 | What was the total energy con- sumption in 2021?                 | According to the table, the total energy consumption in 2021 was 2,491,543 MWh.                                 |        │
│ | Starbucks 2022 | How much packaging material was made from renewable mate- rials? | According to the given data, 31% of packaging materials were made from recycled or renewable materials in FY22. |        │
│                                                                                                                                                                                                                │
│ Table 1: Example question answers from the ESG reports of IBM and Starbucks using Deep Search DocQA system.                                                                                                    │
│                                                                                                                                                                                                                │
│ ESG report in our library via our QA conversational assistant. Our assistant generates answers and also presents the information (paragraph or table), in the ESG report, from which it has generated the      │
│ response.                                                                                                                                                                                                      │
│                                                                                                                                                                                                                │
│ ## Related Work                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
│ The DocQA integrates multiple AI technologies, namely:                                                                                                                                                         │
│                                                                                                                                                                                                                │
│ Document Conversion: Converting unstructured documents, such as PDF files, into a machine-readable format is a challenging task in AI. Early strategies for document conversion were based on geometric layout │
│ analysis (Cattoni et al. 2000; Breuel 2002). Thanks to the availability of large annotated datasets (PubLayNet (Zhong et al. 2019), DocBank (Li et al. 2020), DocLayNet (Pfitzmann et al. 2022; Auer et al.    │
│ 2023), deep learning-based methods are routinely used. Modern approaches for recovering the structure of a document can be broadly divided into two categories: image-based or PDF representation-based .      │
│ Imagebased methods usually employ Transformer or CNN architectures on the images of pages (Zhang et al. 2023; Li et al. 2022; Huang et al. 2022). On the other hand, deep learning-                            │
│                                                                                                                                                                                                                │
│ Figure 1: System architecture: Simplified sketch of document question-answering pipeline.                                                                                                                      │
│                                                                                                                                                                                                                │
│ <!-- image -->                                                                                                                                                                                                 │
│                                                                                                                                                                                                                │
│ based language processing methods are applied on the native PDF content (generated by a single PDF printing command) (Auer et al. 2022; Livathinos et al. 2021; Staar et al. 2018).                            │
│                                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Configuring a serializer [¶](https://docling-project.github.io/docling/examples/serialization/\#configuring-a-serializer)

Let's now assume we would like to reconfigure the Markdown serialization such that:

- it uses a different component serializer, e.g. if we'd prefer tables to be printed in a triplet format (which could potentially improve the vector representation compared to Markdown tables)
- it uses specific user-defined parameters, e.g. if we'd prefer a different image placeholder text than the default one

Check out the following configuration and notice the serialization differences in the output further below:

In \[7\]:

Copied!

```
from docling_core.transforms.chunker.hierarchical_chunker import TripletTableSerializer
from docling_core.transforms.serializer.markdown import MarkdownParams

serializer = MarkdownDocSerializer(
    doc=doc,
    table_serializer=TripletTableSerializer(),
    params=MarkdownParams(
        image_placeholder="<!-- demo picture placeholder -->",
        # ...
    ),
)
ser_result = serializer.serialize()
ser_text = ser_result.text

print_in_console(ser_text[ser_text.find(start_cue) : ser_text.find(stop_cue)])

```

from docling\_core.transforms.chunker.hierarchical\_chunker import TripletTableSerializer
from docling\_core.transforms.serializer.markdown import MarkdownParams

serializer = MarkdownDocSerializer(
doc=doc,
table\_serializer=TripletTableSerializer(),
params=MarkdownParams(
image\_placeholder="",
# ...
),
)
ser\_result = serializer.serialize()
ser\_text = ser\_result.text

print\_in\_console(ser\_text\[ser\_text.find(start\_cue) : ser\_text.find(stop\_cue)\])

```
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Copyright © 2024, Association for the Advancement of Artificial Intelligence (www.aaai.org). All rights reserved.                                                                                              │
│                                                                                                                                                                                                                │
│ IBM 2022, Question = How many hours were spent on employee learning in 2021?. IBM 2022, Answer = 22.5 million hours. IBM 2022, Question = What was the rate of fatalities in 2021?. IBM 2022, Answer = The     │
│ rate of fatalities in 2021 was 0.0016.. IBM 2022, Question = How many full audits were con- ducted in 2022 in India?. IBM 2022, Answer = 2. Starbucks 2022, Question = What is the percentage of women in the  │
│ Board of Directors?. Starbucks 2022, Answer = 25%. Starbucks 2022, Question = What was the total energy con- sumption in 2021?. Starbucks 2022, Answer = According to the table, the total energy consumption  │
│ in 2021 was 2,491,543 MWh.. Starbucks 2022, Question = How much packaging material was made from renewable mate- rials?. Starbucks 2022, Answer = According to the given data, 31% of packaging materials were │
│ made from recycled or renewable materials in FY22.                                                                                                                                                             │
│                                                                                                                                                                                                                │
│ Table 1: Example question answers from the ESG reports of IBM and Starbucks using Deep Search DocQA system.                                                                                                    │
│                                                                                                                                                                                                                │
│ ESG report in our library via our QA conversational assistant. Our assistant generates answers and also presents the information (paragraph or table), in the ESG report, from which it has generated the      │
│ response.                                                                                                                                                                                                      │
│                                                                                                                                                                                                                │
│ ## Related Work                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
│ The DocQA integrates multiple AI technologies, namely:                                                                                                                                                         │
│                                                                                                                                                                                                                │
│ Document Conversion: Converting unstructured documents, such as PDF files, into a machine-readable format is a challenging task in AI. Early strategies for document conversion were based on geometric layout │
│ analysis (Cattoni et al. 2000; Breuel 2002). Thanks to the availability of large annotated datasets (PubLayNet (Zhong et al. 2019), DocBank (Li et al. 2020), DocLayNet (Pfitzmann et al. 2022; Auer et al.    │
│ 2023), deep learning-based methods are routinely used. Modern approaches for recovering the structure of a document can be broadly divided into two categories: image-based or PDF representation-based .      │
│ Imagebased methods usually employ Transformer or CNN architectures on the images of pages (Zhang et al. 2023; Li et al. 2022; Huang et al. 2022). On the other hand, deep learning-                            │
│                                                                                                                                                                                                                │
│ Figure 1: System architecture: Simplified sketch of document question-answering pipeline.                                                                                                                      │
│                                                                                                                                                                                                                │
│ <!-- demo picture placeholder -->                                                                                                                                                                              │
│                                                                                                                                                                                                                │
│ based language processing methods are applied on the native PDF content (generated by a single PDF printing command) (Auer et al. 2022; Livathinos et al. 2021; Staar et al. 2018).                            │
│                                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Creating a custom serializer [¶](https://docling-project.github.io/docling/examples/serialization/\#creating-a-custom-serializer)

In the examples above, we were able to reuse existing implementations for our desired
serialization strategy, but let's now assume we want to define a custom serialization
logic, e.g. we would like picture serialization to include any available picture
description (captioning) annotations.

To that end, we first need to revisit our conversion and include all pipeline options
needed for
[picture description enrichment](https://docling-project.github.io/docling/usage/enrichments/#picture-description).

In \[8\]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionVlmOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(
    do_picture_description=True,
    picture_description_options=PictureDescriptionVlmOptions(
        repo_id="HuggingFaceTB/SmolVLM-256M-Instruct",
        prompt="Describe this picture in three to five sentences. Be precise and concise.",
    ),
    generate_picture_images=True,
    images_scale=2,
)

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
doc = converter.convert(source=DOC_SOURCE).document

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
PdfPipelineOptions,
PictureDescriptionVlmOptions,
)
from docling.document\_converter import DocumentConverter, PdfFormatOption

pipeline\_options = PdfPipelineOptions(
do\_picture\_description=True,
picture\_description\_options=PictureDescriptionVlmOptions(
repo\_id="HuggingFaceTB/SmolVLM-256M-Instruct",
prompt="Describe this picture in three to five sentences. Be precise and concise.",
),
generate\_picture\_images=True,
images\_scale=2,
)

converter = DocumentConverter(
format\_options={InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)}
)
doc = converter.convert(source=DOC\_SOURCE).document

```
/Users/pva/work/github.com/DS4SD/docling/.venv/lib/python3.13/site-packages/torch/utils/data/dataloader.py:683: UserWarning: 'pin_memory' argument is set as true but not supported on MPS now, then device pinned memory won't be used.
  warnings.warn(warn_msg)

```

We can then define our custom picture serializer:

In \[9\]:

Copied!

```
from typing import Any, Optional

from docling_core.transforms.serializer.base import (
    BaseDocSerializer,
    SerializationResult,
)
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import (
    MarkdownParams,
    MarkdownPictureSerializer,
)
from docling_core.types.doc.document import (
    DoclingDocument,
    ImageRefMode,
    PictureDescriptionData,
    PictureItem,
)
from typing_extensions import override

class AnnotationPictureSerializer(MarkdownPictureSerializer):
    @override
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs: Any,
    ) -> SerializationResult:
        text_parts: list[str] = []

        # reusing the existing result:
        parent_res = super().serialize(
            item=item,
            doc_serializer=doc_serializer,
            doc=doc,
            **kwargs,
        )
        text_parts.append(parent_res.text)

        # appending annotations:
        for annotation in item.annotations:
            if isinstance(annotation, PictureDescriptionData):
                text_parts.append(f"<!-- Picture description: {annotation.text} -->")

        text_res = (separator or "\n").join(text_parts)
        return create_ser_result(text=text_res, span_source=item)

```

from typing import Any, Optional

from docling\_core.transforms.serializer.base import (
BaseDocSerializer,
SerializationResult,
)
from docling\_core.transforms.serializer.common import create\_ser\_result
from docling\_core.transforms.serializer.markdown import (
MarkdownParams,
MarkdownPictureSerializer,
)
from docling\_core.types.doc.document import (
DoclingDocument,
ImageRefMode,
PictureDescriptionData,
PictureItem,
)
from typing\_extensions import override

class AnnotationPictureSerializer(MarkdownPictureSerializer):
@override
def serialize(
self,
\*,
item: PictureItem,
doc\_serializer: BaseDocSerializer,
doc: DoclingDocument,
separator: Optional\[str\] = None,
\*\*kwargs: Any,
) -\> SerializationResult:
text\_parts: list\[str\] = \[\]

# reusing the existing result:
parent\_res = super().serialize(
item=item,
doc\_serializer=doc\_serializer,
doc=doc,
\*\*kwargs,
)
text\_parts.append(parent\_res.text)

# appending annotations:
for annotation in item.annotations:
if isinstance(annotation, PictureDescriptionData):
text\_parts.append(f"")

text\_res = (separator or "\\n").join(text\_parts)
return create\_ser\_result(text=text\_res, span\_source=item)

Last but not least, we define a new doc serializer which leverages our custom picture
serializer.

Notice the picture description annotations in the output below:

In \[10\]:

Copied!

```
serializer = MarkdownDocSerializer(
    doc=doc,
    picture_serializer=AnnotationPictureSerializer(),
    params=MarkdownParams(
        image_mode=ImageRefMode.PLACEHOLDER,
        image_placeholder="",
    ),
)
ser_result = serializer.serialize()
ser_text = ser_result.text

print_in_console(ser_text[ser_text.find(start_cue) : ser_text.find(stop_cue)])

```

serializer = MarkdownDocSerializer(
doc=doc,
picture\_serializer=AnnotationPictureSerializer(),
params=MarkdownParams(
image\_mode=ImageRefMode.PLACEHOLDER,
image\_placeholder="",
),
)
ser\_result = serializer.serialize()
ser\_text = ser\_result.text

print\_in\_console(ser\_text\[ser\_text.find(start\_cue) : ser\_text.find(stop\_cue)\])

```
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Copyright © 2024, Association for the Advancement of Artificial Intelligence (www.aaai.org). All rights reserved.                                                                                              │
│                                                                                                                                                                                                                │
│ | Report         | Question                                                         | Answer                                                                                                          |        │
│ |----------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|        │
│ | IBM 2022       | How many hours were spent on employee learning in 2021?          | 22.5 million hours                                                                                              |        │
│ | IBM 2022       | What was the rate of fatalities in 2021?                         | The rate of fatalities in 2021 was 0.0016.                                                                      |        │
│ | IBM 2022       | How many full audits were con- ducted in 2022 in India?          | 2                                                                                                               |        │
│ | Starbucks 2022 | What is the percentage of women in the Board of Directors?       | 25%                                                                                                             |        │
│ | Starbucks 2022 | What was the total energy con- sumption in 2021?                 | According to the table, the total energy consumption in 2021 was 2,491,543 MWh.                                 |        │
│ | Starbucks 2022 | How much packaging material was made from renewable mate- rials? | According to the given data, 31% of packaging materials were made from recycled or renewable materials in FY22. |        │
│                                                                                                                                                                                                                │
│ Table 1: Example question answers from the ESG reports of IBM and Starbucks using Deep Search DocQA system.                                                                                                    │
│                                                                                                                                                                                                                │
│ ESG report in our library via our QA conversational assistant. Our assistant generates answers and also presents the information (paragraph or table), in the ESG report, from which it has generated the      │
│ response.                                                                                                                                                                                                      │
│                                                                                                                                                                                                                │
│ ## Related Work                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
│ The DocQA integrates multiple AI technologies, namely:                                                                                                                                                         │
│                                                                                                                                                                                                                │
│ Document Conversion: Converting unstructured documents, such as PDF files, into a machine-readable format is a challenging task in AI. Early strategies for document conversion were based on geometric layout │
│ analysis (Cattoni et al. 2000; Breuel 2002). Thanks to the availability of large annotated datasets (PubLayNet (Zhong et al. 2019), DocBank (Li et al. 2020), DocLayNet (Pfitzmann et al. 2022; Auer et al.    │
│ 2023), deep learning-based methods are routinely used. Modern approaches for recovering the structure of a document can be broadly divided into two categories: image-based or PDF representation-based .      │
│ Imagebased methods usually employ Transformer or CNN architectures on the images of pages (Zhang et al. 2023; Li et al. 2022; Huang et al. 2022). On the other hand, deep learning-                            │
│                                                                                                                                                                                                                │
│ Figure 1: System architecture: Simplified sketch of document question-answering pipeline.                                                                                                                      │
│ <!-- Picture description: The image depicts a document conversion process. It is a sequence of steps that includes document conversion, information retrieval, and response generation. The document           │
│ conversion step involves converting the document from a text format to a markdown format. The information retrieval step involves retrieving the document from a database or other source. The response        │
│ generation step involves generating a response from the information retrieval step. -->                                                                                                                        │
│                                                                                                                                                                                                                │
│ based language processing methods are applied on the native PDF content (generated by a single PDF printing command) (Auer et al. 2022; Livathinos et al. 2021; Staar et al. 2018).                            │
│                                                                                                                                                                                                                │
│                                                                                                                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Back to top