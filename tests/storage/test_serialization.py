from mltraq import options
from mltraq.storage.serialization import deserialize, serialize
from mltraq.storage.serializers.datapak import DataPakSerializer
from mltraq.storage.serializers.pickle import PickleSerializer


def test_serialization_dict():
    """
    Test: We can use generalized serialize/deserialize procedures.
    """
    obj = {"a": 123, "b": "value"}
    data = serialize(obj)
    assert isinstance(data, bytes)
    obj2 = deserialize(data)
    assert isinstance(obj2, dict)
    assert obj2["a"] == 123


def test_serialization_picke():
    """
    Test: We can configure via options the serializer to use.
    """
    obj = [1, 2, 3]
    with options.ctx({"serialization.serializer": "PickleSerializer"}):
        data = serialize(obj)
    assert isinstance(data, bytes)
    obj2 = PickleSerializer.deserialize(data)
    assert isinstance(obj2, list) and obj2[0] == 1

    with options.ctx({"serialization.serializer": "DataPakSerializer"}):
        data = serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, list) and obj2[0] == 1
