import inspect
import logging
import sys
import time
from typing import Callable

log = logging.getLogger(__name__)


def timeit(f: Callable) -> Callable:
    """Decorator to measure the call execution time.

    Args:
        f (Callable): Function to execute

    Returns:
        Callable: Function with decorator.
    """

    def timed(*args, **kw):
        ts = time.perf_counter()
        result = f(*args, **kw)
        te = time.perf_counter()
        log.info(f"Elapsed time @{f.__name__}: {(te - ts):.2f}s")
        return result

    return timed


def fatal(*args, **kwargs):
    """Handle fatal situations, logging them and handling over the execution
    to IgnoredChainedCallLogger to log chained operations.

    Returns:
        IgnoredChainedCallLogger: Logger of chained opeartions.
    """

    log.error(*args, **kwargs)
    raise Exception("Execution interrupted")


def compact_exception_message(e):
    """Construct string representing , in a compact way, the traceback, useful to handle exceptions.

    Args:
        e (_type_): Raised exception.

    Returns:
        _type_: _description_
    """

    exc_type, exc_value, exc_traceback = sys.exc_info()
    frame = inspect.trace()[-1]

    details = {
        "file": exc_traceback.tb_frame.f_code.co_filename,
        "lineno": exc_traceback.tb_lineno,
        "type": exc_type.__name__,
        "message": str(exc_value),
        "trace": f'{frame.filename}:{frame.lineno}::{frame.function} "{frame.code_context[frame.index].strip()}"',
    }

    return f'{details["type"]} at {details["trace"]}: {details["message"]}'
