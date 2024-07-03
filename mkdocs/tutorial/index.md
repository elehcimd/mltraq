# Getting started

In this tutorial, you will learn how to define and execute experiments, trying the key features.
You can follow it sequentially or jump to specific questions as needed.

## Installation

MLtraq requires **Python 3.9+** and depends on  **SQLAlchemy 2.0+**, **Pandas 1.5.3+**, and **Joblib 1.3.2+**, which are installed as dependencies. To install:

```
pip install mltraq --upgrade
```

## Examples

The code examples are fully self-contained to reproduce the outputs.
In this example, the version of MLtraq used to compile this tutorial is shown.
Make sure to have the latest release installed.

{{include_code("mkdocs/tutorial/examples/version.py", title="MLtraq version")}}


# Key concepts

* **Experimentation**: The process of systematically changing and testing different input values in an algorithm to observe their impact on performance, behavior, or outcomes. Experiments can be defined and executed, with their outcomes and/or results persisted for later analysis.

* **Session**: A `session` object lets you define the connection to a database, load and add experiments. Sessions are bound to a database.

* **Experiment**: An `experiment` object manages a collection of `run` objects. Experiments can be created, persisted, loaded and executed. It implements the experimentation process. A `run` is an instantiation of the experiment with a configuration of input values. The execution of an `experiment` requires the execution of all its `runs`. Experiments are bound to a database and are unaware of sessions.

* **Run**: A `run` object is an instantiation of the experiment with a configuration of input values. The execution of a `run` is defined as the chained evaluation of `step` functions, whose sole parameter is the `run` object itself. Runs are unaware of databases, sessions, experiments or other runs, and are isolated from the rest of the experiment.

* **Step**: Step functions are a Python functions that take as sole input the `run` object, changing its internal state. There is no return value. Steps can access the configuration of the `run` in the attributes `run.config` and `run.params`, and can change the state of the `run` by modifying the attributes `run.vars`, `run.state` and `run.fields`.

!!! Tip
    An overview of the `run` state attributes can be found in [State management](../advanced/state.md), with a discussion of their semantics in the [Model of computation](../advanced/computation-model.md).


