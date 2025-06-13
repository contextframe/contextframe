---
url: "https://docling-project.github.io/docling/examples/run_md/"
title: "Run md - Docling"
---

# Run md

In \[ \]:

Copied!

```
import json
import logging
import os
from pathlib import Path

```

import json
import logging
import os
from pathlib import Path

In \[ \]:

Copied!

```
import yaml

```

import yaml

In \[ \]:

Copied!

```
from docling.backend.md_backend import MarkdownDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

```

from docling.backend.md\_backend import MarkdownDocumentBackend
from docling.datamodel.base\_models import InputFormat
from docling.datamodel.document import InputDocument

In \[ \]:

Copied!

```
_log = logging.getLogger(__name__)

```

\_log = logging.getLogger(\_\_name\_\_)

In \[ \]:

Copied!

```
def main():
    input_paths = [Path("README.md")]

    for path in input_paths:
        in_doc = InputDocument(
            path_or_stream=path,
            format=InputFormat.PDF,
            backend=MarkdownDocumentBackend,
        )
        mdb = MarkdownDocumentBackend(in_doc=in_doc, path_or_stream=path)
        document = mdb.convert()

        out_path = Path("scratch")
        print(f"Document {path} converted.\nSaved markdown output to: {out_path!s}")

        # Export Docling document format to markdowndoc:
        fn = os.path.basename(path)

        with (out_path / f"{fn}.md").open("w") as fp:
            fp.write(document.export_to_markdown())

        with (out_path / f"{fn}.json").open("w") as fp:
            fp.write(json.dumps(document.export_to_dict()))

        with (out_path / f"{fn}.yaml").open("w") as fp:
            fp.write(yaml.safe_dump(document.export_to_dict()))

```

def main():
input\_paths = \[Path("README.md")\]

for path in input\_paths:
in\_doc = InputDocument(
path\_or\_stream=path,
format=InputFormat.PDF,
backend=MarkdownDocumentBackend,
)
mdb = MarkdownDocumentBackend(in\_doc=in\_doc, path\_or\_stream=path)
document = mdb.convert()

out\_path = Path("scratch")
print(f"Document {path} converted.\\nSaved markdown output to: {out\_path!s}")

# Export Docling document format to markdowndoc:
fn = os.path.basename(path)

with (out\_path / f"{fn}.md").open("w") as fp:
fp.write(document.export\_to\_markdown())

with (out\_path / f"{fn}.json").open("w") as fp:
fp.write(json.dumps(document.export\_to\_dict()))

with (out\_path / f"{fn}.yaml").open("w") as fp:
fp.write(yaml.safe\_dump(document.export\_to\_dict()))

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top