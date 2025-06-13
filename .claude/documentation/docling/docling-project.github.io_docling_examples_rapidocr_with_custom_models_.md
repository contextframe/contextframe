---
url: "https://docling-project.github.io/docling/examples/rapidocr_with_custom_models/"
title: "RapidOCR with custom OCR models - Docling"
---

# RapidOCR with custom OCR models

In \[ \]:

Copied!

```
import os

```

import os

In \[ \]:

Copied!

```
from huggingface_hub import snapshot_download

```

from huggingface\_hub import snapshot\_download

In \[ \]:

Copied!

```
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import (
    ConversionResult,
    DocumentConverter,
    InputFormat,
    PdfFormatOption,
)

```

from docling.datamodel.pipeline\_options import PdfPipelineOptions, RapidOcrOptions
from docling.document\_converter import (
ConversionResult,
DocumentConverter,
InputFormat,
PdfFormatOption,
)

In \[ \]:

Copied!

```
def main():
    # Source document to convert
    source = "https://arxiv.org/pdf/2408.09869v4"

    # Download RappidOCR models from HuggingFace
    print("Downloading RapidOCR models")
    download_path = snapshot_download(repo_id="SWHL/RapidOCR")

    # Setup RapidOcrOptions for english detection
    det_model_path = os.path.join(
        download_path, "PP-OCRv4", "en_PP-OCRv3_det_infer.onnx"
    )
    rec_model_path = os.path.join(
        download_path, "PP-OCRv4", "ch_PP-OCRv4_rec_server_infer.onnx"
    )
    cls_model_path = os.path.join(
        download_path, "PP-OCRv3", "ch_ppocr_mobile_v2.0_cls_train.onnx"
    )
    ocr_options = RapidOcrOptions(
        det_model_path=det_model_path,
        rec_model_path=rec_model_path,
        cls_model_path=cls_model_path,
    )

    pipeline_options = PdfPipelineOptions(
        ocr_options=ocr_options,
    )

    # Convert the document
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            ),
        },
    )

    conversion_result: ConversionResult = converter.convert(source=source)
    doc = conversion_result.document
    md = doc.export_to_markdown()
    print(md)

```

def main():
# Source document to convert
source = "https://arxiv.org/pdf/2408.09869v4"

# Download RappidOCR models from HuggingFace
print("Downloading RapidOCR models")
download\_path = snapshot\_download(repo\_id="SWHL/RapidOCR")

# Setup RapidOcrOptions for english detection
det\_model\_path = os.path.join(
download\_path, "PP-OCRv4", "en\_PP-OCRv3\_det\_infer.onnx"
)
rec\_model\_path = os.path.join(
download\_path, "PP-OCRv4", "ch\_PP-OCRv4\_rec\_server\_infer.onnx"
)
cls\_model\_path = os.path.join(
download\_path, "PP-OCRv3", "ch\_ppocr\_mobile\_v2.0\_cls\_train.onnx"
)
ocr\_options = RapidOcrOptions(
det\_model\_path=det\_model\_path,
rec\_model\_path=rec\_model\_path,
cls\_model\_path=cls\_model\_path,
)

pipeline\_options = PdfPipelineOptions(
ocr\_options=ocr\_options,
)

# Convert the document
converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options,
),
},
)

conversion\_result: ConversionResult = converter.convert(source=source)
doc = conversion\_result.document
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