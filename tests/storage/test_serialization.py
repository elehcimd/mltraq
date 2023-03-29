from uuid import UUID

import mltraq
import numpy as np
import pandas as pd
from mltraq import Sequence
from mltraq.storage.serialization import (
    decompress,
    deserialize,
    explode_json_column,
    pickle_dumps,
    pickle_loads,
    pickle_size,
    serialize,
)


def assert_serialize_equal(obj, blob):
    serialized_obj = serialize(obj)
    print(f"\n\nCOMPARING\n{serialized_obj}\nWITH\n{blob}\nEND\n\n")
    assert serialized_obj == blob


def test_decompress_memoryview():
    v = memoryview(b"abcefg")

    assert isinstance(decompress(v), bytes)


def test_serialize_df():
    data = {"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]}
    df = pd.DataFrame(data)

    assert_serialize_equal(
        df,
        (
            b'{"mltraq-type-0.0": "pandas.DataFrame-0.0", "dtype_index": "int64", "dtypes": {"a": "int64", "b":'
            b' "int64", "c": "int64"}, "data": {"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]}, "index": [0, 1, 2]}'
        ),
    )


def test_pickle_size():
    s = mltraq.create_session()

    e1 = s.add_experiment(name="test")
    e2 = s.add_experiment(name="test_bigger")

    # check that a larger object leads to a larger serialized version
    assert pickle_size(e1) < pickle_size(e2)

    # verify conversion to bytes, kilobytes, and megabytes , rounded at two decimals
    assert int(pickle_size(e1, unit="b") / 1024 * 100) == pickle_size(e1, unit="kb") * 100
    assert int(pickle_size(e1, unit="kb") / 1024 * 100) == pickle_size(e1, unit="mb") * 100


def test_deserialize():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
    assert df.equals(deserialize(serialize(df)))

    s = pd.Series([1, 2, 3])
    assert s.equals(deserialize(serialize(s)))

    a = s.values
    assert np.array_equal(a, deserialize(serialize(a)))

    u = UUID("018540aa-bd0f-030b-e1d5-8b38942b5c83")
    assert deserialize(serialize(u)) == u


def test_explode_json_column():
    df = pd.DataFrame({"a": [{"b": 111}], "c": 222})
    df2 = explode_json_column(df, "a")
    assert df2.equals(pd.DataFrame({"c": [222], "b": [111]}))

    df = pd.DataFrame({"a": [{"b": 111}], "c": 222, "b": 333})
    df2 = explode_json_column(df, "a")
    assert df2.equals(pd.DataFrame({"c": [222], "b": [333], "b_a": [111]}))


def test_pickle_dumps_loads():
    data = pickle_dumps({"a": 1111, "b": 222})
    pickle_loads(data)


def test_sequence():
    seq = Sequence()

    seq.log(c=3, a=1, b=2)
    seq.log(d=5)

    # create dataframe from sequence, and sequence from dataframe.
    df = pd.DataFrame(seq)
    seq = Sequence(df=df)

    serialized = serialize(seq)

    assert isinstance(serialized, bytes)
    seq = deserialize(serialized)

    # We expect two rows, first one with values for col c,a,b (and nan for col d),
    # and second one with a non-nan value only for d.
    assert len(seq) == 2
    assert list(seq.columns) == ["timestamp", "c", "a", "b", "d"]
    assert np.isnan(seq["d"].iloc[0])
    assert seq["d"].iloc[1] == 5
    assert seq["a"].iloc[0] == 1

    # Also, timestamp's type is datetime64[ns].
    assert str(seq.timestamp.dtype) == "datetime64[ns]"
