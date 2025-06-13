---
url: "https://docling-project.github.io/docling/examples/visual_grounding/"
title: "Visual grounding - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/visual_grounding/#visual-grounding)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/visual_grounding.ipynb)

# Visual grounding [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#visual-grounding)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | Hugging Face / Sentence Transformers | 💻 Local |
| Vector store | Milvus | 💻 Local |
| Gen AI | Hugging Face Inference API | 🌐 Remote |

This example showcases Docling's **visual grounding** capabilities, which can be combined
with any agentic AI / RAG framework.

In this instance, we illustrate these capabilities leveraging the
[LangChain Docling integration](https://docling-project.github.io/docling/integrations/langchain/), along with a Milvus
vector store, as well as sentence-transformers embeddings.

## Setup [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#setup)

- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.
- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.
- Requirements can be installed as shown below ( `--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):

In \[1\]:

Copied!

```
%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain_milvus langchain matplotlib python-dotenv

```

%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain\_milvus langchain matplotlib python-dotenv

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
SOURCES = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
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
SOURCES = \["https://arxiv.org/pdf/2408.09869"\] # Docling Technical Report
EMBED\_MODEL\_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN\_MODEL\_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
QUESTION = "Which are the main AI models in Docling?"
PROMPT = PromptTemplate.from\_template(
"Context information is below.\\n---------------------\\n{context}\\n---------------------\\nGiven the context information and not prior knowledge, answer the query.\\nQuery: {input}\\nAnswer:\\n",
)
TOP\_K = 3
MILVUS\_URI = str(Path(mkdtemp()) / "docling.db")

## Document store setup [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#document-store-setup)

## Document loading [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#document-loading)

We first define our converter, in this case including options for keeping page images (for visual grounding).

In \[3\]:

Copied!

```
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=PdfPipelineOptions(
                generate_page_images=True,
                images_scale=2.0,
            ),
        )
    }
)

```

from docling.datamodel.base\_models import InputFormat
from docling.datamodel.pipeline\_options import PdfPipelineOptions
from docling.document\_converter import DocumentConverter, PdfFormatOption

converter = DocumentConverter(
format\_options={
InputFormat.PDF: PdfFormatOption(
pipeline\_options=PdfPipelineOptions(
generate\_page\_images=True,
images\_scale=2.0,
),
)
}
)

We set up a simple doc store for keeping converted documents, as that is needed for visual grounding further below.

In \[4\]:

Copied!

```
doc_store = {}
doc_store_root = Path(mkdtemp())
for source in SOURCES:
    dl_doc = converter.convert(source=source).document
    file_path = Path(doc_store_root / f"{dl_doc.origin.binary_hash}.json")
    dl_doc.save_as_json(file_path)
    doc_store[dl_doc.origin.binary_hash] = file_path

```

doc\_store = {}
doc\_store\_root = Path(mkdtemp())
for source in SOURCES:
dl\_doc = converter.convert(source=source).document
file\_path = Path(doc\_store\_root / f"{dl\_doc.origin.binary\_hash}.json")
dl\_doc.save\_as\_json(file\_path)
doc\_store\[dl\_doc.origin.binary\_hash\] = file\_path

Now we can instantiate our loader and load documents.

In \[5\]:

Copied!

```
from langchain_docling import DoclingLoader

from docling.chunking import HybridChunker

loader = DoclingLoader(
    file_path=SOURCES,
    converter=converter,
    export_type=ExportType.DOC_CHUNKS,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
)

docs = loader.load()

```

from langchain\_docling import DoclingLoader

from docling.chunking import HybridChunker

loader = DoclingLoader(
file\_path=SOURCES,
converter=converter,
export\_type=ExportType.DOC\_CHUNKS,
chunker=HybridChunker(tokenizer=EMBED\_MODEL\_ID),
)

docs = loader.load()

```
Token indices sequence length is longer than the specified maximum sequence length for this model (648 > 512). Running this sequence through the model will result in indexing errors

```

> 👉 **NOTE**: As you see above, using the `HybridChunker` can sometimes lead to a warning from the transformers library, however this is a "false alarm" — for details check [here](https://docling-project.github.io/docling/faq/#hybridchunker-triggers-warning-token-indices-sequence-length-is-longer-than-the-specified-maximum-sequence-length-for-this-model).

Inspecting some sample splits:

In \[6\]:

Copied!

```
for d in docs[:3]:
    print(f"- {d.page_content=}")
print("...")

