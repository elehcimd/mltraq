import mltraq

# Connect to a MLTRAQ session and create an experiment.
session = mltraq.create_session("sqlite:///:memory:")
experiment = session.add_experiment("honey")

# Instantiate a new run and track metrics.
run = experiment.runs.next()
run["accuracy"] = 0.87

# Instantiate a new run using the context manager for cleaner code.
with experiment.run() as run:
    run["accuracy"] = 0.95

# Persist experiment to database and query it with SQL.
experiment.persist()
print(session.query("SELECT id_run, accuracy FROM e_honey"))
