---
url: "https://docling-project.github.io/docling/examples/rag_milvus/"
title: "RAG with Milvus - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/rag_milvus/#rag-with-milvus)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/rag_milvus.ipynb)

# RAG with Milvus [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#rag-with-milvus)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | OpenAI (text-embedding-3-small) | 🌐 Remote |
| Vector store | Milvus | 💻 Local |
| Gen AI | OpenAI (gpt-4o) | 🌐 Remote |

## A recipe 🧑‍🍳 🐥 💚 [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#a-recipe)

This is a code recipe that uses [Milvus](https://milvus.io/), the world's most advanced open-source vector database, to perform RAG over documents parsed by [Docling](https://docling-project.github.io/docling/).

In this notebook, we accomplish the following:

- Parse documents using Docling's document conversion capabilities
- Perform hierarchical chunking of the documents using Docling
- Generate text embeddings with OpenAI
- Perform RAG using Milvus, the world's most advanced open-source vector database

Note: For best results, please use **GPU acceleration** to run this notebook. Here are two options for running this notebook:

1. **Locally on a MacBook with an Apple Silicon chip.** Converting all documents in the notebook takes ~2 minutes on a MacBook M2 due to Docling's usage of MPS accelerators.
2. **Run this notebook on Google Colab.** Converting all documents in the notebook takes ~8 minutes on a Google Colab T4 GPU.

## Preparation [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#preparation)

### Dependencies and Environment [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#dependencies-and-environment)

To start, install the required dependencies by running the following command:

In \[ \]:

Copied!

```
! pip install --upgrade pymilvus docling openai torch

```

! pip install --upgrade pymilvus docling openai torch

> If you are using Google Colab, to enable dependencies just installed, you may need to **restart the runtime** (click on the "Runtime" menu at the top of the screen, and select "Restart session" from the dropdown menu).

### GPU Checking [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#gpu-checking)

Part of what makes Docling so remarkable is the fact that it can run on commodity hardware. This means that this notebook can be run on a local machine with GPU acceleration. If you're using a MacBook with a silicon chip, Docling integrates seamlessly with Metal Performance Shaders (MPS). MPS provides out-of-the-box GPU acceleration for macOS, seamlessly integrating with PyTorch and TensorFlow, offering energy-efficient performance on Apple Silicon, and broad compatibility with all Metal-supported GPUs.

The code below checks to see if a GPU is available, either via CUDA or MPS.

In \[1\]:

Copied!

```
import torch

# Check if GPU or MPS is available
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"CUDA GPU is enabled: {torch.cuda.get_device_name(0)}")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    print("MPS GPU is enabled.")
else:
    raise OSError(
        "No GPU or MPS device found. Please check your environment and ensure GPU or MPS support is configured."
    )

```

import torch

\# Check if GPU or MPS is available
if torch.cuda.is\_available():
device = torch.device("cuda")
print(f"CUDA GPU is enabled: {torch.cuda.get\_device\_name(0)}")
elif torch.backends.mps.is\_available():
device = torch.device("mps")
print("MPS GPU is enabled.")
else:
raise OSError(
"No GPU or MPS device found. Please check your environment and ensure GPU or MPS support is configured."
)

```
MPS GPU is enabled.

```

### Setting Up API Keys [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#setting-up-api-keys)

We will use OpenAI as the LLM in this example. You should prepare the [OPENAI\_API\_KEY](https://platform.openai.com/docs/quickstart) as an environment variable.

In \[2\]:

Copied!

```
import os

os.environ["OPENAI_API_KEY"] = "sk-***********"

```

import os

os.environ\["OPENAI\_API\_KEY"\] = "sk-\*\*\*\*\*\*\*\*\*\*\*"

### Prepare the LLM and Embedding Model [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#prepare-the-llm-and-embedding-model)

We initialize the OpenAI client to prepare the embedding model.

In \[3\]:

Copied!

```
from openai import OpenAI

openai_client = OpenAI()

```

from openai import OpenAI

openai\_client = OpenAI()

Define a function to generate text embeddings using OpenAI client. We use the [text-embedding-3-small](https://platform.openai.com/docs/guides/embeddings) model as an example.

In \[4\]:

Copied!

```
def emb_text(text):
    return (
        openai_client.embeddings.create(input=text, model="text-embedding-3-small")
        .data[0]
        .embedding
    )

```

def emb\_text(text):
return (
openai\_client.embeddings.create(input=text, model="text-embedding-3-small")
.data\[0\]
.embedding
)

Generate a test embedding and print its dimension and first few elements.

In \[5\]:

Copied!

```
test_embedding = emb_text("This is a test")
embedding_dim = len(test_embedding)
print(embedding_dim)
print(test_embedding[:10])

```

test\_embedding = emb\_text("This is a test")
embedding\_dim = len(test\_embedding)
print(embedding\_dim)
print(test\_embedding\[:10\])

```
1536
[0.009889289736747742, -0.005578675772994757, 0.00683477520942688, -0.03805781528353691, -0.01824733428657055, -0.04121600463986397, -0.007636285852640867, 0.03225184231996536, 0.018949154764413834, 9.352207416668534e-05]

```

## Process Data Using Docling [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#process-data-using-docling)

Docling can parse various document formats into a unified representation (Docling Document), which can then be exported to different output formats. For a full list of supported input and output formats, please refer to [the official documentation](https://docling-project.github.io/docling/usage/supported_formats/).

In this tutorial, we will use a Markdown file ( [source](https://milvus.io/docs/overview.md)) as the input. We will process the document using a **HierarchicalChunker** provided by Docling to generate structured, hierarchical chunks suitable for downstream RAG tasks.

In \[6\]:

Copied!

```
from docling_core.transforms.chunker import HierarchicalChunker

from docling.document_converter import DocumentConverter

converter = DocumentConverter()
chunker = HierarchicalChunker()

# Convert the input file to Docling Document
source = "https://milvus.io/docs/overview.md"
doc = converter.convert(source).document

# Perform hierarchical chunking
texts = [chunk.text for chunk in chunker.chunk(doc)]

```

from docling\_core.transforms.chunker import HierarchicalChunker

from docling.document\_converter import DocumentConverter

converter = DocumentConverter()
chunker = HierarchicalChunker()

\# Convert the input file to Docling Document
source = "https://milvus.io/docs/overview.md"
doc = converter.convert(source).document

\# Perform hierarchical chunking
texts = \[chunk.text for chunk in chunker.chunk(doc)\]

## Load Data into Milvus [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#load-data-into-milvus)

### Create the collection [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#create-the-collection)

With data in hand, we can create a `MilvusClient` instance and insert the data into a Milvus collection.

In \[7\]:

Copied!

```
from pymilvus import MilvusClient

milvus_client = MilvusClient(uri="./milvus_demo.db")
collection_name = "my_rag_collection"

```

from pymilvus import MilvusClient

milvus\_client = MilvusClient(uri="./milvus\_demo.db")
collection\_name = "my\_rag\_collection"

> As for the argument of `MilvusClient`:
>
> - Setting the `uri` as a local file, e.g. `./milvus.db`, is the most convenient method, as it automatically utilizes [Milvus Lite](https://milvus.io/docs/milvus_lite.md) to store all data in this file.
> - If you have large scale of data, you can set up a more performant Milvus server on [docker or kubernetes](https://milvus.io/docs/quickstart.md). In this setup, please use the server uri, e.g. `http://localhost:19530`, as your `uri`.
> - If you want to use [Zilliz Cloud](https://zilliz.com/cloud), the fully managed cloud service for Milvus, adjust the `uri` and `token`, which correspond to the [Public Endpoint and Api key](https://docs.zilliz.com/docs/on-zilliz-cloud-console#free-cluster-details) in Zilliz Cloud.

Check if the collection already exists and drop it if it does.

In \[8\]:

Copied!

```
if milvus_client.has_collection(collection_name):
    milvus_client.drop_collection(collection_name)

```

if milvus\_client.has\_collection(collection\_name):
milvus\_client.drop\_collection(collection\_name)

Create a new collection with specified parameters.

If we don’t specify any field information, Milvus will automatically create a default `id` field for primary key, and a `vector` field to store the vector data. A reserved JSON field is used to store non-schema-defined fields and their values.

In \[9\]:

Copied!

```
milvus_client.create_collection(
    collection_name=collection_name,
    dimension=embedding_dim,
    metric_type="IP",  # Inner product distance
    consistency_level="Strong",  # Supported values are (`"Strong"`, `"Session"`, `"Bounded"`, `"Eventually"`). See https://milvus.io/docs/consistency.md#Consistency-Level for more details.
)

```

milvus\_client.create\_collection(
collection\_name=collection\_name,
dimension=embedding\_dim,
metric\_type="IP", # Inner product distance
consistency\_level="Strong", # Supported values are (\`"Strong"\`, \`"Session"\`, \`"Bounded"\`, \`"Eventually"\`). See https://milvus.io/docs/consistency.md#Consistency-Level for more details.
)

### Insert data [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#insert-data)

In \[10\]:

Copied!

```
from tqdm import tqdm

data = []

for i, chunk in enumerate(tqdm(texts, desc="Processing chunks")):
    embedding = emb_text(chunk)
    data.append({"id": i, "vector": embedding, "text": chunk})

milvus_client.insert(collection_name=collection_name, data=data)

```

from tqdm import tqdm

data = \[\]

for i, chunk in enumerate(tqdm(texts, desc="Processing chunks")):
embedding = emb\_text(chunk)
data.append({"id": i, "vector": embedding, "text": chunk})

milvus\_client.insert(collection\_name=collection\_name, data=data)

```
Processing chunks: 100%|██████████| 38/38 [00:14<00:00,  2.59it/s]

```

Out\[10\]:

```
{'insert_count': 38, 'ids': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37], 'cost': 0}
```

## Build RAG [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#build-rag)

### Retrieve data for a query [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#retrieve-data-for-a-query)

Let’s specify a query question about the website we just scraped.

In \[11\]:

Copied!

```
question = (
    "What are the three deployment modes of Milvus, and what are their differences?"
)

```

question = (
"What are the three deployment modes of Milvus, and what are their differences?"
)

Search for the question in the collection and retrieve the semantic top-3 matches.

In \[12\]:

Copied!

```
search_res = milvus_client.search(
    collection_name=collection_name,
    data=[emb_text(question)],
    limit=3,
    search_params={"metric_type": "IP", "params": {}},
    output_fields=["text"],
)

```

search\_res = milvus\_client.search(
collection\_name=collection\_name,
data=\[emb\_text(question)\],
limit=3,
search\_params={"metric\_type": "IP", "params": {}},
output\_fields=\["text"\],
)

Let’s take a look at the search results of the query

In \[13\]:

Copied!

```
import json

retrieved_lines_with_distances = [\
    (res["entity"]["text"], res["distance"]) for res in search_res[0]\
]
print(json.dumps(retrieved_lines_with_distances, indent=4))

```

import json

retrieved\_lines\_with\_distances = \[\
(res\["entity"\]\["text"\], res\["distance"\]) for res in search\_res\[0\]\
\]
print(json.dumps(retrieved\_lines\_with\_distances, indent=4))

```
[\
    [\
        "Milvus offers three deployment modes, covering a wide range of data scales\u2014from local prototyping in Jupyter Notebooks to massive Kubernetes clusters managing tens of billions of vectors:",\
        0.6503315567970276\
    ],\
    [\
        "Milvus Lite is a Python library that can be easily integrated into your applications. As a lightweight version of Milvus, it\u2019s ideal for quick prototyping in Jupyter Notebooks or running on edge devices with limited resources. Learn more.\nMilvus Standalone is a single-machine server deployment, with all components bundled into a single Docker image for convenient deployment. Learn more.\nMilvus Distributed can be deployed on Kubernetes clusters, featuring a cloud-native architecture designed for billion-scale or even larger scenarios. This architecture ensures redundancy in critical components. Learn more.",\
        0.6281915903091431\
    ],\
    [\
        "What is Milvus?\nUnstructured Data, Embeddings, and Milvus\nWhat Makes Milvus so Fast\uff1f\nWhat Makes Milvus so Scalable\nTypes of Searches Supported by Milvus\nComprehensive Feature Set",\
        0.6117826700210571\
    ]\
]

```

### Use LLM to get a RAG response [¶](https://docling-project.github.io/docling/examples/rag_milvus/\#use-llm-to-get-a-rag-response)

Convert the retrieved documents into a string format.

In \[14\]:

Copied!

```
context = "\n".join(
    [line_with_distance[0] for line_with_distance in retrieved_lines_with_distances]
)

```

context = "\\n".join(
\[line\_with\_distance\[0\] for line\_with\_distance in retrieved\_lines\_with\_distances\]
)

Define system and user prompts for the Lanage Model. This prompt is assembled with the retrieved documents from Milvus.

In \[16\]:

Copied!

```
SYSTEM_PROMPT = """
Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
"""
USER_PROMPT = f"""
Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.
<context>
{context}
</context>
<question>
{question}
</question>
"""

```

SYSTEM\_PROMPT = """
Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
"""
USER\_PROMPT = f"""
Use the following pieces of information enclosed in  tags to provide an answer to the question enclosed in  tags.

{context}

{question}

"""

Use OpenAI ChatGPT to generate a response based on the prompts.

In \[17\]:

Copied!

```
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[\
        {"role": "system", "content": SYSTEM_PROMPT},\
        {"role": "user", "content": USER_PROMPT},\
    ],
)
print(response.choices[0].message.content)

```

response = openai\_client.chat.completions.create(
model="gpt-4o",
messages=\[\
{"role": "system", "content": SYSTEM\_PROMPT},\
{"role": "user", "content": USER\_PROMPT},\
\],
)
print(response.choices\[0\].message.content)

```
The three deployment modes of Milvus are:

1. **Milvus Lite**: This is a Python library that integrates easily into your applications. It's a lightweight version ideal for quick prototyping in Jupyter Notebooks or for running on edge devices with limited resources.

2. **Milvus Standalone**: This mode is a single-machine server deployment where all components are bundled into a single Docker image, making it convenient to deploy.

3. **Milvus Distributed**: This mode is designed for deployment on Kubernetes clusters. It features a cloud-native architecture suited for managing scenarios at a billion-scale or larger, ensuring redundancy in critical components.

```

Back to top