```

for d in docs\[:3\]:
print(f"- {d.page\_content=}")
print("...")

```
- d.page_content='Docling Technical Report\nVersion 1.0\nChristoph Auer Maksym Lysak Ahmed Nassar Michele Dolfi Nikolaos Livathinos Panos Vagenas Cesar Berrospi Ramis Matteo Omenetti Fabian Lindlbauer Kasper Dinkla Lokesh Mishra Yusik Kim Shubham Gupta Rafael Teixeira de Lima Valery Weber Lucas Morin Ingmar Meijer Viktor Kuropiatnyk Peter W. J. Staar\nAI4K Group, IBM Research R¨ uschlikon, Switzerland'
- d.page_content='Abstract\nThis technical report introduces Docling , an easy to use, self-contained, MITlicensed open-source package for PDF document conversion. It is powered by state-of-the-art specialized AI models for layout analysis (DocLayNet) and table structure recognition (TableFormer), and runs efficiently on commodity hardware in a small resource budget. The code interface allows for easy extensibility and addition of new features and models.'
- d.page_content='1 Introduction\nConverting PDF documents back into a machine-processable format has been a major challenge for decades due to their huge variability in formats, weak standardization and printing-optimized characteristic, which discards most structural features and metadata. With the advent of LLMs and popular application patterns such as retrieval-augmented generation (RAG), leveraging the rich content embedded in PDFs has become ever more relevant. In the past decade, several powerful document understanding solutions have emerged on the market, most of which are commercial software, cloud offerings [3] and most recently, multi-modal vision-language models. As of today, only a handful of open-source tools cover PDF conversion, leaving a significant feature and quality gap to proprietary solutions.\nWith Docling , we open-source a very capable and efficient document conversion tool which builds on the powerful, specialized AI models and datasets for layout analysis and table structure recognition we developed and presented in the recent past [12, 13, 9]. Docling is designed as a simple, self-contained python library with permissive license, running entirely locally on commodity hardware. Its code architecture allows for easy extensibility and addition of new features and models.\nHere is what Docling delivers today:\n· Converts PDF documents to JSON or Markdown format, stable and lightning fast\n· Understands detailed page layout, reading order, locates figures and recovers table structures\n· Extracts metadata from the document, such as title, authors, references and language\n· Optionally applies OCR, e.g. for scanned PDFs\n· Can be configured to be optimal for batch-mode (i.e high throughput, low time-to-solution) or interactive mode (compromise on efficiency, low time-to-solution)\n· Can leverage different accelerators (GPU, MPS, etc).'
...

```

## Ingestion [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#ingestion)

In \[7\]:

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
    documents=docs,
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
documents=docs,
embedding=embedding,
collection\_name="docling\_demo",
connection\_args={"uri": milvus\_uri},
index\_params={"index\_type": "FLAT"},
drop\_old=True,
)

## RAG [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#rag)

In \[8\]:

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

In \[9\]:

Copied!

```
from docling.chunking import DocMeta
from docling.datamodel.document import DoclingDocument

question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
resp_dict = rag_chain.invoke({"input": QUESTION})

clipped_answer = clip_text(resp_dict["answer"], threshold=200)
print(f"Question:\n{resp_dict['input']}\n\nAnswer:\n{clipped_answer}")

```

from docling.chunking import DocMeta
from docling.datamodel.document import DoclingDocument

question\_answer\_chain = create\_stuff\_documents\_chain(llm, PROMPT)
rag\_chain = create\_retrieval\_chain(retriever, question\_answer\_chain)
resp\_dict = rag\_chain.invoke({"input": QUESTION})

clipped\_answer = clip\_text(resp\_dict\["answer"\], threshold=200)
print(f"Question:\\n{resp\_dict\['input'\]}\\n\\nAnswer:\\n{clipped\_answer}")

```
/Users/pva/work/github.com/DS4SD/docling/.venv/lib/python3.12/site-packages/huggingface_hub/utils/_deprecation.py:131: FutureWarning: 'post' (from 'huggingface_hub.inference._client') is deprecated and will be removed from version '0.31.0'. Making direct POST requests to the inference server is not supported anymore. Please use task methods instead (e.g. `InferenceClient.chat_completion`). If your use case is not supported, please open an issue in https://github.com/huggingface/huggingface_hub.
  warnings.warn(warning_message, FutureWarning)

```

```
Question:
Which are the main AI models in Docling?

Answer:
The main AI models in Docling are:
1. A layout analysis model, an accurate object-detector for page elements.
2. TableFormer, a state-of-the-art table structure recognition model.

