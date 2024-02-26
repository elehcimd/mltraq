from joblib.parallel import DEFAULT_BACKEND

from mltraq.utils.base_options import BaseOptions


class Options(BaseOptions):
    """
    Default options.
    """

    default_values = {
        "reproducibility": {"random_seed": 123, "sequential_uuids": False},
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
        "datastore": {"url": "file:///mltraq.datastore", "relative_path_prefix": "undefined"},
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


def options() -> BaseOptions:
    """
    Returns singleton object of options.
    """

    # In some complex cases (parallel execution of runs, options
    # imported in different ways by different modules), the
    # object is quietly copied, causing errors hard to debug.
    #
    # By always calling options(), this issue disappears and
    # things work as expected.
    return Options.instance()
