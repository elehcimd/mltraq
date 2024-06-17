from mltraq import Run, create_session, options


def test_option_get():
    """
    Test: We can get an option value.
    """
    assert options().get("reproducibility.random_seed") == 123


def test_option_set_reset():
    """
    Test: We can reset an option value to its default.
    """

    # Initial value
    assert options().get("reproducibility.random_seed") == 123
    options().set("reproducibility.random_seed", 124)
    # Current value
    assert options().get("reproducibility.random_seed") == 124

    options().reset("reproducibility.random_seed")
    # Default value
    assert options().get("reproducibility.random_seed") == 123


def test_option_context():
    """
    Text: We can temporarily set options with the context manager.
    """
    assert options().get("reproducibility.random_seed") == 123
    with options().ctx({"reproducibility.random_seed": 124}):
        assert options().get("reproducibility.random_seed") == 124
    assert options().get("reproducibility.random_seed") == 123


def test_option_context_parallel():
    """
    Test: We can propagate options to other processes running workers executing steps,
    s.t. steps can access the correct values of options as set in the driver process.
    """

    # Make sure that we're indeed setting a different value
    assert options().get("reproducibility.random_seed") == 123

    with options().ctx({"reproducibility.random_seed": 124}):

        def f1(run: Run):
            # Without proper handling:
            # If we are executing the experiment in parallel workers,
            # the context is recreated using the defaults, ignoring the
            # options set by the context manager.
            # The correct behaviour is implemented transparently by the
            # logic of runs execution, passing an `options` parameter
            # that doesn't interfere with the exposed interface.
            assert options().get("reproducibility.random_seed") == 124

        s = create_session()
        e = s.create_experiment("test")
        e.add_runs(x=range(20))
        e.execute(steps=f1)
