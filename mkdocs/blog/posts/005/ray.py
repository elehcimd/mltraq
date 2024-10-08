from ray import get_runtime_context

from mltraq import Run, create_experiment, options


def get_worker_id(run: Run):
    run.fields.worker_id = get_runtime_context().get_worker_id()


with options().ctx(
    {
        "execution.backend": "ray",
        "execution.backend_params": {"logging_level": "FATAL", "include_dashboard": False, "num_cpus": 4},
    }
):
    e = create_experiment().add_runs(i=range(1000)).execute(get_worker_id)

print(e.runs.df().worker_id.value_counts())
