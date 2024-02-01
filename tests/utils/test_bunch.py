from unittest import TestCase

import pytest
from mltraq.utils.bunch import Bunch


def test_order():
    """
    Test: Inserted elements are ordered in an ordered dict.
    """
    d = Bunch()

    d["c"] = 1
    d["a"] = 2
    d["b"] = 3

    assert str(d) == "{'c': 1, 'a': 2, 'b': 3}"


def test_pair():
    """
    Test: Two dicts containing the same elements are equal.
    """
    d1 = Bunch({"c": 1, "a": 2, "b": 3})
    d2 = Bunch({"c": 1, "a": 2, "b": 3})

    TestCase().assertDictEqual(d1, d2)


def test_attr():
    """
    Test: elements can be accessed by name or by attribute.
    """
    d = Bunch()
    d["a"] = 200
    d["a"] += 10
    d.b = 100
    d.b += 10
    assert d["a"] == 210
    assert d["b"] == 110


def test_nested():
    d = Bunch.dict_to_bunch_deep({"a": {"b": {"c": 123}}})

    assert d.a.b.c == 123


def test_missing_key():
    """
    Test: AttributeError raised if we try to access an unexisting attribute.
    """
    d = Bunch()
    with pytest.raises(AttributeError):
        _ = d.x


def test_del_attr():
    """
    Test: AttributeError raised if we try to delete an unexisting attribute.
    """
    d = Bunch()
    with pytest.raises(AttributeError):
        del d.x


def test_dict_to_bunch_deep():
    """
    Test: We can deep-convert a dict to a Bunch
    """
    d = {"a": {"b": 123}}
    d = Bunch.dict_to_bunch_deep(d)
    assert d.a.b == 123


def test_str():
    """
    Test: The string representation is compact (deeply),
    without reporting the class name.
    """

    d = Bunch({"a": 123})
    print(d.__str__())
    assert "123" in d.__str__()
    assert "Bunch" not in d.__str__()
    assert "Bunch" not in d._repr_html_()

    # Also for nested dicts
    d = Bunch(a=Bunch(a=123))
    print(d.__str__())
    assert "123" in d.__str__()
    assert "Bunch" not in d.__str__()
    assert "Bunch" not in d._repr_html_()


def test_empty():
    """
    Test: Different ways to initialize an empty Bunch.
    """
    assert Bunch(None) == Bunch()
    assert Bunch() == Bunch({})
