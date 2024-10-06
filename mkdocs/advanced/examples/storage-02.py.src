import numpy as np

from mltraq import create_experiment

experiment = create_experiment("example")

with experiment.run() as run:
    run.fields.result = np.array([0.1, 0.2, 0.3])

experiment = experiment.persist().reload()
value = experiment.runs.first().fields.result
print("Type", type(value))
print("Value", value)
