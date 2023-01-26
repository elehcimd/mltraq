import mltraq
import numpy as np


def toss_coins(run: mltraq.Run):
    def estimate_p_head():
        return np.mean([np.random.uniform() < run.kwargs.P for _ in range(run.params.N)])

    errors = [np.abs(estimate_p_head() - run.kwargs.P) for _ in range(run.kwargs.K)]
    run.fields.error = np.mean(errors)
    run.fields.n = run.params.N


session = mltraq.create_session()
experiment = session.add_experiment()
experiment.add_runs(N=[1, 25, 50, 100])
experiment.execute(kwargs={"P": 0.8, "K": 100}, steps=toss_coins)
print(experiment.runs.df().sort_values(by="n"))
