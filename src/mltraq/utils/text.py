import json
from collections.abc import KeysView
from textwrap import wrap


def stringify(d: object, max_len=200):
    """Convert string to object, capping its approximate length

    Args:
        d (object): Object to stringify
        max_len (int, optional): Max length (approximate, we'll add
            some dots that are not taken into account). Defaults to 200.

    Returns:
        _type_: String representation of the object.
    """
    if isinstance(d, KeysView):
        d = list(d)

    s = json.dumps(d)
    if len(s) > max_len:
        if isinstance(d, list):
            s = s[:max_len] + " ...]"
        elif isinstance(d, dict):
            s = s[:max_len] + " ...}"
        else:
            s = s[:max_len] + " ..."
    return s


def wprint(text):
    """print string, wrapping it.

    Args:
        text (_type_): string to wrap and print.

    Returns:
        _type_: stats about the wrapped string.
    """
    lstats = []
    for idx, wrapped_text in enumerate(wrap(text)):
        lstats.append(len(wrapped_text))
        if idx == 0:
            print(wrapped_text)
        else:
            print(f"  {wrapped_text}")

    return lstats
