import inspect
import sys
import traceback

from mltraq.opts import options


class ExceptionWithMessage(Exception):
    """
    Exception with a .message attribute
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidInput(ExceptionWithMessage):
    pass


def exception_message() -> str:
    """
    Option "execution.exceptions.compact_message" controls if
    either a compact or a complete stack trace is reported.
    """

    if options.get("execution.exceptions.compact_message"):
        return compact_exception_message()
    else:
        return complete_exception_message()


def complete_exception_message() -> str:
    """
    Returns a string with the complete stack trace report.
    """
    return traceback.format_exc()


def compact_exception_message() -> str:
    """
    Construct a compact string representing the position anc code
    that caused the exception.
    """

    exc_type, exc_value, exc_traceback = sys.exc_info()
    frame = inspect.trace()[-1]

    code = (
        "<unkown>"
        if (not frame.index or not frame.code_context or len(frame.code_context) == 0)
        else frame.code_context[frame.index].strip()
    )

    details = {
        "file": "<unknown>" if not exc_traceback else exc_traceback.tb_frame.f_code.co_filename,
        "lineno": "<unknown>" if not exc_traceback else exc_traceback.tb_lineno,
        "type": "<unkown>" if not exc_type else exc_type.__name__,
        "message": str(exc_value),
        "trace": f'{frame.filename}:{frame.lineno}::{frame.function} "{code}"',
    }

    return f'{details["type"]} at {details["trace"]}: {details["message"]}'
