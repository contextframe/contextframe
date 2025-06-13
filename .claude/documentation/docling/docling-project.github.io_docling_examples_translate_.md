---
url: "https://docling-project.github.io/docling/examples/translate/"
title: "Simple translation - Docling"
---

# Simple translation

In \[ \]:

Copied!

```
import logging
from pathlib import Path

```

import logging
from pathlib import Path

In \[ \]:

Copied!

```
from docling_core.types.doc import ImageRefMode, TableItem, TextItem

```

from docling\_core.types.doc import ImageRefMode, TableItem, TextItem

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
# FIXME: put in your favorite translation code ....
def translate(text: str, src: str = "en", dest: str = "de"):
    _log.warning("!!! IMPLEMENT HERE YOUR FAVORITE TRANSLATION CODE!!!")
    # from googletrans import Translator

    # Initialize the translator
    # translator = Translator()

    # Translate text from English to German
    # text = "Hello, how are you?"
    # translated = translator.translate(text, src="en", dest="de")

    return text

```

\# FIXME: put in your favorite translation code ....
def translate(text: str, src: str = "en", dest: str = "de"):
\_log.warning("!!! IMPLEMENT HERE YOUR FAVORITE TRANSLATION CODE!!!")
# from googletrans import Translator

# Initialize the translator
# translator = Translator()

# Translate text from English to German
# text = "Hello, how are you?"
# translated = translator.translate(text, src="en", dest="de")

return text

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

    conv_res = doc_converter.convert(input_doc_path)
    conv_doc = conv_res.document
    doc_filename = conv_res.input.file

    # Save markdown with embedded pictures in original text
    md_filename = output_dir / f"{doc_filename}-with-images-orig.md"
    conv_doc.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TextItem):
            element.orig = element.text
            element.text = translate(text=element.text)

        elif isinstance(element, TableItem):
            for cell in element.data.table_cells:
                cell.text = translate(text=element.text)

    # Save markdown with embedded pictures in translated text
    md_filename = output_dir / f"{doc_filename}-with-images-translated.md"
    conv_doc.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

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

conv\_res = doc\_converter.convert(input\_doc\_path)
conv\_doc = conv\_res.document
doc\_filename = conv\_res.input.file

# Save markdown with embedded pictures in original text
md\_filename = output\_dir / f"{doc\_filename}-with-images-orig.md"
conv\_doc.save\_as\_markdown(md\_filename, image\_mode=ImageRefMode.EMBEDDED)

for element, \_level in conv\_res.document.iterate\_items():
if isinstance(element, TextItem):
element.orig = element.text
element.text = translate(text=element.text)

elif isinstance(element, TableItem):
for cell in element.data.table\_cells:
cell.text = translate(text=element.text)

# Save markdown with embedded pictures in translated text
md\_filename = output\_dir / f"{doc\_filename}-with-images-translated.md"
conv\_doc.save\_as\_markdown(md\_filename, image\_mode=ImageRefMode.EMBEDDED)

Back to top