import itertools


class ObjectDictionary(dict):
    """Dictionary whose elements can be accessed as object attributes."""

    def __init__(self, *args, **kwargs):
        """Same constructor of dict type."""
        if args == (None,) and not kwargs:
            super().__init__()
        else:
            super().__init__(*args, **kwargs)

    def __reduce__(self):
        """If serializing, we convert the object to a dictionary.

        Returns:
            _type_:
        """
        return self.__class__, (dict(self),)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(key) from e

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(key) from e

    @classmethod
    def deep(cls, d):
        """Deep-conversion of a dictionary to a ObjectDictionary.

        Args:
            d (_type_): dict object to convert.

        Returns:
            _type_: ObjectDictionary object.
        """
        if isinstance(d, ObjectDictionary):
            return d
        elif not isinstance(d, dict):
            return d
        else:
            return ObjectDictionary({k: ObjectDictionary.deep(v) for k, v in d.items()})


def ordered_dict_equality(p, q):
    """Equality of dictionaries, considering also the position of their keys.

    Args:
        p (_type_): First dictionary
        q (_type_): Second dictionary

    Returns:
        _type_: If the two dictionaries are equivalent and
            their keys are sorted equally, it returns True. False otherwise.
    """
    return p == q and all(k1 == k2 for k1, k2 in zip(p, q))


def product_dict(**kwargs):
    """Cartecian product of arguments.

    Yields:
        _type_: Iterator returning dictionaries of each possible combination.
    """
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))
