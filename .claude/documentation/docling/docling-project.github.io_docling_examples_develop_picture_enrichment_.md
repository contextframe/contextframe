---
url: "https://docling-project.github.io/docling/examples/develop_picture_enrichment/"
title: "Figure enrichment - Docling"
---

# Figure enrichment

WARNING
This example demonstrates only how to develop a new enrichment model.
It does not run the actual picture classifier model.

In \[ \]:

Copied!

```
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

```

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

In \[ \]:

Copied!

```
from docling_core.types.doc import (
    DoclingDocument,
    NodeItem,
    PictureClassificationClass,
    PictureClassificationData,
    PictureItem,
)

```

from docling\_core.types.doc import (
DoclingDocument,
NodeItem,
PictureClassificationClass,
PictureClassificationData,
PictureItem,
)

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.base_model import BaseEnrichmentModel
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import PdfPipelineOptions
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.models.base\_model import BaseEnrichmentModel
from docling.pipeline.standard\_pdf\_pipeline import StandardPdfPipeline

In \[ \]:

Copied!

```
class ExamplePictureClassifierPipelineOptions(PdfPipelineOptions):
    do_picture_classifer: bool = True

```

class ExamplePictureClassifierPipelineOptions(PdfPipelineOptions):
do\_picture\_classifer: bool = True

In \[ \]:

Copied!

```
class ExamplePictureClassifierEnrichmentModel(BaseEnrichmentModel):
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        return self.enabled and isinstance(element, PictureItem)

    def __call__(
        self, doc: DoclingDocument, element_batch: Iterable[NodeItem]
    ) -> Iterable[Any]:
        if not self.enabled:
            return

        for element in element_batch:
            assert isinstance(element, PictureItem)

            # uncomment this to interactively visualize the image
            # element.get_image(doc).show()

            element.annotations.append(
                PictureClassificationData(
                    provenance="example_classifier-0.0.1",
                    predicted_classes=[\
                        PictureClassificationClass(class_name="dummy", confidence=0.42)\
                    ],
                )
            )

            yield element

```

class ExamplePictureClassifierEnrichmentModel(BaseEnrichmentModel):
def \_\_init\_\_(self, enabled: bool):
self.enabled = enabled

def is\_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
return self.enabled and isinstance(element, PictureItem)

def \_\_call\_\_(
self, doc: DoclingDocument, element\_batch: Iterable\[NodeItem\]
) -\> Iterable\[Any\]:
if not self.enabled:
return

for element in element\_batch:
assert isinstance(element, PictureItem)

# uncomment this to interactively visualize the image
# element.get\_image(doc).show()

element.annotations.append(
PictureClassificationData(
provenance="example\_classifier-0.0.1",
predicted\_classes=\[\
PictureClassificationClass(class\_name="dummy", confidence=0.42)\
\],
)
)

yield element

In \[ \]:

Copied!

```
class ExamplePictureClassifierPipeline(StandardPdfPipeline):
    def __init__(self, pipeline_options: ExamplePictureClassifierPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: ExamplePictureClassifierPipeline

        self.enrichment_pipe = [\
            ExamplePictureClassifierEnrichmentModel(\
                enabled=pipeline_options.do_picture_classifer\
            )\
        ]

    @classmethod
    def get_default_options(cls) -> ExamplePictureClassifierPipelineOptions:
        return ExamplePictureClassifierPipelineOptions()

```

class ExamplePictureClassifierPipeline(StandardPdfPipeline):
def \_\_init\_\_(self, pipeline\_options: ExamplePictureClassifierPipelineOptions):
super().\_\_init\_\_(pipeline\_options)
self.pipeline\_options: ExamplePictureClassifierPipeline

self.enrichment\_pipe = \[\
ExamplePictureClassifierEnrichmentModel(\
enabled=pipeline\_options.do\_picture\_classifer\
)\
\]

@classmethod
def get\_default\_options(cls) -> ExamplePictureClassifierPipelineOptions:
return ExamplePictureClassifierPipelineOptions()

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")

    pipeline_options = ExamplePictureClassifierPipelineOptions()
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ExamplePictureClassifierPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    result = doc_converter.convert(input_doc_path)

    for element, _level in result.document.iterate_items():
        if isinstance(element, PictureItem):
            print(
                f"The model populated the `data` portion of picture {element.self_ref}:\n{element.annotations}"
            )

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")

pipeline\_options = ExamplePictureClassifierPipelineOptions()
pipeline\_options.images\_scale = 2.0
pipeline\_options.generate\_picture\_images = True

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=ExamplePictureClassifierPipeline,
pipeline\_options=pipeline\_options,
)
}
)
result = doc\_converter.convert(input\_doc\_path)

for element, \_level in result.document.iterate\_items():
if isinstance(element, PictureItem):
print(
f"The model populated the \`data\` portion of picture {element.self\_ref}:\\n{element.annotations}"
)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top