from mltraq.utils.dicts import ObjectDictionary, ordered_dict_equality


def test_order():
    d = ObjectDictionary()

    d["c"] = 1
    d["a"] = 2
    d["b"] = 3

    assert str(d) == "{'c': 1, 'a': 2, 'b': 3}"


def test_ordered_pair():
    d1 = ObjectDictionary({"c": 1, "a": 2, "b": 3})
    d2 = ObjectDictionary({"c": 1, "a": 2, "b": 3})

    assert ordered_dict_equality(d1, d2)


def test_attr():
    d = ObjectDictionary()

    d.a = 123

    assert d["a"] == d.a
    assert d["a"] == 123


def test_nested():
    d = ObjectDictionary.deep({"a": {"b": {"c": 123}}})

    assert d.a.b.c == 123


def test_missing_key():
    d = ObjectDictionary({})
    try:
        x = d.x
        print(f"Never reached {x}")
    except AttributeError:
        pass


def test_del_attr():
    d = ObjectDictionary({})

    try:
        del d.x
    except AttributeError:
        pass


def test_constructor():
    d = ObjectDictionary({"a": 123})
    d = ObjectDictionary.deep(d)
    assert d["a"] == 123
