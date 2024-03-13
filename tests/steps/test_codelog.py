from functools import partial

from mltraq import Run, create_experiment
from mltraq.opts import options


def test_codelog_func():
    """
    Test: We can track the code of steps (functions).
    """

    experiment = create_experiment()

    def step12(run: Run):
        run.fields.a = 1 + 2

    # disabling loky_chdir, which adds an implicit step.
    with options().ctx({"execution.loky_chdir": False, "codelog.disable": False}):
        experiment.execute(step12)

    codelog = experiment.runs.first().fields.codelog

    # There is a single step
    assert len(codelog) == 1
    assert codelog[0]["name"] == "step12"
    assert "def step12(run: Run):" in codelog[0]["code"]
    assert "run.fields.a = 1 + 2" in codelog[0]["code"]

    # All fields present
    assert "name" in codelog[0]
    assert "code" in codelog[0]
    assert "pathname" in codelog[0]
    assert "pathname_lineno" in codelog[0]
    assert "args" in codelog[0]
    assert "kwargs" in codelog[0]


def test_codelog_partial():
    """
    Test: We can track the code of steps (partial callable functions).
    """

    experiment = create_experiment()

    def step123(run: Run, x=123):
        run.fields.a = 1 + 2

    # disabling loky_chdir, which adds an implicit step.
    with options().ctx({"execution.loky_chdir": False, "codelog.disable": False}):
        experiment.execute(partial(step123, x=123))

    codelog = experiment.runs.first().fields.codelog
    print(codelog)

    # There is a single step
    assert len(codelog) == 1
    assert codelog[0]["name"] == "step123"
    assert codelog[0]["args"] == "[]"
    assert codelog[0]["kwargs"] == "{'x': 123}"
    assert "def step123(run: Run, x=123):" in codelog[0]["code"]
    assert "run.fields.a = 1 + 2" in codelog[0]["code"]
