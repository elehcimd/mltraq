from functools import partial

from mltraq import Run


def step_drop_fields(run: Run, fields=None):
    """
    Drop fields in the run.
    """

    if fields:
        for name in fields:
            if name in run.fields:
                del run.fields[name]


def drop_fields(*fields) -> callable:
    """
    It returns a callable step that drops a set of fields.
    """
    return partial(step_drop_fields, fields=fields)
