import glob
from unittest.mock import patch

import mltraq
from mltraq.opts import options
from mltraq.steps.init_sequences import init_sequences
from mltraq.storage.datastream import DatabaseWriter, DataStreamClient, DataStreamServer
from mltraq.utils.fs import tmpdir_ctx


def print_directory_contents(dirname):
    """
    Given a directory name `dirname`, list its contents.
    """

    print(f"Directory '{dirname}':\n")
    for pathname in glob.glob("**", root_dir=dirname, recursive=True):
        print(pathname)
    print("--")


def test_datastream_send_receive():

    with patch.object(DatabaseWriter, "process_batch"), tmpdir_ctx(), options().ctx(
        {"database.url": "sqlite:///mltraq.db"}
    ):

        # process_batch will not consume the contents of .batch

        srv = DataStreamServer()
        srv.start()

        cli = DataStreamClient()
        cli.send({"test": 123})

        srv.received.wait()

        srv.stop()


def test_datastream_sequence():
    """
    Test: We can stream sequence records, starting/stopping the streaming functionality.
    """

    with tmpdir_ctx(), options().ctx({"database.url": "sqlite:///mltraq.db"}):

        # Start data stream server
        srv = DataStreamServer().start()

        # Create session/experiment
        # Create the Sequence to be streamed
        # Persist experiment
        session = mltraq.create_session()
        experiment = session.create_experiment("test")
        experiment.execute(init_sequences("seq")).persist()

        # Verify that experiment has been persisted, with no tracked values
        assert len(session.load_experiment(name="test").runs.first().fields.seq.df()) == 0

        # Tracking without streaming.
        run = experiment.runs.first()
        run.fields.seq.append(a=100, b=200)

        # Tracking with streaming.
        with run.datastream_client():
            run.fields.seq.append(a=300, b=400)

        # Tracking without streaming.
        run.fields.seq.append(a=500, b=600)

        # Wait for message to be received by server thread
        srv.received.wait()

        # Wait for message to be received by database writer thread
        srv.dbw.received.wait()

        # Stop data stream server
        srv.stop()

        # Verify that record has been tracked, without a .persist(...).
        session = mltraq.create_session()
        df = session.load_experiment(name="test").runs.first().fields.seq.df()
        assert len(df) == 1
        assert df.iloc[0]["a"] == 300
        assert df.iloc[0]["b"] == 400

        # Persist original experiment
        experiment.persist(if_exists="replace")

        # Verify presence of three records with idx [0,1,2]
        df = session.load_experiment(name="test").runs.first().fields.seq.df().sort_values(by="idx")
        assert len(df) == 3
        assert df.iloc[0]["idx"] == 0
        assert df.iloc[0]["a"] == 100
        assert df.iloc[0]["b"] == 200
        assert df.iloc[1]["idx"] == 1
        assert df.iloc[1]["a"] == 300
        assert df.iloc[1]["b"] == 400
        assert df.iloc[2]["idx"] == 2
        assert df.iloc[2]["a"] == 500
        assert df.iloc[2]["b"] == 600
