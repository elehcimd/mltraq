# Database storage

MLTRAQ stores experiments in plain SQL tables in two types of tables:

* Table `experiments`: Fixed name and schema, each row represents an experiment, it stores the serialized value of dictionary `experiment.fields` in the `fields` column;
* Table `e_name`: It represents the tracking data for runs of expriment named `name`, each row represents a distinct run. It stores the `run.fields` values as a set of columns whose names are its dictionary keys, making it easily accessible from SQL.

!!! Important
    The serialization of `experiment.fields` and `run.fields` supports a wide range of object types: `dict`, `list`, `tuple`, `string`, `int`, `float`, `bool`, `pandas.Series`, `pandas.DataFrame`, `numpy.ndarray`, and `datetime64[ns]`. 
    This is a powerful feature that enables a series of very important use cases, such as the
    decoupling of the generation of ML predictions from their evaluation in separate pipelines.

In the next example, we demonstrate the decoupling of simulations from their evaluation: step `toss_coins` is executed once and the outcomes are persisted to database. The evaluation of the error metric is then
executed on a copy of the experiment loaded from the database in the `metrics` step.

{{include_code("mkdocs/tutorial/examples/persist-experiment-001.py", title="Repeated toin cossing")}}

## Picking experiments


In case of pickled experiments, the complete expriment object and its runs are persisted.
You can pickle experiments by passing the optional parameter `store_pickle=True` upon persisting them. In this example, we store and load the pickled object of the experiment, accessing a temporary field that would otherwise not be retained.

{{include_code("mkdocs/tutorial/examples/persist-experiment-002.py", title="Repeated toin cossing")}}


!!! Warning
    Pickling should be avoided if not strictly necessary as [it might not work across different systems and it is not secure](https://docs.python.org/3/library/pickle.html). There are good reasons to pickle experiments, such as the temporary fast reloading of complex large experiments for faster 
    experimentation. Know the pros and cons of pickling Python objects and use them wisely.
