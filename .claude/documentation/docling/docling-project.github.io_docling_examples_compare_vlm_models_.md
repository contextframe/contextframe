---
url: "https://docling-project.github.io/docling/examples/compare_vlm_models/"
title: "Compare VLM models - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/compare_vlm_models/#compare-vlm-models)

# Compare VLM models [¶](https://docling-project.github.io/docling/examples/compare_vlm_models/\#compare-vlm-models)

This example runs the VLM pipeline with different vision-language models.
Their runtime as well output quality is compared.

In \[ \]:

Copied!

```
import json
import sys
import time
from pathlib import Path

```

import json
import sys
import time
from pathlib import Path

In \[ \]:

Copied!

```
from docling_core.types.doc import DocItemLabel, ImageRefMode
from docling_core.types.doc.document import DEFAULT_EXPORT_LABELS
from tabulate import tabulate

```

from docling\_core.types.doc import DocItemLabel, ImageRefMode
from docling\_core.types.doc.document import DEFAULT\_EXPORT\_LABELS
from tabulate import tabulate

In \[ \]:

Copied!

```
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.datamodel.pipeline_options_vlm_model import InferenceFramework
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

```

from docling.datamodel import vlm\_model\_specs
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
VlmPipelineOptions,
)
from docling.datamodel.pipeline\_options\_vlm\_model import InferenceFramework
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm\_pipeline import VlmPipeline

In \[ \]:

Copied!

```
def convert(sources: list[Path], converter: DocumentConverter):
    model_id = pipeline_options.vlm_options.repo_id.replace("/", "_")
    framework = pipeline_options.vlm_options.inference_framework
    for source in sources:
        print("================================================")
        print("Processing...")
        print(f"Source: {source}")
        print("---")
        print(f"Model: {model_id}")
        print(f"Framework: {framework}")
        print("================================================")
        print("")

        res = converter.convert(source)

        print("")

        fname = f"{res.input.file.stem}-{model_id}-{framework}"

        inference_time = 0.0
        for i, page in enumerate(res.pages):
            inference_time += page.predictions.vlm_response.generation_time
            print("")
            print(
                f" ---------- Predicted page {i} in {pipeline_options.vlm_options.response_format} in {page.predictions.vlm_response.generation_time} [sec]:"
            )
            print(page.predictions.vlm_response.text)
            print(" ---------- ")

        print("===== Final output of the converted document =======")

        with (out_path / f"{fname}.json").open("w") as fp:
            fp.write(json.dumps(res.document.export_to_dict()))

        res.document.save_as_json(
            out_path / f"{fname}.json",
            image_mode=ImageRefMode.PLACEHOLDER,
        )
        print(f" => produced {out_path / fname}.json")

        res.document.save_as_markdown(
            out_path / f"{fname}.md",
            image_mode=ImageRefMode.PLACEHOLDER,
        )
        print(f" => produced {out_path / fname}.md")

        res.document.save_as_html(
            out_path / f"{fname}.html",
            image_mode=ImageRefMode.EMBEDDED,
            labels=[*DEFAULT_EXPORT_LABELS, DocItemLabel.FOOTNOTE],
            split_page_view=True,
        )
        print(f" => produced {out_path / fname}.html")

        pg_num = res.document.num_pages()
        print("")
        print(
            f"Total document prediction time: {inference_time:.2f} seconds, pages: {pg_num}"
        )
        print("====================================================")

        return [\
            source,\
            model_id,\
            str(framework),\
            pg_num,\
            inference_time,\
        ]

```

def convert(sources: list\[Path\], converter: DocumentConverter):
model\_id = pipeline\_options.vlm\_options.repo\_id.replace("/", "\_")
framework = pipeline\_options.vlm\_options.inference\_framework
for source in sources:
print("================================================")
print("Processing...")
print(f"Source: {source}")
print("---")
print(f"Model: {model\_id}")
print(f"Framework: {framework}")
print("================================================")
print("")

res = converter.convert(source)

print("")

fname = f"{res.input.file.stem}-{model\_id}-{framework}"

inference\_time = 0.0
for i, page in enumerate(res.pages):
inference\_time += page.predictions.vlm\_response.generation\_time
print("")
print(
f" ---------- Predicted page {i} in {pipeline\_options.vlm\_options.response\_format} in {page.predictions.vlm\_response.generation\_time} \[sec\]:"
)
print(page.predictions.vlm\_response.text)
print(" ---------- ")

print("===== Final output of the converted document =======")

with (out\_path / f"{fname}.json").open("w") as fp:
fp.write(json.dumps(res.document.export\_to\_dict()))

res.document.save\_as\_json(
out\_path / f"{fname}.json",
image\_mode=ImageRefMode.PLACEHOLDER,
)
print(f" => produced {out\_path / fname}.json")

res.document.save\_as\_markdown(
out\_path / f"{fname}.md",
image\_mode=ImageRefMode.PLACEHOLDER,
)
print(f" => produced {out\_path / fname}.md")

