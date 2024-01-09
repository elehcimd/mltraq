import mltraq
from mltraq.storage import models
from mltraq.storage.database import Database


def test_create():
    # Instantiate the database
    db = Database()

    # Ensure that we can query the table, which is empty
    with db.session() as session:
        assert sum(1 for row in session.query(models.Experiment)) == 0


def test_drop_table_not_existing():
    db = Database()
    # Test that we can drop a table
    db.drop_table("table_not_existing")


def test_vacuum():
    # Simply test that we can run vacuum a sqlite database.
    s = mltraq.create_session()
    s.db.vacuum()
