from joblib.parallel import DEFAULT_BACKEND

from mltraq.utils.base_options import BaseOptions


class Options(BaseOptions):
    """
    Default options.
    """

    default_values = {
        "reproducibility": {"random_seed": 123, "fake_incremental_uuids": False},
        "database": {
            "url": "sqlite:///:memory:",
            "echo": False,
            "pool_pre_ping": True,
            "ask_password": False,
            "query_read_chunk_size": 1000,
            "query_write_chunk_size": 1000,
            "experiments_tablename": "experiments",
            "experiment_tableprefix": "experiment_",
        },
        "execution": {
            "exceptions": {"compact_message": False},
            "backend": DEFAULT_BACKEND,
            "n_jobs": -1,
            "args_field": False,
        },
        "tqdm": {"disable": False, "delay": 0.5, "leave": False},
        "serialization": {
            "store_unsafe_pickle": False,
            "serializer": "DataPakSerializer",
            "compression": {"codec": "uncompressed"},
        },
        "app": {},
    }


# Singleton object that handles options.
# It is accessible also within runs running in parallel thanks
# to the propagation of its values on the run workers.
options: BaseOptions = Options.instance()
