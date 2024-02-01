from mltraq import create_experiment

# Create a new experimend, binded to an in-memory SQLite database by default.
experiment = create_experiment("example")

# Add a run and work directly on it.
with experiment.run() as run:
    run.fields.tracked = 5

# Persist experiment to database.
experiment.persist()

# Query experiment with SQL.
print(experiment.db.query("SELECT * FROM experiment_example"))
