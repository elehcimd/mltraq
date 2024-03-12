from __future__ import annotations

import copy
import logging
import random
import uuid
from contextlib import contextmanager
from typing import Callable

import pandas as pd
from sqlalchemy.orm import load_only

from mltraq.opts import options
from mltraq.run import Run
from mltraq.runs import Runs
from mltraq.storage import models, serialization
from mltraq.storage.database import Database, hash_uuid, next_uuid, pandas_query, sanitize_table_name
from mltraq.storage.datastore import DataStoreIO
from mltraq.utils.bunch import Bunch
from mltraq.utils.enums import IfExists, enforce_enum
from mltraq.utils.exceptions import ExceptionWithMessage, InvalidInput
from mltraq.utils.frames import reorder_columns
from mltraq.version import __version__

log = logging.getLogger(__name__)


class PickleNotFoundException(ExceptionWithMessage):
    """
    Exception raised if the pickled experiment is not found.
    """

    def __init__(self, name):
        return super().__init__(f"Pickle not found for experiment '{name}'.")


class ExperimentAlreadyExists(ExceptionWithMessage):
    """
    Raised if we try to overwrite an existing experiment, with if_exists="fail".
    """

    def __init__(self, name):
        return super().__init__(f"Experiment '{name}'already exists, pass if_exists=\"replace\" to overwrite.")


class ExperimentNotFoundException(ExceptionWithMessage):
    """
    Raised if we try to load an experiment that is not found in the database.
    """

    def __init__(self, name):
        return super().__init__(f"Experiment '{name}' not found. List with .ls() the available experiments.")


