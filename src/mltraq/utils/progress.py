import warnings

from mltraq import options
from mltraq.extras.environment import is_pyodide, is_tty

with warnings.catch_warnings():
    # ignore warnings while setting up tqdm auto
    warnings.simplefilter("ignore")

    from tqdm.auto import tqdm

    if is_pyodide():
        # avoid error in case of pyodide environment
        tqdm.monitor_interval = 0


# if not TTY or tqdm explicitly disabled, disable it.
disable = not is_tty() or options.get("tqdm.disable")


def progress(*args, **kwargs):
    """Rerutn a tqdm object with some default values.

    Returns:
        _type_: _description_
    """
    return tqdm(*args, **kwargs, leave=False, delay=options.get("tqdm.delay"), disable=disable)
