import uuid

import mltraq


def test_run():
    """
    Test: We can create a run and its ID is an UUID.
    """
    run = mltraq.Run()
    assert isinstance(run.id_run, uuid.UUID)


def test_run_fields():
    """
    Test: We can create a run, sett a field, and convert it to a Pandas dataframe.
    """
    run = mltraq.Run()

    run.fields.a = 123
    assert len(run.df()) == 1
    assert run.df()["a"].iloc[0] == 123
