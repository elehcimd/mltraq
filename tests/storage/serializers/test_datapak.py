import uuid

import pandas as pd
import pyarrow
import pytest
from mltraq import Sequence, options
from mltraq.storage.database import next_uuid
from mltraq.storage.serializers.datapak import DataPakSerializer, UnsupportedObjectType
from mltraq.utils.bunch import Bunch


def test_serialization_dict():
    """
    Test: we can serialize/deserialize a dictionary.
    """

    obj = {"a": 123, "b": "value"}
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, dict)
    assert obj2["a"] == 123


def test_serialization_uuid():
    """
    Test: We can serialize/deserialize UUIDs.
    """
    obj = next_uuid()
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, uuid.UUID)
    assert obj.hex == obj2.hex


def test_serialization_type_not_supported():
    """
    Test: If unknown/unsupported types are encountered, an exception is triggered.
    """

    class ComplexObject:
        pass

    obj = ComplexObject()

    with pytest.raises(UnsupportedObjectType):
        DataPakSerializer.serialize(obj)


def test_serialization_compression_onoff():
    """
    Test: We can turn compression on and off for DataPakSerializer.
    """
    obj = "THIS_IS_A_TEST THIS_IS_A_TEST"
    # Repeated pattern, otherwise we will find it even in the compressed blob

    with options.ctx({"serialization.compression.codec": "uncompressed"}):
        data = DataPakSerializer.serialize(obj)
        assert b"THIS_IS_A_TEST THIS_IS_A_TEST" in data

    with options.ctx({"serialization.compression.codec": "zlib"}):
        data = DataPakSerializer.serialize(obj)
        assert b"THIS_IS_A_TEST THIS_IS_A_TEST" not in data


def test_serialization_bunch():
    """
    Test: We can serialize/deserialize a Bunch.
    """
    obj = Bunch({"a": 123})
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, Bunch)
    assert obj2.a == 123


def test_serialization_sequence():
    """
    Test: We can serialize/deserialize a Sequence.
    """
    s = Sequence()
    s.append(a=2)
    s.append(b=2)
    data = DataPakSerializer.serialize(s)
    s = DataPakSerializer.deserialize(data)
    assert s.df().dtypes.astype(str).tolist() == ["datetime64[ns]", "float64", "float64"]
    assert s.df().columns.tolist() == ["timestamp", "a", "b"]
    assert s.df().iloc[0].a == 2


def test_serialization_int():
    """
    Test: We can serialize/deserialize an integer.
    """
    obj = 123
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, int)
    assert obj2 == 123


def test_serialization_list():
    """
    Test: We can serialize/deserialize a list.
    """
    obj = [1, 2, 3]
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, list)
    assert obj2 == [1, 2, 3]


def test_serialization_set():
    """
    Test: We can serialize/deserialize a set.
    """
    obj = {1, 2, 3}
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, set)
    assert obj2 == {1, 2, 3}


def test_serialization_dict_nested_encoded():
    """
    Test: We can serialize/deserialize a nested dictionary with a complex object.
    """
    obj = {"a": {"b": pd.Series([1, 2, 3])}}
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2["a"]["b"], pd.Series)
    assert obj2["a"]["b"].iloc[0] == 1


def test_serialization_list_nested_encoded():
    """
    Test: We can serialize/deserialize a list with a nested complex object.
    """
    obj = [123, pd.Series([1, 2, 3])]
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, list)
    assert isinstance(obj2[1], pd.Series)
    assert obj2[1].iloc[0] == 1


def test_serialization_nested_dict():
    """
    Test: We can serialize/deserialize a nested dictionary.
    """
    obj = {"a": {"b": 123}}
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert obj2["a"]["b"] == 123


def test_serialization_pandas_series():
    """
    Test: We can serialize/deserialize a Pandas series.
    """
    obj = pd.Series([1, 2, 3])
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, pd.Series)
    assert obj2.iloc[0] == 1


def test_serialization_pandas_dataframe():
    """
    Test: We can serialize/deserialize a Pandas dataframe.
    """
    obj = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, pd.DataFrame)
    assert obj2.columns.tolist() == ["a", "b"]


def test_serialization_pyarrow_table():
    """
    Test: We can serialize/deserialize a Pyarrow table.
    """
    obj = pyarrow.Table.from_pandas(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
    data = DataPakSerializer.serialize(obj)
    assert isinstance(data, bytes)
    obj2 = DataPakSerializer.deserialize(data)
    assert isinstance(obj2, pyarrow.Table)
    assert obj2.column_names == ["a", "b"]