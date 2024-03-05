from functools import partial

from mltraq import Run


def step_init_fields(run: Run, fields: dict | None = None):
    """
    Initialize fields in the run.
    """

    if fields is None:
        fields = {}

    for name, value in fields.items():
        run.fields[name] = value


def init_fields(fields: dict | None = None) -> callable:
    """
    It returns a callable step that initializes a set of fields.
    """
    return partial(step_init_fields, fields=fields)
