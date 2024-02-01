import json
from collections.abc import KeysView
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    """
    Extension of JSONEncoder to support UUIDs.
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def stringify(d: object, max_len: int = 200) -> str:
    """
    Convert object `d` to JSON string, capping its approximate length to `max_len`.
    Useful to report/log stats of objects without risking too long outputs.
    """
    if isinstance(d, KeysView):
        d = list(d)

    s = json.dumps(d, cls=UUIDEncoder)
    if len(s) > max_len:
        if isinstance(d, list):
            s = s[:max_len] + " ...]"
        elif isinstance(d, dict):
            s = s[:max_len] + " ...}"
        else:
            s = s[:max_len] + " ..."
    return s
