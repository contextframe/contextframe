---
url: "https://docling-project.github.io/docling/examples/rag_langchain/"
title: "RAG with LangChain - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/rag_langchain/#rag-with-langchain)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/rag_langchain.ipynb)

# RAG with LangChain [¶](https://docling-project.github.io/docling/examples/rag_langchain/\#rag-with-langchain)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | Hugging Face / Sentence Transformers | 💻 Local |
| Vector store | Milvus | 💻 Local |
| Gen AI | Hugging Face Inference API | 🌐 Remote |

This example leverages the
[LangChain Docling integration](https://docling-project.github.io/docling/integrations/langchain/), along with a Milvus
vector store, as well as sentence-transformers embeddings.

The presented `DoclingLoader` component enables you to:

- use various document types in your LLM applications with ease and speed, and
- leverage Docling's rich format for advanced, document-native grounding.

`DoclingLoader` supports two different export modes:

- `ExportType.MARKDOWN`: if you want to capture each input document as a separate
LangChain document, or
- `ExportType.DOC_CHUNKS` (default): if you want to have each input document chunked and
to then capture each individual chunk as a separate LangChain document downstream.

The example allows exploring both modes via parameter `EXPORT_TYPE`; depending on the
value set, the example pipeline is then set up accordingly.

## Setup [¶](https://docling-project.github.io/docling/examples/rag_langchain/\#setup)

- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.
- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.
- Requirements can be installed as shown below ( `--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):

In \[1\]:

Copied!

```
%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain_milvus langchain python-dotenv

```

%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain\_milvus langchain python-dotenv

```
Note: you may need to restart the kernel to use updated packages.

```

In \[2\]:

Copied!

```
import os
from pathlib import Path
from tempfile import mkdtemp

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_docling.loader import ExportType

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

# https://github.com/huggingface/transformers/issues/5486:
os.environ["TOKENIZERS_PARALLELISM"] = "false"

HF_TOKEN = _get_env_from_colab_or_os("HF_TOKEN")
FILE_PATH = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT_TYPE = ExportType.DOC_CHUNKS
QUESTION = "Which are the main AI models in Docling?"
PROMPT = PromptTemplate.from_template(
    "Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {input}\nAnswer:\n",
)
TOP_K = 3
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")

```

import os
from pathlib import Path
from tempfile import mkdtemp

from dotenv import load\_dotenv
from langchain\_core.prompts import PromptTemplate
from langchain\_docling.loader import ExportType

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

\# https://github.com/huggingface/transformers/issues/5486:
os.environ\["TOKENIZERS\_PARALLELISM"\] = "false"

HF\_TOKEN = \_get\_env\_from\_colab\_or\_os("HF\_TOKEN")
FILE\_PATH = \["https://arxiv.org/pdf/2408.09869"\] # Docling Technical Report
EMBED\_MODEL\_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN\_MODEL\_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT\_TYPE = ExportType.DOC\_CHUNKS
QUESTION = "Which are the main AI models in Docling?"
PROMPT = PromptTemplate.from\_template(
"Context information is below.\\n---------------------\\n{context}\\n---------------------\\nGiven the context information and not prior knowledge, answer the query.\\nQuery: {input}\\nAnswer:\\n",
)
TOP\_K = 3
MILVUS\_URI = str(Path(mkdtemp()) / "docling.db")

## Document loading [¶](https://docling-project.github.io/docling/examples/rag_langchain/\#document-loading)

Now we can instantiate our loader and load documents.

In \[3\]:

Copied!

```
from langchain_docling import DoclingLoader

from docling.chunking import HybridChunker

loader = DoclingLoader(
    file_path=FILE_PATH,
    export_type=EXPORT_TYPE,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
)

docs = loader.load()

```

from langchain\_docling import DoclingLoader

from docling.chunking import HybridChunker

loader = DoclingLoader(
file\_path=FILE\_PATH,
export\_type=EXPORT\_TYPE,
chunker=HybridChunker(tokenizer=EMBED\_MODEL\_ID),
)

docs = loader.load()

```
Token indices sequence length is longer than the specified maximum sequence length for this model (1041 > 512). Running this sequence through the model will result in indexing errors

```

> Note: a message saying `"Token indices sequence length is longer than the specified maximum sequence length..."` can be ignored in this case — details
> [here](https://github.com/docling-project/docling-core/issues/119#issuecomment-2577418826).

Determining the splits:

In \[4\]:

Copied!

```
if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    splits = docs
elif EXPORT_TYPE == ExportType.MARKDOWN:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[\
            ("#", "Header_1"),\
            ("##", "Header_2"),\
            ("###", "Header_3"),\
        ],
    )
    splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

```

if EXPORT\_TYPE == ExportType.DOC\_CHUNKS:
splits = docs
elif EXPORT\_TYPE == ExportType.MARKDOWN:
from langchain\_text\_splitters import MarkdownHeaderTextSplitter

splitter = MarkdownHeaderTextSplitter(
headers\_to\_split\_on=\[\
("#", "Header\_1"),\
("##", "Header\_2"),\
("###", "Header\_3"),\
\],
)
splits = \[split for doc in docs for split in splitter.split\_text(doc.page\_content)\]
else:
raise ValueError(f"Unexpected export type: {EXPORT\_TYPE}")

Inspecting some sample splits:

In \[5\]:

Copied!

```
for d in splits[:3]:
    print(f"- {d.page_content=}")
print("...")

```

for d in splits\[:3\]:
print(f"- {d.page\_content=}")
print("...")

```
- d.page_content='arXiv:2408.09869v5  [cs.CL]  9 Dec 2024'
- d.page_content='Docling Technical Report\nVersion 1.0\nChristoph Auer Maksym Lysak Ahmed Nassar Michele Dolfi Nikolaos Livathinos Panos Vagenas Cesar Berrospi Ramis Matteo Omenetti Fabian Lindlbauer Kasper Dinkla Lokesh Mishra Yusik Kim Shubham Gupta Rafael Teixeira de Lima Valery Weber Lucas Morin Ingmar Meijer Viktor Kuropiatnyk Peter W. J. Staar\nAI4K Group, IBM Research R¨uschlikon, Switzerland'
- d.page_content='Abstract\nThis technical report introduces Docling , an easy to use, self-contained, MITlicensed open-source package for PDF document conversion. It is powered by state-of-the-art specialized AI models for layout analysis (DocLayNet) and table structure recognition (TableFormer), and runs efficiently on commodity hardware in a small resource budget. The code interface allows for easy extensibility and addition of new features and models.'
...

```

## Ingestion [¶](https://docling-project.github.io/docling/examples/rag_langchain/\#ingestion)

In \[6\]:

Copied!

```
import json
from pathlib import Path
from tempfile import mkdtemp

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)

