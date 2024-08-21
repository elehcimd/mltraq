from mltraq import create_experiment
from mltraq.steps.nothing import nothing


def test_nothing():
    """
    Test: We can run a step doing exactly nothing.
    """

    experiment = create_experiment("example")
    experiment.add_run().execute(nothing)
