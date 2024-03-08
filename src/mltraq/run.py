import logging
import random
from contextlib import contextmanager, nullcontext
from functools import partial
from typing import Any, Callable, List

import numpy as np
import pandas as pd

from mltraq.opts import Options, options
from mltraq.opts import options as global_options
from mltraq.storage.database import next_uuid
from mltraq.utils.bunch import Bunch
from mltraq.utils.exceptions import ExceptionWithMessage, InvalidInput, exception_message
from mltraq.utils.frames import reorder_columns
from mltraq.utils.sequence import Sequence

log = logging.getLogger(__name__)

StepsType = Callable | List[Callable] | None


class RunException(ExceptionWithMessage):
    """
    Created to communicate (not raised) a raised exception within a step function.
    """

    pass


class Run:
    """
    Instance of an experiment with fixed and variable parameters.
    """

    # Attributes to store and serialize.
    __slots__ = (
        "id_experiment",
        "id_run",
        "config",
        "params",
        "fields",
        "state",
        "exception",
        "vars",
        "steps",
    )
    __state__ = ("id_experiment", "id_run", "config", "params", "fields", "state", "exception")

    def __init__(
        self,
        id_experiment: str | None = None,
        id_run: str | None = None,
        steps: StepsType = None,
        config: dict | None = None,
        params: dict | None = None,
        fields: dict | None = None,
    ):
        """
        Create a new run, with:
        - `id_run`: ID of the run (UUID)
        - `steps`: Functions to apply to the run object to execute the run
        - `config`: Fixed parameters for all runs
        - `params`: Variable parameters, might be different for each run
        - `fields`: State of the `run`
        """

        self.id_experiment = id_experiment
        self.id_run = next_uuid() if id_run is None else id_run
        self.config = Bunch(config)
        self.params = Bunch(params)
        self.fields = Bunch(fields)
        self.state = Bunch()
        self.vars = Bunch()

        # Execution state and steps to be executed, and associated ID experiment.
        self.steps = normalize_steps(steps)
        self.exception = None

    def __getstate__(self):
        """
        Create state of the run for pickling. Only attributes in `__state__` are considered.
        """
        state = {key: getattr(self, key) for key in self.__state__}
        return state

    def __setstate__(self, state):
        """
        Set state of the run for unpickling.

        Note: __init__() is not called when unpickling an instance, this is why we need
        to initialise self.vars and self.steps (which are not part of __state__).
        """
        # Set state
        for k, v in state.items():
            self.__setattr__(k, v)
        # Set defaults
        self.vars = Bunch()
        self.steps = []

    @contextmanager
    def sysmon(self) -> Any:
        try:
            # Importing here to avoid circular import error.
            from mltraq.utils.sysmon import SystemMonitor

            sequence = Sequence()
            self.fields[options().get("sysmon.field_name")] = sequence
            sm = SystemMonitor(sequence)
            sm.start()
            yield sm
        finally:
            sm.stop()

    @contextmanager
    def datastream_client(self) -> Any:
        try:
            # Importing here to avoid circular import error.
            from mltraq.storage.datastream import DataStreamClient

            ds = DataStreamClient(run=self)
            for key, value in self.fields.items():
                if isinstance(value, Sequence):
                    log.debug(f"Linking field '{key}' to datastream")
                    value.set_stream(key, ds.send_sequence)
            yield ds
        finally:
            ds.cleanup()
            for value in self.fields.values():
                if isinstance(value, Sequence):
                    value.set_stream(None, None)

    def execute_func(self, steps: StepsType = None, config: dict | None = None, options: Options | None = None):
        """
        Return callable that executes self.run(steps=steps, config=config, options=options).
        """
        return partial(lambda run: run.execute(steps=steps, config=config, options=options), self)

    def execute(self, steps: StepsType | None = None, config: dict | None = None, options: Options | None = None):
        """
        Executes the `steps` callables on `self`, after:
        1. Setting the `config`
        2. Updating theglobal options to reflect `options`
        3. Initializing the numpy/random seeds to a seed that is unique to the run ID, honoring
        the option "reproducibility.random_seed".
        """

        # Set options to what has been passed by the driver process (the process that requested
        # the execution of the experiment).
        # This ensures that options changed at runtime are honored in runs execution.
        global_options().copy_from(options.values)

        # Determine random seed for this run, combining the UUID of the run and the
        # value of "reproducibility.random_seed". We initialise both Numpy and Random seeds.
        # This needs to be _after_ we update `global_options`, to reflect its correct values.
        random_seed = (hash(self.id_run) + global_options().get("reproducibility.random_seed")) % 2**32 - 1
        np.random.seed(random_seed)
        random.seed(random_seed)

        self.steps = normalize_steps(steps)
        self.config = Bunch(config)
        self.exception = None

        # Increment the UUID seed to ensure different incremental UUIDs across different runs.
        # For each run, we reserve 1B sequential UUIDs, above an initial reserved range of 1B.
        # The first 1B UUIDs: might be used by scripts to build the documentation, or other
        # code in the examples, not necessarily runnning inside runs.
        if options.get("reproducibility.sequential_uuids"):
            next_uuid(inc=(1 + self.id_run.int) * 10**9)

        # Start context managers, if not disabled.
        #
        # The datastream client requires fields to be defined before it starts, s.t. it has visibility on them,
        # and it can link Sequence objects to the stream.
        #
        # This is why `cm_sysmon` must precede `cm_datastream_client`.
        cm_datastream_client = nullcontext() if options.get("datastream.disable") else self.datastream_client()
        cm_sysmon = nullcontext() if options.get("sysmon.disable") else self.sysmon()

        with cm_sysmon, cm_datastream_client:
            for step in self.steps:
                try:
                    step(self)
                except Exception:  # noqa
                    # We want to catch ALL exceptions triggered within steps,
                    # s.t. we can communicate them back to the driver process.
                    self.exception = RunException(exception_message())
                    break

        self.clear_after_execution()

        return self

    def clear_after_execution(self):
        """
        Clear attributes that should not be accessed after the execution of steps.
        """
        self.steps = []
        self.vars = Bunch()
        self.config = Bunch()
        self.params = Bunch()

    def __str__(self) -> str:
        return f'Run(id="{self.id_run}")'

    def _repr_html_(self) -> str:
        return self.__str__()

    def df(self, max_level: int = 0) -> pd.DataFrame:
        """
        Return a Pandas dataframe representing the fields of the run, flattending `run.fields` up to `max_level`.
        """

        df = pd.json_normalize(self.fields | {"id_run": self.id_run}, max_level=max_level)
        return reorder_columns(df, ["id_run"])


def normalize_steps(steps: StepsType) -> List[Callable]:
    """
    Normalise `steps` to always return a list of callables (which might be empty).
    """

    if steps is None:
        return []
    elif callable(steps):
        return [steps]
    elif isinstance(steps, list):
        return steps
    elif isinstance(steps, tuple) and len(steps) == 1:
        # Passed as sole parameter of *args.
        return normalize_steps(steps[0])
    else:
        raise InvalidInput(f"Expected list of steps but received type {type(steps)}")
