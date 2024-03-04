import inspect
import logging
import signal
import sys
import traceback
from os.path import basename
from types import FrameType
from typing import Any, TypeVar

from mltraq.opts import options

log = logging.getLogger(__name__)


T = TypeVar("T")


class ExceptionWithMessage(Exception):
    """
    Exception with a .message attribute
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class FatalError(ExceptionWithMessage):
    pass


class TypeValidationError(ExceptionWithMessage):
    pass


class InvalidRequestError(ExceptionWithMessage):
    pass


class InvalidInput(ExceptionWithMessage):
    pass


def exception_message() -> str:
    """
    Option "execution.exceptions.compact_message" controls if
    either a compact or a complete stack trace is reported.
    """

    if options().get("execution.exceptions.compact_message"):
        return compact_exception_message()
    else:
        return complete_exception_message()


def complete_exception_message() -> str:
    """
    Returns a string with the complete stack trace report.
    """
    return traceback.format_exc()


def codepos(self=None):
    frame = inspect.getframeinfo(inspect.currentframe().f_back)
    if self:
        func = f"{self.__class__.__name__}.{frame.function}"
    else:
        func = frame.function
    return f"[{basename(frame.filename)}:{frame.lineno}|{func}]"


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


def validate_type(value: object, expected_type: T) -> Any:
    """
    Validate the type of `value` to be `expected_type`, if provided.
    Otherwise, return `value` with no checks.
    TODO: avoid use of Any.
    """

    if type(value) == expected_type:
        return value
    else:
        raise TypeValidationError(f"Expected type '{expected_type}' but found '{type(value)}'")


class ServiceExit(Exception):
    pass


def service_shutdown(sig: int, frame: FrameType | None = None):
    # Print a new line, to not break the logging line format with a "^C"
    print("")
    log.info(f"Received {signal.Signals(sig).name} signal, shutting down ...")
    raise ServiceExit
