import mltraq

session = mltraq.create_session()
experiment = session.add_experiment(name="test")

with experiment.run() as run:
    run.locals.temporary = 123

experiment.persist(store_pickle=True)
experiment = session.load(name="test", pickle=True)

print(experiment.runs.first().locals.temporary)
