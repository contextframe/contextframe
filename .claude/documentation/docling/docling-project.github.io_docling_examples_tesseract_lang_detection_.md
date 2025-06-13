---
url: "https://docling-project.github.io/docling/examples/tesseract_lang_detection/"
title: "Automatic OCR language detection with tesseract - Docling"
---

# Automatic OCR language detection with tesseract

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

    # Set lang=["auto"] with a tesseract OCR engine: TesseractOcrOptions, TesseractCliOcrOptions
    # ocr_options = TesseractOcrOptions(lang=["auto"])
    ocr_options = TesseractCliOcrOptions(lang=["auto"])

    pipeline_options = PdfPipelineOptions(
        do_ocr=True, force_full_page_ocr=True, ocr_options=ocr_options
    )

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

# Set lang=\["auto"\] with a tesseract OCR engine: TesseractOcrOptions, TesseractCliOcrOptions
# ocr\_options = TesseractOcrOptions(lang=\["auto"\])
ocr\_options = TesseractCliOcrOptions(lang=\["auto"\])

pipeline\_options = PdfPipelineOptions(
do\_ocr=True, force\_full\_page\_ocr=True, ocr\_options=ocr\_options
)

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