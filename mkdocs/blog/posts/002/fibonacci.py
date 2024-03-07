from mltraq import Run, create_experiment
from mltraq.steps.init_fields import init_fields


def step(run: Run):
    run.fields.F.append(run.fields.F[-1] + run.fields.F[-2])


print(create_experiment().execute(init_fields({"F": [0, 1]})).execute([step] * 8).runs.first().fields.F)
