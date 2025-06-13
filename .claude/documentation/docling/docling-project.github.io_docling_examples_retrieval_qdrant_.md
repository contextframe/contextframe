---
url: "https://docling-project.github.io/docling/examples/retrieval_qdrant/"
title: "Retrieval with Qdrant - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/retrieval_qdrant/#retrieval-with-qdrant)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/hybrid_rag_qdrant.ipynb)

# Retrieval with Qdrant [¶](https://docling-project.github.io/docling/examples/retrieval_qdrant/\#retrieval-with-qdrant)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | FastEmbed | 💻 Local |
| Vector store | Qdrant | 💻 Local |

## Overview [¶](https://docling-project.github.io/docling/examples/retrieval_qdrant/\#overview)

This example demonstrates using Docling with [Qdrant](https://qdrant.tech/) to perform a hybrid search across your documents using dense and sparse vectors.

We'll chunk the documents using Docling before adding them to a Qdrant collection. By limiting the length of the chunks, we can preserve the meaning in each vector embedding.

## Setup [¶](https://docling-project.github.io/docling/examples/retrieval_qdrant/\#setup)

- 👉 Qdrant client uses [FastEmbed](https://github.com/qdrant/fastembed) to generate vector embeddings. You can install the `fastembed-gpu` package if you've got the hardware to support it.

In \[1\]:

Copied!

```
%pip install --no-warn-conflicts -q qdrant-client docling fastembed

```

%pip install --no-warn-conflicts -q qdrant-client docling fastembed

```
Note: you may need to restart the kernel to use updated packages.

```

Let's import all the classes we'll be working with.

In \[2\]:

Copied!

```
from qdrant_client import QdrantClient

from docling.chunking import HybridChunker
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter

```

from qdrant\_client import QdrantClient

from docling.chunking import HybridChunker
from docling.datamodel.base\_models import InputFormat
from docling.document\_converter import DocumentConverter

- For Docling, we'll set the allowed formats to HTML since we'll only be working with webpages in this tutorial.
- If we set a sparse model, Qdrant client will fuse the dense and sparse results using RRF. [Reference](https://qdrant.tech/documentation/tutorials/hybrid-search-fastembed/).

In \[3\]:

Copied!

```
COLLECTION_NAME = "docling"

doc_converter = DocumentConverter(allowed_formats=[InputFormat.HTML])
client = QdrantClient(location=":memory:")
# The :memory: mode is a Python imitation of Qdrant's APIs for prototyping and CI.
# For production deployments, use the Docker image: docker run -p 6333:6333 qdrant/qdrant
# client = QdrantClient(location="http://localhost:6333")

client.set_model("sentence-transformers/all-MiniLM-L6-v2")
client.set_sparse_model("Qdrant/bm25")

```

COLLECTION\_NAME = "docling"

doc\_converter = DocumentConverter(allowed\_formats=\[InputFormat.HTML\])
client = QdrantClient(location=":memory:")
\# The :memory: mode is a Python imitation of Qdrant's APIs for prototyping and CI.
\# For production deployments, use the Docker image: docker run -p 6333:6333 qdrant/qdrant
\# client = QdrantClient(location="http://localhost:6333")

client.set\_model("sentence-transformers/all-MiniLM-L6-v2")
client.set\_sparse\_model("Qdrant/bm25")

```
/Users/pva/work/github.com/docling-project/docling/.venv/lib/python3.12/site-packages/huggingface_hub/utils/tqdm.py:155: UserWarning: Cannot enable progress bars: environment variable `HF_HUB_DISABLE_PROGRESS_BARS=1` is set and has priority.
  warnings.warn(

```

We can now download and chunk the document using Docling. For demonstration, we'll use an article about chunking strategies :)

In \[4\]:

Copied!

```
result = doc_converter.convert(
    "https://www.sagacify.com/news/a-guide-to-chunking-strategies-for-retrieval-augmented-generation-rag"
)
documents, metadatas = [], []
for chunk in HybridChunker().chunk(result.document):
    documents.append(chunk.text)
    metadatas.append(chunk.meta.export_json_dict())

```

result = doc\_converter.convert(
"https://www.sagacify.com/news/a-guide-to-chunking-strategies-for-retrieval-augmented-generation-rag"
)
documents, metadatas = \[\], \[\]
for chunk in HybridChunker().chunk(result.document):
documents.append(chunk.text)
metadatas.append(chunk.meta.export\_json\_dict())

Let's now upload the documents to Qdrant.

- The `add()` method batches the documents and uses FastEmbed to generate vector embeddings on our machine.

In \[5\]:

Copied!

```
_ = client.add(
    collection_name=COLLECTION_NAME,
    documents=documents,
    metadata=metadatas,
    batch_size=64,
)

```

\_ = client.add(
collection\_name=COLLECTION\_NAME,
documents=documents,
metadata=metadatas,
batch\_size=64,
)

## Retrieval [¶](https://docling-project.github.io/docling/examples/retrieval_qdrant/\#retrieval)

In \[6\]:

Copied!

```
points = client.query(
    collection_name=COLLECTION_NAME,
    query_text="Can I split documents?",
    limit=10,
)

```

points = client.query(
collection\_name=COLLECTION\_NAME,
query\_text="Can I split documents?",
limit=10,
)

In \[7\]:

Copied!

```
for i, point in enumerate(points):
    print(f"=== {i} ===")
    print(point.document)
    print()

```

for i, point in enumerate(points):
print(f"=== {i} ===")
print(point.document)
print()

```
=== 0 ===
Have you ever wondered how we, humans, would chunk? Here's a breakdown of a possible way a human would process a new document:
1. We start at the top of the document, treating the first part as a chunk.
   2. We continue down the document, deciding if a new sentence or piece of information belongs with the first chunk or should start a new one.
    3. We keep this up until we reach the end of the document.
The ultimate dream? Having an agent do this for you. But slow down! This approach is still being tested and isn't quite ready for the big leagues due to the time it takes to process multiple LLM calls and the cost of those calls. There's no implementation available in public libraries just yet. However, Greg Kamradt has his version available here.

=== 1 ===
Document Specific Chunking is a strategy that respects the document's structure. Rather than using a set number of characters or a recursive process, it creates chunks that align with the logical sections of the document, like paragraphs or subsections. This approach maintains the original author's organization of content and helps keep the text coherent. It makes the retrieved information more relevant and useful, particularly for structured documents with clearly defined sections.
Document Specific Chunking can handle a variety of document formats, such as:
Markdown
HTML
Python
etc
Here we’ll take Markdown as our example and use a modified version of our first sample text:
‍
The result is the following:
You can see here that with a chunk size of 105, the Markdown structure of the document is taken into account, and the chunks thus preserve the semantics of the text!

=== 2 ===
And there you have it! These chunking strategies are like a personal toolbox when it comes to implementing Retrieval Augmented Generation. They're a ton of ways to slice and dice text, each with its unique features and quirks. This variety gives you the freedom to pick the strategy that suits your project best, allowing you to tailor your approach to perfectly fit the unique needs of your work.
To put these strategies into action, there's a whole array of tools and libraries at your disposal. For example, llama_index is a fantastic tool that lets you create document indices and retrieve chunked documents. Let's not forget LangChain, another remarkable tool that makes implementing chunking strategies a breeze, particularly when dealing with multi-language data. Diving into these tools and understanding how they can work in harmony with the chunking strategies we've discussed is a crucial part of mastering Retrieval Augmented Generation.
By the way, if you're eager to experiment with your own examples using the chunking visualisation tool featured in this blog, feel free to give it a try! You can access it right here. Enjoy, and happy chunking! 😉

=== 3 ===
Retrieval Augmented Generation (RAG) has been a hot topic in understanding, interpreting, and generating text with AI for the last few months. It's like a wonderful union of retrieval-based and generative models, creating a playground for researchers, data scientists, and natural language processing enthusiasts, like you and me.
To truly control the results produced by our RAG, we need to understand chunking strategies and their role in the process of retrieving and generating text. Indeed, each chunking strategy enhances RAG's effectiveness in its unique way.
The goal of chunking is, as its name says, to chunk the information into multiple smaller pieces in order to store it in a more efficient and meaningful way. This allows the retrieval to capture pieces of information that are more related to the question at hand, and the generation to be more precise, but also less costly, as only a part of a document will be included in the LLM prompt, instead of the whole document.
Let's explore some chunking strategies together.
The methods mentioned in the article you're about to read usually make use of two key parameters. First, we have [chunk_size]— which controls the size of your text chunks. Then there's [chunk_overlap], which takes care of how much text overlaps between one chunk and the next.

=== 4 ===
Semantic Chunking considers the relationships within the text. It divides the text into meaningful, semantically complete chunks. This approach ensures the information's integrity during retrieval, leading to a more accurate and contextually appropriate outcome.
Semantic chunking involves taking the embeddings of every sentence in the document, comparing the similarity of all sentences with each other, and then grouping sentences with the most similar embeddings together.
By focusing on the text's meaning and context, Semantic Chunking significantly enhances the quality of retrieval. It's a top-notch choice when maintaining the semantic integrity of the text is vital.
However, this method does require more effort and is notably slower than the previous ones.
On our example text, since it is quite short and does not expose varied subjects, this method would only generate a single chunk.

=== 5 ===
Language models used in the rest of your possible RAG pipeline have a token limit, which should not be exceeded. When dividing your text into chunks, it's advisable to count the number of tokens. Plenty of tokenizers are available. To ensure accuracy, use the same tokenizer for counting tokens as the one used in the language model.
Consequently, there are also splitters available for this purpose.
For instance, by using the [SpacyTextSplitter] from LangChain, the following chunks are created:
‍

=== 6 ===
First things first, we have Character Chunking. This strategy divides the text into chunks based on a fixed number of characters. Its simplicity makes it a great starting point, but it can sometimes disrupt the text's flow, breaking sentences or words in unexpected places. Despite its limitations, it's a great stepping stone towards more advanced methods.
Now let’s see that in action with an example. Imagine a text that reads:
If we decide to set our chunk size to 100 and no chunk overlap, we'd end up with the following chunks. As you can see, Character Chunking can lead to some intriguing, albeit sometimes nonsensical, results, cutting some of the sentences in their middle.
By choosing a smaller chunk size,  we would obtain more chunks, and by setting a bigger chunk overlap, we could obtain something like this:
‍
Also, by default this method creates chunks character by character based on the empty character [’ ’]. But you can specify a different one in order to chunk on something else, even a complete word! For instance, by specifying [' '] as the separator, you can avoid cutting words in their middle.

=== 7 ===
Next, let's take a look at Recursive Character Chunking. Based on the basic concept of Character Chunking, this advanced version takes it up a notch by dividing the text into chunks until a certain condition is met, such as reaching a minimum chunk size. This method ensures that the chunking process aligns with the text's structure, preserving more meaning. Its adaptability makes Recursive Character Chunking great for texts with varied structures.
Again, let’s use the same example in order to illustrate this method. With a chunk size of 100, and the default settings for the other parameters, we obtain the following chunks:

```

In \[ \]:

Copied!

```

```

Back to top