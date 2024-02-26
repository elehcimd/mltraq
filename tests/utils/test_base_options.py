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
