# Introducing experiments

We can define, execute, persist and load experiments.

## Creating experiments

Let's create an empty experiment (experiment with no `runs`):

{{include_code("mkdocs/tutorial/examples/01-experiments-01.py", title="Creating an experiment")}}

The statistics reported by the session refer to the persisted experiments. An empty experiment is not very useful, as there are no runs to execute.

## Adding and executing runs

Let's add a `run` to the experiment using the context manager. We introduce three state attributes with different semantics:

* `run.vars`: It can store all object types, accessible only within `steps`
* `run.state`: It can store all object types, accessible within `steps` and at runtime, not accessible after reloading
* `run.fields`: It can store a limited set of object types, it supports reloading from database, and is always accessible

{{include_code("mkdocs/tutorial/examples/01-experiments-02.py", title="Creating a run")}}

The first `print` shows the state of the `experiment`, reporting the count of runs with `runs.count`.
The second `print` shows the contents of the `experiment.runs` object, a dictionary whose keys are the `run` IDs.

In the last block of prints, we see that only the contents of `run.state` and `run.steps` are accessible.
`run.vars` remains available, but it's always empty by design after execution. 

!!! Tip
    * What type of state attribute shall you use? In principle, one should prefer the least powerful yet sufficient semantics that get the job done.
    * You can use regular local variables if their intended scope is within the step: they are the cheapest as they're discarded immediately once the step function returns, and stateless.
    * The semantics of the state of experiments, including `run.vars`, `run.state` and `run.steps`, is presented in detail in the sections [Model of computation](../advanced/computation-model.md) and [State management](../advanced/state.md).


## Persistence of experiments

In the next example, we add a run and execute a `step` function on it.
We will then persist and reload the experiment, looking into its reloaded internal state.

{{include_code("mkdocs/tutorial/examples/01-experiments-03.py", title="Persisting and reloading an experiment")}}

Only `run.steps` is accessible, as expected by design.

!!! Tip
    In `run.steps`, you can store Numpy arrays, Pandas and Pyarrow objects, as well as lists, dictionaries and more.


!!! Success "Congratulations!"
    You have created your first experiment and run, playing with state attributes and persistence.



