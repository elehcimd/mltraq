import mltraq

# Creating the session
session = mltraq.create_session()

# Defining a new experiment
experiment = session.add_experiment()

# [1] Adding a run explicitly
run = mltraq.Run()
run.fields.model_name = "baseline"
run.fields.accuracy = 0.65
experiment.runs.add(run)

# [2] Adding a run using context managers
with experiment.run() as run:
    run.fields.model_name = "random-forest"
    run.fields.accuracy = 0.83

# Displaying the tracked data for the runs
print(experiment.runs.df())
