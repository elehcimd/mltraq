from functools import partial
from typing import Optional

from mltraq import Run, Sequence


def step_init_sequences(run: Run, names: Optional[list[str]] = None):
    """
    Initialize empty sequences to the run.
    """

    if names is None:
        names = []
    elif isinstance(names, str):
        names = [names]

    for name in names:
        run.fields[name] = Sequence()


def init_sequences(names: Optional[list[str]] = None) -> callable:
    """
    It returns a step function that initializes one or more empty sequences to the run.
    """
    return partial(step_init_sequences, names=names)
