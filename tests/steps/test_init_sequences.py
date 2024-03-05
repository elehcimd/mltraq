from mltraq import create_experiment
from mltraq.steps.init_sequences import init_sequences
from mltraq.utils.sequence import Sequence


def test_init_sequences():
    """
    Test: We can initialize sequences with the `init_sequences` step.
    """

    experiment = create_experiment("example")

    # No sequences to initialize
    experiment.add_run().execute(init_sequences())

    # Add one sequence to initialize
    experiment.add_run().execute(init_sequences("abc"))

    assert isinstance(experiment.runs.first().fields.abc, Sequence)
