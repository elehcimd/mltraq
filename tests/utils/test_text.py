from mltraq.utils.text import wprint


def test_wprint():
    text = "a" * 100

    lstats = wprint(text)

    assert lstats == [70, 30]
