---
url: "https://lancedb.github.io/lance/integrations/huggingface.html"
title: "Lance ❤️ HuggingFace - Lance  documentation"
---

# Lance ❤️ HuggingFace [¶](https://lancedb.github.io/lance/integrations/huggingface.html\#lance-huggingface "Link to this heading")

The HuggingFace Hub has become the go to place for ML practitioners to find pre-trained models and useful datasets.

HuggingFace datasets can be written directly into Lance format by using the
[`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") method. You can write the entire dataset or a particular split. For example:

```
# Huggingface datasets
import datasets
import lance

lance.write_dataset(datasets.load_dataset(
    "poloclub/diffusiondb", split="train[:10]",
), "diffusiondb_train.lance")

```