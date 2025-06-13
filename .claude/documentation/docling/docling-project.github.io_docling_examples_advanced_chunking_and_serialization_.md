---
url: "https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/"
title: "Advanced chunking & serialization - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/#advanced-chunking-serialization)

# Advanced chunking & serialization [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#advanced-chunking-serialization)

## Overview [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#overview)

In this notebook we show how to customize the serialization strategies that come into
play during chunking.

## Setup [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#setup)

We will work with a document that contains some [picture annotations](https://docling-project.github.io/docling/examples/pictures_description):

In \[1\]:

Copied!

```
from docling_core.types.doc.document import DoclingDocument

SOURCE = "./data/2408.09869v3_enriched.json"

doc = DoclingDocument.load_from_json(SOURCE)

```

from docling\_core.types.doc.document import DoclingDocument

SOURCE = "./data/2408.09869v3\_enriched.json"

doc = DoclingDocument.load\_from\_json(SOURCE)

Below we define the chunker (for more details check out [Hybrid Chunking](https://docling-project.github.io/docling/examples/hybrid_chunking)):

In \[2\]:

Copied!

```
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.base import BaseTokenizer
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer: BaseTokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
)
chunker = HybridChunker(tokenizer=tokenizer)

```

from docling\_core.transforms.chunker.hybrid\_chunker import HybridChunker
from docling\_core.transforms.chunker.tokenizer.base import BaseTokenizer
from docling\_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

EMBED\_MODEL\_ID = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer: BaseTokenizer = HuggingFaceTokenizer(
tokenizer=AutoTokenizer.from\_pretrained(EMBED\_MODEL\_ID),
)
chunker = HybridChunker(tokenizer=tokenizer)

In \[3\]:

Copied!

```
print(f"{tokenizer.get_max_tokens()=}")

```

print(f"{tokenizer.get\_max\_tokens()=}")

```
tokenizer.get_max_tokens()=512

```

Defining some helper methods:

In \[4\]:

Copied!

```
from typing import Iterable, Optional

from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hierarchical_chunker import DocChunk
from docling_core.types.doc.labels import DocItemLabel
from rich.console import Console
from rich.panel import Panel

console = Console(
    width=200,  # for getting Markdown tables rendered nicely
)

def find_n_th_chunk_with_label(
    iter: Iterable[BaseChunk], n: int, label: DocItemLabel
) -> Optional[DocChunk]:
    num_found = -1
    for i, chunk in enumerate(iter):
        doc_chunk = DocChunk.model_validate(chunk)
        for it in doc_chunk.meta.doc_items:
            if it.label == label:
                num_found += 1
                if num_found == n:
                    return i, chunk
    return None, None

def print_chunk(chunks, chunk_pos):
    chunk = chunks[chunk_pos]
    ctx_text = chunker.contextualize(chunk=chunk)
    num_tokens = tokenizer.count_tokens(text=ctx_text)
    doc_items_refs = [it.self_ref for it in chunk.meta.doc_items]
    title = f"{chunk_pos=} {num_tokens=} {doc_items_refs=}"
    console.print(Panel(ctx_text, title=title))

```

from typing import Iterable, Optional

from docling\_core.transforms.chunker.base import BaseChunk
from docling\_core.transforms.chunker.hierarchical\_chunker import DocChunk
from docling\_core.types.doc.labels import DocItemLabel
from rich.console import Console
from rich.panel import Panel

console = Console(
width=200, # for getting Markdown tables rendered nicely
)

def find\_n\_th\_chunk\_with\_label(
iter: Iterable\[BaseChunk\], n: int, label: DocItemLabel
) -\> Optional\[DocChunk\]:
num\_found = -1
for i, chunk in enumerate(iter):
doc\_chunk = DocChunk.model\_validate(chunk)
for it in doc\_chunk.meta.doc\_items:
if it.label == label:
num\_found += 1
if num\_found == n:
return i, chunk
return None, None

def print\_chunk(chunks, chunk\_pos):
chunk = chunks\[chunk\_pos\]
ctx\_text = chunker.contextualize(chunk=chunk)
num\_tokens = tokenizer.count\_tokens(text=ctx\_text)
doc\_items\_refs = \[it.self\_ref for it in chunk.meta.doc\_items\]
title = f"{chunk\_pos=} {num\_tokens=} {doc\_items\_refs=}"
console.print(Panel(ctx\_text, title=title))

## Table serialization [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#table-serialization)

### Using the default strategy [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#using-the-default-strategy)

Below we inspect the first chunk containing a table — using the default serialization strategy:

In \[5\]:

Copied!

```
chunker = HybridChunker(tokenizer=tokenizer)

chunk_iter = chunker.chunk(dl_doc=doc)

chunks = list(chunk_iter)
i, chunk = find_n_th_chunk_with_label(chunks, n=0, label=DocItemLabel.TABLE)
print_chunk(
    chunks=chunks,
    chunk_pos=i,
)

```

chunker = HybridChunker(tokenizer=tokenizer)

chunk\_iter = chunker.chunk(dl\_doc=doc)

chunks = list(chunk\_iter)
i, chunk = find\_n\_th\_chunk\_with\_label(chunks, n=0, label=DocItemLabel.TABLE)
print\_chunk(
chunks=chunks,
chunk\_pos=i,
)

```
Token indices sequence length is longer than the specified maximum sequence length for this model (652 > 512). Running this sequence through the model will result in indexing errors

```

```
╭────────────────────────────────────────────────────────────── chunk_pos=13 num_tokens=426 doc_items_refs=['#/texts/72', '#/tables/0'] ───────────────────────────────────────────────────────────────╮
│ Docling Technical Report                                                                                                                                                                             │
│ 4 Performance                                                                                                                                                                                        │
│ Table 1: Runtime characteristics of Docling with the standard model pipeline and settings, on our test dataset of 225 pages, on two different systems. OCR is disabled. We show the time-to-solution │
│ (TTS), computed throughput in pages per second, and the peak memory used (resident set size) for both the Docling-native PDF backend and for the pypdfium backend, using 4 and 16 threads.           │
│                                                                                                                                                                                                      │
│ Apple M3 Max, Thread budget. = 4. Apple M3 Max, native backend.TTS = 177 s 167 s. Apple M3 Max, native backend.Pages/s = 1.27 1.34. Apple M3 Max, native backend.Mem = 6.20 GB. Apple M3 Max,        │
│ pypdfium backend.TTS = 103 s 92 s. Apple M3 Max, pypdfium backend.Pages/s = 2.18 2.45. Apple M3 Max, pypdfium backend.Mem = 2.56 GB. (16 cores) Intel(R) Xeon E5-2690, Thread budget. = 16 4 16. (16 │
│ cores) Intel(R) Xeon E5-2690, native backend.TTS = 375 s 244 s. (16 cores) Intel(R) Xeon E5-2690, native backend.Pages/s = 0.60 0.92. (16 cores) Intel(R) Xeon E5-2690, native backend.Mem = 6.16    │
│ GB. (16 cores) Intel(R) Xeon E5-2690, pypdfium backend.TTS = 239 s 143 s. (16 cores) Intel(R) Xeon E5-2690, pypdfium backend.Pages/s = 0.94 1.57. (16 cores) Intel(R) Xeon E5-2690, pypdfium         │
│ backend.Mem = 2.42 GB                                                                                                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

**INFO**: As you see above, using the `HybridChunker` can sometimes lead to a warning from the transformers library, however this is a "false alarm" — for details check [here](https://docling-project.github.io/docling/faq/#hybridchunker-triggers-warning-token-indices-sequence-length-is-longer-than-the-specified-maximum-sequence-length-for-this-model).

### Configuring a different strategy [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#configuring-a-different-strategy)

We can configure a different serialization strategy. In the example below, we specify a different table serializer that serializes tables to Markdown instead of the triplet notation used by default:

In \[6\]:

Copied!

```
from docling_core.transforms.chunker.hierarchical_chunker import (
    ChunkingDocSerializer,
    ChunkingSerializerProvider,
)
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer

class MDTableSerializerProvider(ChunkingSerializerProvider):
    def get_serializer(self, doc):
        return ChunkingDocSerializer(
            doc=doc,
            table_serializer=MarkdownTableSerializer(),  # configuring a different table serializer
        )

chunker = HybridChunker(
    tokenizer=tokenizer,
    serializer_provider=MDTableSerializerProvider(),
)

chunk_iter = chunker.chunk(dl_doc=doc)

chunks = list(chunk_iter)
i, chunk = find_n_th_chunk_with_label(chunks, n=0, label=DocItemLabel.TABLE)
print_chunk(
    chunks=chunks,
    chunk_pos=i,
)

```

from docling\_core.transforms.chunker.hierarchical\_chunker import (
ChunkingDocSerializer,
ChunkingSerializerProvider,
)
from docling\_core.transforms.serializer.markdown import MarkdownTableSerializer

class MDTableSerializerProvider(ChunkingSerializerProvider):
def get\_serializer(self, doc):
return ChunkingDocSerializer(
doc=doc,
table\_serializer=MarkdownTableSerializer(), # configuring a different table serializer
)

chunker = HybridChunker(
tokenizer=tokenizer,
serializer\_provider=MDTableSerializerProvider(),
)

chunk\_iter = chunker.chunk(dl\_doc=doc)

chunks = list(chunk\_iter)
i, chunk = find\_n\_th\_chunk\_with\_label(chunks, n=0, label=DocItemLabel.TABLE)
print\_chunk(
chunks=chunks,
chunk\_pos=i,
)

```
╭────────────────────────────────────────────────────────────── chunk_pos=13 num_tokens=431 doc_items_refs=['#/texts/72', '#/tables/0'] ───────────────────────────────────────────────────────────────╮
│ Docling Technical Report                                                                                                                                                                             │
│ 4 Performance                                                                                                                                                                                        │
│ Table 1: Runtime characteristics of Docling with the standard model pipeline and settings, on our test dataset of 225 pages, on two different systems. OCR is disabled. We show the time-to-solution │
│ (TTS), computed throughput in pages per second, and the peak memory used (resident set size) for both the Docling-native PDF backend and for the pypdfium backend, using 4 and 16 threads.           │
│                                                                                                                                                                                                      │
│ | CPU                              | Thread budget   | native backend   | native backend   | native backend   | pypdfium backend   | pypdfium backend   | pypdfium backend   |                       │
│ |----------------------------------|-----------------|------------------|------------------|------------------|--------------------|--------------------|--------------------|                       │
│ |                                  |                 | TTS              | Pages/s          | Mem              | TTS                | Pages/s            | Mem                |                       │
│ | Apple M3 Max                     | 4               | 177 s 167 s      | 1.27 1.34        | 6.20 GB          | 103 s 92 s         | 2.18 2.45          | 2.56 GB            |                       │
│ | (16 cores) Intel(R) Xeon E5-2690 | 16 4 16         | 375 s 244 s      | 0.60 0.92        | 6.16 GB          | 239 s 143 s        | 0.94 1.57          | 2.42 GB            |                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Picture serialization [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#picture-serialization)

### Using the default strategy [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#using-the-default-strategy)

Below we inspect the first chunk containing a picture.

Even when using the default strategy, we can modify the relevant parameters, e.g. which placeholder is used for pictures:

In \[7\]:

Copied!

```
from docling_core.transforms.serializer.markdown import MarkdownParams

class ImgPlaceholderSerializerProvider(ChunkingSerializerProvider):
    def get_serializer(self, doc):
        return ChunkingDocSerializer(
            doc=doc,
            params=MarkdownParams(
                image_placeholder="<!-- image -->",
            ),
        )

chunker = HybridChunker(
    tokenizer=tokenizer,
    serializer_provider=ImgPlaceholderSerializerProvider(),
)

chunk_iter = chunker.chunk(dl_doc=doc)

chunks = list(chunk_iter)
i, chunk = find_n_th_chunk_with_label(chunks, n=0, label=DocItemLabel.PICTURE)
print_chunk(
    chunks=chunks,
    chunk_pos=i,
)

```

from docling\_core.transforms.serializer.markdown import MarkdownParams

class ImgPlaceholderSerializerProvider(ChunkingSerializerProvider):
def get\_serializer(self, doc):
return ChunkingDocSerializer(
doc=doc,
params=MarkdownParams(
image\_placeholder="",
),
)

chunker = HybridChunker(
tokenizer=tokenizer,
serializer\_provider=ImgPlaceholderSerializerProvider(),
)

chunk\_iter = chunker.chunk(dl\_doc=doc)

chunks = list(chunk\_iter)
i, chunk = find\_n\_th\_chunk\_with\_label(chunks, n=0, label=DocItemLabel.PICTURE)
print\_chunk(
chunks=chunks,
chunk\_pos=i,
)

```
╭───────────────────────────────────────────────── chunk_pos=0 num_tokens=117 doc_items_refs=['#/pictures/0', '#/texts/2', '#/texts/3', '#/texts/4'] ──────────────────────────────────────────────────╮
│ Docling Technical Report                                                                                                                                                                             │
│ <!-- image -->                                                                                                                                                                                       │
│ Version 1.0                                                                                                                                                                                          │
│ Christoph Auer Maksym Lysak Ahmed Nassar Michele Dolfi Nikolaos Livathinos Panos Vagenas Cesar Berrospi Ramis Matteo Omenetti Fabian Lindlbauer Kasper Dinkla Lokesh Mishra Yusik Kim Shubham Gupta  │
│ Rafael Teixeira de Lima Valery Weber Lucas Morin Ingmar Meijer Viktor Kuropiatnyk Peter W. J. Staar                                                                                                  │
│ AI4K Group, IBM Research R¨ uschlikon, Switzerland                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Using a custom strategy [¶](https://docling-project.github.io/docling/examples/advanced_chunking_and_serialization/\#using-a-custom-strategy)

Below we define and use our custom picture serialization strategy which leverages picture annotations:

In \[8\]:

Copied!

```
from typing import Any

from docling_core.transforms.serializer.base import (
    BaseDocSerializer,
    SerializationResult,
)
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import MarkdownPictureSerializer
from docling_core.types.doc.document import (
    PictureClassificationData,
    PictureDescriptionData,
    PictureItem,
    PictureMoleculeData,
)
from typing_extensions import override

class AnnotationPictureSerializer(MarkdownPictureSerializer):
    @override
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        **kwargs: Any,
    ) -> SerializationResult:
        text_parts: list[str] = []
        for annotation in item.annotations:
            if isinstance(annotation, PictureClassificationData):
                predicted_class = (
                    annotation.predicted_classes[0].class_name
                    if annotation.predicted_classes
                    else None
                )
                if predicted_class is not None:
                    text_parts.append(f"Picture type: {predicted_class}")
            elif isinstance(annotation, PictureMoleculeData):
                text_parts.append(f"SMILES: {annotation.smi}")
            elif isinstance(annotation, PictureDescriptionData):
                text_parts.append(f"Picture description: {annotation.text}")

        text_res = "\n".join(text_parts)
        text_res = doc_serializer.post_process(text=text_res)
        return create_ser_result(text=text_res, span_source=item)

```

from typing import Any

from docling\_core.transforms.serializer.base import (
BaseDocSerializer,
SerializationResult,
)
from docling\_core.transforms.serializer.common import create\_ser\_result
from docling\_core.transforms.serializer.markdown import MarkdownPictureSerializer
from docling\_core.types.doc.document import (
PictureClassificationData,
PictureDescriptionData,
PictureItem,
PictureMoleculeData,
)
from typing\_extensions import override

class AnnotationPictureSerializer(MarkdownPictureSerializer):
@override
def serialize(
self,
\*,
item: PictureItem,
doc\_serializer: BaseDocSerializer,
doc: DoclingDocument,
\*\*kwargs: Any,
) -\> SerializationResult:
text\_parts: list\[str\] = \[\]
for annotation in item.annotations:
if isinstance(annotation, PictureClassificationData):
predicted\_class = (
annotation.predicted\_classes\[0\].class\_name
if annotation.predicted\_classes
else None
)
if predicted\_class is not None:
text\_parts.append(f"Picture type: {predicted\_class}")
elif isinstance(annotation, PictureMoleculeData):
text\_parts.append(f"SMILES: {annotation.smi}")
elif isinstance(annotation, PictureDescriptionData):
text\_parts.append(f"Picture description: {annotation.text}")

text\_res = "\\n".join(text\_parts)
text\_res = doc\_serializer.post\_process(text=text\_res)
return create\_ser\_result(text=text\_res, span\_source=item)

In \[9\]:

Copied!

```
class ImgAnnotationSerializerProvider(ChunkingSerializerProvider):
    def get_serializer(self, doc: DoclingDocument):
        return ChunkingDocSerializer(
            doc=doc,
            picture_serializer=AnnotationPictureSerializer(),  # configuring a different picture serializer
        )

chunker = HybridChunker(
    tokenizer=tokenizer,
    serializer_provider=ImgAnnotationSerializerProvider(),
)

chunk_iter = chunker.chunk(dl_doc=doc)

chunks = list(chunk_iter)
i, chunk = find_n_th_chunk_with_label(chunks, n=0, label=DocItemLabel.PICTURE)
print_chunk(
    chunks=chunks,
    chunk_pos=i,
)

```

class ImgAnnotationSerializerProvider(ChunkingSerializerProvider):
def get\_serializer(self, doc: DoclingDocument):
return ChunkingDocSerializer(
doc=doc,
picture\_serializer=AnnotationPictureSerializer(), # configuring a different picture serializer
)

chunker = HybridChunker(
tokenizer=tokenizer,
serializer\_provider=ImgAnnotationSerializerProvider(),
)

chunk\_iter = chunker.chunk(dl\_doc=doc)

chunks = list(chunk\_iter)
i, chunk = find\_n\_th\_chunk\_with\_label(chunks, n=0, label=DocItemLabel.PICTURE)
print\_chunk(
chunks=chunks,
chunk\_pos=i,
)

```
╭───────────────────────────────────────────────── chunk_pos=0 num_tokens=128 doc_items_refs=['#/pictures/0', '#/texts/2', '#/texts/3', '#/texts/4'] ──────────────────────────────────────────────────╮
│ Docling Technical Report                                                                                                                                                                             │
│ Picture description: In this image we can see a cartoon image of a duck holding a paper.                                                                                                             │
│ Version 1.0                                                                                                                                                                                          │
│ Christoph Auer Maksym Lysak Ahmed Nassar Michele Dolfi Nikolaos Livathinos Panos Vagenas Cesar Berrospi Ramis Matteo Omenetti Fabian Lindlbauer Kasper Dinkla Lokesh Mishra Yusik Kim Shubham Gupta  │
│ Rafael Teixeira de Lima Valery Weber Lucas Morin Ingmar Meijer Viktor Kuropiatnyk Peter W. J. Staar                                                                                                  │
│ AI4K Group, IBM Research R¨ uschlikon, Switzerland                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

In \[ \]:

Copied!

```

```

Back to top