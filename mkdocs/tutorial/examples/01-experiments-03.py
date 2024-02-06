from mltraq import Run, create_session

session = create_session()
experiment = session.create_experiment("example")


def step(run: Run):
    run.vars.a = 1
    run.state.b = 2
    run.fields.c = 3


experiment.add_run()
experiment.execute(step)
experiment.persist()

experiment = session.load("example")
run = experiment.runs.first()

print("run.vars", run.vars)
print("run.state", run.state)
print("run.fields", run.fields)
