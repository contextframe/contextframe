---
url: "https://docling-project.github.io/docling/examples/batch_convert/"
title: "Batch conversion - Docling"
---

# Batch conversion

In \[ \]:

Copied!

```
import json
import logging
import time
from collections.abc import Iterable
from pathlib import Path

```

import json
import logging
import time
from collections.abc import Iterable
from pathlib import Path

In \[ \]:

Copied!

```
import yaml
from docling_core.types.doc import ImageRefMode

```

import yaml
from docling\_core.types.doc import ImageRefMode

In \[ \]:

Copied!

```
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.backend.docling\_parse\_v4\_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base\_models import ConversionStatus, InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline\_options import PdfPipelineOptions
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
USE_V2 = True
USE_LEGACY = False

```

USE\_V2 = True
USE\_LEGACY = False

In \[ \]:

Copied!

```
def export_documents(
    conv_results: Iterable[ConversionResult],
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    partial_success_count = 0

    for conv_res in conv_results:
        if conv_res.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = conv_res.input.file.stem

            if USE_V2:
                conv_res.document.save_as_json(
                    output_dir / f"{doc_filename}.json",
                    image_mode=ImageRefMode.PLACEHOLDER,
                )
                conv_res.document.save_as_html(
                    output_dir / f"{doc_filename}.html",
                    image_mode=ImageRefMode.EMBEDDED,
                )
                conv_res.document.save_as_document_tokens(
                    output_dir / f"{doc_filename}.doctags.txt"
                )
                conv_res.document.save_as_markdown(
                    output_dir / f"{doc_filename}.md",
                    image_mode=ImageRefMode.PLACEHOLDER,
                )
                conv_res.document.save_as_markdown(
                    output_dir / f"{doc_filename}.txt",
                    image_mode=ImageRefMode.PLACEHOLDER,
                    strict_text=True,
                )

                # Export Docling document format to YAML:
                with (output_dir / f"{doc_filename}.yaml").open("w") as fp:
                    fp.write(yaml.safe_dump(conv_res.document.export_to_dict()))

                # Export Docling document format to doctags:
                with (output_dir / f"{doc_filename}.doctags.txt").open("w") as fp:
                    fp.write(conv_res.document.export_to_document_tokens())

                # Export Docling document format to markdown:
                with (output_dir / f"{doc_filename}.md").open("w") as fp:
                    fp.write(conv_res.document.export_to_markdown())

                # Export Docling document format to text:
                with (output_dir / f"{doc_filename}.txt").open("w") as fp:
                    fp.write(conv_res.document.export_to_markdown(strict_text=True))

            if USE_LEGACY:
                # Export Deep Search document JSON format:
                with (output_dir / f"{doc_filename}.legacy.json").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(json.dumps(conv_res.legacy_document.export_to_dict()))

                # Export Text format:
                with (output_dir / f"{doc_filename}.legacy.txt").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(
                        conv_res.legacy_document.export_to_markdown(strict_text=True)
                    )

                # Export Markdown format:
                with (output_dir / f"{doc_filename}.legacy.md").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(conv_res.legacy_document.export_to_markdown())

                # Export Document Tags format:
                with (output_dir / f"{doc_filename}.legacy.doctags.txt").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(conv_res.legacy_document.export_to_document_tokens())

        elif conv_res.status == ConversionStatus.PARTIAL_SUCCESS:
            _log.info(
                f"Document {conv_res.input.file} was partially converted with the following errors:"
            )
            for item in conv_res.errors:
                _log.info(f"\t{item.error_message}")
            partial_success_count += 1
        else:
            _log.info(f"Document {conv_res.input.file} failed to convert.")
            failure_count += 1

    _log.info(
        f"Processed {success_count + partial_success_count + failure_count} docs, "
        f"of which {failure_count} failed "
        f"and {partial_success_count} were partially converted."
    )
    return success_count, partial_success_count, failure_count

```

def export\_documents(
conv\_results: Iterable\[ConversionResult\],
output\_dir: Path,
):
output\_dir.mkdir(parents=True, exist\_ok=True)

success\_count = 0
failure\_count = 0
partial\_success\_count = 0

for conv\_res in conv\_results:
if conv\_res.status == ConversionStatus.SUCCESS:
success\_count += 1
doc\_filename = conv\_res.input.file.stem

if USE\_V2:
conv\_res.document.save\_as\_json(
output\_dir / f"{doc\_filename}.json",
image\_mode=ImageRefMode.PLACEHOLDER,
)
conv\_res.document.save\_as\_html(
output\_dir / f"{doc\_filename}.html",
image\_mode=ImageRefMode.EMBEDDED,
)
conv\_res.document.save\_as\_document\_tokens(
output\_dir / f"{doc\_filename}.doctags.txt"
)
conv\_res.document.save\_as\_markdown(
output\_dir / f"{doc\_filename}.md",
image\_mode=ImageRefMode.PLACEHOLDER,
)
conv\_res.document.save\_as\_markdown(
output\_dir / f"{doc\_filename}.txt",
image\_mode=ImageRefMode.PLACEHOLDER,
strict\_text=True,
)

