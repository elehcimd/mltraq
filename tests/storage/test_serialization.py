import datetime

from mltraq import create_experiment, options
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
    with options().ctx({"serialization.serializer": "PickleSerializer"}):
        data = serialize(obj)
    assert isinstance(data, bytes)
    obj2 = PickleSerializer.deserialize(data)
    assert isinstance(obj2, list) and obj2[0] == 1

    with options().ctx({"serialization.serializer": "DataPakSerializer"}):
        data = serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, list) and obj2[0] == 1


def test_db_storage_datetime():
    """
    Test: time values can be stored as native database types.
    """

    experiment = create_experiment()
    dt1 = datetime.datetime.strptime("09/19/22 13:55:26", "%m/%d/%y %H:%M:%S")

    var_type_time = dt1.time()
    var_type_datetime = dt1
    var_type_date = dt1.date()

    with experiment.run() as run:
        run.fields.var_type_time = var_type_time
        run.fields.var_type_datetime = var_type_datetime
        run.fields.var_type_date = var_type_date

    experiment = experiment.persist().reload()

    run = experiment.runs.first()
    assert run.fields.var_type_time == var_type_time
    assert run.fields.var_type_datetime == var_type_datetime
    assert run.fields.var_type_date == var_type_date
