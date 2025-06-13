---
url: "https://docling-project.github.io/docling/examples/full_page_ocr/"
title: "Force full page OCR - Docling"
---

# Force full page OCR

In \[ \]:

Copied!

```
from pathlib import Path

```

from pathlib import Path

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import (
PdfPipelineOptions,
TesseractCliOcrOptions,
)
from docling.document\_converter import DocumentConverter, PdfFormatOption

In \[ \]:

Copied!

```
def main():
    input_doc = Path("./tests/data/pdf/2206.01062.pdf")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    # Any of the OCR options can be used:EasyOcrOptions, TesseractOcrOptions, TesseractCliOcrOptions, OcrMacOptions(Mac only), RapidOcrOptions
    # ocr_options = EasyOcrOptions(force_full_page_ocr=True)
    # ocr_options = TesseractOcrOptions(force_full_page_ocr=True)
    # ocr_options = OcrMacOptions(force_full_page_ocr=True)
    # ocr_options = RapidOcrOptions(force_full_page_ocr=True)
    ocr_options = TesseractCliOcrOptions(force_full_page_ocr=True)
    pipeline_options.ocr_options = ocr_options

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    doc = converter.convert(input_doc).document
    md = doc.export_to_markdown()
    print(md)

```

def main():
input\_doc = Path("./tests/data/pdf/2206.01062.pdf")

pipeline\_options = PdfPipelineOptions()
pipeline\_options.do\_ocr = True
pipeline\_options.do\_table\_structure = True
pipeline\_options.table\_structure\_options.do\_cell\_matching = True

# Any of the OCR options can be used:EasyOcrOptions, TesseractOcrOptions, TesseractCliOcrOptions, OcrMacOptions(Mac only), RapidOcrOptions
# ocr\_options = EasyOcrOptions(force\_full\_page\_ocr=True)
# ocr\_options = TesseractOcrOptions(force\_full\_page\_ocr=True)
# ocr\_options = OcrMacOptions(force\_full\_page\_ocr=True)
# ocr\_options = RapidOcrOptions(force\_full\_page\_ocr=True)
ocr\_options = TesseractCliOcrOptions(force\_full\_page\_ocr=True)
pipeline\_options.ocr\_options = ocr\_options

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
)
}
)

doc = converter.convert(input\_doc).document
md = doc.export\_to\_markdown()
print(md)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top