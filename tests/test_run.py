import mltraq


def test_run():
    run = mltraq.Run()

    assert isinstance(run.id_run, str)


def test_run_fields():
    run = mltraq.Run()

    run.fields.a = 123
    assert len(run.df()) == 1
    assert run.df()["a"].iloc[0] == 123


def test_run_add():
    s = mltraq.create_session()

    def f(run: mltraq.Run):
        run.fields.data = run.params.data

    e = s.add_experiment("test")
    e.add_runs(data=[100, 200, 300])

    e2 = s.add_experiment("test2")
    e2.runs.add(e.runs)
    e2.runs.add(mltraq.Run(params={"data": 400}))

    e2.execute(steps=f)

    assert set(e2.runs.df().data.tolist()) == {100, 200, 300, 400}
