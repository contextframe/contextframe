---
url: "https://docling-project.github.io/docling/examples/hybrid_chunking/"
title: "Hybrid chunking - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/hybrid_chunking/#hybrid-chunking)

# Hybrid chunking [¶](https://docling-project.github.io/docling/examples/hybrid_chunking/\#hybrid-chunking)

## Overview [¶](https://docling-project.github.io/docling/examples/hybrid_chunking/\#overview)

Hybrid chunking applies tokenization-aware refinements on top of document-based hierarchical chunking.

For more details, see [here](https://docling-project.github.io/docling/concepts/chunking#hybrid-chunker).

## Setup [¶](https://docling-project.github.io/docling/examples/hybrid_chunking/\#setup)

In \[1\]:

Copied!

```
%pip install -qU pip docling transformers

```

%pip install -qU pip docling transformers

```
Note: you may need to restart the kernel to use updated packages.

```

In \[2\]:

Copied!

```
DOC_SOURCE = "../../tests/data/md/wiki.md"

```

DOC\_SOURCE = "../../tests/data/md/wiki.md"

## Basic usage [¶](https://docling-project.github.io/docling/examples/hybrid_chunking/\#basic-usage)

We first convert the document:

In \[3\]:

Copied!

```
from docling.document_converter import DocumentConverter

doc = DocumentConverter().convert(source=DOC_SOURCE).document

```

from docling.document\_converter import DocumentConverter

doc = DocumentConverter().convert(source=DOC\_SOURCE).document

For a basic chunking scenario, we can just instantiate a `HybridChunker`, which will use
the default parameters.

In \[4\]:

Copied!

```
from docling.chunking import HybridChunker

chunker = HybridChunker()
chunk_iter = chunker.chunk(dl_doc=doc)

```

from docling.chunking import HybridChunker

chunker = HybridChunker()
chunk\_iter = chunker.chunk(dl\_doc=doc)

```
Token indices sequence length is longer than the specified maximum sequence length for this model (531 > 512). Running this sequence through the model will result in indexing errors

```

> 👉 **NOTE**: As you see above, using the `HybridChunker` can sometimes lead to a warning from the transformers library, however this is a "false alarm" — for details check [here](https://docling-project.github.io/docling/faq/#hybridchunker-triggers-warning-token-indices-sequence-length-is-longer-than-the-specified-maximum-sequence-length-for-this-model).

Note that the text you would typically want to embed is the context-enriched one as
returned by the `contextualize()` method:

In \[5\]:

Copied!

```
for i, chunk in enumerate(chunk_iter):
    print(f"=== {i} ===")
    print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}")

    enriched_text = chunker.contextualize(chunk=chunk)
    print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}")

    print()

```

for i, chunk in enumerate(chunk\_iter):
print(f"=== {i} ===")
print(f"chunk.text:\\n{f'{chunk.text\[:300\]}…'!r}")

enriched\_text = chunker.contextualize(chunk=chunk)
print(f"chunker.contextualize(chunk):\\n{f'{enriched\_text\[:300\]}…'!r}")

print()

```
=== 0 ===
chunk.text:
'International Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Aver…'
chunker.contextualize(chunk):
'IBM\nInternational Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial …'

=== 1 ===
chunk.text:
'IBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine (1889);[19] and Willa…'
chunker.contextualize(chunk):
'IBM\n1910s–1950s\nIBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine (1889…'

=== 2 ===
chunk.text:
'Collectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson,…'
chunker.contextualize(chunk):
'IBM\n1910s–1950s\nCollectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John …'

=== 3 ===
chunk.text:
'In 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.…'
chunker.contextualize(chunk):
'IBM\n1960s–1980s\nIn 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.…'

```

## Configuring tokenization [¶](https://docling-project.github.io/docling/examples/hybrid_chunking/\#configuring-tokenization)

For more control on the chunking, we can parametrize tokenization as shown below.

In a RAG / retrieval context, it is important to make sure that the chunker and
embedding model are using the same tokenizer.

👉 HuggingFace transformers tokenizers can be used as shown in the following example:

In \[6\]:

Copied!

```
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from docling.chunking import HybridChunker

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 64  # set to a small number for illustrative purposes

tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
    max_tokens=MAX_TOKENS,  # optional, by default derived from `tokenizer` for HF case
)

```

from docling\_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from docling.chunking import HybridChunker

EMBED\_MODEL\_ID = "sentence-transformers/all-MiniLM-L6-v2"
MAX\_TOKENS = 64 # set to a small number for illustrative purposes

tokenizer = HuggingFaceTokenizer(
tokenizer=AutoTokenizer.from\_pretrained(EMBED\_MODEL\_ID),
max\_tokens=MAX\_TOKENS, # optional, by default derived from \`tokenizer\` for HF case
)

👉 Alternatively, [OpenAI tokenizers](https://github.com/openai/tiktoken) can be used as shown in the example below (uncomment to use — requires installing `docling-core[chunking-openai]`):

In \[7\]:

Copied!

```
# import tiktoken

# from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer

# tokenizer = OpenAITokenizer(
#     tokenizer=tiktoken.encoding_for_model("gpt-4o"),
#     max_tokens=128 * 1024,  # context window length required for OpenAI tokenizers
# )

```

\# import tiktoken

\# from docling\_core.transforms.chunker.tokenizer.openai import OpenAITokenizer

\# tokenizer = OpenAITokenizer(
\# tokenizer=tiktoken.encoding\_for\_model("gpt-4o"),
\# max\_tokens=128 \* 1024, # context window length required for OpenAI tokenizers
\# )

We can now instantiate our chunker:

In \[8\]:

Copied!

```
chunker = HybridChunker(
    tokenizer=tokenizer,
    merge_peers=True,  # optional, defaults to True
)
chunk_iter = chunker.chunk(dl_doc=doc)
chunks = list(chunk_iter)

```

chunker = HybridChunker(
tokenizer=tokenizer,
merge\_peers=True, # optional, defaults to True
)
chunk\_iter = chunker.chunk(dl\_doc=doc)
chunks = list(chunk\_iter)

Points to notice looking at the output chunks below:

- Where possible, we fit the limit of 64 tokens for the metadata-enriched serialization form (see chunk 2)
- Where needed, we stop before the limit, e.g. see cases of 63 as it would otherwise run into a comma (see chunk 6)
- Where possible, we merge undersized peer chunks (see chunk 0)
- "Tail" chunks trailing right after merges may still be undersized (see chunk 8)

In \[9\]:

Copied!

```
for i, chunk in enumerate(chunks):
    print(f"=== {i} ===")
    txt_tokens = tokenizer.count_tokens(chunk.text)
    print(f"chunk.text ({txt_tokens} tokens):\n{chunk.text!r}")

    ser_txt = chunker.contextualize(chunk=chunk)
    ser_tokens = tokenizer.count_tokens(ser_txt)
    print(f"chunker.contextualize(chunk) ({ser_tokens} tokens):\n{ser_txt!r}")

    print()

```

for i, chunk in enumerate(chunks):
print(f"=== {i} ===")
txt\_tokens = tokenizer.count\_tokens(chunk.text)
print(f"chunk.text ({txt\_tokens} tokens):\\n{chunk.text!r}")

ser\_txt = chunker.contextualize(chunk=chunk)
ser\_tokens = tokenizer.count\_tokens(ser\_txt)
print(f"chunker.contextualize(chunk) ({ser\_tokens} tokens):\\n{ser\_txt!r}")

print()

```
=== 0 ===
chunk.text (55 tokens):
'International Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Average.'
chunker.contextualize(chunk) (56 tokens):
'IBM\nInternational Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Average.'

=== 1 ===
chunk.text (45 tokens):
'IBM is the largest industrial research organization in the world, with 19 research facilities across a dozen countries, having held the record for most annual U.S. patents generated by a business for 29 consecutive years from 1993 to 2021.'
chunker.contextualize(chunk) (46 tokens):
'IBM\nIBM is the largest industrial research organization in the world, with 19 research facilities across a dozen countries, having held the record for most annual U.S. patents generated by a business for 29 consecutive years from 1993 to 2021.'

=== 2 ===
chunk.text (63 tokens):
'IBM was founded in 1911 as the Computing-Tabulating-Recording Company (CTR), a holding company of manufacturers of record-keeping and measuring systems. It was renamed "International Business Machines" in 1924 and soon became the leading manufacturer of punch-card tabulating systems. During the 1960s and 1970s, the'
chunker.contextualize(chunk) (64 tokens):
'IBM\nIBM was founded in 1911 as the Computing-Tabulating-Recording Company (CTR), a holding company of manufacturers of record-keeping and measuring systems. It was renamed "International Business Machines" in 1924 and soon became the leading manufacturer of punch-card tabulating systems. During the 1960s and 1970s, the'

=== 3 ===
chunk.text (44 tokens):
"IBM mainframe, exemplified by the System/360, was the world's dominant computing platform, with the company producing 80 percent of computers in the U.S. and 70 percent of computers worldwide.[11]"
chunker.contextualize(chunk) (45 tokens):
"IBM\nIBM mainframe, exemplified by the System/360, was the world's dominant computing platform, with the company producing 80 percent of computers in the U.S. and 70 percent of computers worldwide.[11]"

=== 4 ===
chunk.text (63 tokens):
'IBM debuted in the microcomputer market in 1981 with the IBM Personal Computer, — its DOS software provided by Microsoft, — which became the basis for the majority of personal computers to the present day.[12] The company later also found success in the portable space with the ThinkPad. Since the 1990s,'
chunker.contextualize(chunk) (64 tokens):
'IBM\nIBM debuted in the microcomputer market in 1981 with the IBM Personal Computer, — its DOS software provided by Microsoft, — which became the basis for the majority of personal computers to the present day.[12] The company later also found success in the portable space with the ThinkPad. Since the 1990s,'

=== 5 ===
chunk.text (61 tokens):
'IBM has concentrated on computer services, software, supercomputers, and scientific research; it sold its microcomputer division to Lenovo in 2005. IBM continues to develop mainframes, and its supercomputers have consistently ranked among the most powerful in the world in the 21st century.'
chunker.contextualize(chunk) (62 tokens):
'IBM\nIBM has concentrated on computer services, software, supercomputers, and scientific research; it sold its microcomputer division to Lenovo in 2005. IBM continues to develop mainframes, and its supercomputers have consistently ranked among the most powerful in the world in the 21st century.'

=== 6 ===
chunk.text (62 tokens):
"As one of the world's oldest and largest technology companies, IBM has been responsible for several technological innovations, including the automated teller machine (ATM), dynamic random-access memory (DRAM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming"
chunker.contextualize(chunk) (63 tokens):
"IBM\nAs one of the world's oldest and largest technology companies, IBM has been responsible for several technological innovations, including the automated teller machine (ATM), dynamic random-access memory (DRAM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming"

=== 7 ===
chunk.text (63 tokens):
'language, and the UPC barcode. The company has made inroads in advanced computer chips, quantum computing, artificial intelligence, and data infrastructure.[13][14][15] IBM employees and alumni have won various recognitions for their scientific research and inventions, including six Nobel Prizes and six Turing'
chunker.contextualize(chunk) (64 tokens):
'IBM\nlanguage, and the UPC barcode. The company has made inroads in advanced computer chips, quantum computing, artificial intelligence, and data infrastructure.[13][14][15] IBM employees and alumni have won various recognitions for their scientific research and inventions, including six Nobel Prizes and six Turing'

=== 8 ===
chunk.text (5 tokens):
'Awards.[16]'
chunker.contextualize(chunk) (6 tokens):
'IBM\nAwards.[16]'

=== 9 ===
chunk.text (56 tokens):
'IBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine'
chunker.contextualize(chunk) (60 tokens):
'IBM\n1910s–1950s\nIBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine'

=== 10 ===
chunk.text (60 tokens):
"(1889);[19] and Willard Bundy invented a time clock to record workers' arrival and departure times on a paper tape (1889).[20] On June 16, 1911, their four companies were amalgamated in New York State by Charles Ranlett Flint forming a fifth company, the"
chunker.contextualize(chunk) (64 tokens):
"IBM\n1910s–1950s\n(1889);[19] and Willard Bundy invented a time clock to record workers' arrival and departure times on a paper tape (1889).[20] On June 16, 1911, their four companies were amalgamated in New York State by Charles Ranlett Flint forming a fifth company, the"

=== 11 ===
chunk.text (59 tokens):
'Computing-Tabulating-Recording Company (CTR) based in Endicott, New York.[1][21] The five companies had 1,300 employees and offices and plants in Endicott and Binghamton, New York; Dayton, Ohio; Detroit, Michigan; Washington,'
chunker.contextualize(chunk) (63 tokens):
'IBM\n1910s–1950s\nComputing-Tabulating-Recording Company (CTR) based in Endicott, New York.[1][21] The five companies had 1,300 employees and offices and plants in Endicott and Binghamton, New York; Dayton, Ohio; Detroit, Michigan; Washington,'

=== 12 ===
chunk.text (13 tokens):
'D.C.; and Toronto, Canada.[22]'
chunker.contextualize(chunk) (17 tokens):
'IBM\n1910s–1950s\nD.C.; and Toronto, Canada.[22]'

=== 13 ===
chunk.text (60 tokens):
'Collectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson, called'
chunker.contextualize(chunk) (64 tokens):
'IBM\n1910s–1950s\nCollectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson, called'

=== 14 ===
chunk.text (59 tokens):
"on Flint and, in 1914, was offered a position at CTR.[23] Watson joined CTR as general manager and then, 11 months later, was made President when antitrust cases relating to his time at NCR were resolved.[24] Having learned Patterson's pioneering business"
chunker.contextualize(chunk) (63 tokens):
"IBM\n1910s–1950s\non Flint and, in 1914, was offered a position at CTR.[23] Watson joined CTR as general manager and then, 11 months later, was made President when antitrust cases relating to his time at NCR were resolved.[24] Having learned Patterson's pioneering business"

=== 15 ===
chunk.text (23 tokens):
"practices, Watson proceeded to put the stamp of NCR onto CTR's companies.[23]:\n105"
chunker.contextualize(chunk) (27 tokens):
"IBM\n1910s–1950s\npractices, Watson proceeded to put the stamp of NCR onto CTR's companies.[23]:\n105"

=== 16 ===
chunk.text (59 tokens):
'He implemented sales conventions, "generous sales incentives, a focus on customer service, an insistence on well-groomed, dark-suited salesmen and had an evangelical fervor for instilling company pride and loyalty in every worker".[25][26] His favorite slogan,'
chunker.contextualize(chunk) (63 tokens):
'IBM\n1910s–1950s\nHe implemented sales conventions, "generous sales incentives, a focus on customer service, an insistence on well-groomed, dark-suited salesmen and had an evangelical fervor for instilling company pride and loyalty in every worker".[25][26] His favorite slogan,'

=== 17 ===
chunk.text (60 tokens):
'"THINK", became a mantra for each company\'s employees.[25] During Watson\'s first four years, revenues reached $9 million ($158 million today) and the company\'s operations expanded to Europe, South America, Asia and Australia.[25] Watson never liked the'
chunker.contextualize(chunk) (64 tokens):
'IBM\n1910s–1950s\n"THINK", became a mantra for each company\'s employees.[25] During Watson\'s first four years, revenues reached $9 million ($158 million today) and the company\'s operations expanded to Europe, South America, Asia and Australia.[25] Watson never liked the'

=== 18 ===
chunk.text (57 tokens):
'clumsy hyphenated name "Computing-Tabulating-Recording Company" and chose to replace it with the more expansive title "International Business Machines" which had previously been used as the name of CTR\'s Canadian Division;[27] the name was changed on February 14,'
chunker.contextualize(chunk) (61 tokens):
'IBM\n1910s–1950s\nclumsy hyphenated name "Computing-Tabulating-Recording Company" and chose to replace it with the more expansive title "International Business Machines" which had previously been used as the name of CTR\'s Canadian Division;[27] the name was changed on February 14,'

=== 19 ===
chunk.text (21 tokens):
'1924.[28] By 1933, most of the subsidiaries had been merged into one company, IBM.'
chunker.contextualize(chunk) (25 tokens):
'IBM\n1910s–1950s\n1924.[28] By 1933, most of the subsidiaries had been merged into one company, IBM.'

=== 20 ===
chunk.text (22 tokens):
'In 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.'
chunker.contextualize(chunk) (26 tokens):
'IBM\n1960s–1980s\nIn 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.'

```

Back to top