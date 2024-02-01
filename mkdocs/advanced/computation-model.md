# Model of computation

A model of computation is a model which describes how an output of a function is computed given an input. In MLtraq, an experiment is a collection of `runs` that are evaluated independently by following the [state monad](https://dev.to/hamzzak/mastering-monad-design-patterns-simplify-your-python-code-and-boost-efficiency-kal) design pattern:

 > "The State monad wraps computations in the context of reading and modifying a global state object. This context chains two operations together in an intuitive way. First, it determines what the state should be after the first operation. Then, it resolves the second operation with the new state."

The `run` is our **state object**, the input dictionaries `run.config` and `run.params` represent the initial **state**, and the `step` functions are the **chained operations**. E.g., the `run` after applying `step` functions `f1`, `f2` and `f3` in this order, is equivalent to `run = f3(f2(f1(run)))`.


!!! Info
     This model encourages two important design patterns:
     
     *  **Composability**: Maximize reuse of existing code, design clean interfaces, separate implementation from expected outcome
     * **Encapsulation**: Limiting of direct access to the internal state via the state dictionaries, easying maintainability and testing

## State

The `step` functions can use the state dictionaries `run.vars`, `run.state`, and `run.fields` to communicate and evolve the computation with varying power (and cost).
In principle, one should prefer the least powerful yet sufficient semantics that get the job done.

### Attribute `run.vars`

It is designed to hold temporary data and is emptied once the execution of the `steps` is complete.

!!! Info "Motivation and details"
    With the parallel/distributed computation of `runs`, we want to avoid the unnecessary picking, transfer, and unpickling of objects. In some cases, objects cannot be pickled, resulting in errors and headaches.
    E.g., a large model of `20GB` can be a good fit for `run.vars` if we care only about evaluation metrics.
    In local notebooks, we can help the garbage collector by tidying up the state of `runs` as soon as possible.

### Attribute `run.state`

It can be accessed once the `run` completes its execution. It is not persisted to database.
   
!!! Info "Motivation and details"
    It enables the inspection of the internal state of experiments for debugging and analysis after their 
    execution. It can hold only pickable objects in case of parallel execution (parallel execution can be disabled with `n_jobs=1` as per joblib.Parallel documentation). In case of unsafe pickled objects to database,
    its contents are persisted.

### Attribute `run.fields`
It works as `run.state` and its values are also stored in the database.

!!! Info "Motivation and details"
    It is the most robust, portable way to store the state of the experiment. With safe serialization, 
    using native database SQL types whenever possible. Many but not all types are supported, see
    [storage](./storage.md) for details.        

### Handling of parameters

Runs can access parameters in `run.config` (fixed, same for all runs) and `run.params` (not necessarily holding the same value for all runs). By default, these attributes are cleared after execution.

In some situations, you might want to retain access to these parameters. You can transparently request to persist them in the state. A designated `run.fields` attribute can be set using `Experiment.execute(..., args_field="args")`. If `args_field` is set (E.g., to `"args"`), their value remains accessible at any time. Under the hood, it is persisted/loaded from the dictionary field `run.fields.args`.
The examples on [Tracking](../howto/01-tracking.md) demonstrate the usage of `args_field` to resume the computation of an experiment, including access to the parameters, after reloading it from database.

## Handling of exceptions

If an exception is raised by a `step` function in a `run`, the attribute `run.exception` is set and the evaluation is interrupted, reverting the `run` (and all the other `runs` of the experiment) to its initial state, triggering an exception `RunException`. In case of parallel/distributed execution, this mechanism ensures complete errors transparency and reporting to the driver node.

You can control the verbosity of the description of the reported exception using the [option](./options.md) `"execution.exceptions.compact_message"`.

## Experiments as collections of aligned and evolving runs

The management of the execution of `runs` at the higher abstraction level of `experiments` ensure that all the `runs` within an `experiment` have their inputs equally structured and the evaluation of the `steps` is aligned, with equal evaluation progress and consistent states.

### Example: Merging runs

Experiments are collections of runs stored in `mltraq.Runs` objects that extend `dict`, with run IDs as keys and `mltraq.Run` objects as values. In this example, two experiments are combined by merging their runs:

{{include_code("mkdocs/advanced/examples/runs-01.py", title="Merging runs of two experiments")}}


## Handling of options

The value of [`mltraq.options`](./options.md) is transparently propagated to the context of the `step` functions, and can be accessed at any time in read-only mode. The options mechanism is useful to pass project configuration constants that are not necessarily mapped in `run.config`. For example, a `step` might call a `load_dataset` function that can be cached and the behaviour could be managed using a dedicated option. The option prefix `"app."` is reserved for the application, is empty by default, and can be used by the application to customize the behaviour of `steps`.
