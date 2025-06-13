---
url: "https://docling-project.github.io/docling/examples/minimal_vlm_pipeline/"
title: "VLM pipeline with SmolDocling - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/minimal_vlm_pipeline/#using-simple-default-values)

# VLM pipeline with SmolDocling

In \[ \]:

Copied!

```
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

```

from docling.datamodel import vlm\_model\_specs
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
VlmPipelineOptions,
)
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm\_pipeline import VlmPipeline

In \[ \]:

Copied!

```
source = "https://arxiv.org/pdf/2501.17887"

```

source = "https://arxiv.org/pdf/2501.17887"

##### USING SIMPLE DEFAULT VALUES [¶](https://docling-project.github.io/docling/examples/minimal_vlm_pipeline/\#using-simple-default-values)

- SmolDocling model
- Using the transformers framework

In \[ \]:

Copied!

```
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
        ),
    }
)

```

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=VlmPipeline,
),
}
)

In \[ \]:

Copied!

```
doc = converter.convert(source=source).document

```

doc = converter.convert(source=source).document

In \[ \]:

Copied!

```
print(doc.export_to_markdown())

```

print(doc.export\_to\_markdown())

##### USING MACOS MPS ACCELERATOR [¶](https://docling-project.github.io/docling/examples/minimal_vlm_pipeline/\#using-macos-mps-accelerator)

For more options see the compare\_vlm\_models.py example.

In \[ \]:

Copied!

```
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLDOCLING_MLX,
)

```

pipeline\_options = VlmPipelineOptions(
vlm\_options=vlm\_model\_specs.SMOLDOCLING\_MLX,
)

In \[ \]:

Copied!

```
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

```

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=VlmPipeline,
pipeline\_options=pipeline\_options,
),
}
)

In \[ \]:

Copied!

```
doc = converter.convert(source=source).document

```

doc = converter.convert(source=source).document

In \[ \]:

Copied!

```
print(doc.export_to_markdown())

```

print(doc.export\_to\_markdown())

Back to top