```

### Visual grounding [¶](https://docling-project.github.io/docling/examples/visual_grounding/\#visual-grounding)

In \[10\]:

Copied!

```
import matplotlib.pyplot as plt
from PIL import ImageDraw

for i, doc in enumerate(resp_dict["context"][:]):
    image_by_page = {}
    print(f"Source {i + 1}:")
    print(f"  text: {json.dumps(clip_text(doc.page_content, threshold=350))}")
    meta = DocMeta.model_validate(doc.metadata["dl_meta"])

    # loading the full DoclingDocument from the document store:
    dl_doc = DoclingDocument.load_from_json(doc_store.get(meta.origin.binary_hash))

    for doc_item in meta.doc_items:
        if doc_item.prov:
            prov = doc_item.prov[0]  # here we only consider the first provenence item
            page_no = prov.page_no
            if img := image_by_page.get(page_no):
                pass
            else:
                page = dl_doc.pages[prov.page_no]
                print(f"  page: {prov.page_no}")
                img = page.image.pil_image
                image_by_page[page_no] = img
            bbox = prov.bbox.to_top_left_origin(page_height=page.size.height)
            bbox = bbox.normalized(page.size)
            thickness = 2
            padding = thickness + 2
            bbox.l = round(bbox.l * img.width - padding)
            bbox.r = round(bbox.r * img.width + padding)
            bbox.t = round(bbox.t * img.height - padding)
            bbox.b = round(bbox.b * img.height + padding)
            draw = ImageDraw.Draw(img)
            draw.rectangle(
                xy=bbox.as_tuple(),
                outline="blue",
                width=thickness,
            )
    for p in image_by_page:
        img = image_by_page[p]
        plt.figure(figsize=[15, 15])
        plt.imshow(img)
        plt.axis("off")
        plt.show()

```

import matplotlib.pyplot as plt
from PIL import ImageDraw

for i, doc in enumerate(resp\_dict\["context"\]\[:\]):
image\_by\_page = {}
print(f"Source {i + 1}:")
print(f" text: {json.dumps(clip\_text(doc.page\_content, threshold=350))}")
meta = DocMeta.model\_validate(doc.metadata\["dl\_meta"\])

# loading the full DoclingDocument from the document store:
dl\_doc = DoclingDocument.load\_from\_json(doc\_store.get(meta.origin.binary\_hash))

for doc\_item in meta.doc\_items:
if doc\_item.prov:
prov = doc\_item.prov\[0\] # here we only consider the first provenence item
page\_no = prov.page\_no
if img := image\_by\_page.get(page\_no):
pass
else:
page = dl\_doc.pages\[prov.page\_no\]
print(f" page: {prov.page\_no}")
img = page.image.pil\_image
image\_by\_page\[page\_no\] = img
bbox = prov.bbox.to\_top\_left\_origin(page\_height=page.size.height)
bbox = bbox.normalized(page.size)
thickness = 2
padding = thickness + 2
bbox.l = round(bbox.l \* img.width - padding)
bbox.r = round(bbox.r \* img.width + padding)
bbox.t = round(bbox.t \* img.height - padding)
bbox.b = round(bbox.b \* img.height + padding)
draw = ImageDraw.Draw(img)
draw.rectangle(
xy=bbox.as\_tuple(),
outline="blue",
width=thickness,
)
for p in image\_by\_page:
img = image\_by\_page\[p\]
plt.figure(figsize=\[15, 15\])
plt.imshow(img)
plt.axis("off")
plt.show()

```
Source 1:
  text: "3.2 AI models\nAs part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure re..."
  page: 3

```

![No description has been provided for this image](<Base64-Image-Removed>)

```
Source 2:
  text: "3 Processing pipeline\nDocling implements a linear pipeline of operations, which execute sequentially on each given document (see Fig. 1). Each document is first parsed by a PDF backend, which retrieves the programmatic text tokens, consisting of string content and its coordinates on the page, and also renders a bitmap image of each page to support ..."
  page: 2

```

![No description has been provided for this image](<Base64-Image-Removed>)

```
Source 3:
  text: "6 Future work and contributions\nDocling is designed to allow easy extension of the model library and pipelines. In the future, we plan to extend Docling with several more models, such as a figure-classifier model, an equationrecognition model, a code-recognition model and more. This will help improve the quality of conversion for specific types of ..."
  page: 5

```

![No description has been provided for this image](<Base64-Image-Removed>)

In \[ \]:

Copied!

```

```

Back to top