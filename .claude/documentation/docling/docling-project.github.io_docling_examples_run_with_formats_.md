---
url: "https://docling-project.github.io/docling/examples/run_with_formats/"
title: "Multi-format conversion - Docling"
---

# Multi-format conversion

In \[ \]:

Copied!

```
import json
import logging
from pathlib import Path

```

import json
import logging
from pathlib import Path

In \[ \]:

Copied!

```
import yaml

```

import yaml

In \[ \]:

Copied!

```
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

```

from docling.backend.pypdfium2\_backend import PyPdfiumDocumentBackend
from docling.datamodel.base\_models import InputFormat
from docling.document\_converter import (
DocumentConverter,
PdfFormatOption,
WordFormatOption,
)
from docling.pipeline.simple\_pipeline import SimplePipeline
from docling.pipeline.standard\_pdf\_pipeline import StandardPdfPipeline

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
    input_paths = [\
        Path("README.md"),\
        Path("tests/data/html/wiki_duck.html"),\
        Path("tests/data/docx/word_sample.docx"),\
        Path("tests/data/docx/lorem_ipsum.docx"),\
        Path("tests/data/pptx/powerpoint_sample.pptx"),\
        Path("tests/data/2305.03393v1-pg9-img.png"),\
        Path("tests/data/pdf/2206.01062.pdf"),\
        Path("tests/data/asciidoc/test_01.asciidoc"),\
    ]

    ## for defaults use:
    # doc_converter = DocumentConverter()

    ## to customize use:

    doc_converter = (
        DocumentConverter(  # all of the below is optional, has internal defaults.
            allowed_formats=[\
                InputFormat.PDF,\
                InputFormat.IMAGE,\
                InputFormat.DOCX,\
                InputFormat.HTML,\
                InputFormat.PPTX,\
                InputFormat.ASCIIDOC,\
                InputFormat.CSV,\
                InputFormat.MD,\
            ],  # whitelist formats, non-matching files are ignored.
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_cls=SimplePipeline  # , backend=MsWordDocumentBackend
                ),
            },
        )
    )

    conv_results = doc_converter.convert_all(input_paths)

    for res in conv_results:
        out_path = Path("scratch")
        print(
            f"Document {res.input.file.name} converted."
            f"\nSaved markdown output to: {out_path!s}"
        )
        _log.debug(res.document._export_to_indented_text(max_text_len=16))
        # Export Docling document format to markdowndoc:
        with (out_path / f"{res.input.file.stem}.md").open("w") as fp:
            fp.write(res.document.export_to_markdown())

        with (out_path / f"{res.input.file.stem}.json").open("w") as fp:
            fp.write(json.dumps(res.document.export_to_dict()))

        with (out_path / f"{res.input.file.stem}.yaml").open("w") as fp:
            fp.write(yaml.safe_dump(res.document.export_to_dict()))

```

def main():
input\_paths = \[\
Path("README.md"),\
Path("tests/data/html/wiki\_duck.html"),\
Path("tests/data/docx/word\_sample.docx"),\
Path("tests/data/docx/lorem\_ipsum.docx"),\
Path("tests/data/pptx/powerpoint\_sample.pptx"),\
Path("tests/data/2305.03393v1-pg9-img.png"),\
Path("tests/data/pdf/2206.01062.pdf"),\
Path("tests/data/asciidoc/test\_01.asciidoc"),\
\]

## for defaults use:
# doc\_converter = DocumentConverter()

## to customize use:

doc\_converter = (
DocumentConverter( # all of the below is optional, has internal defaults.
allowed\_formats=\[\
InputFormat.PDF,\
InputFormat.IMAGE,\
InputFormat.DOCX,\
InputFormat.HTML,\
InputFormat.PPTX,\
InputFormat.ASCIIDOC,\
InputFormat.CSV,\
InputFormat.MD,\
\], # whitelist formats, non-matching files are ignored.
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
),
InputFormat.DOCX: WordFormatOption(
pipeline\_cls=SimplePipeline # , backend=MsWordDocumentBackend
),
},
)
)

conv\_results = doc\_converter.convert\_all(input\_paths)

for res in conv\_results:
out\_path = Path("scratch")
print(
f"Document {res.input.file.name} converted."
f"\\nSaved markdown output to: {out\_path!s}"
)
\_log.debug(res.document.\_export\_to\_indented\_text(max\_text\_len=16))
# Export Docling document format to markdowndoc:
with (out\_path / f"{res.input.file.stem}.md").open("w") as fp:
fp.write(res.document.export\_to\_markdown())

with (out\_path / f"{res.input.file.stem}.json").open("w") as fp:
fp.write(json.dumps(res.document.export\_to\_dict()))

with (out\_path / f"{res.input.file.stem}.yaml").open("w") as fp:
fp.write(yaml.safe\_dump(res.document.export\_to\_dict()))

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top