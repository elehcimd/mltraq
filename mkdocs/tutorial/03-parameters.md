# Parametrized experiments

## Fixed and variable parameters

Parametrized experiments allow you to control and differentiate the behaviour of runs:

* Parameter grids are grids of parameters with a discrete number of values for each, can be set on `runs` using `Experiment.add_runs(A=[1,2,...], B=...)`
and are accessible within the `run` at `run.params`.

* Configuration parameters are fixed for all `runs`, can be accessed at `run.config` and are set by
passing `config={A=1, B=2, ...}` to `Experiment.execute`. The value is the same for all `runs`.

In the next example:

1. We define a fixed configuration parameter `X`. We use a parameter grid, similarly to [`sklearn.model_selection.ParameterGrid`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterGrid.html#sklearn.model_selection.ParameterGrid), to define `run` parameters `A` and `B`.

2. We execute the step function `step_sum`, summing up the value of `A`, `B` and `X`.

3. We persist and query the experiment as a Pandas dataframe.


{{include_code("mkdocs/tutorial/examples/03-parameters-01.py", title="Creating an experiment")}}


!!! Tip
    The attributes `run.config` and `run.params` are **not** persisted to database by default.
    You can request its transparent persistence with `Experiment.execute(...., args_field="args")`,
    which will persist/reload config/params to/from `run.fields.args`.


!!! Success "Congratulations!"
    You know how to define parameter grids and explore the impact of varying parameters on evaluation metrics.
