import logging

import pandas as pd

from mltraq.experiment import Experiment
from mltraq.storage.database import Database
from mltraq.utils.enums import IfExists, enforce_enum
from mltraq.utils.text import stringify

log = logging.getLogger(__name__)


class Session:
    """
    Instantiate a new session handler.
    """

    __slots__ = ("db",)

    def __init__(self, url: str | None = None, ask_password: bool | None = None):
        """
        Create a new session handler, with `url` as database URL and `ask_password`
        triggering the interactive input of the password if True.
        By default, an in-memory SQLite database is initialised.
        """

        self.db = Database(url, ask_password=ask_password)

    def __str__(self) -> str:
        """
        Return a string with an overview of the available experiments in the linked database.
        Experiments that are not persisted are not visible.
        """
        experiment_names = self.ls()["name"].tolist()

        return (
            f"Session(db={stringify(self.db.url.render_as_string(hide_password=True))},"
            f" experiments({len(experiment_names)})={stringify(experiment_names)})"
        )

    def _repr_html_(self) -> str:
        return self.__str__()

    def create_experiment(self, name: str | None = None, **fields) -> Experiment:
        """
        Create a new experiment, binded to the database of this session:
        - `name` is optional, a 6 alphanum hash of ID experiment is used if missing.
        - `fields` is a dictionary loaded on `Experiment.fields`, with database persistence.
        """

        return Experiment(
            db=self.db,
            name=name,
            fields=fields,
        )

    def ls(self) -> pd.DataFrame:
        """
        Returns a Pandas dataframe with the list of persisted experiments.
        """
        return Experiment.ls(self.db)

    def load(self, name: str, unsafe_pickle: bool = False) -> Experiment:
        """
        Loads a persisted experiment by `name`. If `pickle` is True, it will
        attempt to reload the pickled Experiment object from database.
        Unpickling Experiment objects is unsafe, but powerful.
        Whenever possible, prefer the safe persistence of experiment states.
        """

        return Experiment.load(self.db, name, unsafe_pickle=unsafe_pickle)

    def persist(self, experiment: Experiment, name: str | None = None, if_exists: IfExists = "fail") -> Experiment:
        """
        Persist the experiment on the database linked by the session (as a copy), and return it.
        The database considered is the one of the session, allowing us to copy experiments
        between datasets. The new experiment will have a different UUID and its name will be retained.

        If `name` is passed, it is used as name of the experiment to persist.

        Parameter `if_exists` controls the behaviour in case of already existing experiment:
        - If "fail", an exception will be triggered (default).
        - If "replace", we experiment will be overwritten.
        """

        # Enforce if_exists value to be among valid ones.
        if_exists = enforce_enum(if_exists, IfExists)

        # Make a copy of the experiment linked to the session database and persist it.
        experiment_copy = experiment.copy_to(db=self.db, name=name)
        experiment_copy.persist(if_exists=if_exists)

        # We return the newly created experiment, the copy.
        return experiment_copy


def create_experiment(
    name: str | None = None, url: str | None = None, ask_password: bool | None = None, **fields
) -> Experiment:
    """
    Create a new experiment bound to a new session. Shortcut to create a single experiment.
    """

    return Session(url=url, ask_password=ask_password).create_experiment(name=name, **fields)
