import pytest
from mltraq.utils.base_options import BaseOptions


class Options(BaseOptions):
    """
    Default options().
    """

    default_values = {"a": {"b": 123, "c": False}}


def test_options():
    """
    Test the get of an option.
    """

    options = Options.instance()
    assert options.get("a.b") == 123


def test_flatten():
    """
    Test: We can access all defined options as a flattened dictionary.
    """
    d = Options.instance().flatten()
    assert d["a.b"] == 123
    assert d["a.c"] is False


def test_default_if_null():
    """
    Test: If value is None, return option value.
    """
    assert Options.instance().default_if_null(123, "a.c") == 123
    assert Options.instance().default_if_null(None, "a.c") is False


def test_null_if_missing():
    """
    Test: If value is None, return option value.
    """

    # If key is missing, an exception is raised.
    with pytest.raises(KeyError):
        Options.instance().get("x")

    # We can request to return None if key is missing.
    assert Options.instance().get("x", null_if_missing=True) is None
