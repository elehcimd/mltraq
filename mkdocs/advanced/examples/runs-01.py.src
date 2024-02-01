import mltraq


def step(run):
    run.fields.v = run.params.v


e1 = mltraq.create_experiment().add_runs(v=[1, 2]).execute(step)
e2 = mltraq.create_experiment().add_runs(v=[3, 4]).execute(step)
e1.runs.add(e2.runs)
print(e1.runs.df())
