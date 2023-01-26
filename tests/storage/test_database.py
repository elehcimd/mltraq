import mltraq


def test_vacuum():
    # Simply test that we can run vacuum a sqlite database.
    s = mltraq.create_session()
    s.db.vacuum()
