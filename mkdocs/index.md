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
Manage ML Experiments with Persistence
</h1>

MLtraq is an open-source ML framework for Python to manage experiments.
With database persistence for state recovery and collaboration. Using open standards, no vendor lock-in.

!!! Success ""
    **Funding**: You can support as a [sponsor](./sponsor.md), hiring [me](https://www.linkedin.com/in/dallachiesa/) for DS/ML/AI work, [citing](./cite.md) and [starring](https://github.com/elehcimd/mltraq) the project. Thank You!

## Motivations & benefits

* Designed for **maximum interoperability**: Reproducible, transparent and accessible experiments. I and my clients prefer open standards to mitigate the risks associacted to vendor lock-in, coupled with a sound, robust approach to experimentation.

* Architected to **promote distributed collaboration**: Seamlessly create, store, manage and share experiments [using any SQL database](advanced/storage.md). I want to work with my team on the client's existing infrastructure to lower complexity and costs.

* Built for **faster knowledge transfer**: [High-quality documentation](advanced/handover.md) on code organization with detailed instructions for running, reproducing, and accessing results. I want handovers to be a valued, positive and well-designed experience.

## Key features

* **Immediate**: Design and execute experiments with a few lines of code.
* **Collaborative**: Backup, merge, share and reload experiments with their computation state anywhere.
* **Interoperable**: Access your experiments with Python, Pandas and SQL with native database types － no vendor lock-in.
* **Flexible**: Track native Python data types and structures, as well as Numpy, Pandas and PyArrow objects.
* **Lightweight**: Thin layer with minimal dependencies that can run anywhere and can complement other components/services.

## Limitations

* **Not designed for MLOps**: The aim of ML experimentation is to explore the computational spectrum of the possibilities: algorithms, data structures, model architectures, formulation and validation of hypotheses. Model deployment, CI/CD pipelines, monitoring & triggering are out of scope.
* **Computation**: The chained execution of `steps` is implemented with [joblib.Parallel](https://joblib.readthedocs.io/en/latest/parallel.html) using process-based parallelism. Cluster-specific backends for Dask, Ray and Spark, as well as custom ones, can be used. The `step` functions and `run` objects must be serializable with `cloudpickle` (the serializer used by Joblib).
You should not expect a fully fledged orchestrator of ML pipelines, which is out of scope.
* **Persistence**: By default, an in-memory SQLite database is used and its [default limits](https://sqlite.org/limits.html) do apply. Storing large objects (>1GB) is out of scope. Database persistence supports a wide range of types, including: `bool`, `int`, `float`, `string`, `UUID.uuid`, `bytes`, `dict`, `list`, `tuple`, `set`, Numpy, Pandas and Arrow objects.

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
