import uuid
from io import BytesIO

import numpy as np
import pandas as pd
import pyarrow as pa
from mltraq.storage.serializers.pickle import PickleSerializer
from mltraq.storage.serializers.serializer import Serializer
from mltraq.utils.bunch import Bunch
from mltraq.utils.exceptions import ExceptionWithMessage
from mltraq.utils.sequence import Sequence
from pyarrow.feather import read_feather, read_table, write_feather

# Why datapak?
# - Need for a versatile, simple serialization format
# - Combining existing standard components:
#   - Pickle to serialize: int, float, str, bytes, tuple, list, set, dict.
#     We limit aggressively the allowed opcodes to avoid security issues.
#   - numpy/pyarrow/str to serialize: pd.DataFrame, pd.Series, pa.Table, np.ndarray, uuid.UUID

# Semantic version of the format
VERSION_SERIALIZER = "0.0.0"


# Types that are encoded with Pickle
BASIC_TYPES = [
    bool,
    int,
    float,
    str,
    bytes,
]


# Types that are encoded with Pickle. They can be nested.
CONTAINER_TYPES = [tuple, list, set, dict]

# Complex types that are encoded to `bytes``, before being serialized with Pickle.
# Complex types are encoded as dictionaries with the special key MAGIC_KEY.
COMPLEX_TYPES = [Bunch, Sequence, pd.DataFrame, pd.Series, pa.Table, np.ndarray, uuid.UUID]

# Magic dict key encoding types in the list COMPLEX_TYPES (see below), with semantic versioning
KEY_MAGIC = f"datapak-type-{VERSION_SERIALIZER}"

# Key of dictionaries encoding complex types, with semantic versioning
KEY_BUNCH = "mltraq.Bunch-0.0.0"
KEY_SEQUENCE = "mltraq.Sequence-0.0.0"
KEY_PANDAS_SERIES = "pandas.Series-0.0.0"
KEY_PANDAS_DATAFRAME = "pandas.DataFrame-0.0.0"
KEY_PYARROW_TABLE = "pyarrow.Table-0.0.0"
KEY_NUMPY_NDARRAY = "numpy.ndarray-0.0.0"
KEY_UUID = "uuid.UUID-0.0.0"


# No other type is supported. If other types are encountered,
# an exception UnsupportedObjectType is rised.
class UnsupportedObjectType(ExceptionWithMessage):
    pass


class EncodingError(ExceptionWithMessage):
    pass


def ensure_bytes(data: bytes) -> bytes:
    """
    Ensure that the type of `data` is indeed `bytes`, as a safety
    precaution to ensure that we are not writing in the serialized
    blob any unexpected object type.
    """

    if not isinstance(data, bytes):
        raise EncodingError(f"Trying to return non-bytes as encoded object ({data.__class__}), this should not happen.")

    return data


