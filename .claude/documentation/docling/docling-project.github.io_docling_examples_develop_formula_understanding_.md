---
url: "https://docling-project.github.io/docling/examples/develop_formula_understanding/"
title: "Formula enrichment - Docling"
---

# Formula enrichment

WARNING
This example demonstrates only how to develop a new enrichment model.
It does not run the actual formula understanding model.

In \[ \]:

Copied!

```
import logging
from collections.abc import Iterable
from pathlib import Path

```

import logging
from collections.abc import Iterable
from pathlib import Path

In \[ \]:

Copied!

```
from docling_core.types.doc import DocItemLabel, DoclingDocument, NodeItem, TextItem

```

from docling\_core.types.doc import DocItemLabel, DoclingDocument, NodeItem, TextItem

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat, ItemAndImageEnrichmentElement
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.base_model import BaseItemAndImageEnrichmentModel
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

```

from docling.datamodel.base\_models import InputFormat, ItemAndImageEnrichmentElement
from docling.datamodel.pipeline\_options import PdfPipelineOptions
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.models.base\_model import BaseItemAndImageEnrichmentModel
from docling.pipeline.standard\_pdf\_pipeline import StandardPdfPipeline

In \[ \]:

Copied!

```
class ExampleFormulaUnderstandingPipelineOptions(PdfPipelineOptions):
    do_formula_understanding: bool = True

```

class ExampleFormulaUnderstandingPipelineOptions(PdfPipelineOptions):
do\_formula\_understanding: bool = True

In \[ \]:

Copied!

```
# A new enrichment model using both the document element and its image as input
class ExampleFormulaUnderstandingEnrichmentModel(BaseItemAndImageEnrichmentModel):
    images_scale = 2.6

    def __init__(self, enabled: bool):
        self.enabled = enabled

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        return (
            self.enabled
            and isinstance(element, TextItem)
            and element.label == DocItemLabel.FORMULA
        )

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[ItemAndImageEnrichmentElement],
    ) -> Iterable[NodeItem]:
        if not self.enabled:
            return

        for enrich_element in element_batch:
            enrich_element.image.show()

            yield enrich_element.item

```

\# A new enrichment model using both the document element and its image as input
class ExampleFormulaUnderstandingEnrichmentModel(BaseItemAndImageEnrichmentModel):
images\_scale = 2.6

def \_\_init\_\_(self, enabled: bool):
self.enabled = enabled

def is\_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
return (
self.enabled
and isinstance(element, TextItem)
and element.label == DocItemLabel.FORMULA
)

def \_\_call\_\_(
self,
doc: DoclingDocument,
element\_batch: Iterable\[ItemAndImageEnrichmentElement\],
) -\> Iterable\[NodeItem\]:
if not self.enabled:
return

for enrich\_element in element\_batch:
enrich\_element.image.show()

yield enrich\_element.item

In \[ \]:

Copied!

```
# How the pipeline can be extended.
class ExampleFormulaUnderstandingPipeline(StandardPdfPipeline):
    def __init__(self, pipeline_options: ExampleFormulaUnderstandingPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: ExampleFormulaUnderstandingPipelineOptions

        self.enrichment_pipe = [\
            ExampleFormulaUnderstandingEnrichmentModel(\
                enabled=self.pipeline_options.do_formula_understanding\
            )\
        ]

        if self.pipeline_options.do_formula_understanding:
            self.keep_backend = True

    @classmethod
    def get_default_options(cls) -> ExampleFormulaUnderstandingPipelineOptions:
        return ExampleFormulaUnderstandingPipelineOptions()

```

\# How the pipeline can be extended.
class ExampleFormulaUnderstandingPipeline(StandardPdfPipeline):
def \_\_init\_\_(self, pipeline\_options: ExampleFormulaUnderstandingPipelineOptions):
super().\_\_init\_\_(pipeline\_options)
self.pipeline\_options: ExampleFormulaUnderstandingPipelineOptions

self.enrichment\_pipe = \[\
ExampleFormulaUnderstandingEnrichmentModel(\
enabled=self.pipeline\_options.do\_formula\_understanding\
)\
\]

if self.pipeline\_options.do\_formula\_understanding:
self.keep\_backend = True

@classmethod
def get\_default\_options(cls) -> ExampleFormulaUnderstandingPipelineOptions:
return ExampleFormulaUnderstandingPipelineOptions()

In \[ \]:

Copied!

```
# Example main. In the final version, we simply have to set do_formula_understanding to true.
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2203.01017v2.pdf")

    pipeline_options = ExampleFormulaUnderstandingPipelineOptions()
    pipeline_options.do_formula_understanding = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ExampleFormulaUnderstandingPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    doc_converter.convert(input_doc_path)

```

\# Example main. In the final version, we simply have to set do\_formula\_understanding to true.
def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2203.01017v2.pdf")

pipeline\_options = ExampleFormulaUnderstandingPipelineOptions()
pipeline\_options.do\_formula\_understanding = True

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=ExampleFormulaUnderstandingPipeline,
pipeline\_options=pipeline\_options,
)
}
)
doc\_converter.convert(input\_doc\_path)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top