import mltraq

session = mltraq.create_session()
experiment = session.create_experiment()

with experiment.run() as run:
    run.vars.a = 1
    run.state.b = 2
    run.fields.c = 3

print(experiment)
print(experiment.runs)

run = experiment.runs.first()

print("run.vars", run.vars)
print("run.state", run.state)
print("run.fields", run.fields)
