from mltraq import Run, create_session, options
from mltraq.steps.init_sequences import init_sequences
from mltraq.utils.fs import tmpdir_ctx
from mltraq.utils.logging import logging_ctx

with options().ctx({"datastream.disable": False}), logging_ctx(
    level_name="DEBUG", log_format="[%(threadName)s] %(message)s"
), tmpdir_ctx():

    # Create a new experiment
    session = create_session("sqlite:///mltraq.db")
    experiment = session.create_experiment("example")

    # Add the sequence "metrics" and persist the experiment
    experiment.execute(init_sequences("metrics")).persist()

    def track(run: Run):
        """
        Track and stream a record in the `metrics` sequence.
        """
        run.fields.metrics.append(v=123)

    with session.datastream_server() as ds:
        # datastream_server() starts the threads to handle
        # the incoming messages, writing new records to database.

        # Execute `track` step
        experiment.execute(track)

        # Make sure that the DatabaseWriter
        # processed at least one record.
        ds.dbw.received.wait()

    # Up to this point, we did not persist the experiment, only
    # the streamed records have been tracked to database.

    # Load experiment, showing the contents of the metrics Sequence.
    streamed_experiment = session.load("example")

    print("\n--\nStreamed metrics:")
    print(streamed_experiment.runs.first().fields.metrics.df())
