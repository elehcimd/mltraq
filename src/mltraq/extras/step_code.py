import joblib
from mltraq import Run


def track_step_code(run: Run, func):
    """Track source code of steps or other functions

    Args:
        run (Run): run to track to
        func (_type_): funuction to track
    """

    if "steps_code" not in run.fields:
        run.fields.steps_code = {}
    func_code, source_file, _ = joblib.func_inspect.get_func_code(func)
    run.fields.steps_code[func.__name__] = {"func_code": func_code, "source_file": source_file}
