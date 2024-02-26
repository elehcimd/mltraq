import mltraq
from mltraq.opts import options
from mltraq.storage import models
from mltraq.storage.database import Database


def test_create():
    """
    Test: We can create a database in-memory, with an "experiments" table, and query it.
    """
    # Instantiate the database
    db = Database()

    # Ensure that we can query the table, which is empty
    with db.session() as session:
        assert sum(1 for _ in session.query(models.Experiment)) == 0


def test_drop_tables():
    """
    Test: We can drop existing and unexisting tables
    """
    db = Database()
    assert db.drop_table(options().get("database.experiments_tablename"))
    assert not db.drop_table("table_not_existing")


def test_vacuum():
    """
    Test: We can vacuum the databe (at least, no error is reported.)
    """
    s = mltraq.create_session()
    s.db.vacuum()
