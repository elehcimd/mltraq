import mltraq
from mltraq.extras.step_code import track_step_code


def test_track_source_code():
    def f(run: mltraq.Run):
        track_step_code(run, test_track_source_code)

    s = mltraq.create_session()
    e = s.add_experiment("test")
    e.execute(steps=f, n_jobs=1)

    print(e.runs.df())

    step_code = e.runs.df()["steps_code"].iloc[0]["test_track_source_code"]
    assert step_code["func_code"].startswith("def test_track_source_code():")
    assert step_code["source_file"].endswith("test_step_code.py")
