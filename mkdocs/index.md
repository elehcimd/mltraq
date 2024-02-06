<!--
---
hide:
  - toc
---
-->

#

<p align="center">
  <img height="50%" width="50%" src="assets/img/logo-wide-black.svg#only-light" alt="MLtraq">
  <img height="50%" width="50%" src="assets/img/logo-wide-white.svg#only-dark" alt="MLtraq">
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
Track anything, reproduce, collaborate, and resume the computation state anywhere.

---

* **Documentation**: [https://www.mltraq.com](https://www.mltraq.com/)
* **Source code**: [https://github.com/elehcimd/mltraq](https://github.com/elehcimd/mltraq) (License: [BSD 3-Clause](https://mltraq.com/license/))
* **Discussions**: [Ask questions, share ideas, engage](https://github.com/elehcimd/mltraq/discussions)
* **Funding**: You can [sponsor](https://mltraq.com/sponsor/), [cite](https://mltraq.com/cite/), [star](https://github.com/elehcimd/mltraq) the project, and [hire me](https://www.linkedin.com/in/dallachiesa/) for DS/ML/AI work.


## Motivations & benefits


* **Extreme tracking and interoperability**: Using native database types, [Numpy and PyArrow native serialization, and a safe subset of opcodes for Python pickles](./advanced/storage.md#the-datapak-format).

* **Promoting distributed collaboration**: Seamlessly create, store, reload, mix, resume and share experiments with your team in-memory and [using any SQL database](advanced/storage.md).


## Key features

* **Immediate**: Design and execute experiments with a few lines of code.
* **Collaborative**: Backup, merge, share and reload experiments with their computation state anywhere.
* **Interoperable**: Access your experiments with Python, Pandas and SQL with native database types and open formats － no vendor lock-in.
* **Flexible**: Track native Python data types and structures, as well as Numpy, Pandas and PyArrow objects.
* **Lightweight**: Thin layer with minimal dependencies that can run anywhere and can complement other components/services.

## Limitations

* **Computation**: The chained execution of `steps` is implemented with [joblib.Parallel](https://joblib.readthedocs.io/en/latest/parallel.html) using process-based parallelism. Cluster-specific backends for Dask, Ray and Spark, as well as custom ones, can be used. The `step` functions and `run` objects must be serializable with `cloudpickle`. The managed execution is optional.
* **Persistence**: By default, an in-memory SQLite database is used and its [default limits](https://sqlite.org/limits.html) do apply. Database persistence [supports a wide range of types](./advanced/storage.md#list-of-supported-types), including: `bool`, `int`, `float`, `string`, `UUID.uuid`, `bytes`, `dict`, `list`, `tuple`, `set`, Numpy, Pandas and PyArrow objects.
The database is not a good fit for large (>1GB) artifacts. To store model weights, images, datasets, pickled scikit-learn models, [use a separate artifacts store](./howto/02-artifacts-storage.md).

## Requirements

* **Python 3.10+**
* **SQLAlchemy 2.0+**, **Pandas 1.5.3+**, and **Joblib 1.3.2+** (installed as dependencies)


## Installation

To install MLtraq:

```
pip install mltraq --upgrade
```


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
