import getpass
import logging
import re
import uuid
from functools import partial
from typing import Callable, Iterator, List

import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, inspect, sql
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.selectable import Select
from tqdm.auto import tqdm

from mltraq.opts import options
from mltraq.storage.models import Base
from mltraq.utils.bunch import Bunch
from mltraq.utils.enums import IfExists
from mltraq.utils.exceptions import InvalidInput

QueryType = Query | str | Select | TextClause

log = logging.getLogger(__name__)

# If options "reproducibility.sequential_uuids" set to true,
# next UUID (as int) to be used.
next_sequential_uuid = 0


class Database:
    """
    This class is the entry point for all things SQLAlchemy, and it represents the link
    to the database for experiments. It uses the SQAlchemy 2.0 API interface.
    """

    # Attributes to store and serialize.
    __slots__ = ("params", "url", "session", "engine")
    __state__ = ("params",)

    def __init__(
        self,
        url: str | None = None,
        ask_password: bool | None = None,
        echo: bool | None = None,
        pool_pre_ping: bool | None = None,
    ):
        """
        Initialize connection to a new database, with connection `url`,
        asking interactively for a password if `ask_password` is True.
        Options `echo` and `pool_pre_ping` are passed to SQLAlchemy.
        (if None, their defaults do apply.)

        If `lazy` is True, do not initialize the connection to the database.
        Useful to handle unpickling of Database objects.
        """

        # Save original parameters, including the used options
        echo = options().default_if_null(echo, "database.echo")
        pool_pre_ping = options().default_if_null(pool_pre_ping, "database.pool_pre_ping")
        self.params = Bunch(url=url, ask_password=ask_password, echo=echo, pool_pre_ping=pool_pre_ping)

        self.init_url(url, ask_password)

        log.debug(f"Created DB link: '{self.url.render_as_string(hide_password=True)}'")

        # Set up database connector, without establishing any connection yet
        # https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic
        self.engine = create_engine(self.url, echo=self.params.echo, pool_pre_ping=self.params.pool_pre_ping)

        # Session factory
        self.session = sessionmaker(self.engine)

        # create tables if missing
        Base.metadata.create_all(self.engine)

    def copy(self):
        """
        Return an independent thread-safe copy of the object,
        linked to the same URL and using the same options.
        """
        return Database(
            self.url.render_as_string(hide_password=False),
            echo=self.params.echo,
            pool_pre_ping=self.params.pool_pre_ping,
        )

    def init_url(self, url: str, ask_password: bool):
        """
        Initialize the URL to the database, handling defaults,
        special cases and interactive passwords.
        """
        url = options().default_if_null(url, "database.url")
        ask_password = options().default_if_null(ask_password, "database.ask_password")

        if url.startswith("postgres://"):
            # Re-introduce support for the deprecated and then dropped "postgres://" prefix
            url = url.replace("postgres://", "postgresql://")

        self.url = make_url(url)
        if ask_password:
            self.url = self.url.set(password=getpass.getpass(prompt="Password: "))

    def __getstate__(self) -> dict:
        """
        Create state for pickling. Only attributes in `__state__` are considered.
        """
        state = {key: getattr(self, key) for key in self.__state__}
        return state

    def __setstate__(self, state):
        """
        Set state for unpickling.
        """
        for k, v in state.items():
            self.__setattr__(k, v)
        self.__init__(url=self.params.url, ask_password=self.params.ask_password)

    def __str__(self) -> str:
        return f'Database(db="{self.url.render_as_string(hide_password=True)}")'

    def _repr_html_(self) -> str:
        return self.__str__()

    def pandas_to_sql(self, df: pd.DataFrame, name: str, if_exists: IfExists, dtype: dict | None = None):
        """
        Insert a Pandas dataframe `df` as a new database table `name`.
        If `if_exists` == "replace", it overwrite existing tables.
        If `if_exists` == "fail", it will trigger an exception if the table exists.
        `dtype` passes the types to consider, if any.

        Progress bar with tqdm.
        Option "database.query_write_chunk_size" controls the number of rows to write per chunk.
        """

        with self.session() as session:
            if len(df) == 0 or options().get("tqdm.disable"):
                # In case of zero rows, chunked inserts won't create the table.
                # This is why, for zero rows or in case of no tqdm, we swich to a
                # single call to df.to_sql(...).
                df.to_sql(name, session.bind, if_exists=if_exists, index=False, dtype=dtype)
            else:
                dfs = chunker(df, options().get("database.query_write_chunk_size"))
                funcs = []
                for idx, df_chunk in enumerate(dfs):

                    def process_chunk(df_chunk, idx):
                        df_chunk.to_sql(
                            name, session.bind, if_exists=if_exists if idx == 0 else "append", index=False, dtype=dtype
                        )
                        return len(df_chunk), None

                    funcs.append(partial(process_chunk, df_chunk, idx))
                tqdm_chunks(funcs, len(df))

    def get_table_names(self) -> List[str]:
        """
        Return table names.
        """
        with self.session() as session:
            return [str(s) for s in inspect(session.bind).get_table_names()]

    def has_table(self, table_name: str) -> bool:
        with self.session() as session:
            return inspect(session.bind).has_table(table_name)

    def drop_table(self, name: str) -> bool:
        """
        Drop table it it exists, returning True. Returns False otherwise.
        """

        with self.session() as session:

            meta = MetaData()
            meta.reflect(bind=session.bind)

            try:
                Table(name, meta).drop(bind=session.bind, checkfirst=False)
            except (OperationalError, DBAPIError):
                # See https://docs.sqlalchemy.org/en/20/core/exceptions.html#sqlalchemy.exc.DBAPIError
                return 0

            session.commit()
            return 1

    def query_table(self, name: str) -> pd.DataFrame:
        """
        Read the complete table `name` from db
        """
        with self.session() as session:
            meta = MetaData()
            meta.reflect(bind=session.bind)
            table = Table(name, meta)
            return session.query(table)

    def get_table_columns(self, name: str) -> List[str]:
        """
        Given a table `name`, return its SQLAlchemy columns.
        """

        with self.session() as session:
            meta = MetaData()
            meta.reflect(bind=session.bind)
            return [str(s) for s in Table(name, meta).columns]

    def vacuum(self):
        """
        Vacuum the database. This operation makes the database more compact and performant.
        """
        with self.session() as session:
            if self.url.drivername != "sqlite":
                # SQLite wants a transaction to VACUUM,
                # Postgresql doesn't. With a COMMIT,
                # we terminate the transaction, and
                # we can then execute the VACUUM command.
                session.execute(text("COMMIT"))
            session.execute(text("VACUUM"))
        log.debug("VACUUM executed.")

    def query(
        self,
        query: QueryType,
        tqdm_total=None,
    ) -> pd.DataFrame:
        """
        Query database with `query` (a string) and return result as a Pandas dataframe.
        """

        with self.session() as session:
            df = pandas_query(
                query,
                session,
                tqdm_total=tqdm_total,
            )

            # We handle UUID type conversions. If the DB handled natively UUID columns,
            # SQLAlchemy is already handling it transparently. If it doesn't, we need
            # to detect it, and apply the conversion.
            for col_name in ["id_run", "id_experiment"]:
                if col_name in df and not isinstance(df[col_name].iloc[0], uuid.UUID):
                    df[col_name] = df[col_name].apply(uuid.UUID)

            return df

    def query_count(self, query) -> int:
        return query_count(query, self.session)


