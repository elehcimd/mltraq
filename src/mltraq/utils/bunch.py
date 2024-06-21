from __future__ import annotations

import itertools
import os
from collections import OrderedDict
from typing import Iterator

from mltraq.opts import options


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


class BunchEvent(Bunch):
    """
    Bunch with function triggers on events "on_setattr", "on_getattr".
    Useful to implement assertions, debugging procedures and alerts.
    """

    def __init__(self, *args, **kwargs):
        """
        Same constructor of Bunch, with initializations.
        """

        self.clear_triggers()
        super().__init__(*args, **kwargs)

    def clear_triggers(self):
        """
        Initialize triggers, removing existing ones, if any.
        """

        self._on_setattr_triggers = {}
        self._on_getattr_triggers = {}

    def on_setattr(self, key, func):
        """
        Add trigger to call `func` with parameter `key`, `value` on setattr events.
        """

        if key in self._on_setattr_triggers:
            triggers = self.on_setattr_triggers[key]
        else:
            triggers = []
            self._on_setattr_triggers[key] = triggers

        triggers.append(func)

    def on_getattr(self, key, func):
        """
        Add trigger to call `func` with parameter `key`, `value` on getattr events.
        """

        if key in self._on_getattr_triggers:
            triggers = self.on_getattr_triggers[key]
        else:
            triggers = []
            self._on_getattr_triggers[key] = triggers

        triggers.append(func)

    def __setitem__(self, key, value):
        if not key.startswith("_on_") and key in self._on_setattr_triggers:
            for func in self._on_setattr_triggers[key]:
                func(key, value)
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):

        value = super().__getitem__(key)

        if not key.startswith("_on_") and key in self._on_getattr_triggers:
            for func in self._on_getattr_triggers[key]:
                func(key, value)

        return value

    def __getattr__(self, key):
        return self[key]


class BunchStore:
    """
    Basic key-value store on filesystem for a single Bunch object.
    """

    def __init__(self, pathname: str | None = None):
        """
        Initialize and load the key-value store.
        """

        # Importing here to avoid circular dependency.
        from mltraq.storage.serialization import deserialize, serialize  # noqa: F401

        # Storing eveyrthing as part of _meta attribute, s.t. we can use
        # attr and item setters/getters with less overhead.
        self._meta = Bunch()
        self._meta.deserialize = deserialize
        self._meta.serialize = serialize
        self._meta.pathname = options().default_if_null(pathname, "bunchstore.pathname")
        self._meta.data = Bunch()

        # Try to read and write the inner Bunch, ensuring that the pathname is readable/writeable.
        self.read()
        self.write()

    def read(self):
        """
        Load inner Bunch from file (if available).
        """
        if os.path.exists(self._meta.pathname):
            self._meta.data = self._meta.deserialize(open(self._meta.pathname, "rb").read())

    def __setitem__(self, key, value):
        self._meta.data[key] = value
        self.write()

    def __getitem__(self, key):
        self.read()
        return self._meta.data[key]

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key != "_meta":
            self[key] = value
        else:
            super().__setattr__(key, value)

    def __len__(self):
        return len(self._meta.data)

    def __delitem__(self, key):
        del self._meta.data[key]

    def __iter__(self):
        return iter(self._meta.data)

    def data(self):
        return self._meta.data

    def write(self):
        """
        Overwrite BunchStore file on filesystem, using a temporary file
        to avoid concurrency issues.
        """
        with open(f"{self._meta.pathname}.tmp", "wb") as f:
            f.write(self._meta.serialize(self._meta.data))
        os.replace(f"{self._meta.pathname}.tmp", self._meta.pathname)
