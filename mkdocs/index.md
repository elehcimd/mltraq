<p align="center">
  <img height="30%" width="30%" src="assets/img/logo-black.svg#only-light" alt="MLTRAQ">
  <img height="30%" width="30%" src="assets/img/logo-white.svg#only-dark" alt="MLTRAQ">
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

Open source **experiment tracking API** with **ML performance analysis** to build better models faster, facilitating collaboration and transparency within the team and with stakeholders.

---

* **Documentation**: [https://www.mltraq.com](https://www.mltraq.com)
* **Source code**: [https://github.com/elehcimd/mltraq](https://github.com/elehcimd/mltraq)

---

## Key features

* **Immediate**: start tracking experiments with a few lines of code.
* **Collaborative**: Backup and upstream experimental results with your team.
* **Interoperable**: Access the data anywhere with SQL, Pandas and Python API.
* **Flexible**: Track structured types including Numpy arrays and Pandas frames/series.
* **Steps library**: Use pre-built "steps" for tracking, testing, analysis and reporting.
* **Execution engine**: Define and execute parametrized experiment pipelines.


## Requirements

* **Python >=3.10**
* **SQLAlchemy**, **Pandas**, and **Joblib** (installed as dependencies)


## Installation

```
pip install mltraq
```


## Examples

### 1. Track and query with SQL

Add tracking to your experiments with a few lines of code and start querying them with SQL:

{{include_code("mkdocs/examples/001.py", title="Fast tracking")}}


### 2. Iris dataset classification

In less than 70 lines of code, we load, train, and test five models
in parallel, tracking and reporting performance results averaged on ten repeated runs:


{{include_code("mkdocs/examples/002.py", title="Fully managed execution")}}

MLTRAQ makes it easy and intuitive to define, run, execute, and query experiments,
so that you can spend more time on what truly matters.


!!! Info 
    Continue to the hands-on [tutorial](./tutorial/index.md) to learn how to leverage
    at best the capabilities of MLTRAQ for your ML projects.

## License

This project is licensed under the terms of the [BSD 3-Clause License](./license).