def sanitize_table_name(name: str) -> str:
    """
    Sanitize the table name from the experiment name, allowing only lowercase alphanum characters.
    """
    return re.sub("[^0-9a-zA-Z]+", "_", str(name)).strip("_").lower()


def pandas_query(
    query: QueryType,
    session: Session,
    tqdm_total=None,
) -> pd.DataFrame:
    """
    Evaluate an SQL query on the database `session`, returning the result as a
    Pandas dataframe. If `tqdm_total` is passed, it will be used as hint
    on the count of returned rows for the progress bar.

    Option "database.query_read_chunk_size" controls how many rows are read per chunk.
    """

    query = normalize_query(query)

    log.debug(f"SQL: {query.compile(session.bind)}")

    if options().get("tqdm.disable"):
        return pd.read_sql_query(query, session.bind)

    if tqdm_total is None:
        # If hint on total not available, query the database for it.
        tqdm_total = query_count(query, session)

    # With SQLALchemy 2.0, we need to pass session.connection() instead of session.bind.
    # `df_chunks`` is an iterator where `chunksize` is the number of rows to include in each chunk.
    df_chunks_iterator = pd.read_sql_query(
        sql=query, con=session.connection(), chunksize=options().get("database.query_read_chunk_size")
    )

    def fetch_chunk(df_chunk):
        """
        Returns the count of rows fetched, and the resulting dataframe.
        """
        return (len(df_chunk), df_chunk)

    # As soon as the `fetch_chunk` functions are evaluated, the items are retrieved from the iterator.
    chunk_fetchers = [partial(fetch_chunk, df_chunk) for df_chunk in df_chunks_iterator]
    # Fetch chunks
    dfs = tqdm_chunks(chunk_fetchers, tqdm_total)
    # Concatenate dataframes and return
    return pd.concat(dfs, ignore_index=True)


