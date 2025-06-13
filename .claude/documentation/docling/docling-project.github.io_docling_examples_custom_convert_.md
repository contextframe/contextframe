---
url: "https://docling-project.github.io/docling/examples/custom_convert/"
title: "Custom conversion - Docling"
---

# Custom conversion

In \[ \]:

Copied!

```
import json
import logging
import time
from pathlib import Path

```

import json
import logging
import time
from pathlib import Path

In \[ \]:

Copied!

```
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.accelerator\_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
PdfPipelineOptions,
)
from docling.document\_converter import DocumentConverter, PdfFormatOption

In \[ \]:

Copied!

```
_log = logging.getLogger(__name__)

```

\_log = logging.getLogger(\_\_name\_\_)

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")

    ###########################################################################

    # The following sections contain a combination of PipelineOptions
    # and PDF Backends for various configurations.
    # Uncomment one section at the time to see the differences in the output.

    # PyPdfium without EasyOCR
    # --------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = False
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = False

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(
    #             pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
    #         )
    #     }
    # )

    # PyPdfium with EasyOCR
    # -----------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(
    #             pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
    #         )
    #     }
    # )

    # Docling Parse without EasyOCR
    # -------------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = False
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with EasyOCR
    # ----------------------
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["es"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Docling Parse with EasyOCR (CPU only)
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.ocr_options.use_gpu = False  # <-- set this.
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with Tesseract
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = TesseractOcrOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with Tesseract CLI
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = TesseractCliOcrOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with ocrmac(Mac only)
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = OcrMacOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    ###########################################################################

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    end_time = time.time() - start_time

    _log.info(f"Document converted in {end_time:.2f} seconds.")

    ## Export results
    output_dir = Path("scratch")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem

    # Export Deep Search document JSON format:
    with (output_dir / f"{doc_filename}.json").open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(conv_result.document.export_to_dict()))

    # Export Text format:
    with (output_dir / f"{doc_filename}.txt").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_text())

    # Export Markdown format:
    with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown())

    # Export Document Tags format:
    with (output_dir / f"{doc_filename}.doctags").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_document_tokens())

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")

###########################################################################

# The following sections contain a combination of PipelineOptions
# and PDF Backends for various configurations.
# Uncomment one section at the time to see the differences in the output.

# PyPdfium without EasyOCR
# --------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = False
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = False

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(
# pipeline\_options=pipeline\_options, backend=PyPdfiumDocumentBackend
# )
# }
# )

# PyPdfium with EasyOCR
# -----------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = True
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(
# pipeline\_options=pipeline\_options, backend=PyPdfiumDocumentBackend
# )
# }
# )

# Docling Parse without EasyOCR
# -------------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = False
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
# }
# )

# Docling Parse with EasyOCR
# ----------------------
pipeline\_options = PdfPipelineOptions()
pipeline\_options.do\_ocr = True
pipeline\_options.do\_table\_structure = True
pipeline\_options.table\_structure\_options.do\_cell\_matching = True
pipeline\_options.ocr\_options.lang = \["es"\]
pipeline\_options.accelerator\_options = AcceleratorOptions(
num\_threads=4, device=AcceleratorDevice.AUTO
)

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
}
)

# Docling Parse with EasyOCR (CPU only)
# ----------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = True
# pipeline\_options.ocr\_options.use\_gpu = False # <-- set this.
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
# }
# )

# Docling Parse with Tesseract
# ----------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = True
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True
# pipeline\_options.ocr\_options = TesseractOcrOptions()

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
# }
# )

# Docling Parse with Tesseract CLI
# ----------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = True
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True
# pipeline\_options.ocr\_options = TesseractCliOcrOptions()

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
# }
# )

# Docling Parse with ocrmac(Mac only)
# ----------------------
# pipeline\_options = PdfPipelineOptions()
# pipeline\_options.do\_ocr = True
# pipeline\_options.do\_table\_structure = True
# pipeline\_options.table\_structure\_options.do\_cell\_matching = True
# pipeline\_options.ocr\_options = OcrMacOptions()

# doc\_converter = DocumentConverter(
# format\_options={
# InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
# }
# )

###########################################################################

start\_time = time.time()
conv\_result = doc\_converter.convert(input\_doc\_path)
end\_time = time.time() - start\_time

\_log.info(f"Document converted in {end\_time:.2f} seconds.")

## Export results
output\_dir = Path("scratch")
output\_dir.mkdir(parents=True, exist\_ok=True)
doc\_filename = conv\_result.input.file.stem

# Export Deep Search document JSON format:
with (output\_dir / f"{doc\_filename}.json").open("w", encoding="utf-8") as fp:
fp.write(json.dumps(conv\_result.document.export\_to\_dict()))

# Export Text format:
with (output\_dir / f"{doc\_filename}.txt").open("w", encoding="utf-8") as fp:
fp.write(conv\_result.document.export\_to\_text())

# Export Markdown format:
with (output\_dir / f"{doc\_filename}.md").open("w", encoding="utf-8") as fp:
fp.write(conv\_result.document.export\_to\_markdown())

# Export Document Tags format:
with (output\_dir / f"{doc\_filename}.doctags").open("w", encoding="utf-8") as fp:
fp.write(conv\_result.document.export\_to\_document\_tokens())

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top