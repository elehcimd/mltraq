# Managed experiments

MLtraq can handle for you the execution flow of experiments, offering
an higher degree of automation and increased reproducibility:

1. **Definition of execution pipelines**: organize your code into execution steps, enabling code reuse and better documentation;
1. **Handling of parameters**: runs are associated to fixed and variable parameters that can be accessed during their execution, simplifying the exploration of parameter spaces and reducing code duplication;
2. **Continuation of experiments**: reload experiments and continue your analyses thanks to the tracking checkpoints;
3. **Automated parallel execution**: distribute and execute faster your experiments, thanks to their parallel execution offered by the Joblib and Dask backends.

In the next experiment, we demonstrate some of these capabilities with a coin tossing experiment:
we toss `N` times a biased coin `P("head")=.8`, repeating the experiment `K=100` times, and
measuring the average absolute error for a simple estimator of `P("head")`, the head ratio of the `N` outcomes.

{{include_code("mkdocs/tutorial/examples/track-run-002.py", title="Repeated toin cossing")}}

The variable parameter `N` results in four distinct configurations for the runs, which are executed in parallel. Parameters `P,K` are fixed and don't vary across runs. Further, there's only one step to execute, `toss_coins`, that adds `error` and `n` as tracked properties.

!!! Note
    Steps take as input the `run` they are executed on, and are expected to change its state. Steps can access these attributes during their evaluation:
    
    * `run.id_run`: UUID of the run, always available;
    * `run.kwargs`: Dictionary of fixed parameters;
    * `run.params`: Dictionary of variable parameters;
    * `run.fields`: Your tracking data! this is where you store results and metrics

!!! Important
    All attributes but `run.id_run` and `run.fields` are temporary and only these two attributes are handled
    by the JSON serialization. This simple strict rule will keep your experiments clean and easy to understand.
