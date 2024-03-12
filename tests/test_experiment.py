from random import uniform

import mltraq
import numpy as np
import pytest
from mltraq import Run, create_experiment, options
from mltraq.experiment import ExperimentAlreadyExists, PickleNotFoundException
from mltraq.run import RunException
from mltraq.runs import RunsException
from mltraq.steps.init_fields import init_fields
from mltraq.utils.exceptions import InvalidInput


def test_unpickle():
    """
    Test: We can create, pickle and unpickle an Experiment object.
    `fields` and `state` are both accessible.
    """
    session = mltraq.create_session()
    experiment = session.create_experiment(name="test")

    with experiment.run() as run:
        run.fields.a = 100
        run.state.b = 200

    experiment.persist(store_unsafe_pickle=True)
    experiment = session.load(name="test", unsafe_pickle=True)

    unpickled_run = experiment.runs.first()
    assert unpickled_run.fields.a == 100
    assert unpickled_run.state.b == 200


def test_load():
    """
    Test: We can create, persist and load an Experiment object (not pickling it.)
    Only `fields` is accessible.
    """
    session = mltraq.create_session()
    experiment = session.create_experiment(name="test")

    with experiment.run() as run:
        run.fields.a = 100
        run.state.b = 200

    experiment.persist()
    experiment = session.load(name="test")
    loaded_run = experiment.runs.first()

    assert loaded_run.fields.a == 100
    assert loaded_run.state == {}


def test_experiment_Runs():
    """
    Test: We can add three runs with parameter `a`.
    """
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(a=[1, 2, 3])
    assert len(e.runs) == 3
    assert e.runs.first().params.a <= 3


def test_experiment_Run():
    """
    Test: We can add a run with a parameter `a`, and get its value.
    """
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_run(a=123)
    assert e.runs.first().params.a == 123


def test_experiment_three_runs():
    """
    Test: We can execute a simple experiment with three runs and a parameter.
    """

    def f(run: mltraq.Run):
        run.fields.a = 1

    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(a=[1, 2, 3])
    e.execute(f)
    assert len(e.runs.df()) == 3
    assert e.runs.first().fields.a <= 3


def test_experiment_empty():
    """
    Test: An empty experiment (no runs) cannot be executed.
    """
    s = mltraq.create_session()
    e = s.create_experiment("test")

    with pytest.raises(RunsException):
        e.execute()


def test_experiment_empty_with_field_attribute_persist():
    """
    Test: We can persist an experiment with no runs, with a field attribute.
    """
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.fields.a = 100
    e.persist()
    e = s.load("test")
    assert e.fields.a == 100


def test_experiment_simple():
    """
    Test: We can define a simple experiment with two step functions, execute it,
    and retrieve the results from a Pandas dataframe.
    """
    s = mltraq.create_session()

    def f1(run: mltraq.Run):
        run.fields.result1 = run.params.data + run.config["inc"]

    def f2(run: mltraq.Run):
        run.fields.result2 = run.params.data + run.config["inc"] * 2

    e = s.create_experiment("test")
    e.add_runs(data=[100, 200, 300])
    e.execute(steps=[f1, f2], config={"inc": 5})

    assert e.runs.df()["result1"].sort_values().tolist() == [105, 205, 305]
    assert e.runs.df()["result2"].sort_values().tolist() == [110, 210, 310]


def test_experiment_biased_coin():
    """
    Test: We can define an experiment with three runs, a fixed parameter P, a variable parameter N, and execute it.
    """

    def toss_coin(run: mltraq.Run):
        run.fields.P = run.params.P
        run.fields.N = run.config.N

        for i in range(run.config.N):
            if i == 0:
                run.fields.p_head = 0
            elif i == run.config.N - 1:
                run.fields.p_head /= run.config.N
            else:
                run.fields.p_head += 1 if np.random.random() < run.params.P else 0

    s = mltraq.create_session()
    e = s.create_experiment("biased_coin")
    e.add_runs(P=[0.4, 0.5, 0.6])
    e.execute(config={"N": 100}, steps=toss_coin)
    assert len(e.runs.df()) == 3


