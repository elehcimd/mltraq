import json
import uuid
import zlib
from functools import partial
from pickle import PickleError

import cloudpickle
import numpy as np
import pandas as pd
from mltraq.options import options
from mltraq.utils.dicts import ObjectDictionary
from mltraq.utils.frames import json_normalize

# Keyword used to identify serialized values and the version of the serialization format.
TYPE_KEY = "mltraq-type-1.0"

# Introduced with Python 3.0, https://peps.python.org/pep-3154/
# Unpickling might fail: on different architectures, different python version, in case of missing packages.
PICKLE_DEFAULT_PROTOCOL = 4

# Types that are handled by serialization.
SERIALIZED_TYPES = [pd.DataFrame, pd.Series, np.ndarray, uuid.UUID, dict, list]


def compress(data: bytes, enable_compression=None) -> bytes:
    """Compress a sequence of bytes.

    Args:
        data (bytes): Data to compress.
        enable_compression (_type_, optional): Force compression (enable/disable)
            regardless the default. Defaults to None.

    Returns:
        bytes: Compressed data.
    """
    if enable_compression is None:
        enable_compression = options.get("serialization.enable_compression")

    if enable_compression:
        return zlib.compress(data)
    else:
        return data


def decompress(data: bytes) -> bytes:
    """Decompress the data. It works also with uncompressed data: if zlib fails,
        it returns the input data.

    Args:
        data (bytes): Data to decompress.

    Returns:
        bytes: Decompressed data.
    """
    if isinstance(data, memoryview):
        data = data.tobytes()

    try:
        data = zlib.decompress(data)
    except zlib.error:
        pass

    return data


def pickle_dumps(obj: object) -> bytes:
    """It returns the compressed (zlib) pickled object. The Pickle DEFAULT_PROTOCOL is used
    for maximum compatibility.

    Args:
        obj (object): Object to serialize.

    Returns:
        bytes: Compressed serialized object.
    """
    return compress(cloudpickle.dumps(obj, protocol=PICKLE_DEFAULT_PROTOCOL))


def pickle_loads(data: bytes) -> object:
    """It returns the loaded object, afer uncompressing and unpickling it.

    Args:
        data (bytes): Serialized object.

    Returns:
        object: Unserialized object.
    """
    try:
        return cloudpickle.loads(decompress(data))
    except Exception as e:  # noqa # we do want to catch all errors here
        raise PickleError() from e


def pickle_size(obj: object, unit: str = "b") -> int:
    """It returns the size of the object once serialised (including compression).

    Args:
        obj (object): Object to analyse.
        unit (str, optional): Unit of measure, b (Bytes), kb (KiloBytes), mb (MegaBytes). Defaults to "b".

    Returns:
        int: Size of the serialized object.
    """
    size_object = len(pickle_dumps(obj))
    if unit == "b":
        return size_object
    elif unit == "kb":
        return int(size_object / (2**10) * 1e2) / 1e2
    elif unit == "mb":
        return int(size_object / (2**20) * 1e2) / 1e2
    else:
        return None


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        """Return the dictionary that represents the serialized version of an object

        Args:
            obj (_type_): Object to serialize

        Returns:
            _type_: dict containing the serialized object
        """
        if isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series):
            # Since, in presence of timestamps in either columns or index, we're going to change the data,
            # let's work on a copy of the dataframe to not modify the original dataframe.
            # If it's a series, we just convert it to a dataframe, implicitly obtaining a copy of the data.
            if isinstance(obj, pd.Series):
                obj = obj.to_frame()
                obj_type = "pandas.Series"
            else:
                obj = obj.copy()
                obj_type = "pandas.DataFrame"

            dtypes = {col: str(obj[col].dtype) for col in obj.columns}
            dtype_index = str(obj.index.dtype)

            # handle timestamps serialization in columns
            cols_datetime64ns = [col for col in obj.columns if obj[col].dtype == "datetime64[ns]"]
            if len(cols_datetime64ns) > 0:
                # some columns contain timestamps, let's convert them to strings
                for col in cols_datetime64ns:
                    obj[col] = obj[col].astype(int)

            # Timestamps in the index have a dtype "<M8[ns]" instead of "datetime64[ns]" (not sure why
            # it's nost simply "datetime64[ns]" as for columns).  This is why we catch multiple dtype
            # types that might be associated to timestamps.
            if dtype_index in ["<M8[ns]", ">M8[ns]", "datetime64[ns]"]:
                obj.index = obj.index.astype(int)

            return {
                TYPE_KEY: obj_type,
                "dtype_index": dtype_index,
                "dtypes": dtypes,
                "data": obj.to_dict(orient="list"),
                "index": obj.index.tolist(),
            }
        elif isinstance(obj, np.ndarray):
            return {TYPE_KEY: "numpy.ndarray", "data": obj.tolist()}
        elif isinstance(obj, uuid.UUID):
            return {TYPE_KEY: "uuid.UUID", "data": str(obj)}
        else:
            return json.JSONEncoder.default(self, obj)


