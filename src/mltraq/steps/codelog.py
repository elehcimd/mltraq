import functools
import logging
from functools import partial
from os.path import relpath

from joblib.func_inspect import get_func_code

from mltraq import Run
from mltraq.opts import options
from mltraq.run import StepsType, normalize_steps
from mltraq.utils.bunch import Bunch

log = logging.getLogger(__name__)


def get_func_code_ext(func, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    if isinstance(func, functools.partial):
        return get_func_code_ext(func.func, args=args + list(func.args), kwargs=kwargs | func.keywords)
    else:
        code, pathname, pathname_lineno = get_func_code(func)
        if code.isnumeric():
            # joblib failed to locate the code, and the contents of code is the hash of the object itself.
            # This can happen if the code is sourced and executed with `exec`, as in "utils/build_docs.py".
            # In this case, consider the code as not available.
            log.warning(f"Code for function {func.__name__} not found")
            code = "NA"
        return func.__name__, code, relpath(pathname), pathname_lineno, args, kwargs


def codelog_step(run: Run, steps: StepsType = None):
    """
    Track code of `steps` as a `code` field of the run.
    """

    steps = normalize_steps(steps)

    field_name = options().get("codelog.field_name")

    if field_name not in run.fields:
        run.fields[field_name] = []
    for step in steps:
        name, code, pathname, pathname_lineno, args, kwargs = get_func_code_ext(step)
        run.fields[field_name].append(
            Bunch(
                name=name,
                code=code,
                pathname=pathname,
                pathname_lineno=pathname_lineno,
                args=str(args),
                kwargs=str(kwargs),
            )
        )


def codelog(steps: StepsType = None) -> callable:
    return partial(codelog_step, steps=steps)