def test_experiment_nested():
    """
    Test: We can use nested fields in step functions, with varying flattening level.
    """
    s = mltraq.create_session()

    def f(run: mltraq.Run):
        run.fields.x = {"a": 1, "b": 2}
        run.fields.y = {"a": {"b": 1}}

    e = s.create_experiment("test")
    e.add_runs(data=[100])
    e.execute(steps=f)

    # level 0 (default)
    assert e.runs.df().columns.tolist() == ["id_run", "x", "y"]
    assert e.runs.df().iloc[0].y["a"]["b"] == 1

    # level 2
    assert e.runs.df(max_level=2).columns.tolist() == ["id_run", "x.a", "x.b", "y.a.b"]


def test_experiment_many():
    """
    Test: We can define and run an experiment with 2000 runs and 2 step functions,
    persisting it and querying it with SQL.
    """
    s = mltraq.create_session()

    def f1(run: mltraq.Run):
        run.fields.params = run.params
        run.fields.result1 = run.params.data + run.config["inc"]

    def f2(run: mltraq.Run):
        run.fields.result2 = run.params.data + run.config["inc"] * 2

    e = s.create_experiment("test")
    e.add_runs(data=range(2001))
    e.execute(steps=[f1, f2], config={"inc": 5})
    e.persist()

    prefix = options().get("database.experiment_tableprefix")
    assert s.db.query(f"select count(*) as count_rows from {prefix}test").count_rows.iloc[0] == 2001  # noqa


def test_experiment_replace():
    """
    Test:
    """
    s = mltraq.create_session()

    def f(run: mltraq.Run):
        run.fields.a = run.config.a

    e = s.create_experiment("test")
    e.add_runs(data=range(10))

    e.execute(steps=f, config={"a": 123}).persist()
    assert s.load("test").runs.first().fields.a == 123

    # By default, we cannot overwrite a persisted experiment.
    with pytest.raises(ExperimentAlreadyExists):
        e.persist()

    # We can replace it by passing if_exists.
    # We are setting a new config, so setting `args_field` to False to prevent
    # an attempt to overwrite `run.fields.args`, which would fail and trigger an exception.
    e.execute(steps=f, config={"a": 124}).persist(if_exists="replace")
    assert s.load("test").runs.first().fields.a == 124


def test_experiment_load_experimentid():
    """
    Test: We can load an experiment using its experiment ID.
    """
    session = mltraq.create_session()
    experiment = session.create_experiment("test")
    experiment.persist()
    id_experiment = experiment.id_experiment
    experiment = session.load(id_experiment=id_experiment)
    assert experiment.id_experiment == id_experiment
    assert experiment.name == "test"


def test_experiment_overwrite():
    """
    Test: Verify that an experiment can be overwritten.
    """
    session = mltraq.create_session()
    session.create_experiment("experiment").persist()
    with pytest.raises(ExperimentAlreadyExists):
        # By default, if the expeirment already exists, it's not overwritten.
        session.create_experiment(
            "experiment",
        ).persist()
    # We can overwrite it with "replace".
    session.create_experiment(
        "experiment",
    ).persist(if_exists="replace")


def test_copy():
    """
    Test: We can create a deep copy of an experiment.
    """
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(data=range(10))

    e2 = e.copy_to()
    assert len(e.runs) == 10
    assert len(e2.runs) == 10
    assert e.runs.first() != e2.runs.first()


def test_experiment_exection_no_runs():
    """
    Test that the execution fails if no steps have been defined.
    """
    s = mltraq.create_session()

    def f(run: Run):
        run.fields.a = 123

    e = s.create_experiment(name="test")

    with pytest.raises(InvalidInput):
        # No parameters, fails
        e.add_runs()

    with pytest.raises(RunsException):
        # No steps, fails
        e.execute()

    # Execute expriment, ans make sure that there is exactly one run.
    # No runs defined, default one is created.
    e.execute(steps=f)

    assert len(e.runs) == 1


def test_experiment_run_context():
    """
    Test: We can use the run context to experiment with runs, without
    explicitly using step functions.
    """
    s = mltraq.create_session()

    e = s.create_experiment(name="test")

    with e.run() as run:
        run.fields.a = 123

    # Make sure that there is one run.
    assert len(e.runs) == 1


def test_experiment_run_explicit():
    """
    Test: We can create a run, modify its state, and link it to an experiment.
    """
    s = mltraq.create_session()

    e = s.create_experiment(name="test")

    run = mltraq.Run()
    run.fields.a = 123

    e.runs.add(run)

    # Make sure that there is one run.
    assert len(e.runs) == 1


