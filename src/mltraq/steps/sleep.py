import time
from functools import partial

from mltraq import Run


def step_sleep(run: Run, duration: float = 0):
    """
    Sleep for `duration` seconds.
    """

    time.sleep(duration)


def sleep(duration: float = 0) -> callable:
    """
    It returns a callable step that sleeps for `duration` seconds.
    """
    return partial(step_sleep, duration=duration)
