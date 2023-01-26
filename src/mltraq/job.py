import multiprocessing

import joblib
from mltraq.utils.log import logger

try:
    # We expect this import to work if we want to use Dask.
    # Otherwise, not necessary.
    from distributed import get_client
except ImportError:
    pass

from typing import Callable, List

from mltraq.utils.progress import progress


class ProgressParallel(joblib.Parallel):
    """This class managed a progress bar monitoring the parallel execution of tasks."""

    def __init__(self, total: int = None, *args, **kwargs):
        """Create a new progress bar.

        Args:
            total (int, optional): Total number of tasks planned for execution.
                Defaults to None.
            args: Additional args to pass to the joblib.Parallel constructor.
            kwargs: Additional kwargs pass to the joblib.Parallel constructor.
        """

        self._total = total
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with progress(total=self._total) as self._pbar:
            return joblib.Parallel.__call__(self, *args, **kwargs)

    def print_progress(self) -> None:
        if self._total is None:
            self._pbar.total = self.n_dispatched_tasks
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()


def parallel(steps: List[Callable], n_jobs: int = -1) -> List[object]:
    """Execute a list of functions in parallel, returning their return values as a list.

    Args:
        steps (List[Callable]): Functions to execute, no parameters. You can
        use functools.partial to build suitable functions.
        n_jobs (int, optional): Level of parallelization, passed to Joblib. Defaults to -1.

    Returns:
        List[object]: List of return values of the executed functions.
    """

    # We leave -1 as default value for n_jobs, so that Joblib will figure out a reasonable value.

    # Instantiate the parallel executor
    p = ProgressParallel(n_jobs=n_jobs, total=len(steps))

    # Get the reeturn values, and return them as a lsit.
    # This function completes once all tasks return.

    rets = p(joblib.delayed(func)() for func in steps)
    return rets


class Job:
    """This class is the entry point for all things execution."""

    def __init__(
        self,
        tasks: List[Callable] = None,
        n_jobs: int = -1,
        backend: str = joblib.parallel.DEFAULT_BACKEND,
    ):
        """Prepare a new job to execute.

        Args:
            tasks (List[Callable], optional): List of functions to be executed. Defaults to None.
            n_jobs (int, optional): Number of tasks to execute in parallel, same meaning as in
            Joblib. Defaults to -1.
            backend (str, optional): Backend to use, same meaning as in Joblib.
            Defaults to joblib.parallel.DEFAULT_BACKEND.
        """

        self.tasks = tasks
        self.n_jobs = n_jobs
        self.backend = backend

    def execute(self):
        """Execute the plan.

        Returns:
            List[Run]: List of runs, after being passed as
            input to the functions.
        """

        n_jobs = self.n_jobs

        if self.backend == "dask":
            client = get_client()
            logger.info(f"Using backend: {self.backend}")
            logger.info(f"Dashboard: {client.dashboard_link}")
            logger.info(f"Scheduler: {client.scheduler.address}")
            if self.n_jobs == -1:
                n_jobs = len(client.scheduler_info()["workers"])
        elif self.backend == joblib.parallel.DEFAULT_BACKEND:
            if self.n_jobs == -1:
                n_jobs = multiprocessing.cpu_count()

        with joblib.parallel_backend(self.backend):
            logger.info(f"Executing {len(self.tasks)} tasks on {n_jobs} workers (backend:{self.backend})")

            executed_tasks = parallel(self.tasks, n_jobs=n_jobs)

            return executed_tasks
