import subprocess
import sys
import time

import mltraq
from mltraq.opts import options
from mltraq.run import RunException
from mltraq.utils.logging import logging_ctx


def faulty_step(run: mltraq.Run):
    """
    Faulty step: it's slow if a==1, and raises an exception if a==5.
    """

    class TestException(Exception):
        pass

    if run.params.a == 5:
        raise TestException("test error")
    elif run.params.a == 1:
        # make this task slower (faster than the one with a==5)
        time.sleep(0.1)


def experiment():
    """
    Execute the experiment.
    """

    # Define experiment with 10 runs
    s = mltraq.create_session()
    e = s.create_experiment("test")
    e.add_runs(a=range(10))

    with options().ctx(
        {
            "execution.return_as": "generator_unordered",
            "execution.exceptions.compact_message": True,
            "execution.exceptions.report_basenames": True,
        }
    ):
        try:
            # Run using only two parallel running jobs
            e.execute(faulty_step, n_jobs=2)
        except RunException as ex:
            print(ex)


def local(args: list[str]):
    """
    Run command with argv `args` and return output as a string, suppressing stderr.
    """
    return subprocess.check_output(args, stderr=subprocess.DEVNULL).decode("utf-8")  # noqa: S603


if sys.argv[-1] != "failfast_experiment":
    # If executing the script with no parameters, run the same script as a separate process,
    # returning only the standard output. This avoids unnecessariy debug information from
    # other threads and processes handled by Joblib, on which we cannot control the output.

    # We pass the full path of the script to make sure the automated generation of the
    # documentation files doesn't interfere with it.
    out = local(["python", "mkdocs/blog/posts/011/failfast.py", "failfast_experiment"]).strip()
    print(f"\n--\n{out}\n--\n")
else:
    # Run the experiment if this script is executed by passing "failfast_experiment" as last argument.
    with logging_ctx(level_name="DEBUG"):
        experiment()
