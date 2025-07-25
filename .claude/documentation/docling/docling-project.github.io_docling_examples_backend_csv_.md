---
url: "https://docling-project.github.io/docling/examples/backend_csv/"
title: "Conversion of CSV files - Docling"
---

[Skip to content](https://docling-project.github.io/docling/examples/backend_csv/#conversion-of-csv-files)

# Conversion of CSV files [¶](https://docling-project.github.io/docling/examples/backend_csv/\#conversion-of-csv-files)

This example shows how to convert CSV files to a structured Docling Document.

- Multiple delimiters are supported: `,` `;` `|` `[tab]`
- Additional CSV dialect settings are detected automatically (e.g. quotes, line separator, escape character)

## Example Code [¶](https://docling-project.github.io/docling/examples/backend_csv/\#example-code)

In \[59\]:

Copied!

```
from pathlib import Path

from docling.document_converter import DocumentConverter

# Convert CSV to Docling document
converter = DocumentConverter()
result = converter.convert(Path("../../tests/data/csv/csv-comma.csv"))
output = result.document.export_to_markdown()

```

from pathlib import Path

from docling.document\_converter import DocumentConverter

\# Convert CSV to Docling document
converter = DocumentConverter()
result = converter.convert(Path("../../tests/data/csv/csv-comma.csv"))
output = result.document.export\_to\_markdown()

This code generates the following output:

| Index | Customer Id | First Name | Last Name | Company | City | Country | Phone 1 | Phone 2 | Email | Subscription Date | Website |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | DD37Cf93aecA6Dc | Sheryl | Baxter | Rasmussen Group | East Leonard | Chile | 229.077.5154 | 397.884.0519x718 | zunigavanessa@smith.info | 2020-08-24 | [http://www.stephenson.com/](http://www.stephenson.com/) |
| 2 | 1Ef7b82A4CAAD10 | Preston | Lozano, Dr | Vega-Gentry | East Jimmychester | Djibouti | 5153435776 | 686-620-1820x944 | vmata@colon.com | 2021-04-23 | [http://www.hobbs.com/](http://www.hobbs.com/) |
| 3 | 6F94879bDAfE5a6 | Roy | Berry | Murillo-Perry | Isabelborough | Antigua and Barbuda | +1-539-402-0259 | (496)978-3969x58947 | beckycarr@hogan.com | 2020-03-25 | [http://www.lawrence.com/](http://www.lawrence.com/) |
| 4 | 5Cef8BFA16c5e3c | Linda | Olsen | Dominguez, Mcmillan and Donovan | Bensonview | Dominican Republic | 001-808-617-6467x12895 | +1-813-324-8756 | stanleyblackwell@benson.org | 2020-06-02 | [http://www.good-lyons.com/](http://www.good-lyons.com/) |
| 5 | 053d585Ab6b3159 | Joanna | Bender | Martin, Lang and Andrade | West Priscilla | Slovakia (Slovak Republic) | 001-234-203-0635x76146 | 001-199-446-3860x3486 | colinalvarado@miles.net | 2021-04-17 | [https://goodwin-ingram.com/](https://goodwin-ingram.com/) |

Back to top