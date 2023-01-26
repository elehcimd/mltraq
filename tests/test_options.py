import mltraq


def test_option_get():
    assert mltraq.options.get("reproducibility.random_seed") == 123


def test_option_set_reset():
    assert mltraq.options.get("reproducibility.random_seed") == 123
    mltraq.options.set("reproducibility.random_seed", 124)
    assert mltraq.options.get("reproducibility.random_seed") == 124

    mltraq.options.reset("reproducibility.random_seed")
    assert mltraq.options.get("reproducibility.random_seed") == 123


def test_option_context():
    assert mltraq.options.get("reproducibility.random_seed") == 123
    with mltraq.options.option_context({"reproducibility.random_seed": 124}):
        assert mltraq.options.get("reproducibility.random_seed") == 124
    assert mltraq.options.get("reproducibility.random_seed") == 123
