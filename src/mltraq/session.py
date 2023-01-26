import copy

import pandas as pd
from mltraq.experiment import Experiment
from mltraq.options import options
from mltraq.storage.database import Database
from mltraq.utils.enums import IfExists, enforce_enum
from mltraq.utils.log import default_exception_handler, init_logging, logger
from mltraq.utils.text import stringify
from mltraq.version import __version__


class Session:
    """Instantiate the MLTRAQ handler, it can then be sued
    to create, query, manage experiments. You can instantiate one or more,
    they do work together nicely without interfering.
    """

    def __init__(self, url: str = None, ask_password=False):
        """Create a new MLTRAQ handler.

        Args:
            url (str, optional): Database URL. Defaults to db.default_url.
            echo (bool, optional): Enable SQLAlchemy logging. Defaults to False.
        """

        if url is None:
            url = options.get("db.url")

        init_logging()
        self.db = Database(url, ask_password=ask_password)
        logger.info(f"MLTRAQ v{__version__} initialized")

    def _repr_html_(self):
        experiment_names = self.ls()["name"].tolist()

        return (
            f"MLTRAQ(db={stringify(self.db.url.render_as_string(hide_password=True))},"
            f" experiments({len(experiment_names)})={stringify(experiment_names)})"
        )

    @default_exception_handler
    def add_experiment(self, name: str = None, **fields) -> Experiment:
        """Define a new experiment.

        Args:
            name (str, optional): Name of the experiment (must be unique). Defaults to None.
            steps (Union[Callable, List[Callable]], optional): Function(s) we want to apply to
            the input parameters. Defaults to None. kwargs (dict, optional): Fixed arguments to
            the functions. Defaults to None. attributes (dict, optional): Fixed experiment properties
            to be tracked. Defaults to None. parameter_grid (List, optional): Variable parameters
            to pass to the functions. Defaults to None.

        Returns:
            Experiment: The newly defined experiment, reaady to be executed.
        """

        return Experiment(
            db=self.db,
            name=name,
            fields=fields,
        )

    @default_exception_handler
    def ls(self, include_properties=False) -> pd.DataFrame:
        """List the tracked experiments.

        Returns:
            pd.DataFrame: Pandas dataframe.
        """
        return Experiment.ls(self.db, include_properties=include_properties)

    @default_exception_handler
    def load(self, name: str = None, pickle=False) -> Experiment:
        """Load an experiment from the database and return it.

        Args:
            name (str, optional): The name of the experiment. Defaults to None.

        Returns:
            Experiment: The loaded experiment.
        """
        return Experiment.load(self.db, name, pickle=pickle)

    @default_exception_handler
    def persist(self, experiment: Experiment, if_exists: IfExists = "fail") -> Experiment:
        """Persist the experiment to the database (not necessarily
        the one used to track it initially).

        Args:
            experiment (Experiment): Experiment object to be persisted.
            if_exists (IfExists, optional): Either "replace" of "fail" in case
            the experiment name is already present. Defaults to "fail".

        Returns:
            Experiment: The persisted experiment.
        """

        # Enforce if_exists value
        if_exists = enforce_enum(if_exists, IfExists)

        # We make a copy of the experiment, and change the database reference.
        # We can then use all its methods, including persist(...).
        experiment = copy.deepcopy(experiment)
        experiment.db = self.db
        experiment.persist(if_exists=if_exists)
        return experiment

    def query(self, query: str, verbose: bool = False) -> pd.DataFrame:
        """Query the experiment's table

        Args:
            query (str): SQL query. "{ee}" occurrences are substituted with the experiments table name.
            verbose (bool, optional): If true, print the resulting query. Defaults to False.

        Returns:
            pd.DataFrame: Result of the query.
        """

        return self.db.pandas(query.format(ee=options.get("db.experiments_tablename")))

    def version(self):
        """Log MLTRAQ version"""
        logger.info(f"MLTRAQ v{__version__}")
