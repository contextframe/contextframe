---
url: "https://docling-project.github.io/docling/examples/rag_haystack/"
title: "RAG with Haystack - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/rag_haystack/#rag-with-haystack)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/rag_haystack.ipynb)

# RAG with Haystack [¶](https://docling-project.github.io/docling/examples/rag_haystack/\#rag-with-haystack)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | Hugging Face / Sentence Transformers | 💻 Local |
| Vector store | Milvus | 💻 Local |
| Gen AI | Hugging Face Inference API | 🌐 Remote |

## Overview [¶](https://docling-project.github.io/docling/examples/rag_haystack/\#overview)

This example leverages the
[Haystack Docling extension](https://docling-project.github.io/docling/integrations/haystack/), along with
Milvus-based document store and retriever instances, as well as sentence-transformers
embeddings.

The presented `DoclingConverter` component enables you to:

- use various document types in your LLM applications with ease and speed, and
- leverage Docling's rich format for advanced, document-native grounding.

`DoclingConverter` supports two different export modes:

- `ExportType.MARKDOWN`: if you want to capture each input document as a separate
Haystack document, or
- `ExportType.DOC_CHUNKS` (default): if you want to have each input document chunked and
to then capture each individual chunk as a separate Haystack document downstream.

The example allows to explore both modes via parameter `EXPORT_TYPE`; depending on the
value set, the ingestion and RAG pipelines are then set up accordingly.

## Setup [¶](https://docling-project.github.io/docling/examples/rag_haystack/\#setup)

- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.
- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.
- Requirements can be installed as shown below ( `--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):

In \[1\]:

Copied!

```
%pip install -q --progress-bar off --no-warn-conflicts docling-haystack haystack-ai docling pymilvus milvus-haystack sentence-transformers python-dotenv

```

%pip install -q --progress-bar off --no-warn-conflicts docling-haystack haystack-ai docling pymilvus milvus-haystack sentence-transformers python-dotenv

```
Note: you may need to restart the kernel to use updated packages.

```

In \[2\]:

Copied!

```
import os
from pathlib import Path
from tempfile import mkdtemp

from docling_haystack.converter import ExportType
from dotenv import load_dotenv

def _get_env_from_colab_or_os(key):
    try:
        from google.colab import userdata

        try:
            return userdata.get(key)
        except userdata.SecretNotFoundError:
            pass
    except ImportError:
        pass
    return os.getenv(key)

load_dotenv()
HF_TOKEN = _get_env_from_colab_or_os("HF_TOKEN")
PATHS = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT_TYPE = ExportType.DOC_CHUNKS
QUESTION = "Which are the main AI models in Docling?"
TOP_K = 3
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")

```

import os
from pathlib import Path
from tempfile import mkdtemp

from docling\_haystack.converter import ExportType
from dotenv import load\_dotenv

def \_get\_env\_from\_colab\_or\_os(key):
try:
from google.colab import userdata

try:
return userdata.get(key)
except userdata.SecretNotFoundError:
pass
except ImportError:
pass
return os.getenv(key)

load\_dotenv()
HF\_TOKEN = \_get\_env\_from\_colab\_or\_os("HF\_TOKEN")
PATHS = \["https://arxiv.org/pdf/2408.09869"\] # Docling Technical Report
EMBED\_MODEL\_ID = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION\_MODEL\_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT\_TYPE = ExportType.DOC\_CHUNKS
QUESTION = "Which are the main AI models in Docling?"
TOP\_K = 3
MILVUS\_URI = str(Path(mkdtemp()) / "docling.db")

## Indexing pipeline [¶](https://docling-project.github.io/docling/examples/rag_haystack/\#indexing-pipeline)

In \[3\]:

Copied!

```
from docling_haystack.converter import DoclingConverter
from haystack import Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from milvus_haystack import MilvusDocumentStore, MilvusEmbeddingRetriever

from docling.chunking import HybridChunker

document_store = MilvusDocumentStore(
    connection_args={"uri": MILVUS_URI},
    drop_old=True,
    text_field="txt",  # set for preventing conflict with same-name metadata field
)

idx_pipe = Pipeline()
idx_pipe.add_component(
    "converter",
    DoclingConverter(
        export_type=EXPORT_TYPE,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
    ),
)
idx_pipe.add_component(
    "embedder",
    SentenceTransformersDocumentEmbedder(model=EMBED_MODEL_ID),
)
idx_pipe.add_component("writer", DocumentWriter(document_store=document_store))
if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    idx_pipe.connect("converter", "embedder")
elif EXPORT_TYPE == ExportType.MARKDOWN:
    idx_pipe.add_component(
        "splitter",
        DocumentSplitter(split_by="sentence", split_length=1),
    )
    idx_pipe.connect("converter.documents", "splitter.documents")
    idx_pipe.connect("splitter.documents", "embedder.documents")
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")
idx_pipe.connect("embedder", "writer")
idx_pipe.run({"converter": {"paths": PATHS}})

```

from docling\_haystack.converter import DoclingConverter
from haystack import Pipeline
from haystack.components.embedders import (
SentenceTransformersDocumentEmbedder,
SentenceTransformersTextEmbedder,
)
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from milvus\_haystack import MilvusDocumentStore, MilvusEmbeddingRetriever

from docling.chunking import HybridChunker

document\_store = MilvusDocumentStore(
connection\_args={"uri": MILVUS\_URI},
drop\_old=True,
text\_field="txt", # set for preventing conflict with same-name metadata field
)

idx\_pipe = Pipeline()
idx\_pipe.add\_component(
"converter",
DoclingConverter(
export\_type=EXPORT\_TYPE,
chunker=HybridChunker(tokenizer=EMBED\_MODEL\_ID),
),
)
idx\_pipe.add\_component(
"embedder",
SentenceTransformersDocumentEmbedder(model=EMBED\_MODEL\_ID),
)
idx\_pipe.add\_component("writer", DocumentWriter(document\_store=document\_store))
if EXPORT\_TYPE == ExportType.DOC\_CHUNKS:
idx\_pipe.connect("converter", "embedder")
elif EXPORT\_TYPE == ExportType.MARKDOWN:
idx\_pipe.add\_component(
"splitter",
DocumentSplitter(split\_by="sentence", split\_length=1),
)
idx\_pipe.connect("converter.documents", "splitter.documents")
idx\_pipe.connect("splitter.documents", "embedder.documents")
else:
raise ValueError(f"Unexpected export type: {EXPORT\_TYPE}")
idx\_pipe.connect("embedder", "writer")
idx\_pipe.run({"converter": {"paths": PATHS}})

```
Token indices sequence length is longer than the specified maximum sequence length for this model (1041 > 512). Running this sequence through the model will result in indexing errors

```

```
Batches:   0%|          | 0/2 [00:00<?, ?it/s]
```

Out\[3\]:

```
{'writer': {'documents_written': 54}}
```

## RAG pipeline [¶](https://docling-project.github.io/docling/examples/rag_haystack/\#rag-pipeline)

In \[4\]:

Copied!

```
from haystack.components.builders import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.utils import Secret

prompt_template = """
    Given these documents, answer the question.
    Documents:
    {% for doc in documents %}
        {{ doc.content }}
    {% endfor %}
    Question: {{query}}
    Answer:
    """

rag_pipe = Pipeline()
rag_pipe.add_component(
    "embedder",
    SentenceTransformersTextEmbedder(model=EMBED_MODEL_ID),
)
rag_pipe.add_component(
    "retriever",
    MilvusEmbeddingRetriever(document_store=document_store, top_k=TOP_K),
)
rag_pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipe.add_component(
    "llm",
    HuggingFaceAPIGenerator(
        api_type="serverless_inference_api",
        api_params={"model": GENERATION_MODEL_ID},
        token=Secret.from_token(HF_TOKEN) if HF_TOKEN else None,
    ),
)
rag_pipe.add_component("answer_builder", AnswerBuilder())
rag_pipe.connect("embedder.embedding", "retriever")
rag_pipe.connect("retriever", "prompt_builder.documents")
rag_pipe.connect("prompt_builder", "llm")
rag_pipe.connect("llm.replies", "answer_builder.replies")
rag_pipe.connect("llm.meta", "answer_builder.meta")
rag_pipe.connect("retriever", "answer_builder.documents")
rag_res = rag_pipe.run(
    {
        "embedder": {"text": QUESTION},
        "prompt_builder": {"query": QUESTION},
        "answer_builder": {"query": QUESTION},
    }
)

```

from haystack.components.builders import AnswerBuilder
from haystack.components.builders.prompt\_builder import PromptBuilder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.utils import Secret

prompt\_template = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}
Question: {{query}}
Answer:
"""

rag\_pipe = Pipeline()
rag\_pipe.add\_component(
"embedder",
SentenceTransformersTextEmbedder(model=EMBED\_MODEL\_ID),
)
rag\_pipe.add\_component(
"retriever",
MilvusEmbeddingRetriever(document\_store=document\_store, top\_k=TOP\_K),
)
rag\_pipe.add\_component("prompt\_builder", PromptBuilder(template=prompt\_template))
rag\_pipe.add\_component(
"llm",
HuggingFaceAPIGenerator(
api\_type="serverless\_inference\_api",
api\_params={"model": GENERATION\_MODEL\_ID},
token=Secret.from\_token(HF\_TOKEN) if HF\_TOKEN else None,
),
)
rag\_pipe.add\_component("answer\_builder", AnswerBuilder())
rag\_pipe.connect("embedder.embedding", "retriever")
rag\_pipe.connect("retriever", "prompt\_builder.documents")
rag\_pipe.connect("prompt\_builder", "llm")
rag\_pipe.connect("llm.replies", "answer\_builder.replies")
rag\_pipe.connect("llm.meta", "answer\_builder.meta")
rag\_pipe.connect("retriever", "answer\_builder.documents")
rag\_res = rag\_pipe.run(
{
"embedder": {"text": QUESTION},
"prompt\_builder": {"query": QUESTION},
"answer\_builder": {"query": QUESTION},
}
)

```
Batches:   0%|          | 0/1 [00:00<?, ?it/s]
```

```
/Users/pva/work/github.com/docling-project/docling/.venv/lib/python3.12/site-packages/huggingface_hub/inference/_client.py:2232: FutureWarning: `stop_sequences` is a deprecated argument for `text_generation` task and will be removed in version '0.28.0'. Use `stop` instead.
  warnings.warn(

```

Below we print out the RAG results. If you have used `ExportType.DOC_CHUNKS`, notice how
the sources contain document-level grounding (e.g. page number or bounding box
information):

In \[5\]:

Copied!

```
from docling.chunking import DocChunk

print(f"Question:\n{QUESTION}\n")
print(f"Answer:\n{rag_res['answer_builder']['answers'][0].data.strip()}\n")
print("Sources:")
sources = rag_res["answer_builder"]["answers"][0].documents
for source in sources:
    if EXPORT_TYPE == ExportType.DOC_CHUNKS:
        doc_chunk = DocChunk.model_validate(source.meta["dl_meta"])
        print(f"- text: {doc_chunk.text!r}")
        if doc_chunk.meta.origin:
            print(f"  file: {doc_chunk.meta.origin.filename}")
        if doc_chunk.meta.headings:
            print(f"  section: {' / '.join(doc_chunk.meta.headings)}")
        bbox = doc_chunk.meta.doc_items[0].prov[0].bbox
        print(
            f"  page: {doc_chunk.meta.doc_items[0].prov[0].page_no}, "
            f"bounding box: [{int(bbox.l)}, {int(bbox.t)}, {int(bbox.r)}, {int(bbox.b)}]"
        )
    elif EXPORT_TYPE == ExportType.MARKDOWN:
        print(repr(source.content))
    else:
        raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

```

from docling.chunking import DocChunk

print(f"Question:\\n{QUESTION}\\n")
print(f"Answer:\\n{rag\_res\['answer\_builder'\]\['answers'\]\[0\].data.strip()}\\n")
print("Sources:")
sources = rag\_res\["answer\_builder"\]\["answers"\]\[0\].documents
for source in sources:
if EXPORT\_TYPE == ExportType.DOC\_CHUNKS:
doc\_chunk = DocChunk.model\_validate(source.meta\["dl\_meta"\])
print(f"- text: {doc\_chunk.text!r}")
if doc\_chunk.meta.origin:
print(f" file: {doc\_chunk.meta.origin.filename}")
if doc\_chunk.meta.headings:
print(f" section: {' / '.join(doc\_chunk.meta.headings)}")
bbox = doc\_chunk.meta.doc\_items\[0\].prov\[0\].bbox
print(
f" page: {doc\_chunk.meta.doc\_items\[0\].prov\[0\].page\_no}, "
f"bounding box: \[{int(bbox.l)}, {int(bbox.t)}, {int(bbox.r)}, {int(bbox.b)}\]"
)
elif EXPORT\_TYPE == ExportType.MARKDOWN:
print(repr(source.content))
else:
raise ValueError(f"Unexpected export type: {EXPORT\_TYPE}")

```
Question:
Which are the main AI models in Docling?

Answer:
The main AI models in Docling are a layout analysis model and TableFormer. The layout analysis model is an accurate object-detector for page elements, while TableFormer is a state-of-the-art table structure recognition model. These models are provided with pre-trained weights and a separate package for the inference code as docling-ibm-models. They are also used in the open-access deepsearch-experience, a cloud-native service for knowledge exploration tasks. Additionally, Docling plans to extend its model library with a figure-classifier model, an equation-recognition model, a code-recognition model, and more in the future.

Sources:
- text: 'As part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure recognition model. We provide the pre-trained weights (hosted on huggingface) and a separate package for the inference code as docling-ibm-models . Both models are also powering the open-access deepsearch-experience, our cloud-native service for knowledge exploration tasks.'
  file: 2408.09869v5.pdf
  section: 3.2 AI models
  page: 3, bounding box: [107, 406, 504, 330]
- text: 'Docling implements a linear pipeline of operations, which execute sequentially on each given document (see Fig. 1). Each document is first parsed by a PDF backend, which retrieves the programmatic text tokens, consisting of string content and its coordinates on the page, and also renders a bitmap image of each page to support downstream operations. Then, the standard model pipeline applies a sequence of AI models independently on every page in the document to extract features and content, such as layout and table structures. Finally, the results from all pages are aggregated and passed through a post-processing stage, which augments metadata, detects the document language, infers reading-order and eventually assembles a typed document object which can be serialized to JSON or Markdown.'
  file: 2408.09869v5.pdf
  section: 3 Processing pipeline
  page: 2, bounding box: [107, 273, 504, 176]
- text: 'Docling is designed to allow easy extension of the model library and pipelines. In the future, we plan to extend Docling with several more models, such as a figure-classifier model, an equationrecognition model, a code-recognition model and more. This will help improve the quality of conversion for specific types of content, as well as augment extracted document metadata with additional information. Further investment into testing and optimizing GPU acceleration as well as improving the Docling-native PDF backend are on our roadmap, too.\nWe encourage everyone to propose or implement additional features and models, and will gladly take your inputs and contributions under review . The codebase of Docling is open for use and contribution, under the MIT license agreement and in alignment with our contributing guidelines included in the Docling repository. If you use Docling in your projects, please consider citing this technical report.'
  section: 6 Future work and contributions
  page: 5, bounding box: [106, 323, 504, 258]

```

In \[ \]:

Copied!

```

```

Back to top