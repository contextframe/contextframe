---
url: "https://docling-project.github.io/docling/integrations/apify/"
title: "Apify - Docling"
---

# Apify

You can run Docling in the cloud without installation using the [Docling Actor](https://apify.com/vancura/docling?fpr=docling) on Apify platform. Simply provide a document URL and get the processed result:

[![Run Docling Actor on Apify](https://apify.com/ext/run-on-apify.png)](https://apify.com/vancura/docling?fpr=docling)

```
apify call vancura/docling -i '{
  "options": {
    "to_formats": ["md", "json", "html", "text", "doctags"]
  },
  "http_sources": [\
    {"url": "https://vancura.dev/assets/actor-test/facial-hairstyles-and-filtering-facepiece-respirators.pdf"},\
    {"url": "https://arxiv.org/pdf/2408.09869"}\
  ]
}'

```

The Actor stores results in:

- Processed document in key-value store ( `OUTPUT_RESULT`)
- Processing logs ( `DOCLING_LOG`)
- Dataset record with result URL and status

Read more about the [Docling Actor](https://docling-project.github.io/docling/integrations/apify/.actor/README.md), including how to use it via the Apify API and CLI.

- 💻 [GitHub](https://github.com/docling-project/docling/tree/main/.actor/)
- 📖 [Docs](https://github.com/docling-project/docling/tree/main/.actor/README.md)
- 📦 [Docling Actor](https://apify.com/vancura/docling?fpr=docling)

Back to top