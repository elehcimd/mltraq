from functools import partial

from mltraq import Run, Sequence


def step_create_sequences(run: Run, names: list[str] | None = None):
    if names is None:
        names = []
    elif isinstance(names, str):
        names = [names]

    for name in names:
        run.fields[name] = Sequence()


def create_sequences(names: list[str] | None = None) -> callable:
    return partial(step_create_sequences, names=names)