def serialize(obj: object, enable_compression=None) -> bytes:
    """Serialize an object

    Args:
        obj (object): Object to serialize
        enable_compression (_type_, optional): If not None, enable/disable compression.
            If None, consider default preference. Defaults to None.

    Returns:
        bytes: Serialized object.
    """
    if enable_compression is None:
        enable_compression = options.get("serialization.enable_compression")

    return compress(json.dumps(obj, cls=JSONEncoder).encode("UTF-8"), enable_compression=enable_compression)


def deserialize(obj: bytes) -> object:
    """Deserialize an object

    Args:
        obj (bytes): Object to deserialize.

    Returns:
        object: Unserialized object.
    """

    def f(v):
        if isinstance(v, dict) and TYPE_KEY in v:
            # This ia a value to deserialize
            if v[TYPE_KEY] in ["pandas.DataFrame", "pandas.Series"]:
                df = pd.DataFrame.from_dict(v["data"], orient="columns")
                df.index = pd.Index(v["index"]).astype(v["dtype_index"])
                for col, dtype in v["dtypes"].items():
                    df[col] = df[col].astype(dtype)
                if v[TYPE_KEY] == "pandas.DataFrame":
                    return df
                else:
                    # Return first column, a series
                    return df[df.columns[0]]
            elif v[TYPE_KEY] == "numpy.ndarray":
                return np.asarray(v["data"])
            elif v[TYPE_KEY] == "uuid.UUID":
                return uuid.UUID(v["data"])
            else:
                # We don't know how to deserialize it, return it as a dictionary.
                return ObjectDictionary(v)
        elif isinstance(v, list):
            # Walk thru the list, trying to decode values.
            return [f(v) for v in v]
        elif isinstance(v, dict):
            # Walk thru the dict, trying to decode values.
            return ObjectDictionary({kv[0]: f(kv[1]) for kv in v.items()})
        else:
            # Nothing to do, return value.
            return v

    return json.loads(decompress(obj).decode("UTF-8"), object_hook=f)


def serialize_df(df: pd.DataFrame, ignore_columns: list = None, enable_compression=None):
    """Serialize some of the columns of the dataframe, making it ready for database storage.

    Args:
        df (pd.DataFrame): Dataframe to process.
        ignore_columns (list, optional): Columns to ignore. Defaults to None.
        enable_compression (_type_, optional): If not None, force enable/disable of compression. Defaults to None.

    Returns:
        _type_: _description_
    """
    if enable_compression is None:
        enable_compression = options.get("serialization.enable_compression")

    consider_columns = [col_name for col_name in df.columns if col_name not in ignore_columns]

    # Identify columns to serialize
    serialized_cols = []
    for col_name in consider_columns:
        for serialized_type in SERIALIZED_TYPES:
            # We assume that the types in the first row are the same of the other rows.
            if isinstance(df[col_name].iloc[0], serialized_type):
                serialized_cols.append(col_name)
                break

    if len(serialized_cols) > 0:
        # If there are columns to serialize, work on a frame deep copy.
        df = df.copy()
        for col_name in serialized_cols:
            df[col_name] = df[col_name].map(partial(serialize, enable_compression=enable_compression))

    # Identify columns that haven't been serialized, among the ones to be considered.
    non_serialized_cols = [col_name for col_name in consider_columns if col_name not in serialized_cols]

    columns = {"serialized": serialized_cols, "non_serialized": non_serialized_cols, "compression": enable_compression}
    return df, columns


def explode_json_column(df: pd.DataFrame, col_name: str, prefix: str = None, suffix: str = None) -> pd.DataFrame:
    """Explode a column in the Pandas dataframe containing a dict to a list of columns.
    Useful to handle the "attributes" column in the "Experiments" table, which contains
    the serialized values as JSON.
    Args:
        df (pd.DataFrame): Pandas dataframe
        col_name (str): Column to process.
        prefix (str, optional): Prefix to consider for all exploded columns.
        suffix (str, optional): In case exploded columns already exist, use this suffix.
        Defaults to _{col_name}.
    Returns:
        pd.DataFrame: Resulting Pandas dataframe.
    """

    if suffix is None:
        suffix = f"_{col_name}"

    # Explode column containing json to multiple columns, in a dataframe.
    df_exploded = json_normalize(df[col_name])

    if prefix is not None:
        df_exploded.columns = [f"{prefix}{col_name}" for col_name in df_exploded.columns]

    return df.drop(columns=[col_name]).merge(
        df_exploded,
        how="left",
        left_index=True,
        right_index=True,
        suffixes=(None, suffix),
    )
