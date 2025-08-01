---
url: "https://docling-project.github.io/docling/examples/export_figures/"
title: "Figure export - Docling"
---

# Figure export

In \[ \]:

Copied!

```
import logging
import time
from pathlib import Path

```

import logging
import time
from pathlib import Path

In \[ \]:

Copied!

```
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

```

from docling\_core.types.doc import ImageRefMode, PictureItem, TableItem

In \[ \]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

```

from docling.datamodel.base\_models import InputFormat
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
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-table-{table_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

    # Save markdown with embedded pictures
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    # Save HTML with externally referenced pictures
    html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
    conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

    end_time = time.time() - start_time

    _log.info(f"Document converted and figures exported in {end_time:.2f} seconds.")

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")
output\_dir = Path("scratch")

# Important: For operating with page images, we must keep them, otherwise the DocumentConverter
# will destroy them for cleaning up memory.
# This is done by setting PdfPipelineOptions.images\_scale, which also defines the scale of images.
# scale=1 correspond of a standard 72 DPI image
# The PdfPipelineOptions.generate\_\* are the selectors for the document elements which will be enriched
# with the image field
pipeline\_options = PdfPipelineOptions()
pipeline\_options.images\_scale = IMAGE\_RESOLUTION\_SCALE
pipeline\_options.generate\_page\_images = True
pipeline\_options.generate\_picture\_images = True

doc\_converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)
}
)

start\_time = time.time()

conv\_res = doc\_converter.convert(input\_doc\_path)

output\_dir.mkdir(parents=True, exist\_ok=True)
doc\_filename = conv\_res.input.file.stem

# Save page images
for page\_no, page in conv\_res.document.pages.items():
page\_no = page.page\_no
page\_image\_filename = output\_dir / f"{doc\_filename}-{page\_no}.png"
with page\_image\_filename.open("wb") as fp:
page.image.pil\_image.save(fp, format="PNG")

# Save images of figures and tables
table\_counter = 0
picture\_counter = 0
for element, \_level in conv\_res.document.iterate\_items():
if isinstance(element, TableItem):
table\_counter += 1
element\_image\_filename = (
output\_dir / f"{doc\_filename}-table-{table\_counter}.png"
)
with element\_image\_filename.open("wb") as fp:
element.get\_image(conv\_res.document).save(fp, "PNG")

if isinstance(element, PictureItem):
picture\_counter += 1
element\_image\_filename = (
output\_dir / f"{doc\_filename}-picture-{picture\_counter}.png"
)
with element\_image\_filename.open("wb") as fp:
element.get\_image(conv\_res.document).save(fp, "PNG")

# Save markdown with embedded pictures
md\_filename = output\_dir / f"{doc\_filename}-with-images.md"
conv\_res.document.save\_as\_markdown(md\_filename, image\_mode=ImageRefMode.EMBEDDED)

# Save markdown with externally referenced pictures
md\_filename = output\_dir / f"{doc\_filename}-with-image-refs.md"
conv\_res.document.save\_as\_markdown(md\_filename, image\_mode=ImageRefMode.REFERENCED)

# Save HTML with externally referenced pictures
html\_filename = output\_dir / f"{doc\_filename}-with-image-refs.html"
conv\_res.document.save\_as\_html(html\_filename, image\_mode=ImageRefMode.REFERENCED)

end\_time = time.time() - start\_time

\_log.info(f"Document converted and figures exported in {end\_time:.2f} seconds.")

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top