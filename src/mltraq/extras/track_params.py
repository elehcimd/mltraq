from mltraq.run import Run


def track_params(run: Run):
    """Step function that tracks the parameters.

    Args:
        run (Run): Run to apply the step to
    """

    run.fields.params = run.params


def track_param(name):
    """Step function that tracks one parameter.

    Args:
        run (Run): Run to apply the step to
    """

    def func(run: Run):
        run.fields[f"param_{name}"] = run.params[name]

    return func
