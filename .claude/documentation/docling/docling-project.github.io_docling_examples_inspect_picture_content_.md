---
url: "https://docling-project.github.io/docling/examples/inspect_picture_content/"
title: "Inspect picture content - Docling"
---

# Inspect picture content

In \[ \]:

Copied!

```
from docling_core.types.doc import TextItem

```

from docling\_core.types.doc import TextItem

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
source = "tests/data/pdf/amt_handbook_sample.pdf"

```

source = "tests/data/pdf/amt\_handbook\_sample.pdf"

In \[ \]:

Copied!

```
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = 2
pipeline_options.generate_page_images = True

```

pipeline\_options = PdfPipelineOptions()
pipeline\_options.images\_scale = 2
pipeline\_options.generate\_page\_images = True

In \[ \]:

Copied!

```
doc_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

```

doc\_converter = DocumentConverter(
format\_options={InputFormat.PDF: PdfFormatOption(pipeline\_options=pipeline\_options)}
)

In \[ \]:

Copied!

```
result = doc_converter.convert(source)

```

result = doc\_converter.convert(source)

In \[ \]:

Copied!

```
doc = result.document

```

doc = result.document

In \[ \]:

Copied!

```
for picture in doc.pictures:
    # picture.get_image(doc).show() # display the picture
    print(picture.caption_text(doc), " contains these elements:")

    for item, level in doc.iterate_items(root=picture, traverse_pictures=True):
        if isinstance(item, TextItem):
            print(item.text)

    print("\n")

```

for picture in doc.pictures:
# picture.get\_image(doc).show() # display the picture
print(picture.caption\_text(doc), " contains these elements:")

for item, level in doc.iterate\_items(root=picture, traverse\_pictures=True):
if isinstance(item, TextItem):
print(item.text)

print("\\n")

Back to top