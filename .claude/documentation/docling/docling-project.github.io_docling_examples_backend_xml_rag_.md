---
url: "https://docling-project.github.io/docling/examples/backend_xml_rag/"
title: "Conversion of custom XML - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/backend_xml_rag/#conversion-of-custom-xml)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/docling-project/docling/blob/main/docs/examples/backend_xml_rag.ipynb)

# Conversion of custom XML [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#conversion-of-custom-xml)

| Step | Tech | Execution |
| --- | --- | --- |
| Embedding | Hugging Face / Sentence Transformers | 💻 Local |
| Vector store | Milvus | 💻 Local |
| Gen AI | Hugging Face Inference API | 🌐 Remote |

## Overview [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#overview)

This is an example of using [Docling](https://docling-project.github.io/docling/) for converting structured data (XML) into a unified document
representation format, `DoclingDocument`, and leverage its riched structured content for RAG applications.

Data used in this example consist of patents from the [United States Patent and Trademark Office (USPTO)](https://www.uspto.gov/) and medical
articles from [PubMed Central® (PMC)](https://pmc.ncbi.nlm.nih.gov/).

In this notebook, we accomplish the following:

- [Simple conversion](https://docling-project.github.io/docling/examples/backend_xml_rag/#simple-conversion) of supported XML files in a nutshell
- An [end-to-end application](https://docling-project.github.io/docling/examples/backend_xml_rag/#end-to-end-application) using public collections of XML files supported by Docling
  - [Setup](https://docling-project.github.io/docling/examples/backend_xml_rag/#setup) the API access for generative AI
  - [Fetch the data](https://docling-project.github.io/docling/examples/backend_xml_rag/#fetch-the-data) from USPTO and PubMed Central® sites, using Docling custom backends
  - [Parse, chunk, and index](https://docling-project.github.io/docling/examples/backend_xml_rag/#parse-chunk-and-index) the documents in a vector database
  - [Perform RAG](https://docling-project.github.io/docling/examples/backend_xml_rag/#question-answering-with-rag) using [LlamaIndex Docling extension](https://docling-project.github.io/docling/integrations/llamaindex/)

For more details on document chunking with Docling, refer to the [Chunking](https://docling-project.github.io/docling/concepts/chunking/) documentation. For RAG with Docling and LlamaIndex, also check the example [RAG with LlamaIndex](https://docling-project.github.io/docling/examples/rag_llamaindex/).

## Simple conversion [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#simple-conversion)

The XML file format defines and stores data in a format that is both human-readable and machine-readable.
Because of this flexibility, Docling requires custom backend processors to interpret XML definitions and convert them into `DoclingDocument` objects.

Some public data collections in XML format are already supported by Docling (USTPO patents and PMC articles). In these cases, the document conversion is straightforward and the same as with any other supported format, such as PDF or HTML. The execution example in [Simple Conversion](https://docling-project.github.io/docling/examples/minimal/) is the recommended usage of Docling for a single file:

In \[1\]:

Copied!

```
from docling.document_converter import DocumentConverter

# a sample PMC article:
source = "../../tests/data/jats/elife-56337.nxml"
converter = DocumentConverter()
result = converter.convert(source)
print(result.status)

```

from docling.document\_converter import DocumentConverter

\# a sample PMC article:
source = "../../tests/data/jats/elife-56337.nxml"
converter = DocumentConverter()
result = converter.convert(source)
print(result.status)

```
ConversionStatus.SUCCESS

```

Once the document is converted, it can be exported to any format supported by Docling. For instance, to markdown (showing here the first lines only):

In \[2\]:

Copied!

```
md_doc = result.document.export_to_markdown()

delim = "\n"
print(delim.join(md_doc.split(delim)[:8]))

```

md\_doc = result.document.export\_to\_markdown()

delim = "\\n"
print(delim.join(md\_doc.split(delim)\[:8\]))

```
# KRAB-zinc finger protein gene expansion in response to active retrotransposons in the murine lineage

Gernot Wolf, Alberto de Iaco, Ming-An Sun, Melania Bruno, Matthew Tinkham, Don Hoang, Apratim Mitra, Sherry Ralls, Didier Trono, Todd S Macfarlan

The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health, Bethesda, United States; School of Life Sciences, École Polytechnique Fédérale de Lausanne (EPFL), Lausanne, Switzerland

## Abstract

```

If the XML file is not supported, a `ConversionError` message will be raised.

In \[3\]:

Copied!

```
from io import BytesIO

from docling.datamodel.base_models import DocumentStream
from docling.exceptions import ConversionError

xml_content = (
    b'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE docling_test SYSTEM '
    b'"test.dtd"><docling>Random content</docling>'
)
stream = DocumentStream(name="docling_test.xml", stream=BytesIO(xml_content))
try:
    result = converter.convert(stream)
except ConversionError as ce:
    print(ce)

```

from io import BytesIO

from docling.datamodel.base\_models import DocumentStream
from docling.exceptions import ConversionError

xml\_content = (
b'Random content'
)
stream = DocumentStream(name="docling\_test.xml", stream=BytesIO(xml\_content))
try:
result = converter.convert(stream)
except ConversionError as ce:
print(ce)

```
Input document docling_test.xml does not match any allowed format.

```

```
File format not allowed: docling_test.xml

```

You can always refer to the [Usage](https://docling-project.github.io/docling/usage/#supported-formats) documentation page for a list of supported formats.

## End-to-end application [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#end-to-end-application)

This section describes a step-by-step application for processing XML files from supported public collections and use them for question-answering.

### Setup [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#setup)

Requirements can be installed as shown below. The `--no-warn-conflicts` argument is meant for Colab's pre-populated Python environment, feel free to remove for stricter usage.

In \[4\]:

Copied!

```
%pip install -q --progress-bar off --no-warn-conflicts llama-index-core llama-index-readers-docling llama-index-node-parser-docling llama-index-embeddings-huggingface llama-index-llms-huggingface-api llama-index-vector-stores-milvus llama-index-readers-file python-dotenv

```

%pip install -q --progress-bar off --no-warn-conflicts llama-index-core llama-index-readers-docling llama-index-node-parser-docling llama-index-embeddings-huggingface llama-index-llms-huggingface-api llama-index-vector-stores-milvus llama-index-readers-file python-dotenv

```
Note: you may need to restart the kernel to use updated packages.

```

This notebook uses HuggingFace's Inference API. For an increased LLM quota, a token can be provided via the environment variable `HF_TOKEN`.

If you're running this notebook in Google Colab, make sure you [add](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75) your API key as a secret.

In \[5\]:

Copied!

```
import os
from warnings import filterwarnings

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

filterwarnings(action="ignore", category=UserWarning, module="pydantic")

```

import os
from warnings import filterwarnings

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

filterwarnings(action="ignore", category=UserWarning, module="pydantic")

We can now define the main parameters:

In \[6\]:

Copied!

```
from pathlib import Path
from tempfile import mkdtemp

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

EMBED_MODEL_ID = "BAAI/bge-small-en-v1.5"
EMBED_MODEL = HuggingFaceEmbedding(model_name=EMBED_MODEL_ID)
TEMP_DIR = Path(mkdtemp())
MILVUS_URI = str(TEMP_DIR / "docling.db")
GEN_MODEL = HuggingFaceInferenceAPI(
    token=_get_env_from_colab_or_os("HF_TOKEN"),
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
)
embed_dim = len(EMBED_MODEL.get_text_embedding("hi"))
# https://github.com/huggingface/transformers/issues/5486:
os.environ["TOKENIZERS_PARALLELISM"] = "false"

```

from pathlib import Path
from tempfile import mkdtemp

from llama\_index.embeddings.huggingface import HuggingFaceEmbedding
from llama\_index.llms.huggingface\_api import HuggingFaceInferenceAPI

EMBED\_MODEL\_ID = "BAAI/bge-small-en-v1.5"
EMBED\_MODEL = HuggingFaceEmbedding(model\_name=EMBED\_MODEL\_ID)
TEMP\_DIR = Path(mkdtemp())
MILVUS\_URI = str(TEMP\_DIR / "docling.db")
GEN\_MODEL = HuggingFaceInferenceAPI(
token=\_get\_env\_from\_colab\_or\_os("HF\_TOKEN"),
model\_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
)
embed\_dim = len(EMBED\_MODEL.get\_text\_embedding("hi"))
\# https://github.com/huggingface/transformers/issues/5486:
os.environ\["TOKENIZERS\_PARALLELISM"\] = "false"

### Fetch the data [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#fetch-the-data)

In this notebook we will use XML data from collections supported by Docling:

- Medical articles from the [PubMed Central® (PMC)](https://pmc.ncbi.nlm.nih.gov/). They are available in an [FTP server](https://ftp.ncbi.nlm.nih.gov/pub/pmc/) as `.tar.gz` files. Each file contains the full article data in XML format, among other supplementary files like images or spreadsheets.
- Patents from the [United States Patent and Trademark Office](https://www.uspto.gov/). They are available in the [Bulk Data Storage System (BDSS)](https://bulkdata.uspto.gov/) as zip files. Each zip file may contain several patents in XML format.

The raw files will be downloaded form the source and saved in a temporary directory.

#### PMC articles [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#pmc-articles)

The [OA file](https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv) is a manifest file of all the PMC articles, including the URL path to download the source files. In this notebook we will use as example the article [Pathogens spread by high-altitude windborne mosquitoes](https://pmc.ncbi.nlm.nih.gov/articles/PMC11703268/), which is available in the archive file [PMC11703268.tar.gz](https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz).

In \[7\]:

Copied!

```
import tarfile
from io import BytesIO

import requests

# PMC article PMC11703268
url: str = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz"

print(f"Downloading {url}...")
buf = BytesIO(requests.get(url).content)
print("Extracting and storing the XML file containing the article text...")
with tarfile.open(fileobj=buf, mode="r:gz") as tar_file:
    for tarinfo in tar_file:
        if tarinfo.isreg():
            file_path = Path(tarinfo.name)
            if file_path.suffix == ".nxml":
                with open(TEMP_DIR / file_path.name, "wb") as file_obj:
                    file_obj.write(tar_file.extractfile(tarinfo).read())
                print(f"Stored XML file {file_path.name}")

```

import tarfile
from io import BytesIO

import requests

\# PMC article PMC11703268
url: str = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa\_package/e3/6b/PMC11703268.tar.gz"

print(f"Downloading {url}...")
buf = BytesIO(requests.get(url).content)
print("Extracting and storing the XML file containing the article text...")
with tarfile.open(fileobj=buf, mode="r:gz") as tar\_file:
for tarinfo in tar\_file:
if tarinfo.isreg():
file\_path = Path(tarinfo.name)
if file\_path.suffix == ".nxml":
with open(TEMP\_DIR / file\_path.name, "wb") as file\_obj:
file\_obj.write(tar\_file.extractfile(tarinfo).read())
print(f"Stored XML file {file\_path.name}")

```
Downloading https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz...
Extracting and storing the XML file containing the article text...
Stored XML file nihpp-2024.12.26.630351v1.nxml

```

#### USPTO patents [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#uspto-patents)

Since each USPTO file is a concatenation of several patents, we need to split its content into valid XML pieces. The following code downloads a sample zip file, split its content in sections, and dumps each section as an XML file. For simplicity, this pipeline is shown here in a sequential manner, but it could be parallelized.

In \[8\]:

Copied!

```
import zipfile

# Patent grants from December 17-23, 2024
url: str = (
    "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2024/ipg241217.zip"
)
XML_SPLITTER: str = '<?xml version="1.0"'
doc_num: int = 0

print(f"Downloading {url}...")
buf = BytesIO(requests.get(url).content)
print("Parsing zip file, splitting into XML sections, and exporting to files...")
with zipfile.ZipFile(buf) as zf:
    res = zf.testzip()
    if res:
        print("Error validating zip file")
    else:
        with zf.open(zf.namelist()[0]) as xf:
            is_patent = False
            patent_buffer = BytesIO()
            for xf_line in xf:
                decoded_line = xf_line.decode(errors="ignore").rstrip()
                xml_index = decoded_line.find(XML_SPLITTER)
                if xml_index != -1:
                    if (
                        xml_index > 0
                    ):  # cases like </sequence-cwu><?xml version="1.0"...
                        patent_buffer.write(xf_line[:xml_index])
                        patent_buffer.write(b"\r\n")
                        xf_line = xf_line[xml_index:]
                    if patent_buffer.getbuffer().nbytes > 0 and is_patent:
                        doc_num += 1
                        patent_id = f"ipg241217-{doc_num}"
                        with open(TEMP_DIR / f"{patent_id}.xml", "wb") as file_obj:
                            file_obj.write(patent_buffer.getbuffer())
                    is_patent = False
                    patent_buffer = BytesIO()
                elif decoded_line.startswith("<!DOCTYPE"):
                    is_patent = True
                patent_buffer.write(xf_line)

```

import zipfile

\# Patent grants from December 17-23, 2024
url: str = (
"https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2024/ipg241217.zip"
)
XML\_SPLITTER: str = ' 0
): # cases like  0 and is\_patent:
doc\_num += 1
patent\_id = f"ipg241217-{doc\_num}"
with open(TEMP\_DIR / f"{patent\_id}.xml", "wb") as file\_obj:
file\_obj.write(patent\_buffer.getbuffer())
is\_patent = False
patent\_buffer = BytesIO()
elif decoded\_line.startswith("

```
Downloading https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2024/ipg241217.zip...
Parsing zip file, splitting into XML sections, and exporting to files...

```

In \[9\]:

Copied!

```
print(f"Fetched and exported {doc_num} documents.")

```

print(f"Fetched and exported {doc\_num} documents.")

```
Fetched and exported 4014 documents.

```

### Using the backend converter (optional) [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#using-the-backend-converter-optional)

- The custom backend converters `PubMedDocumentBackend` and `PatentUsptoDocumentBackend` aim at handling the parsing of PMC articles and USPTO patents, respectively.
- As any other backends, you can leverage the function `is_valid()` to check if the input document is supported by the this backend.
- Note that some XML sections in the original USPTO zip file may not represent patents, like sequence listings, and therefore they will show as invalid by the backend.

In \[11\]:

Copied!

```
from tqdm.notebook import tqdm

from docling.backend.xml.jats_backend import JatsDocumentBackend
from docling.backend.xml.uspto_backend import PatentUsptoDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

# check PMC
in_doc = InputDocument(
    path_or_stream=TEMP_DIR / "nihpp-2024.12.26.630351v1.nxml",
    format=InputFormat.XML_JATS,
    backend=JatsDocumentBackend,
)
backend = JatsDocumentBackend(
    in_doc=in_doc, path_or_stream=TEMP_DIR / "nihpp-2024.12.26.630351v1.nxml"
)
print(f"Document {in_doc.file.name} is a valid PMC article? {backend.is_valid()}")

# check USPTO
in_doc = InputDocument(
    path_or_stream=TEMP_DIR / "ipg241217-1.xml",
    format=InputFormat.XML_USPTO,
    backend=PatentUsptoDocumentBackend,
)
backend = PatentUsptoDocumentBackend(
    in_doc=in_doc, path_or_stream=TEMP_DIR / "ipg241217-1.xml"
)
print(f"Document {in_doc.file.name} is a valid patent? {backend.is_valid()}")

patent_valid = 0
pbar = tqdm(TEMP_DIR.glob("*.xml"), total=doc_num)
for in_path in pbar:
    in_doc = InputDocument(
        path_or_stream=in_path,
        format=InputFormat.XML_USPTO,
        backend=PatentUsptoDocumentBackend,
    )
    backend = PatentUsptoDocumentBackend(in_doc=in_doc, path_or_stream=in_path)
    patent_valid += int(backend.is_valid())

print(f"Found {patent_valid} patents out of {doc_num} XML files.")

```

from tqdm.notebook import tqdm

from docling.backend.xml.jats\_backend import JatsDocumentBackend
from docling.backend.xml.uspto\_backend import PatentUsptoDocumentBackend
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.document import InputDocument

\# check PMC
in\_doc = InputDocument(
path\_or\_stream=TEMP\_DIR / "nihpp-2024.12.26.630351v1.nxml",
format=InputFormat.XML\_JATS,
backend=JatsDocumentBackend,
)
backend = JatsDocumentBackend(
in\_doc=in\_doc, path\_or\_stream=TEMP\_DIR / "nihpp-2024.12.26.630351v1.nxml"
)
print(f"Document {in\_doc.file.name} is a valid PMC article? {backend.is\_valid()}")

\# check USPTO
in\_doc = InputDocument(
path\_or\_stream=TEMP\_DIR / "ipg241217-1.xml",
format=InputFormat.XML\_USPTO,
backend=PatentUsptoDocumentBackend,
)
backend = PatentUsptoDocumentBackend(
in\_doc=in\_doc, path\_or\_stream=TEMP\_DIR / "ipg241217-1.xml"
)
print(f"Document {in\_doc.file.name} is a valid patent? {backend.is\_valid()}")

patent\_valid = 0
pbar = tqdm(TEMP\_DIR.glob("\*.xml"), total=doc\_num)
for in\_path in pbar:
in\_doc = InputDocument(
path\_or\_stream=in\_path,
format=InputFormat.XML\_USPTO,
backend=PatentUsptoDocumentBackend,
)
backend = PatentUsptoDocumentBackend(in\_doc=in\_doc, path\_or\_stream=in\_path)
patent\_valid += int(backend.is\_valid())

print(f"Found {patent\_valid} patents out of {doc\_num} XML files.")

```
Document nihpp-2024.12.26.630351v1.nxml is a valid PMC article? True
Document ipg241217-1.xml is a valid patent? True

```

```
  0%|          | 0/4014 [00:00<?, ?it/s]
```

```
Found 3928 patents out of 4014 XML files.

```

Calling the function `convert()` will convert the input document into a `DoclingDocument`

In \[12\]:

Copied!

```
doc = backend.convert()

claims_sec = next(item for item in doc.texts if item.text == "CLAIMS")
print(f'Patent "{doc.texts[0].text}" has {len(claims_sec.children)} claims')

```

doc = backend.convert()

claims\_sec = next(item for item in doc.texts if item.text == "CLAIMS")
print(f'Patent "{doc.texts\[0\].text}" has {len(claims\_sec.children)} claims')

```
Patent "Semiconductor package" has 19 claims

```

✏️ **Tip**: in general, there is no need to use the backend converters to parse USPTO or JATS (PubMed) XML files. The generic `DocumentConverter` object tries to guess the input document format and applies the corresponding backend parser. The conversion shown in [Simple Conversion](https://docling-project.github.io/docling/examples/backend_xml_rag/#simple-conversion) is the recommended usage for the supported XML files.

### Parse, chunk, and index [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#parse-chunk-and-index)

The `DoclingDocument` format of the converted patents has a rich hierarchical structure, inherited from the original XML document and preserved by the Docling custom backend.
In this notebook, we will leverage:

- The `SimpleDirectoryReader` pattern to iterate over the exported XML files created in section [Fetch the data](https://docling-project.github.io/docling/examples/backend_xml_rag/#fetch-the-data).
- The LlamaIndex extensions, `DoclingReader` and `DoclingNodeParser`, to ingest the patent chunks into a Milvus vector store.
- The `HierarchicalChunker` implementation, which applies a document-based hierarchical chunking, to leverage the patent structures like sections and paragraphs within sections.

Refer to other possible implementations and usage patterns in the [Chunking](https://docling-project.github.io/docling/concepts/chunking/) documentation and the [RAG with LlamaIndex](https://docling-project.github.io/docling/examples/rag_llamaindex/) notebook.

##### Set the Docling reader and the directory reader [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#set-the-docling-reader-and-the-directory-reader)

Note that `DoclingReader` uses Docling's `DocumentConverter` by default and therefore it will recognize the format of the XML files and leverage the `PatentUsptoDocumentBackend` automatically.

For demonstration purposes, we limit the scope of the analysis to the first 100 patents.

In \[13\]:

Copied!

```
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.docling import DoclingReader

reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
dir_reader = SimpleDirectoryReader(
    input_dir=TEMP_DIR,
    exclude=["docling.db", "*.nxml"],
    file_extractor={".xml": reader},
    filename_as_id=True,
    num_files_limit=100,
)

```

from llama\_index.core import SimpleDirectoryReader
from llama\_index.readers.docling import DoclingReader

reader = DoclingReader(export\_type=DoclingReader.ExportType.JSON)
dir\_reader = SimpleDirectoryReader(
input\_dir=TEMP\_DIR,
exclude=\["docling.db", "\*.nxml"\],
file\_extractor={".xml": reader},
filename\_as\_id=True,
num\_files\_limit=100,
)

##### Set the node parser [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#set-the-node-parser)

Note that the `HierarchicalChunker` is the default chunking implementation of the `DoclingNodeParser`.

In \[14\]:

Copied!

```
from llama_index.node_parser.docling import DoclingNodeParser

node_parser = DoclingNodeParser()

```

from llama\_index.node\_parser.docling import DoclingNodeParser

node\_parser = DoclingNodeParser()

##### Set a local Milvus database and run the ingestion [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#set-a-local-milvus-database-and-run-the-ingestion)

In \[ \]:

Copied!

```
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.milvus import MilvusVectorStore

vector_store = MilvusVectorStore(
    uri=MILVUS_URI,
    dim=embed_dim,
    overwrite=True,
)

index = VectorStoreIndex.from_documents(
    documents=dir_reader.load_data(show_progress=True),
    transformations=[node_parser],
    storage_context=StorageContext.from_defaults(vector_store=vector_store),
    embed_model=EMBED_MODEL,
    show_progress=True,
)

```

from llama\_index.core import StorageContext, VectorStoreIndex
from llama\_index.vector\_stores.milvus import MilvusVectorStore

vector\_store = MilvusVectorStore(
uri=MILVUS\_URI,
dim=embed\_dim,
overwrite=True,
)

index = VectorStoreIndex.from\_documents(
documents=dir\_reader.load\_data(show\_progress=True),
transformations=\[node\_parser\],
storage\_context=StorageContext.from\_defaults(vector\_store=vector\_store),
embed\_model=EMBED\_MODEL,
show\_progress=True,
)

Finally, add the PMC article to the vector store directly from the reader.

In \[14\]:

Copied!

```
index.from_documents(
    documents=reader.load_data(TEMP_DIR / "nihpp-2024.12.26.630351v1.nxml"),
    transformations=[node_parser],
    storage_context=StorageContext.from_defaults(vector_store=vector_store),
    embed_model=EMBED_MODEL,
)

```

index.from\_documents(
documents=reader.load\_data(TEMP\_DIR / "nihpp-2024.12.26.630351v1.nxml"),
transformations=\[node\_parser\],
storage\_context=StorageContext.from\_defaults(vector\_store=vector\_store),
embed\_model=EMBED\_MODEL,
)

Out\[14\]:

```
<llama_index.core.indices.vector_store.base.VectorStoreIndex at 0x373a7f7d0>
```

### Question-answering with RAG [¶](https://docling-project.github.io/docling/examples/backend_xml_rag/\#question-answering-with-rag)

The retriever can be used to identify highly relevant documents:

In \[15\]:

Copied!

```
retriever = index.as_retriever(similarity_top_k=3)
results = retriever.retrieve("What patents are related to fitness devices?")

for item in results:
    print(item)

```

retriever = index.as\_retriever(similarity\_top\_k=3)
results = retriever.retrieve("What patents are related to fitness devices?")

for item in results:
print(item)

```
Node ID: 5afd36c0-a739-4a88-a51c-6d0f75358db5
Text: The portable fitness monitoring device 102 may be a device such
as, for example, a mobile phone, a personal digital assistant, a music
file player (e.g. and MP3 player), an intelligent article for wearing
(e.g. a fitness monitoring garment, wrist band, or watch), a dongle
(e.g. a small hardware device that protects software) that includes a
fitn...
Score:  0.772

Node ID: f294b5fd-9089-43cb-8c4e-d1095a634ff1
Text: US Patent Application US 20120071306 entitled “Portable
Multipurpose Whole Body Exercise Device” discloses a portable
multipurpose whole body exercise device which can be used for general
fitness, Pilates-type, core strengthening, therapeutic, and
rehabilitative exercises as well as stretching and physical therapy
and which includes storable acc...
Score:  0.749

Node ID: 8251c7ef-1165-42e1-8c91-c99c8a711bf7
Text: Program products, methods, and systems for providing fitness
monitoring services of the present invention can include any software
application executed by one or more computing devices. A computing
device can be any type of computing device having one or more
processors. For example, a computing device can be a workstation,
mobile device (e.g., ...
Score:  0.744

```

With the query engine, we can run the question-answering with the RAG pattern on the set of indexed documents.

First, we can prompt the LLM directly:

In \[16\]:

Copied!

```
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from rich.console import Console
from rich.panel import Panel

console = Console()
query = "Do mosquitoes in high altitude expand viruses over large distances?"

usr_msg = ChatMessage(role=MessageRole.USER, content=query)
response = GEN_MODEL.chat(messages=[usr_msg])

console.print(Panel(query, title="Prompt", border_style="bold red"))
console.print(
    Panel(
        response.message.content.strip(),
        title="Generated Content",
        border_style="bold green",
    )
)

```

from llama\_index.core.base.llms.types import ChatMessage, MessageRole
from rich.console import Console
from rich.panel import Panel

console = Console()
query = "Do mosquitoes in high altitude expand viruses over large distances?"

usr\_msg = ChatMessage(role=MessageRole.USER, content=query)
response = GEN\_MODEL.chat(messages=\[usr\_msg\])

console.print(Panel(query, title="Prompt", border\_style="bold red"))
console.print(
Panel(
response.message.content.strip(),
title="Generated Content",
border\_style="bold green",
)
)

```
╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮
│ Do mosquitoes in high altitude expand viruses over large distances?                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

```
╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮
│ Mosquitoes can be found at high altitudes, but their ability to transmit viruses over long distances is not     │
│ primarily dependent on altitude. Mosquitoes are vectors for various diseases, such as malaria, dengue fever,    │
│ and Zika virus, and their transmission range is more closely related to their movement, the presence of a host, │
│ and environmental conditions that support their survival and reproduction.                                      │
│                                                                                                                 │
│ At high altitudes, the environment can be less suitable for mosquitoes due to factors such as colder            │
│ temperatures, lower humidity, and stronger winds, which can limit their population size and distribution.       │
│ However, some species of mosquitoes have adapted to high-altitude environments and can still transmit diseases  │
│ in these areas.                                                                                                 │
│                                                                                                                 │
│ It is possible for mosquitoes to be transported by wind or human activities to higher altitudes, but this is    │
│ not a significant factor in their ability to transmit viruses over long distances. Instead, long-distance       │
│ transmission of viruses is more often associated with human travel and transportation, which can rapidly spread │
│ infected mosquitoes or humans to new areas, leading to the spread of disease.                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Now, we can compare the response when the model is prompted with the indexed PMC article as supporting context:

In \[17\]:

Copied!

```
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

filters = MetadataFilters(
    filters=[\
        ExactMatchFilter(key="filename", value="nihpp-2024.12.26.630351v1.nxml"),\
    ]
)

query_engine = index.as_query_engine(llm=GEN_MODEL, filter=filters, similarity_top_k=3)
result = query_engine.query(query)

console.print(
    Panel(
        result.response.strip(),
        title="Generated Content with RAG",
        border_style="bold green",
    )
)

```

from llama\_index.core.vector\_stores import ExactMatchFilter, MetadataFilters

filters = MetadataFilters(
filters=\[\
ExactMatchFilter(key="filename", value="nihpp-2024.12.26.630351v1.nxml"),\
\]
)

query\_engine = index.as\_query\_engine(llm=GEN\_MODEL, filter=filters, similarity\_top\_k=3)
result = query\_engine.query(query)

console.print(
Panel(
result.response.strip(),
title="Generated Content with RAG",
border\_style="bold green",
)
)

```
╭────────────────────────────────────────── Generated Content with RAG ───────────────────────────────────────────╮
│ Yes, mosquitoes in high altitude can expand viruses over large distances. A study intercepted 1,017 female      │
│ mosquitoes at altitudes of 120-290 m above ground over Mali and Ghana and screened them for infection with      │
│ arboviruses, plasmodia, and filariae. The study found that 3.5% of the mosquitoes were infected with            │
│ flaviviruses, and 1.1% were infectious. Additionally, the study identified 19 mosquito-borne pathogens,         │
│ including three arboviruses that affect humans (dengue, West Nile, and M’Poko viruses). The study provides      │
│ compelling evidence that mosquito-borne pathogens are often spread by windborne mosquitoes at altitude.         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Back to top