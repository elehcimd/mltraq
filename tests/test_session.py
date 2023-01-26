import mltraq


def test_session():
    session = mltraq.create_session()
    assert len(session.ls()) == 0


def test_session_html_repr():
    s = mltraq.create_session()
    assert s._repr_html_().startswith('MLTRAQ(db="sqlite:///:memory:"')


def test_copy_experiment():
    s1 = mltraq.create_session()
    s2 = mltraq.create_session()

    e = s1.add_experiment("test")
    s2.persist(e)

    assert s2.ls().name.iloc[0] == "test"
