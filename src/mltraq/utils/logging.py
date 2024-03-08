import logging
import sys
from contextlib import contextmanager

from mltraq.opts import options

log = logging.getLogger(__name__)


def init_logging(level_name: str | None = None, log_format: str | None = None):
    """
    Initialize the logging to stdout, setting it to `level_name` or the level specified in the options.
    """
    level_name = options().default_if_null(level_name, "cli.logging.level")
    log_format = options().default_if_null(log_format, "cli.logging.format")
    basic_config_params = {"stream": sys.stdout, "datefmt": "%Y-%m-%d %H:%M:%S"}
    if log_format:
        basic_config_params["format"] = log_format
    logging.basicConfig(**basic_config_params)
    logging.getLogger().setLevel(logging.getLevelName(level_name))
    log.debug(f"Logging level set to {level_name}")


@contextmanager
def logging_ctx(level_name: str | None = None, log_format: str | None = None):
    """
    Temporarily configure the logging `level_name` and `log_format`.
    """

    old_level_name = logging.getLevelName(logging.getLogger().level)

    try:
        # If we didn't set a logger with an handler before, there's
        # no formatter.
        old_format = logging.getLogger().handlers[0].formatter._fmt
    except IndexError:
        old_format = None

    try:
        init_logging(level_name=level_name, log_format=log_format)
        yield None
    finally:
        init_logging(level_name=old_level_name, log_format=old_format)