class Experiment:
    """
    Class modeling a new experiment. Class attribute `model_cls` is the SQLAlchemy model representing the
    "experiments" table in the database.
    """

    # model_cls is the SQLAlchemy model mapped to this class.
    model_cls = models.Experiment

    __slots__ = ("id_experiment", "name", "fields", "runs", "db")
    __state__ = ("id_experiment", "name", "fields", "runs")

    def __init__(
        self,
        db: Database | None = None,
        id_experiment: str | None = None,
        name: str | None = None,
        fields: dict | None = None,
        runs: list[Run] | None = None,
    ):
        """
        Crete a new experiment linked to database `db`.
        """

        self.db = db
        self.id_experiment = next_uuid() if id_experiment is None else id_experiment
        self.name = hash_uuid(self.id_experiment) if name is None else name
        self.fields = Bunch(fields)
        self.runs = Runs(runs)

    def __getstate__(self):
        """
        Build state for pickling.
        """
        state = {key: getattr(self, key) for key in self.__state__}
        return state

    def __setstate__(self, state):
        """
        Load state for unpickling.
        """
        for k, v in state.items():
            self.__setattr__(k, v)
        self.db = None

    @contextmanager
    def run(self):
        """
        Returns a new Run object as temporary context.
        """

        try:
            run = Run(id_experiment=self.id_experiment)
            yield run
        finally:
            run.clear_after_execution()
            self.runs.add(run)

    def __str__(self) -> str:
        """
        Compact representation of the experiment with its runs.
        """
        return f'Experiment(name="{self.name}", runs.count={len(self.runs)}, id="{self.id_experiment}")'

    def _repr_html_(self) -> str:
        return self.__str__()

    def add_runs(self, **params) -> Experiment:
        """
        Add runs to experiment. `params` is a dictionary containing lists and it's used to generate
        parameters for experiments from its Cartesian product.
        """

        params_list = list(Bunch(params).cartesian_product())
        random.Random(options().get("reproducibility.random_seed")).shuffle(params_list)

        if len(params_list) == 1 and params_list[0] == {}:
            raise InvalidInput(
                "Invalid parameters grid, no added runs. This is likely due to a parameter associated to zero possible"
                " values."
            )

        for params in params_list:
            self.add_run(**params)

        return self

    def merge_runs(self, runs) -> Experiment:
        """
        Given a list of `runs`, merge them into the experiment.
        """
        self.runs |= runs
        return self

    def add_run(self, **params) -> Experiment:
        """
        Add single run with a list of parameters.
        """
        run = Run(id_experiment=self.id_experiment, params=params)
        self.runs.add(run)
        return self

    def get_tablename(self) -> str:
        """
        Return the table name of the experiment.
        The table name is constructed by concatenating the option prefix "database.experiment_tableprefix"
        and the experiment name, sanitizing the resulting value to consier only characters [^0-9a-zA-Z].
        """

        return sanitize_table_name(f"{options().get('database.experiment_tableprefix')}{self.name}")

    def load_runs(self, meta: dict) -> Experiment:
        """
        Load self.runs from database, using the serialization config as found in `meta`.
        """

        # Retrieve the table of the experiment.
        df = self.db.query(self.db.query_table(self.get_tablename()))
        # Columns have type `sqlalchemy.sql.elements.quoted_name`, convert to str
        # (this avoids explicit handling of this type in serialization.)
        df.columns = [str(s) for s in df.columns]

        # Take care of deserialization
        for col_name in meta.runs.columns.serialized:
            df[col_name] = df[col_name].map(serialization.deserialize)

        def series_to_run(row: pd.Series) -> Run:
            """
            Given a `row` fetched from the database, reconstruct the `run` represented by it.
            """
            fields = row[meta.runs.columns.serialized + meta.runs.columns.non_serialized].to_dict()
            run = Run(id_run=row["id_run"], fields=fields)
            return run

        # Reconstruct runs with their fields
        self.runs = Runs(df.apply(lambda row: series_to_run(row), axis=1).tolist())

    def copy_to(self, name: str | None = None, db: Database | None = None) -> Experiment:
        """
        Return a deep copy of the experiment, setting `name` and `db` if provided.
        A new UUID for the copy of the experiment is always generated.
        If the name of the experiment was the hashed UUID, in case of no `name`,
        a `name` value aligned with the new UUID is generated from its hash.
        """

        experiment = copy.deepcopy(self)
        experiment.id_experiment = next_uuid()

        if name:
            experiment.name = name
        else:
            if self.id_experiment == hash_uuid(self.id_experiment):
                experiment.name = hash_uuid(experiment.id_experiment)
            else:
                experiment.name = self.name

        if db:
            experiment.db = db
        else:
            experiment.db = self.db

        return experiment

    @classmethod
    def load_pickle(cls, db: Database, name: str) -> Experiment:
        """
        Load an Experiment object from its pickle, provided a `db` and an experiment `name`.
        This is *unsafe* and error-prone, you should prefer the offered persistence of `the fields attribute`.
        """

        log.debug(f"Loading experiment '{name}' (pickle)")

        with db.session() as session:
            # Retrieving only the "pickle" column
            record = (
                session.query(cls.model_cls)
                .options(load_only(Experiment.model_cls.unsafe_pickle))
                .filter_by(name=name)
                .first()
            )

            if record is None:
                raise ExperimentNotFoundException(name)

            if record.unsafe_pickle is None:
                raise PickleNotFoundException(name)

            experiment = serialization.unsafe_unpickle(record.unsafe_pickle)

            # Pickling/unpickling experiments excludes the .db attribute,
            # which we can set now to the provided `db`.
            experiment.db = db

            return experiment

    def reload(self, unsafe_pickle: bool = False) -> Experiment:
        """
        Reload the experiment from database (discarding its current state).
        """
        return Experiment.load(self.db, self.name, unsafe_pickle=unsafe_pickle)

    @classmethod
    def load(
        cls, db: Database, name: str | None = None, id_experiment: uuid.UUID | None = None, unsafe_pickle: bool = False
    ):
        """
        Load experiment `name` (or `id_experiment`) from `db`. If `pickle` is True, load
        it from its pickled Experiment object (unsafe).
        """

        log.debug(f"Loading experiment id_experiment='{id_experiment}' name='{name}'")

        if unsafe_pickle:
            return cls.load_pickle(db, name)

        with db.session() as session:

            # Load all columns but "pickle", which might be heavy.
            columns = [
                Experiment.model_cls.id_experiment,
                Experiment.model_cls.name,
                Experiment.model_cls.meta,
                Experiment.model_cls.fields,
            ]

            if id_experiment:
                record = (
                    session.query(cls.model_cls)
                    .options(load_only(*columns))
                    .filter_by(id_experiment=id_experiment)
                    .first()
                )
            elif name:
                record = session.query(cls.model_cls).options(load_only(*columns)).filter_by(name=name).first()
            else:
                raise InvalidInput("You must provide either `name` or `id_experiment`")

            if record is None:
                raise ExperimentNotFoundException(name)

            # Create Experiment object from loaded columns.
            experiment = Experiment(
                db=db,
                id_experiment=record.id_experiment,
                name=record.name,
                fields=serialization.deserialize(record.fields),
            )

            # Deserialize "meta" column, required to load runs.
            meta = serialization.deserialize(record.meta)
            if meta.runs.count > 0:
                experiment.load_runs(meta=meta)

            return experiment

    def __call__(self, *args, **kwargs) -> Experiment:
        """
        Shortcut to .execute(...).
        """
        return self.execute(*args, **kwargs)

    def execute(
        self,
        steps: Callable | list[Callable] | None = None,
        config: dict | None = None,
        backend: str | None = None,
        n_jobs: int | None = None,
        args_field: str | None = None,
    ):
        """
        Execute the experiment, by executing its runs:

        - `steps` is an ordered list of functions applied to all runs in `self.Runs`
        - `config` is passed to the runs (constant), accessible as `Run.config`
        - `backend` and `n_jobs` are passed to joblib.Parallel
        - `args_field` is the optional field name used to store/load both `Run.config` and `Run.params`
        """

        if len(self.runs) == 0:
            # No runs defined, add the default one.
            self.add_run()

        self.runs.execute(steps=steps, config=config, backend=backend, n_jobs=n_jobs, args_field=args_field)
        return self

    def record(
        self,
        meta: dict | None = None,
        store_unsafe_pickle: bool | None = None,
    ) -> models.Experiment:
        """
        Build an SQLAlchemy ORM object from the existing Experiment object.
        """

        store_unsafe_pickle = options().default_if_null(store_unsafe_pickle, "serialization.store_unsafe_pickle")

        return self.model_cls(
            id_experiment=self.id_experiment,
            name=self.name,
            fields=serialization.serialize(self.fields),
            unsafe_pickle=serialization.unsafe_pickle(self) if store_unsafe_pickle else None,
            meta=serialization.serialize(meta),
        )

    def get_metadata(self) -> dict:
        """
        Return a tree-like dictionary with properties about the experiment and its
        serialization strategy.
        """
        meta = Bunch()
        meta.runs = serialization.meta_runs(self.runs, table_name=self.get_tablename())
        meta.serialization = serialization.meta()
        meta.mltraq = Bunch()
        meta.mltraq.version = __version__
        return meta

    def persist(
        self,
        if_exists: IfExists = IfExists["fail"],
        store_unsafe_pickle: bool | None = None,
    ):
        """
        Persist an experiment to the bound database, honoring `if_exists` the `store_unsafe_pickle`.
        If `if_exists` is set to "fail" and the experiment exists, an exception will be triggered.
        To overwrite existing experiments, set `if_exists` to "replace".
        """

        log.debug(f"Persisting experiment (table name: {self.get_tablename()})")

        # Ensure a valid value for if_exists.
        if_exists = enforce_enum(if_exists, IfExists)

        # Delete experiment from database/datastore.
        self.delete(if_exists)

        # If there are no runs, add the default one.
        if len(self.runs) == 0:
            self.add_run()

        # Generate metadata about experiment to persist.
        # We must count the number of runs, so important to
        # call .get_metadata() AFTER adding the default run, if necessary.
        meta = self.get_metadata()

        # Insert row in "experiments" table.
        with self.db.session() as session:
            session.add(self.record(meta=meta, store_unsafe_pickle=store_unsafe_pickle))
            session.commit()

        # Create and insert rows in "experiment_..." table.
        df_runs, dtype = serialization.runs_to_sql(self.id_experiment, meta, self.runs)
        self.db.pandas_to_sql(df_runs, meta.runs.table_name, if_exists.name, dtype=dtype)

        return self

    def delete(self, if_exists: IfExists = IfExists["delete"]):
        """
        Delete experiment from database, honoring `if_exists`.
        """

        # Ensure a valid value for if_exists
        if_exists = enforce_enum(if_exists, IfExists)

        with self.db.session() as session:
            if session.query(self.model_cls).filter_by(name=self.name).count() > 0:
                # If we find the record ...
                if if_exists in [IfExists["replace"], IfExists["delete"]]:
                    # And we are fine deleting it, proceed.
                    session.query(Experiment.model_cls).filter(Experiment.model_cls.name == self.name).delete()
                else:
                    # Otherwise, raise an exception.
                    raise ExperimentAlreadyExists(
                        f"Experiment '{self.name}' already existing, use if_exists=\"replace\" to overwrite it."
                    )
            session.commit()

        # Drop also the entire "experiment_..." table.
        self.db.drop_table(self.get_tablename())

        # Drop datastore documents of experiment, if any.
        DataStoreIO.delete(relative_path_prefix=str(self.id_experiment))

    def df(self, max_level=0) -> pd.DataFrame:
        """
        Return a Pandas dataframe representing the experiment, flattening
        the fields up to `max_level`.
        """

        df_experiment = pd.json_normalize(
            self.fields | {"id_experiment": self.id_experiment, "name": self.name},
            max_level=max_level,
        )

        return reorder_columns(df_experiment, ["id_experiment", "name"])

    @classmethod
    def ls(cls, db: Database) -> pd.DataFrame:
        """
        Return a Pandas Dataframe with a list of experiments referenced in table "experiments in `db`.
        Three columns are returned:
        - `id_experiment`: ID of the experiment (UUID)
        - `name`: Name of the experiment
        - `table_name` Table name with runs of the experiment
        """

        with db.session() as session:
            columns = [Experiment.model_cls.id_experiment, Experiment.model_cls.name]
            df_experiments = pandas_query(
                session.query(Experiment.model_cls).options(load_only(*columns)),
                session,
            )

            df_experiments["table_name"] = df_experiments["name"].apply(
                lambda name: sanitize_table_name(f"{options().get('database.experiment_tableprefix')}{name}")
            )

            return df_experiments
