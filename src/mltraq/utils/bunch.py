from __future__ import annotations

import itertools
from collections import OrderedDict
from typing import Iterator


class Bunch(OrderedDict):
    """
    Ordered dictionary whose elements can be accessed as object attributes.
    """

    def __init__(self, *args, **kwargs):
        """
        Same constructor of dict type. Additionally,
        if input is None, it returns an empty dict.
        """
        if args == (None,) and not kwargs:
            super().__init__()
        else:
            super().__init__(*args, **kwargs)

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

    def __str__(self):
        return Bunch.bunch_to_dict_deep(self).__str__()

    def __repr__(self):
        return self.__str__()

    def _repr_html_(self):
        return self.__str__()

    @classmethod
    def dict_to_bunch_deep(cls, d: dict) -> Bunch:
        """
        Deep-conversion of a dict to a Bunch.
        """

        if isinstance(d, dict):
            return Bunch({k: Bunch.dict_to_bunch_deep(v) for k, v in d.items()})
        else:
            return d

    @classmethod
    def bunch_to_dict_deep(cls, d: Bunch) -> dict:
        """
        Deep-conversion of a Bunch to a dict.
        We return dict objects without looking for Bunch values inside them.
        """

        if isinstance(d, Bunch):
            return {k: Bunch.bunch_to_dict_deep(v) for k, v in d.items()}
        else:
            return d

    def cartesian_product(self) -> Iterator[dict]:
        """
        Cartesian product of arguments:

        Given a list of key:value pairs, values are treated as lists
        and the Cartesian product of all possible combinations of
        values form each item is returned.
        """
        for instance in itertools.product(*self.values()):
            yield dict(zip(self.keys(), instance))
