from mltraq import create_experiment
from mltraq.steps.init_fields import init_fields
from mltraq.utils.sequence import Sequence


def test_init_fields():
    """
    Test: We can initialize fields with the `init_fields` step.
    """

    experiment = create_experiment("example")

    # No fields to initialize
    experiment.add_run().execute(init_fields())

    # Add two fields to initialize
    experiment.add_run().execute(init_fields(a=Sequence(), b=123))

    assert isinstance(experiment.runs.first().fields.a, Sequence)
    assert experiment.runs.first().fields.b == 123
