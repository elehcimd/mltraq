
import mltraq
import numpy as np

# Create a new session, bound to an in-memory SQLite database by default.
session = mltraq.create_session()
print(session)
print("--\n")

# Create a new experiment "example" with two runs and grid parameter "X".
experiment = session.create_experiment("example").add_runs(X=[1, 2])
print(experiment)
print("--\n")


def fibonacci(n):
    """
    Return n-th value in Fibonacci series.
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


# Define a step function to execute on the runs.
def step(run):
    """
    This step tracks:
     1. the number of times we call it in `N`
     2. A sequential log of Fibonacci numbers generated at each execution in `sequence`
     3. A constant scalar in `score`
     4. A constant Numpy array in `predictions`
    """

    # Dictionary `run.fields` can use it to track a rich set of object types, including:
    # dict, list, set, tuple, int, float, str, and Numpy arrays,
    # Pandas series/frames, PyArrow tables.
    run.fields.X = run.params.X
    run.fields.N = run.fields.get("N", 0)
    run.fields.N += 1
    run.fields.sequence = run.fields.get("sequence", mltraq.Sequence())
    run.fields.sequence.append(n=run.fields.N, fibonacci=fibonacci(run.fields.N))
    run.fields.score = 1
    run.fields.predictions = np.array([1, 2, 3])


# Execute the experiment twice on the two runs, running each time the step function 3 times.
# Functions are chained together, creating a pipeline to execute on each run.
experiment.execute([step] * 3, args_field="args")
experiment.execute([step] * 3, args_field="args")

# Persist the experiment to database.
experiment.persist()

# Reload the experiment from database.
experiment = session.load("example")

# Execute the step one more time, reaching 7 evaluations per run.
experiment.execute([step], args_field="args")

# Print the tracked sequence in one of the executed runs.
print("Contents of sequence in a single run:")
print(experiment.runs.first().fields.sequence.df()[["n", "fibonacci"]])
print("--\n")

print("Contents of X, N and score on all runs:")
print(experiment.runs.df()[["X", "N", "score"]])
