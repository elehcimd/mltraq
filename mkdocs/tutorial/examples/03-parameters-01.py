from mltraq import create_experiment


def step_sum(run):
    run.fields.sum_ABX = run.params.A + run.params.B + run.config.X


experiment = create_experiment("example").add_runs(A=[1, 10], B=[100, 1000]).execute([step_sum], config={"X": 10000})

print("Runs:")
print(experiment.runs.df())
