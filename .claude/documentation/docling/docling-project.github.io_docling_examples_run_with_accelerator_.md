---
url: "https://docling-project.github.io/docling/examples/run_with_accelerator/"
title: "Accelerator options - Docling"
---

# Accelerator options

In \[ \]:

Copied!

```
from pathlib import Path

```

from pathlib import Path

In \[ \]:

Copied!

```
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.accelerator\_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document\_converter import DocumentConverter, PdfFormatOption

In \[ \]:

Copied!

```
def main():
    input_doc = Path("./tests/data/pdf/2206.01062.pdf")

    # Explicitly set the accelerator
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.AUTO
    # )
    accelerator_options = AcceleratorOptions(
        num_threads=8, device=AcceleratorDevice.CPU
    )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.MPS
    # )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.CUDA
    # )

    # easyocr doesnt support cuda:N allocation, defaults to cuda:0
    # accelerator_options = AcceleratorOptions(num_threads=8, device="cuda:1")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator_options
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    # Enable the profiling to measure the time spent
    settings.debug.profile_pipeline_timings = True

    # Convert the document
    conversion_result = converter.convert(input_doc)
    doc = conversion_result.document

    # List with total time per document
    doc_conversion_secs = conversion_result.timings["pipeline_total"].times

    md = doc.export_to_markdown()
    print(md)
    print(f"Conversion secs: {doc_conversion_secs}")

```

def main():
input\_doc = Path("./tests/data/pdf/2206.01062.pdf")

# Explicitly set the accelerator
# accelerator\_options = AcceleratorOptions(
# num\_threads=8, device=AcceleratorDevice.AUTO
# )
accelerator\_options = AcceleratorOptions(
num\_threads=8, device=AcceleratorDevice.CPU
)
# accelerator\_options = AcceleratorOptions(
# num\_threads=8, device=AcceleratorDevice.MPS
# )
# accelerator\_options = AcceleratorOptions(
# num\_threads=8, device=AcceleratorDevice.CUDA
# )

# easyocr doesnt support cuda:N allocation, defaults to cuda:0
# accelerator\_options = AcceleratorOptions(num\_threads=8, device="cuda:1")

pipeline\_options = PdfPipelineOptions()
pipeline\_options.accelerator\_options = accelerator\_options
pipeline\_options.do\_ocr = True
pipeline\_options.do\_table\_structure = True
pipeline\_options.table\_structure\_options.do\_cell\_matching = True

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)

# Enable the profiling to measure the time spent
settings.debug.profile\_pipeline\_timings = True

# Convert the document
conversion\_result = converter.convert(input\_doc)
doc = conversion\_result.document

# List with total time per document
doc\_conversion\_secs = conversion\_result.timings\["pipeline\_total"\].times

md = doc.export\_to\_markdown()
print(md)
print(f"Conversion secs: {doc\_conversion\_secs}")

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top