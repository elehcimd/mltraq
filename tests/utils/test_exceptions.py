import pytest

from mltraq.utils.exceptions import TypeValidationError, codepos, validate_type


def test_validate_type():
    """
    Test the validation of the expected type.
    """

    # If type correct, return value
    assert validate_type(123, int) == 123

    # If we expect a different type, an exception is raised
    with pytest.raises(TypeValidationError):
        assert validate_type("abc", int)


def test_codepos():
    """
    Test: we can detect the current position in the code.
    """
    codepos_str = codepos()
    codepos_str.startswith("tests/utils/test_exceptions.py [test_exceptions.py:")
    codepos_str.endswith("|test_codepos]")