def test_direct_create_experiment_next_run():
    """
    Test: We can directly create an experiment, without passing
    by the explicit creation of a session.
    We can create new runs by asking for the "next" fresh one.
    In this experiment, we combine two methods to create runs.
    """
    # Connect to the MLtraq session and create an experiment.
    e = mltraq.create_experiment("test")

    # Instantiate a new run and track metrics.
    run = e.runs.next()
    run.fields.accuracy = 0.87

    # Instantiate a new run using the context manager for cleaner code.
    with e.run() as run:
        run.fields.accuracy = 0.95

    # Make sure that there are two runs.
    assert len(e.runs) == 2


def test_experiment_exception():
    """
    Excetions inside steps are reported as RunException exceptions.
    """

    def step(run: mltraq.Run):
        if run.params.data == 300:
            # Trigger exception only in one of the runs.
            raise Exception("error 123")

    s = mltraq.create_session()
    e = s.create_experiment("test")

    e.add_runs(data=[100, 200, 300])

    with pytest.raises(RunException):
        e.execute(step)


def test_experiment_fields_on_exception():
    """
    Test: In case of an exception, the state of runs is retained as before the execution causing it.
    """

    def step_ok(run: mltraq.Run):
        run.fields.a = 1

    def step_ex(run: mltraq.Run):
        if run.params.value == 100:
            # Make only 1 of 3 runs fail, not defining field attribute `a`
            raise Exception("error 123")
        run.fields.b = 2

    # Define experiment
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(data=[100, 200, 300])

    # This execution runs smoothly, no errors.
    e.execute(step_ok)

    with pytest.raises(RunException):
        # this one fails, as there's one exception.
        e.execute(step_ex)

    # All runs have the same fields: 'a'
    for run in e.runs.values():
        assert run.fields == {"a": 1}


def test_ExperimentNotFoundException():
    """
    Test: In case of unpickling an unexisting experiment, a PickleNotFoundException exception is raised.
    """
    session = mltraq.create_session()
    experiment = session.create_experiment(name="test")
    experiment.add_runs(A=[1, 2, 3])
    experiment.persist(store_unsafe_pickle=False)

    with pytest.raises(PickleNotFoundException):
        experiment = session.load(name="test", unsafe_pickle=True)


def test_experiment_runs_reload_execution():
    """
    Test: We can reload an experiment and run more steps,
    reloading config/params via `args_field`.
    """

    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(A=[10, 100, 1000])

    def step_inc(run: Run):
        if "A" in run.fields:
            run.fields.A += run.params.A
        else:
            run.fields.A = run.params.A

    e.execute(step_inc, args_field="args")
    print(e.runs.df())
    assert e.runs.df()["A"].max() == 1000

    e.persist()
    e = s.load("test")
    e.execute(step_inc, args_field="args")
    assert e.runs.df()["A"].max() == 2000


def test_experiment_parallel():
    """
    Test: We can execute 100 runs in parallel, aggregating their output.
    """

    def step(run: Run):
        run.fields.v = uniform(0, 1)  # noqa

    v_mean = create_experiment().add_runs(i=range(100)).execute(step).runs.df().v.mean()
    # Without enough runs, it might be rather off from .5
    assert v_mean > 0


def test_persist_experiment_no_runs():
    """
    Test: If we persist an experiment with no runs, a default one is added.
    """
    experiment = create_experiment()

    assert len(experiment.runs) == 0

    experiment.persist()

    # If executed, we have one run.
    assert len(experiment.runs) == 1

    # If reloaded, we have one run.
    assert len(experiment.reload().runs) == 1


def test_execute_experiment_no_runs():
    """
    Test: If we execute an experiment with no runs, a default one is added.
    """
    experiment = create_experiment()

    assert len(experiment.runs) == 0

    experiment.execute(init_fields(a=1))

    # If executed, we have one run.
    assert len(experiment.runs) == 1


def test_runs_or():
    """
    Test: We can add runs to an experiment from multiple experiments with "|" and "|="
    """
    e1 = create_experiment().execute(init_fields(a=1))
    e2 = create_experiment().execute(init_fields(b=2))

    e = create_experiment()
    e.runs = e1.runs | e2.runs
    assert len(e.runs) == 2

    e = create_experiment()
    e.runs = e1.runs
    e.runs |= e2.runs
    assert len(e.runs) == 2

    e = create_experiment()
    e.merge_runs(e1.runs | e2.runs)
    assert len(e.runs) == 2
