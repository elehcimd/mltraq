from mltraq import create_experiment
from mltraq.steps.drop_fields import drop_fields
from mltraq.steps.init_fields import init_fields


def test_init_fields():
    """
    Test: We can drop fields with the `drop_fields` step.
    """

    experiment = create_experiment("example")

    # Add a run
    experiment.add_run()

    # Add three fields to initialize
    experiment.execute(init_fields(a=123, b=456, c=789))

    assert "a" in experiment.runs.first().fields
    assert "b" in experiment.runs.first().fields
    assert "c" in experiment.runs.first().fields

    # Drop one
    experiment.execute(drop_fields("a"))

    assert "a" not in experiment.runs.first().fields
    assert "b" in experiment.runs.first().fields
    assert "c" in experiment.runs.first().fields

    # Drop two
    experiment.execute(drop_fields("b", "c"))

    assert "a" not in experiment.runs.first().fields
    assert "b" not in experiment.runs.first().fields
    assert "c" not in experiment.runs.first().fields

    # Drop unexistend fields, does nothing
    experiment.execute(drop_fields("b", "c"))

    # Drop no fields.
    experiment.execute(drop_fields())
