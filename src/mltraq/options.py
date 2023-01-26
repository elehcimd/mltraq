import copy
import logging
from contextlib import contextmanager

from joblib.parallel import DEFAULT_BACKEND


default_options = {
    "reproducibility": {"random_seed": 123},
    "db": {
        "url": "sqlite:///:memory:",
        "echo": False,
        "pool_pre_ping": True,
        "ask_password": False,
        "query_read_chunk_size": 1000,
        "query_write_chunk_size": 1000,
        "experiments_tablename": "experiments",
        "experiment_tableprefix": "e_",
    },
    "execution": {
        "default_backend": DEFAULT_BACKEND,
        "cache": {
            "disable": True,
            "backend": "joblib.Memory",
            "location": ".joblib.memory",
        },
    },
    "tqdm": {"disable": False, "delay": 1},
    "serialization": {
        "enable_compression": False,
        "store_pickle": False,
    },
    "log": {
        "stdout": False,
        "level": logging.INFO,
        "catch_exceptions": False,
    },
    "dask": {
        "scheduler_address": "tcp://127.0.0.1:8786",
        "dashboard_address": ":8787",
        "scheduler_port": 8786,
        "client_timeout": "5s",
    },
    "doc": {"url": "https://mltraq.com/doc"},
}


class Options:
    """Handle options (preferences) for the package.

    Raises:
        RuntimeError: _description_

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """

    _instance = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.options = copy.deepcopy(default_options)
        return cls._instance

    def get(self, path):
        steps = path.split(".")

        d = self.options

        for step in steps:
            d = d[step]
        return d

    def set(self, path, value):
        *steps, last = path.split(".")

        d = self.options

        for step in steps:
            d = d.setdefault(step, {})
        d[last] = value

    def reset(self, path):
        steps = path.split(".")
        d = default_options
        for step in steps:
            d = d[step]
        self.set(path, d)

    @contextmanager
    def option_context(self, options):
        try:
            orig_options = copy.deepcopy(self.options)
            for k, v in options.items():
                self.set(k, v)
            yield self
        finally:
            self.options = orig_options


# This object handles the options for the package, process-wide.
# To change locally the preferences, use option_context.
options = Options.instance()
