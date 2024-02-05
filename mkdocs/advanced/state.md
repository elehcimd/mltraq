# State management

## Experiment state

The state of an experiment is defined by these attributes:

* `id_experiment`: UUID of the experiment.
* `name`: Name of the experiment. If not provided, a short 6-alphanum hash of `id_experiment` is generated.
* `db`: Database handler (discarded on pickling).
* `fields`: Accessible at any time, with database storage.
* `runs`: Collection of `runs` associated with the experiment implemented as a dictionary with `run` IDs as keys.

## Run state

The state of a run is defined by these attributes:

* `id_experiment`: UUID of the associated experiment.
* `id_run`: UUID of the run.
* `config`: Fixed parameters of the `run`, cleared after execution.
* `params`: Variable parameters of the `run`, cleared after execution.
* `vars`: Accessible only within `steps` execution.
* `state`: Accessible after execution of `steps`.
* `fields`: Accessible at any time, with database storage.
* `exception`: Set transparently if the `step` raised an exception before raising the exception at experiment-level.
* `steps`: Sequence of functions to execute, accessible only within `steps` execution.

!!! Tip
    * For a comprehensive discussion of the semantics of the different attributes, see [Model of computation](./computation-model.md).
    * The `steps` attribute can be inspected by a `step` function to read the Python source code of the `steps`, which can be used to track the state lineage and/or the `steps` code for backup and later analysis.

## Example

We programmatically print the attributes that constitute the strict state of `experiments` and `runs`, as well as the respective subsets that are considered for pickling. Declaring the [\__slots__](https://docs.python.org/3/reference/datamodel.html#slots) attribute allows us to declare explicitly which attributes are allowed, and deny the creation of new ones. This behaviour keeps these objects clean, and enforces the correct use of the available `run` state attributes. The `__state__` attribute is not inherited by Object, it simply defines a list of attributes to be considered by [\__getstate__](https://docs.python.org/3/library/pickle.html#object.__getstate__) for pickling.
    
{{include_code("mkdocs/advanced/examples/pickling-01.py", title="The state attributes of experiments and runs")}}


