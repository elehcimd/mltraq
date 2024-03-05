import json
from uuid import UUID


class MyEncoder(json.JSONEncoder):
    """
    JSON encoder supporting `UUID` and `type` types.
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, type):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def dumps(*args, **kwargs):
    """
    Same as json.dumps, but it supports also additional types
    as provided by `UUIDEncoder`.
    """
    return json.dumps(*args, **kwargs, cls=MyEncoder)
