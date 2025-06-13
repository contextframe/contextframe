---
url: "https://docling-project.github.io/docling/reference/cli/"
title: "CLI reference - Docling"
---

[Skip to content](https://docling-project.github.io/docling/reference/cli/#cli-reference)

# CLI reference

This page provides documentation for our command line tools.

# docling

**Usage:**

```
docling [OPTIONS] source

```

**Options:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `--from` | choice ( `docx` \| `pptx` \| `html` \| `image` \| `pdf` \| `asciidoc` \| `md` \| `csv` \| `xlsx` \| `xml_uspto` \| `xml_jats` \| `json_docling`) | Specify input formats to convert from. Defaults to all formats. | None |
| `--to` | choice ( `md` \| `json` \| `html` \| `html_split_page` \| `text` \| `doctags`) | Specify output formats. Defaults to Markdown. | None |
| `--show-layout` / `--no-show-layout` | boolean | If enabled, the page images will show the bounding-boxes of the items. | `False` |
| `--headers` | text | Specify http request headers used when fetching url input sources in the form of a JSON string | None |
| `--image-export-mode` | choice ( `placeholder` \| `embedded` \| `referenced`) | Image export mode for the document (only in case of JSON, Markdown or HTML). With `placeholder`, only the position of the image is marked in the output. In `embedded` mode, the image is embedded as base64 encoded string. In `referenced` mode, the image is exported in PNG format and referenced from the main exported document. | `ImageRefMode.EMBEDDED` |
| `--pipeline` | choice ( `standard` \| `vlm`) | Choose the pipeline to process PDF or image files. | `PdfPipeline.STANDARD` |
| `--vlm-model` | choice ( `smoldocling` \| `granite_vision` \| `granite_vision_ollama`) | Choose the VLM model to use with PDF or image files. | `VlmModelType.SMOLDOCLING` |
| `--ocr` / `--no-ocr` | boolean | If enabled, the bitmap content will be processed using OCR. | `True` |
| `--force-ocr` / `--no-force-ocr` | boolean | Replace any existing text with OCR generated text over the full content. | `False` |
| `--ocr-engine` | text | The OCR engine to use. When --allow-external-plugins is _not_ set, the available values are: easyocr, ocrmac, rapidocr, tesserocr, tesseract. Use the option --show-external-plugins to see the options allowed with external plugins. | `easyocr` |
| `--ocr-lang` | text | Provide a comma-separated list of languages used by the OCR engine. Note that each OCR engine has different values for the language names. | None |
| `--pdf-backend` | choice ( `pypdfium2` \| `dlparse_v1` \| `dlparse_v2` \| `dlparse_v4`) | The PDF backend to use. | `PdfBackend.DLPARSE_V2` |
| `--table-mode` | choice ( `fast` \| `accurate`) | The mode to use in the table structure model. | `TableFormerMode.ACCURATE` |
| `--enrich-code` / `--no-enrich-code` | boolean | Enable the code enrichment model in the pipeline. | `False` |
| `--enrich-formula` / `--no-enrich-formula` | boolean | Enable the formula enrichment model in the pipeline. | `False` |
| `--enrich-picture-classes` / `--no-enrich-picture-classes` | boolean | Enable the picture classification enrichment model in the pipeline. | `False` |
| `--enrich-picture-description` / `--no-enrich-picture-description` | boolean | Enable the picture description model in the pipeline. | `False` |
| `--artifacts-path` | path | If provided, the location of the model artifacts. | None |
| `--enable-remote-services` / `--no-enable-remote-services` | boolean | Must be enabled when using models connecting to remote services. | `False` |
| `--allow-external-plugins` / `--no-allow-external-plugins` | boolean | Must be enabled for loading modules from third-party plugins. | `False` |
| `--show-external-plugins` / `--no-show-external-plugins` | boolean | List the third-party plugins which are available when the option --allow-external-plugins is set. | `False` |
| `--abort-on-error` / `--no-abort-on-error` | boolean | If enabled, the processing will be aborted when the first error is encountered. | `False` |
| `--output` | path | Output directory where results are saved. | `.` |
| `--verbose`, `-v` | integer | Set the verbosity level. -v for info logging, -vv for debug logging. | `0` |
| `--debug-visualize-cells` / `--no-debug-visualize-cells` | boolean | Enable debug output which visualizes the PDF cells | `False` |
| `--debug-visualize-ocr` / `--no-debug-visualize-ocr` | boolean | Enable debug output which visualizes the OCR cells | `False` |
| `--debug-visualize-layout` / `--no-debug-visualize-layout` | boolean | Enable debug output which visualizes the layour clusters | `False` |
| `--debug-visualize-tables` / `--no-debug-visualize-tables` | boolean | Enable debug output which visualizes the table cells | `False` |
| `--version` | boolean | Show version information. | None |
| `--document-timeout` | float | The timeout for processing each document, in seconds. | None |
| `--num-threads` | integer | Number of threads | `4` |
| `--device` | choice ( `auto` \| `cpu` \| `cuda` \| `mps`) | Accelerator device | `AcceleratorDevice.AUTO` |
| `--logo` | boolean | Docling logo | None |
| `--help` | boolean | Show this message and exit. | `False` |

Back to top