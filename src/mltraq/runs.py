from __future__ import annotations

import logging
import random
from types import GeneratorType
from typing import Any, Generator, List, Optional, Tuple, Union

import pandas as pd
from joblib.parallel import DEFAULT_BACKEND

from mltraq.job import Job
from mltraq.opts import options
from mltraq.run import Run, StepsType, normalize_steps
from mltraq.utils.bunch import Bunch
from mltraq.utils.exceptions import ExceptionWithMessage, InvalidInput
from mltraq.utils.frames import reorder_columns
from mltraq.utils.text import stringify

log = logging.getLogger(__name__)

# `Runs` cannot be added as not yet defined
RunsListType = Union[Run, List[Run], Tuple[Run], None]


class RunsException(ExceptionWithMessage):
    """
    Raised in case of exceptions within runs.
    """

    pass


class Runs(dict):
    """
    Dict handling of a collection of Run objects.
    """

    def __init__(self, runs: Union[RunsListType, Runs]):
        """
        Initialise the runs.
        """

        runs = normalize_runs(runs)
        super().__init__({run.id_run: run for run in runs})

    def add(self, *runs: Union[RunsListType, Runs]):
        """
        Add run(s).
        """
        runs = normalize_runs(runs)
        self.update({run.id_run: run for run in runs})

    def __or__(self, runs: Union[RunsListType, Runs]) -> Runs:
        return Runs(dict(self) | dict(runs))

    def __ior__(self, runs: Union[RunsListType, Runs]) -> Runs:
        return self.__or__(runs)

    def first(self) -> Run:
        """
        Return a run, no guarantees on which one.
        """
        return self[next(iter(self))]

    def apply(self, func: callable) -> Any:
        return [func(run) for run in self.values()]

    def next(self) -> Run:
        """
        Add a new run and return it.
        """

        run = Run()
        self[run.id_run] = run
        return run

    def df(self, max_level: int = 0) -> pd.DataFrame:
        """
        Return a pandas DataFrame representation of the collection of runs,
        flattending run.fields up to `max_level`.
        """

        if len(self) == 0:
            return pd.DataFrame(columns=["id_run"])

        df = pd.json_normalize([run.fields | {"id_run": run.id_run} for run in self.values()], max_level=max_level)
        return reorder_columns(df, ["id_run"])

    def handle_args_field(self, name: str, config: dict) -> dict:
        """
        Save/reload to/from run.fields[name] both run.params and run.config in a dictionary.
        """

        for run in self.values():
            if name not in run.fields:
                run.fields[name] = Bunch(config=Bunch(config), params=run.params)
                ret_config = config
            else:
                if config or run.params:
                    raise InvalidInput("Trying to overwrite existing `config` or `params` via `args_field`.")
                ret_config = run.fields[name].config
                run.params = run.fields[name].params
        return ret_config

    def execute(  # noqa: C901
        self,
        steps: StepsType,
        config: Optional[dict] = None,
        backend: Optional[str] = None,
        n_jobs: Optional[int] = None,
        args_field: Optional[str] = None,
    ):
        """
        Given an existing collection of runs, execute `steps` on them, considering `config`, `backend`, and `n_jobs`.
        `backend` and `n_jobs` are passed to joblib.Parallel.
        `args_field` is the optional field name used to store/load both `Run.config` and `Run.params`.
        """

        if len(self) == 0:
            raise RunsException("No runs to execute.")

        steps = normalize_steps(steps)

        if len(steps) == 0:
            raise RunsException("No step functions to execute.")

        args_field = options().get("execution.args_field", prefer=args_field)
        if args_field:
            config = self.handle_args_field(args_field, config)

        if options().get("execution.backend") == DEFAULT_BACKEND and options().get("execution.loky_chdir"):
            # Make sure that the workers' current directory is aligned
            # with the main process current directory, this ensures
            # that using `tmpdir_ctx` in examples and tests doesn't fail,
            # without having to deal with this explicitly.
            # This makes sense only with the loky backend, the default one.
            # See https://github.com/joblib/joblib/issues/945.
            from mltraq.steps.chdir import chdir

            steps = [chdir()] + steps

        if not options().get("codelog.disable"):
            from mltraq.steps.codelog import codelog

            steps = [codelog(steps)] + steps

        # List of functions to execute.
        task_funcs = [run.execute_func(steps=steps, config=config, options=options()) for run in self.values()]

        # Randomize order of tasks (in place), so that partial results are more representative
        # of the entire set of runs being executed (and errors might be catched earlier).
        random.Random(options().get("reproducibility.random_seed")).shuffle(task_funcs)

        # Execute runs.
        executed_runs: Union[Generator[Run, None, None], list[Run]] = Job(
            task_funcs, n_jobs=n_jobs, backend=backend
        ).execute()

        if isinstance(executed_runs, GeneratorType):
            # If joblib returned a generator, we handle it, checking for errors and interrupting as soon as possible.
            executed_runs_iter = executed_runs
            executed_runs = []

            while True:
                try:
                    run = next(executed_runs_iter)
                    executed_runs.append(run)
                    if run.exception is not None:
                        # A step failed, interrupt
                        break
                except StopIteration:
                    # No more tasks, interrupt
                    break

        # Check for exceptions, and raise first one encountered.
        for run in executed_runs:
            if run.exception is not None:
                n_tasks = len(task_funcs)
                n_executed = len(executed_runs)
                ratio_executed = n_executed / n_tasks
                log.debug("Encountered exception in task, propagating to main process")
                log.debug(
                    f"Executed {n_executed} of {n_tasks} tasks ({int(ratio_executed*100)}%) "
                    f"with return_as={options().get('execution.return_as')}"
                )
                raise run.exception

        # Point the runs to new instances that contain the result of the execution.
        for run in executed_runs:
            self[run.id_run] = run

    def __str__(self) -> str:
        return f"Runs(keys({len(self)})={stringify(self.keys())})"

    def _repr_html_(self) -> str:
        return self.__str__()


def normalize_runs(runs: Union[RunsListType, Runs]) -> list[Run]:
    """
    Normalise `runs` to always return a list of Run objects (which might be empty).
    """

    if runs is None:
        return []
    elif isinstance(runs, Run):
        return [runs]
    elif isinstance(runs, Runs):
        return runs.values()
    elif isinstance(runs, list):
        return runs
    elif isinstance(runs, dict):
        return runs.values()
    elif isinstance(runs, tuple) and len(runs) == 1:
        # Passed as sole parameter of *args. E.g., in Runs.add(...).
        return normalize_runs(runs[0])
    else:
        raise InvalidInput(f"Expected Run objects but received type {type(runs)}")