# Export Docling document format to YAML:
with (output\_dir / f"{doc\_filename}.yaml").open("w") as fp:
fp.write(yaml.safe\_dump(conv\_res.document.export\_to\_dict()))

# Export Docling document format to doctags:
with (output\_dir / f"{doc\_filename}.doctags.txt").open("w") as fp:
fp.write(conv\_res.document.export\_to\_document\_tokens())

# Export Docling document format to markdown:
with (output\_dir / f"{doc\_filename}.md").open("w") as fp:
fp.write(conv\_res.document.export\_to\_markdown())

# Export Docling document format to text:
with (output\_dir / f"{doc\_filename}.txt").open("w") as fp:
fp.write(conv\_res.document.export\_to\_markdown(strict\_text=True))

if USE\_LEGACY:
# Export Deep Search document JSON format:
with (output\_dir / f"{doc\_filename}.legacy.json").open(
"w", encoding="utf-8"
) as fp:
fp.write(json.dumps(conv\_res.legacy\_document.export\_to\_dict()))

# Export Text format:
with (output\_dir / f"{doc\_filename}.legacy.txt").open(
"w", encoding="utf-8"
) as fp:
fp.write(
conv\_res.legacy\_document.export\_to\_markdown(strict\_text=True)
)

# Export Markdown format:
with (output\_dir / f"{doc\_filename}.legacy.md").open(
"w", encoding="utf-8"
) as fp:
fp.write(conv\_res.legacy\_document.export\_to\_markdown())

# Export Document Tags format:
with (output\_dir / f"{doc\_filename}.legacy.doctags.txt").open(
"w", encoding="utf-8"
) as fp:
fp.write(conv\_res.legacy\_document.export\_to\_document\_tokens())

elif conv\_res.status == ConversionStatus.PARTIAL\_SUCCESS:
\_log.info(
f"Document {conv\_res.input.file} was partially converted with the following errors:"
)
for item in conv\_res.errors:
\_log.info(f"\\t{item.error\_message}")
partial\_success\_count += 1
else:
\_log.info(f"Document {conv\_res.input.file} failed to convert.")
failure\_count += 1

\_log.info(
f"Processed {success\_count + partial\_success\_count + failure\_count} docs, "
f"of which {failure\_count} failed "
f"and {partial\_success\_count} were partially converted."
)
return success\_count, partial\_success\_count, failure\_count

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_paths = [\
        Path("./tests/data/pdf/2206.01062.pdf"),\
        Path("./tests/data/pdf/2203.01017v2.pdf"),\
        Path("./tests/data/pdf/2305.03393v1.pdf"),\
        Path("./tests/data/pdf/redp5110_sampled.pdf"),\
    ]

    # buf = BytesIO(Path("./test/data/2206.01062.pdf").open("rb").read())
    # docs = [DocumentStream(name="my_doc.pdf", stream=buf)]
    # input = DocumentConversionInput.from_streams(docs)

    # # Turn on inline debug visualizations:
    # settings.debug.visualize_layout = True
    # settings.debug.visualize_ocr = True
    # settings.debug.visualize_tables = True
    # settings.debug.visualize_cells = True

    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, backend=DoclingParseV4DocumentBackend
            )
        }
    )

    start_time = time.time()

    conv_results = doc_converter.convert_all(
        input_doc_paths,
        raises_on_error=False,  # to let conversion run through all and examine results at the end
    )
    success_count, partial_success_count, failure_count = export_documents(
        conv_results, output_dir=Path("scratch")
    )

    end_time = time.time() - start_time

    _log.info(f"Document conversion complete in {end_time:.2f} seconds.")

    if failure_count > 0:
        raise RuntimeError(
            f"The example failed converting {failure_count} on {len(input_doc_paths)}."
        )

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_paths = \[\
Path("./tests/data/pdf/2206.01062.pdf"),\
Path("./tests/data/pdf/2203.01017v2.pdf"),\
Path("./tests/data/pdf/2305.03393v1.pdf"),\
Path("./tests/data/pdf/redp5110\_sampled.pdf"),\
\]

# buf = BytesIO(Path("./test/data/2206.01062.pdf").open("rb").read())
# docs = \[DocumentStream(name="my\_doc.pdf", stream=buf)\]
# input = DocumentConversionInput.from\_streams(docs)

# # Turn on inline debug visualizations:
# settings.debug.visualize\_layout = True
# settings.debug.visualize\_ocr = True
# settings.debug.visualize\_tables = True
# settings.debug.visualize\_cells = True

pipeline\_options = PdfPipelineOptions()
pipeline\_options.generate\_page\_images = True

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=pipeline\_options, backend=DoclingParseV4DocumentBackend
)
}
)

start\_time = time.time()

conv\_results = doc\_converter.convert\_all(
input\_doc\_paths,
raises\_on\_error=False, # to let conversion run through all and examine results at the end
)
success\_count, partial\_success\_count, failure\_count = export\_documents(
conv\_results, output\_dir=Path("scratch")
)

end\_time = time.time() - start\_time

\_log.info(f"Document conversion complete in {end\_time:.2f} seconds.")

if failure\_count > 0:
raise RuntimeError(
f"The example failed converting {failure\_count} on {len(input\_doc\_paths)}."
)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top