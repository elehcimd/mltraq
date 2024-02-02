from __future__ import annotations

import copy
from contextlib import contextmanager
from typing import Any, TypeVar

T = TypeVar("T")


class TypeValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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

    def get(self, path: str) -> object:
        """
        Returns option or dictionary representing the subtree at `path`.
        """
        steps = path.split(".")
        d = self.values
        for step in steps:
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
