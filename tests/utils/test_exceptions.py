import pytest
from mltraq.utils.exceptions import TypeValidationError, validate_type


def test_validate_type():
    """
    Test the validation of the expected type.
    """

    # If type correct, return value
    assert validate_type(123, int) == 123

    # If we expect a different type, an exception is raised
    with pytest.raises(TypeValidationError):
        assert validate_type("abc", int)