milvus_uri = str(Path(mkdtemp()) / "docling.db")  # or set as needed
vectorstore = Milvus.from_documents(
    documents=splits,
    embedding=embedding,
    collection_name="docling_demo",
    connection_args={"uri": milvus_uri},
    index_params={"index_type": "FLAT"},
    drop_old=True,
)

```

import json
from pathlib import Path
from tempfile import mkdtemp

from langchain\_huggingface.embeddings import HuggingFaceEmbeddings
from langchain\_milvus import Milvus

embedding = HuggingFaceEmbeddings(model\_name=EMBED\_MODEL\_ID)

milvus\_uri = str(Path(mkdtemp()) / "docling.db") # or set as needed
vectorstore = Milvus.from\_documents(
documents=splits,
embedding=embedding,
collection\_name="docling\_demo",
connection\_args={"uri": milvus\_uri},
index\_params={"index\_type": "FLAT"},
drop\_old=True,
)

## RAG [¶](https://docling-project.github.io/docling/examples/rag_langchain/\#rag)

In \[7\]:

Copied!

```
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEndpoint

retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm = HuggingFaceEndpoint(
    repo_id=GEN_MODEL_ID,
    huggingfacehub_api_token=HF_TOKEN,
)

def clip_text(text, threshold=100):
    return f"{text[:threshold]}..." if len(text) > threshold else text

