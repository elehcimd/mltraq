import numpy as np

from mltraq import Run, create_session, options
from mltraq.steps.init_sequences import init_sequences
from mltraq.utils.fs import tmpdir_ctx
from mltraq.utils.logging import logging_ctx

with options().ctx(
    {
        "datastream.cli_address": "127.0.0.1:9000",
        "datastream.srv_address": "127.0.0.1:9000",
        "datastream.kind": "INET",
    }
), logging_ctx(level_name="DEBUG", log_format="[%(threadName)s] %(message)s"), tmpdir_ctx():

    # Create a new experiment
    session = create_session("sqlite:///mltraq.db")
    experiment = session.create_experiment("example")

    # Add a sequence "metrics" and persist experiment
    experiment.execute(init_sequences("metrics"), n_jobs=1).persist(if_exists="replace")

    def track(run: Run):
        """
        Add 10 values to the `metrics`, streaming them.

        We track also a field `dataset`, which is not streamed
        as its type is not `Sequence`.
        """
        with run.datastream_client():
            run.fields.dataset = np.zeros(100)
            for v in range(10):
                run.fields.metrics.append(v=v)

    with session.datastream_server() as ds:
        # datastream_server() starts the threads to handle
        # the incoming messages, writing new records to database.

        # Execute `track` step
        experiment.execute(track, n_jobs=1)

        # Make sure that the DatabaseWriter
        # processed at least one record.
        ds.dbw.received.wait()

    print("\n")

    # Up to this point, we did not persist the experiment, only
    # the streamed records have been tracked to database.

    # Load experiment, showing the contents of the metrics Sequence.
    streamed_experiment = session.load_experiment("example")

    # Show tracked fields. Only "metrics" is present,
    # `run.fields.dataset` is not a Sequence and therefore not streamed.
    print("Streamed fields:", list(streamed_experiment.runs.first().fields.keys()))
    print("--\n")

    print("Streamed metrics:")
    print(streamed_experiment.runs.first().fields.metrics.df())
    print("--\n")

    # Persist and reload reload experiment, showing the tracked fields.
    # The copy with the streamed data is replaced by the complete experiment.
    experiment.persist(if_exists="replace")

    print("Tracked fields:", list(session.load_experiment("example").runs.first().fields.keys()))
