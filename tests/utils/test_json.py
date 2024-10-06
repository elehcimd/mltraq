from uuid import uuid4

from mltraq.utils.json import dumps


def test_json_uuid():
    print(dumps({"uuid": uuid4()}))


def test_json_type():
    print(dumps({"tyoe": int}))
