import pytest
from mltraq.utils.base_options import BaseOptions, TypeValidationError, validate_type


class Options(BaseOptions):
    """
    Default options.
    """

    default_values = {"a": {"b": 123, "c": False}}


def test_options():
    """
    Test the get of an option.
    """

    options = Options.instance()
    assert options.get("a.b") == 123


def test_validate_type():
    """
    Test the validation of the expected type.
    """

    # If type correct, return value
    assert validate_type(123, int) == 123

    # If we expect a different type, an exception is raised
    with pytest.raises(TypeValidationError):
        assert validate_type("abc", int)