class DataPakSerializer(Serializer):
    """
    Class that implement the DataPak serialization format.

    """

    @classmethod
    def name(cls) -> str:
        return f"{cls.__name__}-{VERSION_SERIALIZER}"

    @classmethod
    def serialize(cls, obj: object) -> bytes:
        """
        Serialize an object:
        1. Encode it
        2. Serialize it with Pickle
        3. Compress it, if requested
        """

        return PickleSerializer.serialize(cls.encode(obj))

    @classmethod
    def deserialize(cls, data: bytes) -> object:
        """
        Deserialize a bytes object:
        1. Decompress it, if compressed
        2. Unpickle it, making sure that only safe opcodes are used
        3. Decode it
        """
        return cls.decode(PickleSerializer.deserialize(data))

    @classmethod
    def encode(cls, obj: object) -> object:
        for obj_type in BASIC_TYPES:
            if isinstance(obj, obj_type):
                return obj
        if isinstance(obj, dict) and not isinstance(obj, Bunch):
            return {k: cls.encode(v) for k, v in obj.items()}
        elif isinstance(obj, set):
            return {cls.encode(v) for v in obj}
        elif isinstance(obj, list):
            return [cls.encode(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple([cls.encode(v) for v in obj])
        else:
            return encode_magic_key(cls, obj)

    @classmethod
    def decode(cls, obj: object) -> object:
        for obj_type in BASIC_TYPES:
            if isinstance(obj, obj_type):
                return obj
        if isinstance(obj, list):
            return [cls.decode(v) for v in obj]
        if isinstance(obj, set):
            return {cls.decode(v) for v in obj}
        elif isinstance(obj, tuple):
            return tuple([cls.decode(v) for v in obj])
        elif isinstance(obj, dict):
            if KEY_MAGIC not in obj:
                return {k: cls.decode(v) for k, v in obj.items()}
            else:
                return decode_magic_key(cls, obj)
        else:
            raise UnsupportedObjectType(f"{cls.__class__} is unable to deserialize type {obj.__class__}")


def encode_magic_key(cls, obj: object) -> dict:
    """
    Encode the complex object, using as key MAGIC_KEY to identify
    the dictionary as a serialized complex object.
    """
    if isinstance(obj, Sequence):
        obj.flush()
        return {KEY_MAGIC: KEY_SEQUENCE, "value": cls.encode(obj.flush().frame)}
    if isinstance(obj, Bunch):
        return {KEY_MAGIC: KEY_BUNCH, "value": cls.encode(dict(obj))}
    elif isinstance(obj, uuid.UUID):
        return {KEY_MAGIC: KEY_UUID, "value": obj.hex}
    elif isinstance(obj, pd.DataFrame):
        buffer = BytesIO()
        write_feather(obj, buffer, compression="uncompressed")
        return {KEY_MAGIC: KEY_PANDAS_DATAFRAME, "value": ensure_bytes(buffer.getvalue())}
    elif isinstance(obj, pd.Series):
        buffer = BytesIO()
        write_feather(obj.to_frame(), buffer, compression="uncompressed")
        return {KEY_MAGIC: KEY_PANDAS_SERIES, "value": ensure_bytes(buffer.getvalue())}
    elif isinstance(obj, pa.Table):
        buffer = BytesIO()
        write_feather(obj, buffer, compression="uncompressed")
        return {KEY_MAGIC: KEY_PYARROW_TABLE, "value": ensure_bytes(buffer.getvalue())}
    elif isinstance(obj, np.ndarray):
        # Store in NPY format, a "simple format for saving numpy arrays to disk with the full information about them."
        # https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html
        buffer = BytesIO()
        np.save(buffer, obj, allow_pickle=False)
        return {KEY_MAGIC: KEY_NUMPY_NDARRAY, "value": ensure_bytes(buffer.getvalue())}
    else:
        raise UnsupportedObjectType(f"{cls.__name__} does not support type {obj.__class__}")


def decode_magic_key(cls, obj: dict) -> object:
    """
    Decode a complex object, encoded as a dictionary {k:v}
    where `k` is a predefined list of string values, and
    `v` is a bytes object that contains the serialized value.
    """
    if obj[KEY_MAGIC] == KEY_SEQUENCE:
        return Sequence(frame=cls.decode(obj["value"]))
    if obj[KEY_MAGIC] == KEY_UUID:
        return uuid.UUID(hex=obj["value"])
    if obj[KEY_MAGIC] == KEY_BUNCH:
        return Bunch(cls.decode(obj["value"]))
    if obj[KEY_MAGIC] == KEY_PANDAS_DATAFRAME:
        output_stream = pa.BufferOutputStream()
        output_stream.write(obj["value"])
        return read_feather(output_stream.getvalue())
    elif obj[KEY_MAGIC] == KEY_PANDAS_SERIES:
        output_stream = pa.BufferOutputStream()
        output_stream.write(obj["value"])
        return read_feather(output_stream.getvalue())[0]
    elif obj[KEY_MAGIC] == KEY_NUMPY_NDARRAY:
        memfile = BytesIO()
        memfile.write(obj["value"])
        memfile.seek(0)
        return np.load(memfile, allow_pickle=False)
    elif obj[KEY_MAGIC] == KEY_PYARROW_TABLE:
        output_stream = pa.BufferOutputStream()
        output_stream.write(obj["value"])
        return read_table(output_stream.getvalue())
    else:
        raise UnsupportedObjectType(f"{cls.__class__} does not support type {obj[KEY_MAGIC]}")
