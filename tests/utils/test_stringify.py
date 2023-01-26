from mltraq.utils.text import stringify


def test_stringify():
    assert stringify({"a" * 200: 1}) == '{"' + "a" * 198 + " ...}"

    assert stringify({"a": 1}.keys()) == '["a"]'

    assert stringify("a" * 250) == '"' + "a" * 199 + " ..."

    assert (
        stringify(["a"] * 100)
        == '["a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a",'
        ' "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", ...]'
    )
