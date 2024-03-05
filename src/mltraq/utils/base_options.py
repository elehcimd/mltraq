from __future__ import annotations

import copy
import logging
from argparse import ArgumentParser
from contextlib import contextmanager

log = logging.getLogger(__name__)


class InvalidOption(Exception):
    pass


class BaseOptions:
    """
    Handle options as a tree of dictionaries.
    Following singletorn pattern.
    This class must be extended with a preoper initialization
    for `default_values`, it should not be used directly.
    Options can be addressed with dotted strings.
    E.g., "group1.value".
    """

    _instance: BaseOptions | None = None
    default_values: dict = {}

    def __init__(self):
        raise RuntimeError("There can be up to one instance of this class, you can get it with .instance()")

    @classmethod
    def instance(cls) -> BaseOptions:
        """
        Get instance of the class.
        """
        if cls._instance is None:
            # If there isn't yet an instance, instantiate it and initialize
            cls._instance = cls.__new__(cls)
            # Classes extending BaseOption can change the default values
            # overriding the attribute cls.default_values.
            # We work on a copy, to allow option resets.
            cls._instance.values = copy.deepcopy(cls.default_values)
        return cls._instance

    def get(self, path: str, null_if_missing: bool = False) -> object:
        """
        Returns option or dictionary representing the subtree at `path`.
        If `null_if_missing` is True, return NULL if the key is missing,
        otherwise fail.
        """

        steps = path.split(".")
        d = self.values
        for step in steps:
            if step not in d and null_if_missing:
                return None
            d = d[step]

        return d

    def set(self, path: str, value: object):
        """
        Sets the value of `path` to value.
        """
        *steps, last = path.split(".")
        d = self.values
        for step in steps:
            d = d.setdefault(step, {})
        d[last] = value

    def copy_from(self, values: dict):
        """
        Copy the values of the options from a dictionary of `values`.
        """
        self.values = copy.deepcopy(values)

    def copy_values(self) -> dict:
        """
        Returns a deepcopy of the `values`.
        """
        return copy.deepcopy(self.values)

    def reset(self, path: str | None = None):
        """
        Rset the `path` value to its default.
        If `path` is None, it resets all options.
        """
        if path is None:
            self.copy_from(self.default_values)
            return

        steps = path.split(".")
        d = self.default_values
        for step in steps:
            d = d[step]
        self.set(path, d)

    def default_if_null(self, value: object, path: str) -> object:
        """
        Returns the option value if `value` is NULL, `value` otherwise.
        """

        if value is not None:
            return value
        else:
            return self.get(path)

    def set_argument_options(self, options: list[ArgumentOption] | None = None):
        """
        Given a list of Option objects, set them.
        """

        if not options:
            return

        for option in options:
            log.info(f"Setting option {option.name}={option.value}")
            self.set(option.name, option.value)

    def flatten(self):
        """
        Return a dictionary of KEY:VALUE pairs, no nested dictionaries.
        """

        values = {}

        def traverse(x, name=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    traverse(v, name=f"{name}.{k}")
            else:
                values[name[1:]] = x

        traverse(self.values)
        return values

    @contextmanager
    def ctx(self, options: dict):
        """
        Provides context manager for temporary options.
        E.g., options.ctx({'a.b': 123}).
        """
        try:
            orig_options = copy.deepcopy(self.values)
            for k, v in options.items():
                self.set(k, v)
            yield self
        finally:
            self.values = orig_options


class ArgumentOption:
    """
    It represents an option passed as an argument,
    used for input validation.
    """

    __slots__ = ("name", "value")

    def __init__(self, option: str):
        """
        Given an `option` string in the format NAME=VALUE,
        checks the validity of `name` and `value` and sets them.
        """

        if "=" not in option:
            raise ValueError("'=' not present")
        name, value = option.split(sep="=", maxsplit=1)
        name = name.strip()
        value = value.strip()
        if len(name) == 0:
            raise ValueError("Option name missing")
        if len(value) == 0:
            raise ValueError("Option value missing")
        self.name = name
        self.value = value


def add_option_argument(parser: ArgumentParser):
    """
    Add option --option to cli parameters, to change the
    value of package options via command line.
    """

    parser.add_argument(
        "--option",
        metavar="KEY=VALUE",
        action="extend",
        nargs="+",
        help="Change the default package options.",
        type=ArgumentOption,
    )
