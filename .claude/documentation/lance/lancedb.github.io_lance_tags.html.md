---
url: "https://lancedb.github.io/lance/tags.html"
title: "Manage Tags - Lance  documentation"
---

# Manage Tags [¶](https://lancedb.github.io/lance/tags.html\#manage-tags "Link to this heading")

Lance, much like Git, employs the [`LanceDataset.tags`](https://lancedb.github.io/lance/api/python/LanceDataset.tags.html "lance.LanceDataset.tags — Tag management for the dataset.")
property to label specific versions within a dataset’s history.

[`Tags`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags "lance.dataset.Tags — Dataset tag manager.") are particularly useful for tracking the evolution of datasets,
especially in machine learning workflows where datasets are frequently updated.
For example, you can [`create`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create "lance.dataset.Tags.create — Create a tag for a given dataset version."), [`update`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update "lance.dataset.Tags.update — Update tag to a new version."),
and [`delete`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete "lance.dataset.Tags.delete — Delete tag from the dataset.") or [`list`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.list "lance.dataset.Tags.list — List all dataset tags.") tags.

Note

Creating or deleting tags does not generate new dataset versions.
Tags exist as auxiliary metadata stored in a separate directory.

```
>>> import lance
>>> ds = lance.dataset("./tags.lance")
>>> len(ds.versions())
2
>>> ds.tags.list()
{}
>>> ds.tags.create("v1-prod", 1)
>>> ds.tags.list()
{'v1-prod': {'version': 1, ...}}
>>> ds.tags.update("v1-prod", 2)
>>> ds.tags.list()
{'v1-prod': {'version': 2, ...}}
>>> ds.tags.delete("v1-prod")
>>> ds.tags.list()
{}

```

Note

Tagged versions are exempted from the [`LanceDataset.cleanup_old_versions()`](https://lancedb.github.io/lance/api/python/LanceDataset.cleanup_old_versions.html "lance.LanceDataset.cleanup_old_versions — Cleans up old versions of the dataset.")
process.

To remove a version that has been tagged, you must first [`LanceDataset.tags.delete()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete "lance.dataset.Tags.delete — Delete tag from the dataset.")
the associated tag.