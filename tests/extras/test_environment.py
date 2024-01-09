from mltraq.extras.environment import get_environment


def test_get_environment():
    env = get_environment()
    assert list(env.keys()) == ["platform"]
