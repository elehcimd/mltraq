import datetime
import uuid
from typing import List

import pandas as pd
from numpy import float32, float64, int32, int64

from mltraq.opts import options
from mltraq.runs import Runs
from mltraq.storage import models
from mltraq.storage.serializers.datapak import DataPakSerializer
from mltraq.storage.serializers.pickle import PickleSerializer
from mltraq.storage.serializers.serializer import Serializer
from mltraq.utils.bunch import Bunch
from mltraq.utils.frames import reorder_columns

# Dictionary of available serializers
SERIALIZERS = {"DataPakSerializer": DataPakSerializer, "PickleSerializer": PickleSerializer}

# List of Python types that are mapped to native database types.
# All other types are serialized using one of the SERIALIZERS.
NATIVE_DATABASE_TYPES = [
    bool,
    int,
    int32,
    int64,
    float,
    float32,
    float64,
    str,
    datetime.time,
    datetime.datetime,
    datetime.date,
    uuid.UUID,
    bytes,
]


def serialize(obj: object) -> bytes:
    """
    Serialize object, using the preferred serializer.
    """

    serializer: Serializer = SERIALIZERS[options().get("serialization.serializer")]
    return serializer.serialize(obj)


def deserialize(data: bytes) -> object:
    """
    Deserialize object, using the preferred serializer.
    """

    serializer: Serializer = SERIALIZERS[options().get("serialization.serializer")]
    return serializer.deserialize(data)


def meta() -> dict:
    """
    Get dictionary describing the preferred serialization strategy, and
    serializer name/version.
    """
    serializer: Serializer = SERIALIZERS[options().get("serialization.serializer")]
    return serializer.meta()


def unsafe_pickle(obj: object) -> bytes:
    """
    Pickle object, compression is optional.
    """
    return PickleSerializer.serialize(obj, assert_safe=False)


def unsafe_unpickle(data: bytes) -> object:
    """
    Unpickle object, without limiting to safe opcodes.
    Used to unpickle complete Experiment objects.
    """
    return PickleSerializer.deserialize(data, assert_safe=False)


def meta_runs(runs: Runs, table_name: str) -> dict:
    """
    Return dictionary with metadata about the runs persistence:
    - table name for experiment
    - numer of runs
    - fields and their python types
    - serialized/non-serialized columns
    """
    meta = Bunch({"count": len(runs), "table_name": table_name})
    meta.columns = Bunch()

    if runs:
        fields = runs.first().fields
        meta.columns.types = {k: type(v).__name__ for k, v in fields.items()}
        meta.columns.serialized = set()
        for k, v in fields.items():
            if not any(isinstance(v, db_type) for db_type in NATIVE_DATABASE_TYPES):
                meta.columns.serialized.add(k)
        meta.columns.non_serialized = list(set(fields.keys()) - meta.columns.serialized)
        meta.columns.serialized = list(meta.columns.serialized)
        meta.columns.non_serialized = list(meta.columns.non_serialized)
    else:
        meta.columns.types = {}
        meta.columns.serialized = []
        meta.columns.non_serialized = []

    return meta


def runs_to_sql(id_experiment: uuid.UUID, meta: dict, runs: Runs) -> tuple[pd.DataFrame, List]:
    """
    Prepare a Runs object for experiment `id_experiment`,
    with metadata `meta`, to be stored in SQL.
    It returns a Pandas dataframe and dtype(s) to use in the insert.
    """

    if runs:
        # The experiment has runs, let's find out the columns definition and persist it with the experiment.
        # Work on a copy, to avoid modifications a slided copy of the dataframe.
        df_runs = runs.df(max_level=0).copy()
        df_runs["id_experiment"] = id_experiment
        df_runs = reorder_columns(df_runs, ["id_experiment", "id_run"])

        if len(meta.runs.columns.serialized) > 0:
            # If there are columns to serialize, handle them.
            with options().ctx({"datastore.relative_path_prefix": str(id_experiment)}):
                for col_name in meta.runs.columns.serialized:
                    df_runs[col_name] = df_runs[col_name].map(lambda v: serialize(v))

    else:
        df_runs = pd.DataFrame(columns=["id_experiment", "id_run"])

    dtype = (
        {"id_experiment": models.Uuid}
        | {"id_run": models.Uuid}
        | {col_name: models.LargeBinary for col_name in meta.runs.columns.serialized}
    )

    return df_runs, dtype
