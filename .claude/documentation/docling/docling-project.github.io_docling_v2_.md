---
url: "https://docling-project.github.io/docling/v2/"
title: "V2 - Docling"
---

[Skip to content](https://docling-project.github.io/docling/v2/#whats-new)

# V2

## What's new

Docling v2 introduces several new features:

- Understands and converts PDF, MS Word, MS Powerpoint, HTML and several image formats
- Produces a new, universal document representation which can encapsulate document hierarchy
- Comes with a fresh new API and CLI

## Changes in Docling v2

### CLI

We updated the command line syntax of Docling v2 to support many formats. Examples are seen below.

```
# Convert a single file to Markdown (default)
docling myfile.pdf

# Convert a single file to Markdown and JSON, without OCR
docling myfile.pdf --to json --to md --no-ocr

# Convert PDF files in input directory to Markdown (default)
docling ./input/dir --from pdf

# Convert PDF and Word files in input directory to Markdown and JSON
docling ./input/dir --from pdf --from docx --to md --to json --output ./scratch

# Convert all supported files in input directory to Markdown, but abort on first error
docling ./input/dir --output ./scratch --abort-on-error

```

**Notable changes from Docling v1:**

- The standalone switches for different export formats are removed, and replaced with `--from` and `--to` arguments, to define input and output formats respectively.
- The new `--abort-on-error` will abort any batch conversion as soon an error is encountered
- The `--backend` option for PDFs was removed

### Setting up a `DocumentConverter`

To accommodate many input formats, we changed the way you need to set up your `DocumentConverter` object.
You can now define a list of allowed formats on the `DocumentConverter` initialization, and specify custom options
per-format if desired. By default, all supported formats are allowed. If you don't provide `format_options`, defaults
will be used for all `allowed_formats`.

Format options can include the pipeline class to use, the options to provide to the pipeline, and the document backend.
They are provided as format-specific types, such as `PdfFormatOption` or `WordFormatOption`, as seen below.

```
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

## Default initialization still works as before:
# doc_converter = DocumentConverter()

# previous `PipelineOptions` is now `PdfPipelineOptions`
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True
#...

## Custom options are now defined per format.
doc_converter = (
    DocumentConverter(  # all of the below is optional, has internal defaults.
        allowed_formats=[\
            InputFormat.PDF,\
            InputFormat.IMAGE,\
            InputFormat.DOCX,\
            InputFormat.HTML,\
            InputFormat.PPTX,\
        ],  # whitelist formats, non-matching files are ignored.
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, # pipeline options go here.
                backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline # default for office formats and HTML
            ),
        },
    )
)

```

**Note**: If you work only with defaults, all remains the same as in Docling v1.

More options are shown in the following example units:

- [run\_with\_formats.py](https://docling-project.github.io/docling/examples/run_with_formats/)
- [custom\_convert.py](https://docling-project.github.io/docling/examples/custom_convert/)

### Converting documents

We have simplified the way you can feed input to the `DocumentConverter` and renamed the conversion methods for
better semantics. You can now call the conversion directly with a single file, or a list of input files,
or `DocumentStream` objects, without constructing a `DocumentConversionInput` object first.

- `DocumentConverter.convert` now converts a single file input (previously `DocumentConverter.convert_single`).
- `DocumentConverter.convert_all` now converts many files at once (previously `DocumentConverter.convert`).

```
...
from docling.datamodel.document import ConversionResult
## Convert a single file (from URL or local path)
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Convert several files at once:

input_files = [\
    "tests/data/html/wiki_duck.html",\
    "tests/data/docx/word_sample.docx",\
    "tests/data/docx/lorem_ipsum.docx",\
    "tests/data/pptx/powerpoint_sample.pptx",\
    "tests/data/2305.03393v1-pg9-img.png",\
    "tests/data/pdf/2206.01062.pdf",\
]

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(input_files) # previously `convert`

```

Through the `raises_on_error` argument, you can also control if the conversion should raise exceptions when first
encountering a problem, or resiliently convert all files first and reflect errors in each file's conversion status.
By default, any error is immediately raised and the conversion aborts (previously, exceptions were swallowed).

```
...
conv_results_iter = doc_converter.convert_all(input_files, raises_on_error=False) # previously `convert`

```

### Access document structures

We have simplified how you can access and export the converted document data, too. Our universal document representation
is now available in conversion results as a `DoclingDocument` object.
`DoclingDocument` provides a neat set of APIs to construct, iterate and export content in the document, as shown below.

```
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Inspect the converted document:
conv_result.document.print_element_tree()

## Iterate the elements in reading order, including hierarchy level:
for item, level in conv_result.document.iterate_items():
    if isinstance(item, TextItem):
        print(item.text)
    elif isinstance(item, TableItem):
        table_df: pd.DataFrame = item.export_to_dataframe()
        print(table_df.to_markdown())
    elif ...:
        #...

```

**Note**: While it is deprecated, you can _still_ work with the Docling v1 document representation, it is available as:

```
conv_result.legacy_document # provides the representation in previous ExportedCCSDocument type

```

### Export into JSON, Markdown, Doctags

**Note**: All `render_...` methods in `ConversionResult` have been removed in Docling v2,
and are now available on `DoclingDocument` as:

- `DoclingDocument.export_to_dict`
- `DoclingDocument.export_to_markdown`
- `DoclingDocument.export_to_document_tokens`

```
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Export to desired format:
print(json.dumps(conv_res.document.export_to_dict()))
print(conv_res.document.export_to_markdown())
print(conv_res.document.export_to_document_tokens())

```

**Note**: While it is deprecated, you can _still_ export Docling v1 JSON format. This is available through the same
methods as on the `DoclingDocument` type:

```
## Export legacy document representation to desired format, for v1 compatibility:
print(json.dumps(conv_res.legacy_document.export_to_dict()))
print(conv_res.legacy_document.export_to_markdown())
print(conv_res.legacy_document.export_to_document_tokens())

```

### Reload a `DoclingDocument` stored as JSON

You can save and reload a `DoclingDocument` to disk in JSON format using the following codes:

```
# Save to disk:
doc: DoclingDocument = conv_res.document # produced from conversion result...

with Path("./doc.json").open("w") as fp:
    fp.write(json.dumps(doc.export_to_dict())) # use `export_to_dict` to ensure consistency

# Load from disk:
with Path("./doc.json").open("r") as fp:
    doc_dict = json.loads(fp.read())
    doc = DoclingDocument.model_validate(doc_dict) # use standard pydantic API to populate doc

```

### Chunking

Docling v2 defines new base classes for chunking:

- `BaseMeta` for chunk metadata
- `BaseChunk` containing the chunk text and metadata, and
- `BaseChunker` for chunkers, producing chunks out of a `DoclingDocument`.

Additionally, it provides an updated `HierarchicalChunker` implementation, which
leverages the new `DoclingDocument` and provides a new, richer chunk output format, including:

- the respective doc items for grounding
- any applicable headings for context
- any applicable captions for context

For an example, check out [Chunking usage](https://docling-project.github.io/docling/v2/usage.md#chunking).

Back to top