```

from langchain.chains import create\_retrieval\_chain
from langchain.chains.combine\_documents import create\_stuff\_documents\_chain
from langchain\_huggingface import HuggingFaceEndpoint

retriever = vectorstore.as\_retriever(search\_kwargs={"k": TOP\_K})
llm = HuggingFaceEndpoint(
repo\_id=GEN\_MODEL\_ID,
huggingfacehub\_api\_token=HF\_TOKEN,
)

def clip\_text(text, threshold=100):
return f"{text\[:threshold\]}..." if len(text) > threshold else text

```
Note: Environment variable`HF_TOKEN` is set and is the current active token independently from the token you've just configured.

```

In \[8\]:

Copied!

```
question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
resp_dict = rag_chain.invoke({"input": QUESTION})

clipped_answer = clip_text(resp_dict["answer"], threshold=200)
print(f"Question:\n{resp_dict['input']}\n\nAnswer:\n{clipped_answer}")
for i, doc in enumerate(resp_dict["context"]):
    print()
    print(f"Source {i + 1}:")
    print(f"  text: {json.dumps(clip_text(doc.page_content, threshold=350))}")
    for key in doc.metadata:
        if key != "pk":
            val = doc.metadata.get(key)
            clipped_val = clip_text(val) if isinstance(val, str) else val
            print(f"  {key}: {clipped_val}")

```

question\_answer\_chain = create\_stuff\_documents\_chain(llm, PROMPT)
rag\_chain = create\_retrieval\_chain(retriever, question\_answer\_chain)
resp\_dict = rag\_chain.invoke({"input": QUESTION})

clipped\_answer = clip\_text(resp\_dict\["answer"\], threshold=200)
print(f"Question:\\n{resp\_dict\['input'\]}\\n\\nAnswer:\\n{clipped\_answer}")
for i, doc in enumerate(resp\_dict\["context"\]):
print()
print(f"Source {i + 1}:")
print(f" text: {json.dumps(clip\_text(doc.page\_content, threshold=350))}")
for key in doc.metadata:
if key != "pk":
val = doc.metadata.get(key)
clipped\_val = clip\_text(val) if isinstance(val, str) else val
print(f" {key}: {clipped\_val}")

```
Question:
Which are the main AI models in Docling?

Answer:
Docling initially releases two AI models, a layout analysis model and TableFormer. The layout analysis model is an accurate object-detector for page elements, and TableFormer is a state-of-the-art tab...

Source 1:
  text: "3.2 AI models\nAs part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure re..."
  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/50', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 3, 'bbox': {'l': 108.0, 't': 405.1419982910156, 'r': 504.00299072265625, 'b': 330.7799987792969, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 608]}]}], 'headings': ['3.2 AI models'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}
  source: https://arxiv.org/pdf/2408.09869

Source 2:
  text: "3 Processing pipeline\nDocling implements a linear pipeline of operations, which execute sequentially on each given document (see Fig. 1). Each document is first parsed by a PDF backend, which retrieves the programmatic text tokens, consisting of string content and its coordinates on the page, and also renders a bitmap image of each page to support ..."
  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/26', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 2, 'bbox': {'l': 108.0, 't': 273.01800537109375, 'r': 504.00299072265625, 'b': 176.83799743652344, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 796]}]}], 'headings': ['3 Processing pipeline'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}
  source: https://arxiv.org/pdf/2408.09869

Source 3:
  text: "6 Future work and contributions\nDocling is designed to allow easy extension of the model library and pipelines. In the future, we plan to extend Docling with several more models, such as a figure-classifier model, an equationrecognition model, a code-recognition model and more. This will help improve the quality of conversion for specific types of ..."
  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/76', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 5, 'bbox': {'l': 108.0, 't': 322.468994140625, 'r': 504.00299072265625, 'b': 259.0169982910156, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 543]}]}, {'self_ref': '#/texts/77', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 5, 'bbox': {'l': 108.0, 't': 251.6540069580078, 'r': 504.00299072265625, 'b': 198.99200439453125, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 402]}]}], 'headings': ['6 Future work and contributions'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}
  source: https://arxiv.org/pdf/2408.09869

```

In \[ \]:

Copied!

```

```

Back to top