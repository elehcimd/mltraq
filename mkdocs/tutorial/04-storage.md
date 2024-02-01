# Persisting experiments

The state of experiments is persisted to database with the method `Experiment.persist(...)`.
In this example, we demonstrate how to run an experiment with two runs, persisting it and loading it
from database, querying with with SQL an with Pandas.

{{include_code("mkdocs/tutorial/examples/04-storage-01.py", title="Storing and reloading an experiment")}}

!!! Tip
    The dictionary `fields` is available for both `Experiment` and `Run` objects.
    `Experiment.fields` is unique to the experiment while `Run.fields` holds values from the `Run` instance.

!!! Info
    The serialization format and more details on the persistence logic are presented in depth at [State storage](../advanced/storage.md).

!!! Success "Congratulations!"
    You experimented with serialization, deserialization, and the usage of native database types.
