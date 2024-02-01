# Your project handover

You are tasked to manage the handover as the technical future owner.
This document will walk you through the organization of the code, with instructions for reproducing and accessing the results.

## How to use this guide

1. Start with a first quick pass, within 5 minutes. Scan the titles, the highlighted text, with a quick look to then tasks.

2. Have a look at what you might be missing to create a clean environment (see Reproducing the results). Ask for what you are missing, and move to the next step (no need to wait).

2. Read the General concepts section and do the exercise. This ensures that you can setup a basic, functioning environment, sufficient to at least execute a simple local experiment. This activity does not depend on assets of the project.

3. Proceed sequentially with the rest of the document, executing the proposed tasks: They ensure that you can reproduce and access the results.


## General concepts

<!-- general_concepts:begin -->

* **Experimentation**: The process of systematically changing and testing different input values in an algorithm to observe their impact on performance, behavior, or outcomes. Experiments can be defined and executed, with their outcomes and/or results persisted for later analysis.

* **Session**: A `session` object lets you define the connection to a database, load and add experiments. Sessions are binded to a database.

* **Experiment**: An `experiment` object manages a collection of `run` objects. Experiments can be created, persisted, loaded and executed. It implements the experimentation process. A `run` is an instantiation of the experiment with a configuration of input values. The execution of an `experiment` requires the execution of all its `runs`. Experiments are binded to a database and are unaware of sessions.

* **Run**: A `run` object is an instantiation of the experiment with a configuration of input values. The execution of a `run` is defined as the chained evaluation of `step` functions, whose sole parameter is the `run` object itself. Runs are unaware of databases, sessions, experiments or other runs, and are isolated from the rest of the experiment.

* **Step**: Step functions are a Python functions that take as sole input the `run` object, changing its internal state. There is no return value. Steps can access the configuration of the `run` in the attributes `run.config` and `run.params`, and can change the state of the `run` by modifying the attributes `run.vars`, `run.state` and `run.fields`.

!!! Tip
    An overview of the `run` state attributes can be found in [State management](./state.md), with a discussion of their semantics in the [Model of computation](./computation-model.md).

<!-- general_concepts:end -->

!!! Example "Exercise"

    * Install the package: `pip install mltraq --upgrade`
    * Run a simple experiment: [Define, execute and query an experiment with SQL](../index.md#example-define-execute-and-query-an-experiment-with-sql)

!!! Success "Congratulations!"
    You have familiarized with the key concepts and the logical representation of experiments.

## Code organization

1. The entry point of MLtraq is either `mltraq.create_session` or `mltraq.create_experiment`. 

    !!! Tip
        The parameters of these methods tell you where the state of the experiment(s) are persisted.
        By default, an in-memory SQLite database is used. You must specify a file location
        or a database connection string to ensure persistence. Make sure that this information,
        including access credentials, is present and available to you.

2. The runs are added to the experiment either explicitly or with the method `Experiment.add_runs` that generates the Cartesian product of the possible parameter values. For example, parameters `A=[1,2,3]` and `B=[4,5]` will result in six `Run` objecs added to the experiment with parameters `A=1 B=4, ..., A=3 B=5`. You might not want to have all possible combinations, and runs can be added explicitly to the `Experiment.runs` attribute. Variable parameters are set in `Run.params`. Locate calls to `Experiment.add_runs` or the direct access to the `Experiment.runs` attribute.
3. Variable parameters are set in the `run` objects upon creation. Experiments can have fixed parameters, whose value is constant across all runs. These constant parameters are set upon the execution of the experiment with the `Experiment.execute` method. Fixed parameters are set in `Run.config`.
4. The `step` functions are passed as a list to `Experiment.execute`, as a pipeline to execute. Locate calls to the `Experiment.execute` method to find out what are the steps. Steps are designed to access solely the `run` attributes to advance the state of the experiment. Read the [Model of computation](./computation-model.md) and [State management](./state.md) to understand the semantics of the `run` attributes and its internal state. A typical sequence of steps could be: `[load_dataset, train_predict, evaluate]`.

## Reproducing the results

1. Creating a clean environment

    Make sure that you have access to the code, data, computing and storage resources, and you can reproduce a clean environment where to run the code.

    !!! Example "Task"
    
        Make sure that you have access to the code and you can reproduce a clean environment where to run the code with this checklist:

        * Access to code repository or ZIP file with deliverables and accompanying documentation
        * access to required cloud resources if any, datasets, buckets, databases, other assets
        * Instructions to build a clean Python environment with the required dependencies
        * Instructions to access the MLtraq database (it might be a local SQLite file)

2. Experiments are executed by calling the `Experiment.execute` method. Let's start by reviewing the inputs of an experiment with no `step` functions to execute.

    !!! Example "Task"
        * Modify the experiment, leaving in only the `config` parameter. After executing it,
        you can access a random `run` and inspect its state, reviewing its fixed and variable parameters inspecting the dictionary returned by the [\__getstate__](https://docs.python.org/3/library/pickle.html#object.__getstate__) method of the standard library:
    
            ```py
            from mltraq import options
            experiment.execute([], config=...).runs.first().__getstate__()
            ```

    !!! Success "Congratulations!"
        You are able to generate and review the input parameters for the experiment.
        Inputs might include partial paths to datasets or other resources, which you can verify
        before even running the real experiment.

3. It's now time to run the complete experiment, adding back the original parameters passed to the `Experiment.execute` method.

    !!! Example "Task"

        Experiments might have a large number (hundreds of thousands) of runs or fewer, more expensive runs to evaluate. You might want to just run a single `run` first to make sure that things work properly at a smaller scale:

        ```py
        # Added code
        from mltraq import Runs
        experiment.runs = Runs(experiment.runs.first())

        # Original code
        experiment.execute(...)
        ```

        Once the execution completes, you can easily inspect the state of the `run` to verify the structure of the `run.state` and `run.fields` attributes.

    !!! Success "Congratulations!"
        You are able to run the simplest instantiation of the experiment, a single run. This means that
        datasets have been loaded correctly with no errors, the step functions have been found and evaluated,
        there are no dependency issues, and the experiment is well defined/reproducible.

4. Verify that the experiment state is persisted with the `Experiment.persist` method, this ensures that you can access the results at any time without running it again. You can now run the complete experiment to reproduce the results.

## Accessing the results

1. The results of an experiment (configurations, metadata, environment setups, source code, small datasets, arrays of true and predicted values, evaluation metrics, tags and text comments) can be persisted to database for later analysis. Storage of very large objects within the MLtraq managed persistence tables is discouraged. 

    !!! Tip
        The `step` functions can serialize/store them independently to disk or relying on third-party solutions for model versioning/registry.

2. You can access the results by accessing directly the [database and its tables](./storage.md) with SQL. Whenever possible, native database types such as INT, FLOAT and STRING are used.

    !!! Example "Task"
        Access the SQL database used for persistence and review the existing tables. You will find a table `"experiments"` with an index of all the present experiments and their data, as well as a set of `"experiment_"` tables for individual experiments, with each row representing a `run`.

    !!! Success "Congratulations!"
        You are able to reproduce the experiments and access the results with SQL.