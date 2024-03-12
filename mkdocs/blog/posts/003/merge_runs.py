from mltraq import create_experiment
from mltraq.steps.init_fields import init_fields

# First experiment
e1 = create_experiment().execute(init_fields(a=1, c=10))

# Second experiment
e2 = create_experiment().execute(init_fields(b=2, c=20))

# Merge of experiments `e1` and `e2`
e12 = create_experiment().merge_runs(e1.runs | e2.runs)

print("Experiment runs:")
print(e12.runs)
print("--\n")

print("Run fields:")
print(e12.runs.df())
