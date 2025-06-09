---
url: "https://lancedb.github.io/lance/contributing.html"
title: "Guide for New Contributors - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/contributing.html#getting-started)

# Guide for New Contributors [¶](https://lancedb.github.io/lance/contributing.html\#guide-for-new-contributors "Link to this heading")

This is a guide for new contributors to the Lance project.
Even if you have no previous experience with python, rust, and open source, you can still make an non-trivial
impact by helping us improve documentation, examples, and more.
For experienced developers, the issues you can work on run the gamut from warm-ups to serious challenges in python and rust.

If you have any questions, please join our [Discord](https://discord.gg/zMM32dvNtd) for real-time support. Your feedback is always welcome!

## Getting Started [¶](https://lancedb.github.io/lance/contributing.html\#getting-started "Link to this heading")

1. Join our Discord and say hi

2. Setup your development environment

3. Pick an issue to work on. See [https://github.com/lancedb/lance/contribute](https://github.com/lancedb/lance/contribute) for good first issues.

4. Have fun!


## Development Environment [¶](https://lancedb.github.io/lance/contributing.html\#development-environment "Link to this heading")

Currently Lance is implemented in Rust and comes with a Python wrapper. So you’ll want to make sure you setup both.

1. Install Rust: [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install)

2. Install Python 3.9+: [https://www.python.org/downloads/](https://www.python.org/downloads/)

3. Install protoctol buffers: [https://grpc.io/docs/protoc-installation/](https://grpc.io/docs/protoc-installation/) (make sure you have version 3.20 or higher)

4. Install commit hooks:

1. Install pre-commit: [https://pre-commit.com/#install](https://pre-commit.com/#install)

2. Run pre-commit install in the root of the repo


## Sample Workflow [¶](https://lancedb.github.io/lance/contributing.html\#sample-workflow "Link to this heading")

1. Fork the repo

2. Pick [Github issue](https://github.com/lancedb/lance/issues)

3. Create a branch for the issue

4. Make your changes

5. Create a pull request from your fork to lancedb/lance

6. Get feedback and iterate

7. Merge!

8. Go back to step 2


## Python Development [¶](https://lancedb.github.io/lance/contributing.html\#python-development "Link to this heading")

See: [https://github.com/lancedb/lance/blob/main/python/DEVELOPMENT.md](https://github.com/lancedb/lance/blob/main/python/DEVELOPMENT.md)

## Rust Development [¶](https://lancedb.github.io/lance/contributing.html\#rust-development "Link to this heading")

To format and lint Rust code:

```
cargo fmt --all
cargo clippy --all-features --tests --benches

```

## Repo Structure [¶](https://lancedb.github.io/lance/contributing.html\#repo-structure "Link to this heading")

### Core Format [¶](https://lancedb.github.io/lance/contributing.html\#core-format "Link to this heading")

The core format is implemented in Rust under the rust directory. Once you’ve setup Rust you can build the core format with:

```
cargo build

```

This builds the debug build. For the optimized release build:

```
cargo build -r

```

To run the Rust unit tests:

```
cargo test

```

If you’re working on a performance related feature, benchmarks can be run via:

```
cargo bench

```

### Python Bindings [¶](https://lancedb.github.io/lance/contributing.html\#python-bindings "Link to this heading")

The Python bindings for Lance uses a mix of Rust (pyo3) and Python.
The Rust code that directly supports the Python bindings are under python/src while the pure Python code lives under python/python.

To build the Python bindings, first install requirements:

```
pip install maturin

```

To make a dev install:

```
cd python
maturin develop

```

To use the local python bindings, it’s recommended to use venv or conda
environment.

### Documentation [¶](https://lancedb.github.io/lance/contributing.html\#documentation "Link to this heading")

The documentation is built using Sphinx and lives under docs.
To build the docs, first install requirements:

```
pip install -r docs/requirements.txt

```

Then build the docs:

```
cd docs
make html

```

The docs will be built under docs/build/html.

### Example Notebooks [¶](https://lancedb.github.io/lance/contributing.html\#example-notebooks "Link to this heading")

Example notebooks are under examples. These are standalone notebooks you should be able to download and run.

### Benchmarks [¶](https://lancedb.github.io/lance/contributing.html\#benchmarks "Link to this heading")

Our Rust benchmarks are run multiple times a day and the history can be found [here](https://github.com/lancedb/lance-benchmark-results).

Separately, we have vector index benchmarks that test against the sift1m dataset, as well as benchmarks for tpch.
These live under benchmarks.

## Code of Conduct [¶](https://lancedb.github.io/lance/contributing.html\#code-of-conduct "Link to this heading")

See [https://www.python.org/psf/conduct/](https://www.python.org/psf/conduct/) and [https://www.rust-lang.org/policies/code-of-conduct](https://www.rust-lang.org/policies/code-of-conduct) for details.