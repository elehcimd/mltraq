import mltraq


def test_session():
    """
    Test: We can create a session and list the available experiments.
    """
    session = mltraq.create_session()
    assert len(session.ls()) == 0


def test_session_html_repr():
    """
    Test: The str and html representations of a Session object are the same and include
    a description of the linked db.
    """
    s = mltraq.create_session()
    assert s.__str__().startswith('Session(db="sqlite:///:memory:"')
    assert s.__str__() == s._repr_html_()


def test_copy_experiment():
    """
    Test: We can copy an expriment between sessions.
    """
    s1 = mltraq.create_session()
    s2 = mltraq.create_session()

    e = s1.create_experiment("test")

    # Persist experiment on s1
    e.persist()

    # Persist a copy of the experiment on s2
    s2.persist(e)

    # The two experiments have equal names and distinct IDs.
    # We can demonstrate this by reloading and comparing them.
    e1 = s1.load("test")
    e2 = s2.load("test")
    assert e1.name == e2.name
    assert e1.name == "test"
    assert e1.id_experiment.hex != e2.id_experiment.hex
