---
url: "https://docling-project.github.io/docling/examples/minimal/"
title: "Simple conversion - Docling"
---

# Simple conversion

In \[ \]:

Copied!

```
from docling.document_converter import DocumentConverter

```

from docling.document\_converter import DocumentConverter

In \[ \]:

Copied!

```
source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL

```

source = "https://arxiv.org/pdf/2408.09869" # document per local path or URL

In \[ \]:

Copied!

```
converter = DocumentConverter()
doc = converter.convert(source).document

```

converter = DocumentConverter()
doc = converter.convert(source).document

In \[ \]:

Copied!

```
print(doc.export_to_markdown())
# output: ## Docling Technical Report [...]"

```

print(doc.export\_to\_markdown())
\# output: ## Docling Technical Report \[...\]"

Back to top