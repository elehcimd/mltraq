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


def test_prefer():
    """
    Test: If value is None, return option value.
    """
    assert Options.instance().get("a.c", prefer=123) == 123
    assert Options.instance().get("a.b", prefer=None) == 123


def test_otherwise():
    """
    Test: If a key is missing, we can change the default returned value.
    """

    assert Options.instance().get("doesntexist", otherwise=None) is None
    assert Options.instance().get("doesntexist", otherwise=123) == 123

    with pytest.raises(KeyError):
        Options.instance().get("doesntexist")
