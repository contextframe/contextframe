---
url: "https://docling-project.github.io/docling/concepts/serialization/"
title: "Serialization - Docling"
---

[Skip to content](https://docling-project.github.io/docling/concepts/serialization/#introduction)

# Serialization

## Introduction

A _document serializer_ (AKA simply _serializer_) is a Docling abstraction that is
initialized with a given [`DoclingDocument`](https://docling-project.github.io/docling/concepts/docling_document/) and returns a
textual representation for that document.

Besides the document serializer, Docling defines similar abstractions for several
document subcomponents, for example: _text serializer_, _table serializer_,
_picture serializer_, _list serializer_, _inline serializer_, and more.

Last but not least, a _serializer provider_ is a wrapper that abstracts the
document serialization strategy from the document instance.

## Base classes

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a serialization class hierarchy, providing:

- base types for the above abstractions: `BaseDocSerializer`, as well as
`BaseTextSerializer`, `BaseTableSerializer` etc, and `BaseSerializerProvider`, and
- specific subclasses for the above-mentioned base types, e.g. `MarkdownDocSerializer`.

You can review all methods required to define the above base classes [here](https://github.com/docling-project/docling-core/blob/main/docling_core/transforms/serializer/base.py).

From a client perspective, the most relevant is `BaseDocSerializer.serialize()`, which
returns the textual representation, as well as relevant metadata on which document
components contributed to that serialization.

## Use in `DoclingDocument` export methods

Docling provides predefined serializers for Markdown, HTML, and DocTags.

The respective `DoclingDocument` export methods (e.g. `export_to_markdown()`) are
provided as user shorthands — internally directly instantiating and delegating to
respective serializers.

## Examples

For an example showcasing how to use serializers, see
[here](https://docling-project.github.io/docling/examples/serialization/).

Back to top