def next_uuid(seed: int | None = None, inc: int = 1) -> uuid.UUID:
    """
    Return the next UUID to use.

    If "reproducibility.sequential_uuids" is set to True:
        - Return an ascending, sequential list of UUIDs, with increments of `inc`.
        - `seq` is used as static variable and should not be set directly.
    """

    global next_sequential_uuid

    if options().get("reproducibility.sequential_uuids"):
        if seed:
            next_sequential_uuid = seed
        next_sequential_uuid = (next_sequential_uuid + inc) % (2**128 - 1)
        return uuid.UUID(int=next_sequential_uuid)
    else:
        return uuid.uuid4()


def chunker(seq: List, size: int) -> List[List]:
    """
    Given a `list` of items, return a list of lists of items,
    where each sub-list is up to a certain chunk `size`.
    """

    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def tqdm_chunks(
    iterator: Iterator[Callable],
    total: int,
) -> List:
    """
    Renders a progress bar, working on chunks of work.
    Functions to execute are fetched from `iterator`,
    `total` is the expected count to reach.

    Functions return a pair (size, result), with
    `size` being accumulate to reach `total`.

    It returns a list of the accumulated `result` values.
    """

    pbar = tqdm(**(options().get("tqdm") | {"total": total}))

    pbar.clear()
    rets = []
    for item in iterator:
        size, ret = item()
        pbar.update(size)
        rets.append(ret)
    pbar.close()

    return rets


def hash_uuid(value: uuid.UUID | str) -> str:
    """
    Create a 6-alphanum hash of `value`, which can be
    either a string representing an UUID or an UUID object.
    If uuid1 == uuid2, hash_uuid(uuid1) == hash_uuid(uuid2).
    """

    if isinstance(value, uuid.UUID):
        int_value = value.int
    else:
        int_value = uuid.UUID(value).int

    expected_length = 6
    padding = "0" * expected_length
    alphabet = "123456789ACEFHJKLMNPRTUVWXY"
    length = len(alphabet)
    result = ""
    remain = int_value
    while remain > 0:
        pos = remain % length
        remain //= length
        result += alphabet[pos]
    result += padding
    return result[:expected_length].lower()


def query_count(query: QueryType, session: Session):
    """
    Returns the number of rows returned if executing `query`.
    """

    query = normalize_query(query)
    return session.execute(text(f"SELECT COUNT(*) FROM ({query})")).first()[0]  # noqa


def normalize_query(query: QueryType):
    """
    Normalize SQL query to an executable statement.
    """

    if isinstance(query, Query):
        return query.statement
    elif isinstance(query, str):
        return sql.expression.text(query)
    elif isinstance(query, Select):
        return query
    elif isinstance(query, TextClause):
        return query
    else:
        raise InvalidInput(f"Expected Query or string, found {type(query)}")
