import warnings

import mltraq
from dask.distributed import Client, LocalCluster


def test_dask():
    # Ignoring warnings on asyncio and numpy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        s = mltraq.create_session()

        def f1(run: mltraq.Run):
            run.fields.result1 = run.params.data + run.kwargs["inc"]

        def f2(run: mltraq.Run):
            run.fields.result2 = run.params.data + run.kwargs["inc"] * 2

        e = s.add_experiment("test")
        e.add_runs(data=[100, 200, 300])

        with LocalCluster(scheduler_port=8786, dashboard_address=":8787") as cluster:
            with Client(cluster):
                e.execute(steps=[f1, f2], kwargs={"inc": 5}, backend="dask")

        assert e.runs.df()["result1"].sort_values().tolist() == [105, 205, 305]
        assert e.runs.df()["result2"].sort_values().tolist() == [110, 210, 310]
