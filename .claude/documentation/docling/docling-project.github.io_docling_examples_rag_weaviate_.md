---
url: "https://docling-project.github.io/docling/examples/rag_weaviate/"
title: "RAG with Weaviate - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/rag_weaviate/#rag-with-weaviate)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/rag_weaviate.ipynb)

# RAG with Weaviate [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#rag-with-weaviate)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | Open AI | 🌐 Remote |
| Vector store | Weavieate | 💻 Local |
| Gen AI | Open AI | 🌐 Remote |

## A recipe 🧑‍🍳 🐥 💚 [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#a-recipe)

This is a code recipe that uses [Weaviate](https://weaviate.io/) to perform RAG over PDF documents parsed by [Docling](https://docling-project.github.io/docling/).

In this notebook, we accomplish the following:

- Parse the top machine learning papers on [arXiv](https://arxiv.org/) using Docling
- Perform hierarchical chunking of the documents using Docling
- Generate text embeddings with OpenAI
- Perform RAG using [Weaviate](https://weaviate.io/developers/weaviate/search/generative)

To run this notebook, you'll need:

- An [OpenAI API key](https://platform.openai.com/docs/quickstart)
- Access to GPU/s

Note: For best results, please use **GPU acceleration** to run this notebook. Here are two options for running this notebook:

1. **Locally on a MacBook with an Apple Silicon chip.** Converting all documents in the notebook takes ~2 minutes on a MacBook M2 due to Docling's usage of MPS accelerators.
2. **Run this notebook on Google Colab.** Converting all documents in the notebook takes ~8 minutes on a Google Colab T4 GPU.

### Install Docling and Weaviate client [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#install-docling-and-weaviate-client)

Note: If Colab prompts you to restart the session after running the cell below, click "restart" and proceed with running the rest of the notebook.

In \[ \]:

Copied!

```
%%capture
%pip install docling~="2.7.0"
%pip install -U weaviate-client~="4.9.4"
%pip install rich
%pip install torch

import logging
import warnings

warnings.filterwarnings("ignore")

# Suppress Weaviate client logs
logging.getLogger("weaviate").setLevel(logging.ERROR)

```

%%capture
%pip install docling~="2.7.0"
%pip install -U weaviate-client~="4.9.4"
%pip install rich
%pip install torch

import logging
import warnings

warnings.filterwarnings("ignore")

\# Suppress Weaviate client logs
logging.getLogger("weaviate").setLevel(logging.ERROR)

## 🐥 Part 1: Docling [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#part-1-docling)

Part of what makes Docling so remarkable is the fact that it can run on commodity hardware. This means that this notebook can be run on a local machine with GPU acceleration. If you're using a MacBook with a silicon chip, Docling integrates seamlessly with Metal Performance Shaders (MPS). MPS provides out-of-the-box GPU acceleration for macOS, seamlessly integrating with PyTorch and TensorFlow, offering energy-efficient performance on Apple Silicon, and broad compatibility with all Metal-supported GPUs.

The code below checks to see if a GPU is available, either via CUDA or MPS.

In \[2\]:

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

Here, we've collected 10 influential machine learning papers published as PDFs on arXiv. Because Docling does not yet have title extraction for PDFs, we manually add the titles in a corresponding list.

Note: Converting all 10 papers should take around 8 minutes with a T4 GPU.

In \[3\]:

Copied!

```
# Influential machine learning papers
source_urls = [\
    "https://arxiv.org/pdf/1706.03762",\
    "https://arxiv.org/pdf/1810.04805",\
    "https://arxiv.org/pdf/1406.2661",\
    "https://arxiv.org/pdf/1409.0473",\
    "https://arxiv.org/pdf/1412.6980",\
    "https://arxiv.org/pdf/1312.6114",\
    "https://arxiv.org/pdf/1312.5602",\
    "https://arxiv.org/pdf/1512.03385",\
    "https://arxiv.org/pdf/1409.3215",\
    "https://arxiv.org/pdf/1301.3781",\
]

# And their corresponding titles (because Docling doesn't have title extraction yet!)
source_titles = [\
    "Attention Is All You Need",\
    "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",\
    "Generative Adversarial Nets",\
    "Neural Machine Translation by Jointly Learning to Align and Translate",\
    "Adam: A Method for Stochastic Optimization",\
    "Auto-Encoding Variational Bayes",\
    "Playing Atari with Deep Reinforcement Learning",\
    "Deep Residual Learning for Image Recognition",\
    "Sequence to Sequence Learning with Neural Networks",\
    "A Neural Probabilistic Language Model",\
]

```

\# Influential machine learning papers
source\_urls = \[\
"https://arxiv.org/pdf/1706.03762",\
"https://arxiv.org/pdf/1810.04805",\
"https://arxiv.org/pdf/1406.2661",\
"https://arxiv.org/pdf/1409.0473",\
"https://arxiv.org/pdf/1412.6980",\
"https://arxiv.org/pdf/1312.6114",\
"https://arxiv.org/pdf/1312.5602",\
"https://arxiv.org/pdf/1512.03385",\
"https://arxiv.org/pdf/1409.3215",\
"https://arxiv.org/pdf/1301.3781",\
\]

\# And their corresponding titles (because Docling doesn't have title extraction yet!)
source\_titles = \[\
"Attention Is All You Need",\
"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",\
"Generative Adversarial Nets",\
"Neural Machine Translation by Jointly Learning to Align and Translate",\
"Adam: A Method for Stochastic Optimization",\
"Auto-Encoding Variational Bayes",\
"Playing Atari with Deep Reinforcement Learning",\
"Deep Residual Learning for Image Recognition",\
"Sequence to Sequence Learning with Neural Networks",\
"A Neural Probabilistic Language Model",\
\]

### Convert PDFs to Docling documents [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#convert-pdfs-to-docling-documents)

Here we use Docling's `.convert_all()` to parse a batch of PDFs. The result is a list of Docling documents that we can use for text extraction.

Note: Please ignore the `ERR#` message.

In \[4\]:

Copied!

```
from docling.document_converter import DocumentConverter

# Instantiate the doc converter
doc_converter = DocumentConverter()

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(source_urls)  # previously `convert`

# Iterate over the generator to get a list of Docling documents
docs = [result.document for result in conv_results_iter]

```

from docling.document\_converter import DocumentConverter

\# Instantiate the doc converter
doc\_converter = DocumentConverter()

\# Directly pass list of files or streams to \`convert\_all\`
conv\_results\_iter = doc\_converter.convert\_all(source\_urls) # previously \`convert\`

\# Iterate over the generator to get a list of Docling documents
docs = \[result.document for result in conv\_results\_iter\]

```
Fetching 9 files: 100%|██████████| 9/9 [00:00<00:00, 84072.91it/s]

```

```
ERR#: COULD NOT CONVERT TO RS THIS TABLE TO COMPUTE SPANS

```

### Post-process extracted document data [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#post-process-extracted-document-data)

#### Perform hierarchical chunking on documents [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#perform-hierarchical-chunking-on-documents)

We use Docling's `HierarchicalChunker()` to perform hierarchy-aware chunking of our list of documents. This is meant to preserve some of the structure and relationships within the document, which enables more accurate and relevant retrieval in our RAG pipeline.

In \[5\]:

Copied!

```
from docling_core.transforms.chunker import HierarchicalChunker

# Initialize lists for text, and titles
texts, titles = [], []

chunker = HierarchicalChunker()

# Process each document in the list
for doc, title in zip(docs, source_titles):  # Pair each document with its title
    chunks = list(
        chunker.chunk(doc)
    )  # Perform hierarchical chunking and get text from chunks
    for chunk in chunks:
        texts.append(chunk.text)
        titles.append(title)

```

from docling\_core.transforms.chunker import HierarchicalChunker

\# Initialize lists for text, and titles
texts, titles = \[\], \[\]

chunker = HierarchicalChunker()

\# Process each document in the list
for doc, title in zip(docs, source\_titles): # Pair each document with its title
chunks = list(
chunker.chunk(doc)
) # Perform hierarchical chunking and get text from chunks
for chunk in chunks:
texts.append(chunk.text)
titles.append(title)

Because we're splitting the documents into chunks, we'll concatenate the article title to the beginning of each chunk for additional context.

In \[6\]:

Copied!

```
# Concatenate title and text
for i in range(len(texts)):
    texts[i] = f"{titles[i]} {texts[i]}"

```

\# Concatenate title and text
for i in range(len(texts)):
texts\[i\] = f"{titles\[i\]} {texts\[i\]}"

## 💚 Part 2: Weaviate [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#part-2-weaviate)

### Create and configure an embedded Weaviate collection [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#create-and-configure-an-embedded-weaviate-collection)

We'll be using the OpenAI API for both generating the text embeddings and for the generative model in our RAG pipeline. The code below dynamically fetches your API key based on whether you're running this notebook in Google Colab and running it as a regular Jupyter notebook. All you need to do is replace `openai_api_key_var` with the name of your environmental variable name or Colab secret name for the API key.

If you're running this notebook in Google Colab, make sure you [add](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75) your API key as a secret.

In \[7\]:

Copied!

```
# OpenAI API key variable name
openai_api_key_var = "OPENAI_API_KEY"  # Replace with the name of your secret/env var

# Fetch OpenAI API key
try:
    # If running in Colab, fetch API key from Secrets
    import google.colab
    from google.colab import userdata

    openai_api_key = userdata.get(openai_api_key_var)
    if not openai_api_key:
        raise ValueError(f"Secret '{openai_api_key_var}' not found in Colab secrets.")
except ImportError:
    # If not running in Colab, fetch API key from environment variable
    import os

    openai_api_key = os.getenv(openai_api_key_var)
    if not openai_api_key:
        raise OSError(
            f"Environment variable '{openai_api_key_var}' is not set. "
            "Please define it before running this script."
        )

```

\# OpenAI API key variable name
openai\_api\_key\_var = "OPENAI\_API\_KEY" # Replace with the name of your secret/env var

\# Fetch OpenAI API key
try:
# If running in Colab, fetch API key from Secrets
import google.colab
from google.colab import userdata

openai\_api\_key = userdata.get(openai\_api\_key\_var)
if not openai\_api\_key:
raise ValueError(f"Secret '{openai\_api\_key\_var}' not found in Colab secrets.")
except ImportError:
# If not running in Colab, fetch API key from environment variable
import os

openai\_api\_key = os.getenv(openai\_api\_key\_var)
if not openai\_api\_key:
raise OSError(
f"Environment variable '{openai\_api\_key\_var}' is not set. "
"Please define it before running this script."
)

[Embedded Weaviate](https://weaviate.io/developers/weaviate/installation/embedded) allows you to spin up a Weaviate instance directly from your application code, without having to use a Docker container. If you're interested in other deployment methods, like using Docker-Compose or Kubernetes, check out this [page](https://weaviate.io/developers/weaviate/installation) in the Weaviate docs.

In \[ \]:

Copied!

```
import weaviate

# Connect to Weaviate embedded
client = weaviate.connect_to_embedded(headers={"X-OpenAI-Api-Key": openai_api_key})

```

import weaviate

\# Connect to Weaviate embedded
client = weaviate.connect\_to\_embedded(headers={"X-OpenAI-Api-Key": openai\_api\_key})

In \[ \]:

Copied!

```
import weaviate.classes.config as wc

# Define the collection name
collection_name = "docling"

# Delete the collection if it already exists
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)

# Create the collection
collection = client.collections.create(
    name=collection_name,
    vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-large",  # Specify your embedding model here
    ),
    # Enable generative model from Cohere
    generative_config=wc.Configure.Generative.openai(
        model="gpt-4o"  # Specify your generative model for RAG here
    ),
    # Define properties of metadata
    properties=[\
        wc.Property(name="text", data_type=wc.DataType.TEXT),\
        wc.Property(name="title", data_type=wc.DataType.TEXT, skip_vectorization=True),\
    ],
)

```

import weaviate.classes.config as wc

\# Define the collection name
collection\_name = "docling"

\# Delete the collection if it already exists
if client.collections.exists(collection\_name):
client.collections.delete(collection\_name)

\# Create the collection
collection = client.collections.create(
name=collection\_name,
vectorizer\_config=wc.Configure.Vectorizer.text2vec\_openai(
model="text-embedding-3-large", # Specify your embedding model here
),
# Enable generative model from Cohere
generative\_config=wc.Configure.Generative.openai(
model="gpt-4o" # Specify your generative model for RAG here
),
# Define properties of metadata
properties=\[\
wc.Property(name="text", data\_type=wc.DataType.TEXT),\
wc.Property(name="title", data\_type=wc.DataType.TEXT, skip\_vectorization=True),\
\],
)

### Wrangle data into an acceptable format for Weaviate [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#wrangle-data-into-an-acceptable-format-for-weaviate)

Transform our data from lists to a list of dictionaries for insertion into our Weaviate collection.

In \[10\]:

Copied!

```
# Initialize the data object
data = []

# Create a dictionary for each row by iterating through the corresponding lists
for text, title in zip(texts, titles):
    data_point = {
        "text": text,
        "title": title,
    }
    data.append(data_point)

```

\# Initialize the data object
data = \[\]

\# Create a dictionary for each row by iterating through the corresponding lists
for text, title in zip(texts, titles):
data\_point = {
"text": text,
"title": title,
}
data.append(data\_point)

### Insert data into Weaviate and generate embeddings [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#insert-data-into-weaviate-and-generate-embeddings)

Embeddings will be generated upon insertion to our Weaviate collection.

In \[ \]:

Copied!

```
# Insert text chunks and metadata into vector DB collection
response = collection.data.insert_many(data)

if response.has_errors:
    print(response.errors)
else:
    print("Insert complete.")

```

\# Insert text chunks and metadata into vector DB collection
response = collection.data.insert\_many(data)

if response.has\_errors:
print(response.errors)
else:
print("Insert complete.")

### Query the data [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#query-the-data)

Here, we perform a simple similarity search to return the most similar embedded chunks to our search query.

In \[12\]:

Copied!

```
from weaviate.classes.query import MetadataQuery

response = collection.query.near_text(
    query="bert",
    limit=2,
    return_metadata=MetadataQuery(distance=True),
    return_properties=["text", "title"],
)

for o in response.objects:
    print(o.properties)
    print(o.metadata.distance)

```

from weaviate.classes.query import MetadataQuery

response = collection.query.near\_text(
query="bert",
limit=2,
return\_metadata=MetadataQuery(distance=True),
return\_properties=\["text", "title"\],
)

for o in response.objects:
print(o.properties)
print(o.metadata.distance)

```
{'text': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding A distinctive feature of BERT is its unified architecture across different tasks. There is mini-', 'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'}
0.6578550338745117
{'text': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding We introduce a new language representation model called BERT , which stands for B idirectional E ncoder R epresentations from T ransformers. Unlike recent language representation models (Peters et al., 2018a; Radford et al., 2018), BERT is designed to pretrain deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.', 'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'}
0.6696287989616394

```

### Perform RAG on parsed articles [¶](https://docling-project.github.io/docling/examples/rag_weaviate/\#perform-rag-on-parsed-articles)

Weaviate's `generate` module allows you to perform RAG over your embedded data without having to use a separate framework.

We specify a prompt that includes the field we want to search through in the database (in this case it's `text`), a query that includes our search term, and the number of retrieved results to use in the generation.

In \[13\]:

Copied!

```
from rich.console import Console
from rich.panel import Panel

# Create a prompt where context from the Weaviate collection will be injected
prompt = "Explain how {text} works, using only the retrieved context."
query = "bert"

response = collection.generate.near_text(
    query=query, limit=3, grouped_task=prompt, return_properties=["text", "title"]
)

# Prettify the output using Rich
console = Console()

console.print(
    Panel(f"{prompt}".replace("{text}", query), title="Prompt", border_style="bold red")
)
console.print(
    Panel(response.generated, title="Generated Content", border_style="bold green")
)

```

from rich.console import Console
from rich.panel import Panel

\# Create a prompt where context from the Weaviate collection will be injected
prompt = "Explain how {text} works, using only the retrieved context."
query = "bert"

response = collection.generate.near\_text(
query=query, limit=3, grouped\_task=prompt, return\_properties=\["text", "title"\]
)

\# Prettify the output using Rich
console = Console()

console.print(
Panel(f"{prompt}".replace("{text}", query), title="Prompt", border\_style="bold red")
)
console.print(
Panel(response.generated, title="Generated Content", border\_style="bold green")
)

```
╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮
│ Explain how bert works, using only the retrieved context.                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

```
╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮
│ BERT, which stands for Bidirectional Encoder Representations from Transformers, is a language representation    │
│ model designed to pretrain deep bidirectional representations from unlabeled text. It conditions on both left   │
│ and right context in all layers, unlike traditional left-to-right or right-to-left language models. This        │
│ pre-training involves two unsupervised tasks. The pre-trained BERT model can then be fine-tuned with just one   │
│ additional output layer to create state-of-the-art models for various tasks, such as question answering and     │
│ language inference, without needing substantial task-specific architecture modifications. A distinctive feature │
│ of BERT is its unified architecture across different tasks.                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

In \[14\]:

Copied!

```
# Create a prompt where context from the Weaviate collection will be injected
prompt = "Explain how {text} works, using only the retrieved context."
query = "a generative adversarial net"

response = collection.generate.near_text(
    query=query, limit=3, grouped_task=prompt, return_properties=["text", "title"]
)

# Prettify the output using Rich
console = Console()

console.print(
    Panel(f"{prompt}".replace("{text}", query), title="Prompt", border_style="bold red")
)
console.print(
    Panel(response.generated, title="Generated Content", border_style="bold green")
)

```

\# Create a prompt where context from the Weaviate collection will be injected
prompt = "Explain how {text} works, using only the retrieved context."
query = "a generative adversarial net"

response = collection.generate.near\_text(
query=query, limit=3, grouped\_task=prompt, return\_properties=\["text", "title"\]
)

\# Prettify the output using Rich
console = Console()

console.print(
Panel(f"{prompt}".replace("{text}", query), title="Prompt", border\_style="bold red")
)
console.print(
Panel(response.generated, title="Generated Content", border\_style="bold green")
)

```
╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮
│ Explain how a generative adversarial net works, using only the retrieved context.                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

```
╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮
│ Generative Adversarial Nets (GANs) operate within an adversarial framework where two models are trained         │
│ simultaneously: a generative model (G) and a discriminative model (D). The generative model aims to capture the │
│ data distribution and generate samples that mimic real data, while the discriminative model's task is to        │
│ distinguish between samples from the real data and those generated by G. This setup is akin to a game where the │
│ generative model acts like counterfeiters trying to produce indistinguishable fake currency, and the            │
│ discriminative model acts like the police trying to detect these counterfeits.                                  │
│                                                                                                                 │
│ The training process involves a minimax two-player game where G tries to maximize the probability of D making a │
│ mistake, while D tries to minimize it. When both models are defined by multilayer perceptrons, they can be      │
│ trained using backpropagation without the need for Markov chains or approximate inference networks. The         │
│ ultimate goal is for G to perfectly replicate the training data distribution, making D's output equal to 1/2    │
│ everywhere, indicating it cannot distinguish between real and generated data. This framework allows for         │
│ specific training algorithms and optimization techniques, such as backpropagation and dropout, to be            │
│ effectively utilized.                                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

We can see that our RAG pipeline performs relatively well for simple queries, especially given the small size of the dataset. Scaling this method for converting a larger sample of PDFs would require more compute (GPUs) and a more advanced deployment of Weaviate (like Docker, Kubernetes, or Weaviate Cloud). For more information on available Weaviate configurations, check out the [documentation](https://weaviate.io/developers/weaviate/starter-guides/which-weaviate).

Back to top