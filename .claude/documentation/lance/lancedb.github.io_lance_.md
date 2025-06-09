---
url: "https://lancedb.github.io/lance/"
title: "Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/#)

[![_images/lance_logo.png](https://lancedb.github.io/lance/_images/lance_logo.png)](https://lancedb.github.io/lance/_images/lance_logo.png)

# Lance: modern columnar format for ML workloads [¶](https://lancedb.github.io/lance/\#lance-modern-columnar-format-for-ml-workloads "Link to this heading")

Lance is a columnar format that is easy and fast to version, query and train on.
It’s designed to be used with images, videos, 3D point clouds, audio and of course tabular data.
It supports any POSIX file systems, and cloud storage like AWS S3 and Google Cloud Storage.
The key features of Lance include:

- **High-performance random access:** 100x faster than Parquet.

- **Zero-copy schema evolution:** add and drop columns without copying the entire dataset.

- **Vector search:** find nearest neighbors in under 1 millisecond and combine OLAP-queries with vector search.

- **Ecosystem integrations:** Apache-Arrow, DuckDB and more on the way.


## Installation [¶](https://lancedb.github.io/lance/\#installation "Link to this heading")

You can install Lance via pip:

```
pip install pylance

```

For the latest features and bug fixes, you can install the preview version:

```
pip install --pre --extra-index-url https://pypi.fury.io/lancedb/ pylance

```

Preview releases receive the same level of testing as regular releases.

Introduction

- [Quickstart](https://lancedb.github.io/lance/notebooks/quickstart.html)
  - [Creating datasets](https://lancedb.github.io/lance/notebooks/quickstart.html#creating-datasets)
  - [Versioning](https://lancedb.github.io/lance/notebooks/quickstart.html#versioning)
  - [Vectors](https://lancedb.github.io/lance/notebooks/quickstart.html#vectors)
- [Read and Write Data](https://lancedb.github.io/lance/introduction/read_and_write.html)
  - [Writing Lance Dataset](https://lancedb.github.io/lance/introduction/read_and_write.html#writing-lance-dataset)
  - [Adding Rows](https://lancedb.github.io/lance/introduction/read_and_write.html#adding-rows)
  - [Deleting rows](https://lancedb.github.io/lance/introduction/read_and_write.html#deleting-rows)
  - [Updating rows](https://lancedb.github.io/lance/introduction/read_and_write.html#updating-rows)
  - [Merge Insert](https://lancedb.github.io/lance/introduction/read_and_write.html#merge-insert)
  - [Reading Lance Dataset](https://lancedb.github.io/lance/introduction/read_and_write.html#reading-lance-dataset)
  - [Table Maintenance](https://lancedb.github.io/lance/introduction/read_and_write.html#table-maintenance)
- [Schema Evolution](https://lancedb.github.io/lance/introduction/schema_evolution.html)
  - [Renaming columns](https://lancedb.github.io/lance/introduction/schema_evolution.html#renaming-columns)
  - [Casting column data types](https://lancedb.github.io/lance/introduction/schema_evolution.html#casting-column-data-types)
  - [Adding new columns](https://lancedb.github.io/lance/introduction/schema_evolution.html#adding-new-columns)
  - [Adding new columns with Schema only](https://lancedb.github.io/lance/introduction/schema_evolution.html#adding-new-columns-with-schema-only)
  - [Adding new columns using merge](https://lancedb.github.io/lance/introduction/schema_evolution.html#adding-new-columns-using-merge)
  - [Dropping columns](https://lancedb.github.io/lance/introduction/schema_evolution.html#dropping-columns)

Advanced Usage

- [Lance Format Spec](https://lancedb.github.io/lance/format.html)
- [Blob API](https://lancedb.github.io/lance/blob.html)
- [Manage Tags](https://lancedb.github.io/lance/tags.html)
- [Object Store Configuration](https://lancedb.github.io/lance/object_store.html)
- [Distributed Write](https://lancedb.github.io/lance/distributed_write.html)
- [Performance Guide](https://lancedb.github.io/lance/performance.html)
- [Tokenizer](https://lancedb.github.io/lance/tokenizer.html)
- [Extension Arrays](https://lancedb.github.io/lance/arrays.html)

Integrations

- [Huggingface](https://lancedb.github.io/lance/integrations/huggingface.html)
- [Tensorflow](https://lancedb.github.io/lance/integrations/tensorflow.html)
  - [Reading from Lance](https://lancedb.github.io/lance/integrations/tensorflow.html#reading-from-lance)
  - [Distributed Training and Shuffling](https://lancedb.github.io/lance/integrations/tensorflow.html#distributed-training-and-shuffling)
- [PyTorch](https://lancedb.github.io/lance/integrations/pytorch.html)
- [Ray](https://lancedb.github.io/lance/integrations/ray.html)
  - [Basic Operations](https://lancedb.github.io/lance/integrations/ray.html#basic-operations)
  - [Advanced Operations](https://lancedb.github.io/lance/integrations/ray.html#advanced-operations)
    - [Parallel Column Merging](https://lancedb.github.io/lance/integrations/ray.html#parallel-column-merging)
- [Spark](https://lancedb.github.io/lance/integrations/spark.html)
  - [Build from source code](https://lancedb.github.io/lance/integrations/spark.html#build-from-source-code)
  - [Download the pre-build jars](https://lancedb.github.io/lance/integrations/spark.html#download-the-pre-build-jars)
  - [Configurations for Lance Spark Connector](https://lancedb.github.io/lance/integrations/spark.html#configurations-for-lance-spark-connector)
  - [Startup the Spark Shell](https://lancedb.github.io/lance/integrations/spark.html#startup-the-spark-shell)
  - [Using Spark Shell to manipulate lance dataset](https://lancedb.github.io/lance/integrations/spark.html#using-spark-shell-to-manipulate-lance-dataset)

- [API References](https://lancedb.github.io/lance/api/api.html)
- [Contributor Guide](https://lancedb.github.io/lance/contributing.html)
- [Examples](https://lancedb.github.io/lance/examples/examples.html)

# Indices and tables [¶](https://lancedb.github.io/lance/\#indices-and-tables "Link to this heading")

- [Index](https://lancedb.github.io/lance/genindex.html)

- [Module Index](https://lancedb.github.io/lance/py-modindex.html)

- [Search Page](https://lancedb.github.io/lance/search.html)