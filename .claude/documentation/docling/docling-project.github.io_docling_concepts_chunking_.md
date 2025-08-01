---
url: "https://docling-project.github.io/docling/concepts/chunking/"
title: "Chunking - Docling"
---

[Skip to content](https://docling-project.github.io/docling/concepts/chunking/#introduction)

# Chunking

## Introduction

Chunking approaches

Starting from a `DoclingDocument`, there are in principle two possible chunking
approaches:

1. exporting the `DoclingDocument` to Markdown (or similar format) and then
    performing user-defined chunking as a post-processing step, or
2. using native Docling chunkers, i.e. operating directly on the `DoclingDocument`

This page is about the latter, i.e. using native Docling chunkers.
For an example of using approach (1) check out e.g.
[this recipe](https://docling-project.github.io/docling/examples/rag_langchain/) looking at the Markdown export mode.

A _chunker_ is a Docling abstraction that, given a
[`DoclingDocument`](https://docling-project.github.io/docling/concepts/docling_document/), returns a stream of chunks, each of which
captures some part of the document as a string accompanied by respective metadata.

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a chunker class hierarchy, providing a base type, `BaseChunker`, as well
as specific subclasses.

Docling integration with gen AI frameworks like LlamaIndex is done using the
`BaseChunker` interface, so users can easily plug in any built-in, self-defined, or
third-party `BaseChunker` implementation.

## Base Chunker

The `BaseChunker` base class API defines that any chunker should provide the following:

- `def chunk(self, dl_doc: DoclingDocument, **kwargs) -> Iterator[BaseChunk]`:
Returning the chunks for the provided document.
- `def contextualize(self, chunk: BaseChunk) -> str`:
Returning the potentially metadata-enriched serialization of the chunk, typically
used to feed an embedding model (or generation model).

## Hybrid Chunker

To access `HybridChunker`

- If you are using the `docling` package, you can import as follows:



```
from docling.chunking import HybridChunker

```

- If you are only using the `docling-core` package, you must ensure to install
the `chunking` extra if you want to use HuggingFace tokenizers, e.g.



```
pip install 'docling-core[chunking]'

```



or the `chunking-openai` extra if you prefer Open AI tokenizers (tiktoken), e.g.



```
pip install 'docling-core[chunking-openai]'

```



and then you
can import as follows:



```
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

```


The `HybridChunker` implementation uses a hybrid approach, applying tokenization-aware
refinements on top of document-based [hierarchical](https://docling-project.github.io/docling/concepts/chunking/#hierarchical-chunker) chunking.

More precisely:

- it starts from the result of the hierarchical chunker and, based on the user-provided
tokenizer (typically to be aligned to the embedding model tokenizer), it:
- does one pass where it splits chunks only when needed (i.e. oversized w.r.t.
tokens), &
- another pass where it merges chunks only when possible (i.e. undersized successive
chunks with same headings & captions) — users can opt out of this step via param
`merge_peers` (by default `True`)

👉 Usage examples:

- [Hybrid chunking](https://docling-project.github.io/docling/examples/hybrid_chunking/)
- [Advanced chunking & serialization](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/)

## Hierarchical Chunker

The `HierarchicalChunker` implementation uses the document structure information from
the [`DoclingDocument`](https://docling-project.github.io/docling/concepts/docling_document/) to create one chunk for each individual
detected document element, by default only merging together list items (can be opted out
via param `merge_list_items`). It also takes care of attaching all relevant document
metadata, including headers and captions.

Back to top