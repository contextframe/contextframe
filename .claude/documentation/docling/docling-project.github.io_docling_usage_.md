---
url: "https://docling-project.github.io/docling/usage/"
title: "Usage - Docling"
---

[Skip to content](https://docling-project.github.io/docling/usage/#conversion)

# Usage

## Conversion

### Convert a single document

To convert individual PDF documents, use `convert()`, for example:

```
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"

```

### CLI

You can also use Docling directly from your command line to convert individual files —be it local or by URL— or whole directories.

```
docling https://arxiv.org/pdf/2206.01062

```

You can also use 🥚 [SmolDocling](https://huggingface.co/ds4sd/SmolDocling-256M-preview) and other VLMs via Docling CLI:

```
docling --pipeline vlm --vlm-model smoldocling https://arxiv.org/pdf/2206.01062

```

This will use MLX acceleration on supported Apple Silicon hardware.

To see all available options (export formats etc.) run `docling --help`. More details in the [CLI reference page](https://docling-project.github.io/docling/reference/cli/).

### Advanced options

#### Model prefetching and offline usage

By default, models are downloaded automatically upon first usage. If you would prefer
to explicitly prefetch them for offline use (e.g. in air-gapped environments) you can do
that as follows:

**Step 1: Prefetch the models**

Use the `docling-tools models download` utility:

```
$ docling-tools models download
Downloading layout model...
Downloading tableformer model...
Downloading picture classifier model...
Downloading code formula model...
Downloading easyocr models...
Models downloaded into $HOME/.cache/docling/models.

```

Alternatively, models can be programmatically downloaded using `docling.utils.model_downloader.download_models()`.

**Step 2: Use the prefetched models**

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

artifacts_path = "/local/path/to/models"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

```

Or using the CLI:

```
docling --artifacts-path="/local/path/to/models" FILE

```

Or using the `DOCLING_ARTIFACTS_PATH` environment variable:

```
export DOCLING_ARTIFACTS_PATH="/local/path/to/models"
python my_docling_script.py

```

#### Using remote services

The main purpose of Docling is to run local models which are not sharing any user data with remote services.
Anyhow, there are valid use cases for processing part of the pipeline using remote services, for example invoking OCR engines from cloud vendors or the usage of hosted LLMs.

In Docling we decided to allow such models, but we require the user to explicitly opt-in in communicating with external services.

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

```

When the value `enable_remote_services=True` is not set, the system will raise an exception `OperationNotAllowed()`.

_Note: This option is only related to the system sending user data to remote services. Control of pulling data (e.g. model weights) follows the logic described in [Model prefetching and offline usage](https://docling-project.github.io/docling/usage/#model-prefetching-and-offline-usage)._

##### List of remote model services

The options in this list require the explicit `enable_remote_services=True` when processing the documents.

- `PictureDescriptionApiOptions`: Using vision models via API calls.

#### Adjust pipeline features

The example file [custom\_convert.py](https://docling-project.github.io/docling/examples/custom_convert/) contains multiple ways
one can adjust the conversion pipeline and features.

##### Control PDF table extraction options

You can control if table structure recognition should map the recognized structure back to PDF cells (default) or use text cells from the structure prediction itself.
This can improve output quality if you find that multiple columns in extracted tables are erroneously merged into one.

```
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

```

Since docling 1.16.0: You can control which TableFormer mode you want to use. Choose between `TableFormerMode.FAST` (faster but less accurate) and `TableFormerMode.ACCURATE` (default) to receive better quality with difficult table structures.

```
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

```

#### Impose limits on the document size

You can limit the file size and number of pages which should be allowed to process per document:

```
from pathlib import Path
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)

```

#### Convert from binary PDF streams

You can convert PDFs from a binary stream instead of from the filesystem as follows:

```
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)

```

#### Limit resource usage

You can limit the CPU threads used by Docling by setting the environment variable `OMP_NUM_THREADS` accordingly. The default setting is using 4 CPU threads.

#### Use specific backend converters

Note

This section discusses directly invoking a [backend](https://docling-project.github.io/docling/concepts/architecture/),
i.e. using a low-level API. This should only be done when necessary. For most cases,
using a `DocumentConverter` (high-level API) as discussed in the sections above
should suffice — and is the recommended way.

By default, Docling will try to identify the document format to apply the appropriate conversion backend (see the list of [supported formats](https://docling-project.github.io/docling/usage/supported_formats/)).
You can restrict the `DocumentConverter` to a set of allowed document formats, as shown in the [Multi-format conversion](https://docling-project.github.io/docling/examples/run_with_formats/) example.
Alternatively, you can also use the specific backend that matches your document content. For instance, you can use `HTMLDocumentBackend` for HTML pages:

```
import urllib.request
from io import BytesIO
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

url = "https://en.wikipedia.org/wiki/Duck"
text = urllib.request.urlopen(url).read()
in_doc = InputDocument(
    path_or_stream=BytesIO(text),
    format=InputFormat.HTML,
    backend=HTMLDocumentBackend,
    filename="duck.html",
)
backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(text))
dl_doc = backend.convert()
print(dl_doc.export_to_markdown())

```

## Chunking

You can chunk a Docling document using a [chunker](https://docling-project.github.io/docling/concepts/chunking/), such as a
`HybridChunker`, as shown below (for more details check out
[this example](https://docling-project.github.io/docling/examples/hybrid_chunking/)):

```
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

conv_res = DocumentConverter().convert("https://arxiv.org/pdf/2206.01062")
doc = conv_res.document

chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")  # set tokenizer as needed
chunk_iter = chunker.chunk(doc)

```

An example chunk would look like this:

```
print(list(chunk_iter)[11])
# {
#   "text": "In this paper, we present the DocLayNet dataset. [...]",
#   "meta": {
#     "doc_items": [{\
#       "self_ref": "#/texts/28",\
#       "label": "text",\
#       "prov": [{\
#         "page_no": 2,\
#         "bbox": {"l": 53.29, "t": 287.14, "r": 295.56, "b": 212.37, ...},\
#       }], ...,\
#     }, ...],
#     "headings": ["1 INTRODUCTION"],
#   }
# }

```

Back to top