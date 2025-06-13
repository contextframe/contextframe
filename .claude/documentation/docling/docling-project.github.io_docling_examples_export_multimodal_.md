---
url: "https://docling-project.github.io/docling/examples/export_multimodal/"
title: "Multimodal export - Docling"
---

# Multimodal export

In \[ \]:

Copied!

```
import datetime
import logging
import time
from pathlib import Path

```

import datetime
import logging
import time
from pathlib import Path

In \[ \]:

Copied!

```
import pandas as pd

```

import pandas as pd

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate_multimodal_pages
from docling.utils.utils import create_hash

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import PdfPipelineOptions
from docling.document\_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate\_multimodal\_pages
from docling.utils.utils import create\_hash

In \[ \]:

Copied!

```
_log = logging.getLogger(__name__)

```

\_log = logging.getLogger(\_\_name\_\_)

In \[ \]:

Copied!

```
IMAGE_RESOLUTION_SCALE = 2.0

```

IMAGE\_RESOLUTION\_SCALE = 2.0

In \[ \]:

Copied!

```
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")
    output_dir = Path("scratch")

    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting AssembleOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for (
        content_text,
        content_md,
        content_dt,
        page_cells,
        page_segments,
        page,
    ) in generate_multimodal_pages(conv_res):
        dpi = page._default_image_scale * 72

        rows.append(
            {
                "document": conv_res.input.file.name,
                "hash": conv_res.input.document_hash,
                "page_hash": create_hash(
                    conv_res.input.document_hash + ":" + str(page.page_no - 1)
                ),
                "image": {
                    "width": page.image.width,
                    "height": page.image.height,
                    "bytes": page.image.tobytes(),
                },
                "cells": page_cells,
                "contents": content_text,
                "contents_md": content_md,
                "contents_dt": content_dt,
                "segments": page_segments,
                "extra": {
                    "page_num": page.page_no + 1,
                    "width_in_points": page.size.width,
                    "height_in_points": page.size.height,
                    "dpi": dpi,
                },
            }
        )

    # Generate one parquet from all documents
    df_result = pd.json_normalize(rows)
    now = datetime.datetime.now()
    output_filename = output_dir / f"multimodal_{now:%Y-%m-%d_%H%M%S}.parquet"
    df_result.to_parquet(output_filename)

    end_time = time.time() - start_time

    _log.info(
        f"Document converted and multimodal pages generated in {end_time:.2f} seconds."
    )

    # This block demonstrates how the file can be opened with the HF datasets library
    # from datasets import Dataset
    # from PIL import Image
    # multimodal_df = pd.read_parquet(output_filename)

    # # Convert pandas DataFrame to Hugging Face Dataset and load bytes into image
    # dataset = Dataset.from_pandas(multimodal_df)
    # def transforms(examples):
    #     examples["image"] = Image.frombytes('RGB', (examples["image.width"], examples["image.height"]), examples["image.bytes"], 'raw')
    #     return examples
    # dataset = dataset.map(transforms)

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")
output\_dir = Path("scratch")

# Important: For operating with page images, we must keep them, otherwise the DocumentConverter
# will destroy them for cleaning up memory.
# This is done by setting AssembleOptions.images\_scale, which also defines the scale of images.
# scale=1 correspond of a standard 72 DPI image
pipeline\_options = PdfPipelineOptions()
pipeline\_options.images\_scale = IMAGE\_RESOLUTION\_SCALE
pipeline\_options.generate\_page\_images = True

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
}
)

start\_time = time.time()

conv\_res = doc\_converter.convert(input\_doc\_path)

output\_dir.mkdir(parents=True, exist\_ok=True)

rows = \[\]
for (
content\_text,
content\_md,
content\_dt,
page\_cells,
page\_segments,
page,
) in generate\_multimodal\_pages(conv\_res):
dpi = page.\_default\_image\_scale \* 72

rows.append(
{
"document": conv\_res.input.file.name,
"hash": conv\_res.input.document\_hash,
"page\_hash": create\_hash(
conv\_res.input.document\_hash + ":" + str(page.page\_no - 1)
),
"image": {
"width": page.image.width,
"height": page.image.height,
"bytes": page.image.tobytes(),
},
"cells": page\_cells,
"contents": content\_text,
"contents\_md": content\_md,
"contents\_dt": content\_dt,
"segments": page\_segments,
"extra": {
"page\_num": page.page\_no + 1,
"width\_in\_points": page.size.width,
"height\_in\_points": page.size.height,
"dpi": dpi,
},
}
)

# Generate one parquet from all documents
df\_result = pd.json\_normalize(rows)
now = datetime.datetime.now()
output\_filename = output\_dir / f"multimodal\_{now:%Y-%m-%d\_%H%M%S}.parquet"
df\_result.to\_parquet(output\_filename)

end\_time = time.time() - start\_time

\_log.info(
f"Document converted and multimodal pages generated in {end\_time:.2f} seconds."
)

# This block demonstrates how the file can be opened with the HF datasets library
# from datasets import Dataset
# from PIL import Image
# multimodal\_df = pd.read\_parquet(output\_filename)

# # Convert pandas DataFrame to Hugging Face Dataset and load bytes into image
# dataset = Dataset.from\_pandas(multimodal\_df)
# def transforms(examples):
# examples\["image"\] = Image.frombytes('RGB', (examples\["image.width"\], examples\["image.height"\]), examples\["image.bytes"\], 'raw')
# return examples
# dataset = dataset.map(transforms)

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top