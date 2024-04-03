<!--
---
hide:
  - toc
---
-->

#

<p align="center">
  <img height="75%" width="75%" src="assets/img/logo-wide-black.svg#only-light" alt="MLtraq">
  <img height="75%" width="75%" src="assets/img/logo-wide-white.svg#only-dark" alt="MLtraq">
</p>

<p align="center">
<img src="/assets/img/badges/test.svg" alt="Test">
<img src="/assets/img/badges/coverage.svg" alt="Coverage">
<img src="/assets/img/badges/python.svg" alt="Python">
<a href="https://pypi.org/project/mltraq/"><img src="/assets/img/badges/pypi.svg" alt="PyPi"></a>
<a href="/license"><img src="/assets/img/badges/license.svg" alt="License"></a>
<img src="/assets/img/badges/code-style.svg" alt="Code style">
</p>


---
<h1 align="center">
Track and Collaborate on AI Experiments.
</h1>

The open-source Python library for AI developers to design, execute and share experiments.
Track anything, stream, reproduce, collaborate, and resume the computation state anywhere.

---

* **Documentation**: [https://www.mltraq.com](https://www.mltraq.com/)
* **Source code**: [https://github.com/elehcimd/mltraq](https://github.com/elehcimd/mltraq) (License: [BSD 3-Clause](https://mltraq.com/license/))
* **Discussions**: [Ask questions, share ideas, engage](https://github.com/elehcimd/mltraq/discussions)
* **Funding**: You can [sponsor](https://mltraq.com/sponsor/), [cite](https://mltraq.com/cite/), [star](https://github.com/elehcimd/mltraq) the project, and [hire me](https://www.linkedin.com/in/dallachiesa/) for DS/ML/AI work


## Motivations & benefits

* **Blazing fast**: The [fastest](./benchmarks/speed.md) experiment tracking solution in the industry.

* **Extreme tracking and interoperability**: With native database types, [Numpy and PyArrow serialization, and a safe subset of opcodes for Python pickles](./advanced/storage.md#the-datapak-format).

* **Promoting collaboration**: Work seamlessly with your team by creating, storing, reloading, mixing, resuming, and sharing experiments using [any local or remote SQL database](advanced/storage.md).

* **Flexible and open**: Interact with your experiments using Python, Pandas, and SQL from Python scripts, Jupyter notebooks, and dashboards without vendor lock-in.

## Key features

* **Immediate**: Design and execute experiments with a few lines of code, stream your metrics.
* **Collaborative**: Backup, merge, share, and reload experiments with their computation state anywhere.
* **Interoperable**: Access your experiments with Python, Pandas, and SQL with native database types and open formats － no vendor lock-in.
* **Flexible**: Track native Python data types and structures, as well as NumPy, Pandas, and PyArrow objects.
* **Lightweight**: Thin layer with minimal dependencies that can run anywhere and complement other components/services.

## Design choices

* **Computation**: The chained execution of `steps` is implemented with [joblib.Parallel](https://joblib.readthedocs.io/en/latest/parallel.html) using process-based parallelism. The cluster-specific backends of Dask, Ray, Spark, and custom ones can be used. The `step` functions and `run` objects must be serializable with `cloudpickle`. You can directly handle the evaluation of your runs without `joblib`, with less automation and more flexibility.

* **Persistence**: The default database is SQLite, and its [limits](https://sqlite.org/limits.html) apply. You can connect to any SQL database supported by `SQLAlchemy`. Database persistence [supports a wide range of types](./advanced/storage.md#list-of-supported-types), including `bool`, `int`, `float`, `string`, `UUID.uuid`, `bytes`, `dict`, `list`, `tuple`, `set`, `Numpy`, `Pandas` and `PyArrow` objects. The [Data store](./advanced/datastore.md) interface is designed to handle out-of-database large objects. Compression is available and disabled by default.


## Requirements

* **Python 3.10+**
* **SQLAlchemy 2.0+**, **Pandas 1.5.3+**, and **Joblib 1.3.2+** (installed as dependencies)


## Installation

To install MLtraq:

```
pip install mltraq --upgrade
```

!!! Question "How to integrate MLtraq it in your projects?"
    MLtraq is progressing rapidly and interfaces might change at any time.
    Pin its exact version for your project, to make sure it all works.
    Have tests for your project, and update it once you verify that things work correctly.


## Example 1: Define, execute and query an experiment with SQL

{{include_code("mkdocs/examples/000.py", title="Define, execute and query an experiment with SQL", drop_comments=False)}}

## Example 2: Parameter grids, parallel and resumed execution

{{include_code("mkdocs/examples/001.py", title="Parameter grids, parallel and resumed execution", drop_comments=False)}}

## Example 3: IRIS Flowers Classification

{{include_code("mkdocs/examples/002.py", title="IRIS Flowers Classification", drop_comments=False)}}

## License

This project is licensed under the terms of the [BSD 3-Clause License](./license.md).

---

*Latest update: `{{include_current_date()}}` using `mltraq=={{include_mltraq_version()}}`*
