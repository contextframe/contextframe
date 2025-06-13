---
url: "https://docling-project.github.io/docling/concepts/plugins/"
title: "Plugins - Docling"
---

[Skip to content](https://docling-project.github.io/docling/concepts/plugins/#plugin-factories)

# Plugins

Docling allows to be extended with third-party plugins which extend the choice of options provided in several steps of the pipeline.

Plugins are loaded via the [pluggy](https://github.com/pytest-dev/pluggy/) system which allows third-party developers to register the new capabilities using the [setuptools entrypoint](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins).

The actual entrypoint definition might vary, depending on the packaging system you are using. Here are a few examples:

[pyproject.toml](https://docling-project.github.io/docling/concepts/plugins/#pyprojecttoml)[poetry v1 pyproject.toml](https://docling-project.github.io/docling/concepts/plugins/#poetry-v1-pyprojecttoml)[setup.cfg](https://docling-project.github.io/docling/concepts/plugins/#setupcfg)[setup.py](https://docling-project.github.io/docling/concepts/plugins/#setuppy)

```
[project.entry-points."docling"]
your_plugin_name = "your_package.module"

```

```
[tool.poetry.plugins."docling"]
your_plugin_name = "your_package.module"

```

```
[options.entry_points]
docling =
    your_plugin_name = your_package.module

```

```
from setuptools import setup

setup(
    # ...,
    entry_points = {
        'docling': [\
            'your_plugin_name = "your_package.module"'\
        ]
    }
)

```

- `your_plugin_name` is the name you choose for your plugin. This must be unique among the broader Docling ecosystem.
- `your_package.module` is the reference to the module in your package which is responsible for the plugin registration.

## Plugin factories

### OCR factory

The OCR factory allows to provide more OCR engines to the Docling users.

The content of `your_package.module` registers the OCR engines with a code similar to:

```
# Factory registration
def ocr_engines():
    return {
        "ocr_engines": [\
            YourOcrModel,\
        ]
    }

```

where `YourOcrModel` must implement the [`BaseOcrModel`](https://github.com/docling-project/docling/blob/main/docling/models/base_ocr_model.py#L23) and provide an options class derived from [`OcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L105).

If you look for an example, the [default Docling plugins](https://github.com/docling-project/docling/blob/main/docling/models/plugins/defaults.py) is a good starting point.

## Third-party plugins

When the plugin is not provided by the main `docling` package but by a third-party package this have to be enabled explicitly via the `allow_external_plugins` option.

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True  # <-- enabled the external plugins
pipeline_options.ocr_options = YourOptions  # <-- your options here

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

```

### Using the `docling` CLI

Similarly, when using the `docling` users have to enable external plugins before selecting the new one.

```
# Show the external plugins
docling --show-external-plugins

# Run docling with the new plugin
docling --allow-external-plugins --ocr-engine=NAME

```

Back to top