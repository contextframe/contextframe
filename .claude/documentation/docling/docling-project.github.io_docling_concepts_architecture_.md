---
url: "https://docling-project.github.io/docling/concepts/architecture/"
title: "Architecture - Docling"
---

# Architecture

![docling_architecture](https://docling-project.github.io/docling/assets/docling_arch.png)

In a nutshell, Docling's architecture is outlined in the diagram above.

For each document format, the _document converter_ knows which format-specific _backend_ to employ for parsing the document and which _pipeline_ to use for orchestrating the execution, along with any relevant _options_.

Tip

While the document converter holds a default mapping, this configuration is parametrizable, so e.g. for the PDF format, different backends and different pipeline options can be used — see [Usage](https://docling-project.github.io/docling/usage/#adjust-pipeline-features).

The _conversion result_ contains the [_Docling document_](https://docling-project.github.io/docling/concepts/docling_document/), Docling's fundamental document representation.

Some typical scenarios for using a Docling document include directly calling its _export methods_, such as for markdown, dictionary etc., or having it serialized by a
[_serializer_](https://docling-project.github.io/docling/concepts/serialization/) or chunked by a [_chunker_](https://docling-project.github.io/docling/concepts/chunking/).

For more details on Docling's architecture, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

Note

The components illustrated with dashed outline indicate base classes that can be subclassed for specialized implementations.

Back to top