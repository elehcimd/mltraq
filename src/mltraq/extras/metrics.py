from mltraq.extras.assertions import assert_df
from mltraq.run import Run


def eval_metrics(run: Run):
    """Step function that calculates the accuracy metric.

    Args:
        run (Run): Run to apply the step to
    """

    # Verify that the run contains an attribute fields, containing a dataframe
    # "predictions", with two columns, y_true and y_pred
    run.apply(assert_df(name="fields", key="predictions", columns=["y_true", "y_pred"]))

    # calculate metrics (just accuracy)
    metrics = {"accuracy": (run.fields["predictions"]["y_true"] == run.fields["predictions"]["y_pred"]).mean()}

    # add metrics dictionary to run fields
    run.fields["metrics"] = metrics
