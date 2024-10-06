import locale
import platform
import sys
from datetime import datetime
from types import ModuleType
from typing import Callable

from IPython.core.getipython import get_ipython

from mltraq.utils.bunch import Bunch
from mltraq.utils.sysmon import get_stats

catch_exceptions = (FileNotFoundError, AttributeError)


def is_tty() -> bool:
    """
    Returns true if code is running inside a terminal.
    """
    return sys.stdout.isatty()


def is_colab() -> bool:
    """
    Returns true if code is running inside a Google Colab.
    """

    return "google.colab" in sys.modules


def is_pyodide() -> bool:
    """
    Returns true if code is running inside Pyodide (JupyterLite, ...).
    """

    return "pyodide" in sys.modules


def is_notebook() -> bool:
    """
    Returns true if code is running inside a Notebook (IPython).
    """

    # Colab returns "Shell"
    # Jupyter Lab returns "ZMQInteractiveShell"
    # JypyterLite returns "Interpreter"
    return get_ipython() is not None and get_ipython().__class__.__name__ in [
        "ZMQInteractiveShell",
        "Shell",
        "Interpreter",
    ]


def try_callable(func: Callable) -> str:
    """
    Call the function. In case of exceptions or None, return an empty string.
    """

    try:
        value = func()
        if value is None:
            return ""
        else:
            return value
    except catch_exceptions:
        return ""


def try_module(module: ModuleType, method_name: str) -> str:
    """
    Call the function from a module. If missing, exceptions
    or None, return an empty string. If not callable, return
    it as a string.
    """
    try:
        value = getattr(module, method_name)
        if callable(value):
            return try_callable(value)
        else:
            return str(value)
    except catch_exceptions:
        return ""


def get_sysenv_info() -> Bunch:
    """
    Return a summary of the Python environment, including installed packages, Python, platform, system versions.
    """

    return Bunch.dict_to_bunch_deep(
        {
            "platform": {
                "machine": try_module(platform, "machine"),
                "processor": try_module(platform, "processor"),
                "mac_ver": try_module(platform, "mac_ver"),
                "libc_ver": try_module(platform, "libc_ver"),
                "system": try_module(platform, "system"),
                "release": try_module(platform, "release"),
                "version": try_module(platform, "version"),
                "java_ver": try_module(platform, "java_ver"),
                "win32_ver": try_module(platform, "win32_ver"),
                "win32_edition": try_module(platform, "win32_edition"),
                "linux_distribution": try_module(platform, "linux_distribution"),  # available in Python 3.7
                "freedesktop_os_release": try_module(platform, "freedesktop_os_release"),  # available in Python 3.10
                "python_implementation": try_module(platform, "python_implementation"),
                "python_version": try_module(platform, "python_version"),
            },
            "system": {
                "version": try_module(sys, "version"),
                "is_colab": is_colab(),
                "is_pyodide": is_pyodide(),
                "is_tty": is_tty(),
                "is_notebook": is_notebook(),
            },
            "locale": {"current": try_module(locale, "getlocale")},
            "time": {"current": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")},
            "sysmon_stats": get_stats(interval=0.1),
        }
    )
