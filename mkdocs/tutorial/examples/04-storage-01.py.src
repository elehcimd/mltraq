import numpy as np
from mltraq import create_session

session = create_session()
experiment = session.create_experiment("example")

# Set a property in the `fields` dictionary at experiment scope
experiment.fields.a = 10

# Adding first run
with experiment.run() as run:
    # Set properties in the `fields` dictionary at run scope
    run.fields.b = 20
    run.fields.c = np.array([1, 2, 3])

# Adding second run
with experiment.run() as run:
    run.fields.b = 30

# Persist the experiment to database
experiment.persist()

# Load the experiment from database
experiment = session.load_experiment("example")
print("Experiment:")
print(experiment.df())
print("\n--")

print("SQL query:")
print(session.db.query("SELECT id_run, b FROM experiment_example"))
print("\n--")


print("NumPy array in first run:")
print(experiment.runs.first().fields.c)
print("\n--")
