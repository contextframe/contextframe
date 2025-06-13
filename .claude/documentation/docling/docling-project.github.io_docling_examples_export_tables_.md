---
url: "https://docling-project.github.io/docling/examples/export_tables/"
title: "Table export - Docling"
---

# Table export

In \[ \]:

Copied!

```
import logging
import time
from pathlib import Path

```

import logging
import time
from pathlib import Path

In \[ \]:

Copied!

```
import pandas as pd

```

import pandas as pd

In \[ \]:

Copied!

```
from docling.document_converter import DocumentConverter

```

from docling.document\_converter import DocumentConverter

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
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/pdf/2206.01062.pdf")
    output_dir = Path("scratch")

    doc_converter = DocumentConverter()

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    doc_filename = conv_res.input.file.stem

    # Export tables
    for table_ix, table in enumerate(conv_res.document.tables):
        table_df: pd.DataFrame = table.export_to_dataframe()
        print(f"## Table {table_ix}")
        print(table_df.to_markdown())

        # Save the table as csv
        element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.csv"
        _log.info(f"Saving CSV table to {element_csv_filename}")
        table_df.to_csv(element_csv_filename)

        # Save the table as html
        element_html_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.html"
        _log.info(f"Saving HTML table to {element_html_filename}")
        with element_html_filename.open("w") as fp:
            fp.write(table.export_to_html(doc=conv_res.document))

    end_time = time.time() - start_time

    _log.info(f"Document converted and tables exported in {end_time:.2f} seconds.")

```

def main():
logging.basicConfig(level=logging.INFO)

input\_doc\_path = Path("./tests/data/pdf/2206.01062.pdf")
output\_dir = Path("scratch")

doc\_converter = DocumentConverter()

start\_time = time.time()

conv\_res = doc\_converter.convert(input\_doc\_path)

output\_dir.mkdir(parents=True, exist\_ok=True)

doc\_filename = conv\_res.input.file.stem

# Export tables
for table\_ix, table in enumerate(conv\_res.document.tables):
table\_df: pd.DataFrame = table.export\_to\_dataframe()
print(f"## Table {table\_ix}")
print(table\_df.to\_markdown())

# Save the table as csv
element\_csv\_filename = output\_dir / f"{doc\_filename}-table-{table\_ix + 1}.csv"
\_log.info(f"Saving CSV table to {element\_csv\_filename}")
table\_df.to\_csv(element\_csv\_filename)

# Save the table as html
element\_html\_filename = output\_dir / f"{doc\_filename}-table-{table\_ix + 1}.html"
\_log.info(f"Saving HTML table to {element\_html\_filename}")
with element\_html\_filename.open("w") as fp:
fp.write(table.export\_to\_html(doc=conv\_res.document))

end\_time = time.time() - start\_time

\_log.info(f"Document converted and tables exported in {end\_time:.2f} seconds.")

In \[ \]:

Copied!

```
if __name__ == "__main__":
    main()

```

if \_\_name\_\_ == "\_\_main\_\_":
main()

Back to top