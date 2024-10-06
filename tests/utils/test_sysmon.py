from mltraq import Run, create_session, options
from mltraq.utils.logging import logging_ctx
from mltraq.utils.sequence import Sequence
from mltraq.utils.sysmon import SystemMonitor


def test_sysmon():
    """
    Test: We can monitor the system stats in a separate thread.
    """

    session = create_session()
    experiment = session.create_experiment("example")

    # Make sure that the default system monitor will not be created in the run context
    with options().ctx({"sysmon.field_name": "system123", "sysmon.interval": 0.1}), logging_ctx(level_name="DEBUG"):

        def step(run: Run):
            with run.sysmon() as sm:
                sm.produced.wait()

        df = experiment.execute(step).runs.first().fields.system123.df()
        # There is at least one record an at least one expected column, with a positive value.
        assert len(df) > 0
        assert "cpu_pct" in df.columns
        assert df.iloc[0].cpu_pct > 0


def test_sysmon_direct():
    """
    Test: We start sysmon explicitly, collecting stats on system usage.
    """

    with options().ctx({"sysmon.interval": 0.1}), logging_ctx(level_name="DEBUG"):

        sequence = Sequence()
        sm = SystemMonitor(sequence)
        sm.start()
        sm.produced.wait()
        sm.stop()
        sequence.flush()
        assert sequence.frame.iloc[0].cpu_pct > 0