res.document.save\_as\_html(
out\_path / f"{fname}.html",
image\_mode=ImageRefMode.EMBEDDED,
labels=\[\*DEFAULT\_EXPORT\_LABELS, DocItemLabel.FOOTNOTE\],
split\_page\_view=True,
)
print(f" => produced {out\_path / fname}.html")

pg\_num = res.document.num\_pages()
print("")
print(
f"Total document prediction time: {inference\_time:.2f} seconds, pages: {pg\_num}"
)
print("====================================================")

return \[\
source,\
model\_id,\
str(framework),\
pg\_num,\
inference\_time,\
\]

In \[ \]:

Copied!

```
if __name__ == "__main__":
    sources = [\
        "tests/data/pdf/2305.03393v1-pg9.pdf",\
    ]

    out_path = Path("scratch")
    out_path.mkdir(parents=True, exist_ok=True)

    ## Use VlmPipeline
    pipeline_options = VlmPipelineOptions()
    pipeline_options.generate_page_images = True

    ## On GPU systems, enable flash_attention_2 with CUDA:
    # pipeline_options.accelerator_options.device = AcceleratorDevice.CUDA
    # pipeline_options.accelerator_options.cuda_use_flash_attention2 = True

    vlm_models = [\
        ## DocTags / SmolDocling models\
        vlm_model_specs.SMOLDOCLING_MLX,\
        vlm_model_specs.SMOLDOCLING_TRANSFORMERS,\
        ## Markdown models (using MLX framework)\
        vlm_model_specs.QWEN25_VL_3B_MLX,\
        vlm_model_specs.PIXTRAL_12B_MLX,\
        vlm_model_specs.GEMMA3_12B_MLX,\
        ## Markdown models (using Transformers framework)\
        vlm_model_specs.GRANITE_VISION_TRANSFORMERS,\
        vlm_model_specs.PHI4_TRANSFORMERS,\
        vlm_model_specs.PIXTRAL_12B_TRANSFORMERS,\
    ]

    # Remove MLX models if not on Mac
    if sys.platform != "darwin":
        vlm_models = [\
            m for m in vlm_models if m.inference_framework != InferenceFramework.MLX\
        ]

    rows = []
    for vlm_options in vlm_models:
        pipeline_options.vlm_options = vlm_options

        ## Set up pipeline for PDF or image inputs
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
                InputFormat.IMAGE: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
            },
        )

        row = convert(sources=sources, converter=converter)
        rows.append(row)

        print(
            tabulate(
                rows, headers=["source", "model_id", "framework", "num_pages", "time"]
            )
        )

        print("see if memory gets released ...")
        time.sleep(10)

```

if \_\_name\_\_ == "\_\_main\_\_":
sources = \[\
"tests/data/pdf/2305.03393v1-pg9.pdf",\
\]

out\_path = Path("scratch")
out\_path.mkdir(parents=True, exist\_ok=True)

## Use VlmPipeline
pipeline\_options = VlmPipelineOptions()
pipeline\_options.generate\_page\_images = True

## On GPU systems, enable flash\_attention\_2 with CUDA:
# pipeline\_options.accelerator\_options.device = AcceleratorDevice.CUDA
# pipeline\_options.accelerator\_options.cuda\_use\_flash\_attention2 = True

vlm\_models = \[\
## DocTags / SmolDocling models\
vlm\_model\_specs.SMOLDOCLING\_MLX,\
vlm\_model\_specs.SMOLDOCLING\_TRANSFORMERS,\
## Markdown models (using MLX framework)\
vlm\_model\_specs.QWEN25\_VL\_3B\_MLX,\
vlm\_model\_specs.PIXTRAL\_12B\_MLX,\
vlm\_model\_specs.GEMMA3\_12B\_MLX,\
## Markdown models (using Transformers framework)\
vlm\_model\_specs.GRANITE\_VISION\_TRANSFORMERS,\
vlm\_model\_specs.PHI4\_TRANSFORMERS,\
vlm\_model\_specs.PIXTRAL\_12B\_TRANSFORMERS,\
\]

# Remove MLX models if not on Mac
if sys.platform != "darwin":
vlm\_models = \[\
m for m in vlm\_models if m.inference\_framework != InferenceFramework.MLX\
\]

rows = \[\]
for vlm\_options in vlm\_models:
pipeline\_options.vlm\_options = vlm\_options

## Set up pipeline for PDF or image inputs
converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=VlmPipeline,
pipeline\_options=pipeline\_options,
),
InputFormat.IMAGE: PdfFormatOption(
pipeline\_cls=VlmPipeline,
pipeline\_options=pipeline\_options,
),
},
)

row = convert(sources=sources, converter=converter)
rows.append(row)

print(
tabulate(
rows, headers=\["source", "model\_id", "framework", "num\_pages", "time"\]
)
)

print("see if memory gets released ...")
time.sleep(10)

Back to top