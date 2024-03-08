import os
from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp

from joblib.externals.loky import get_reusable_executor


@contextmanager
def tmpdir_ctx():
    """
    Create and enter a temporary directory, deleted as the context exits.
    if `shutdown_joblib_workers` is true, terminate the workers created y joblib.
    This ensures that the current directory is honored by all newly created workers.
    """
    try:
        old_dirname = os.getcwd()
        tmp_dirname = mkdtemp()
        os.chdir(tmp_dirname)

        yield tmp_dirname
    finally:
        os.chdir(old_dirname)
        rmtree(tmp_dirname)


@contextmanager
def chdir(dirname):
    """
    Enter `dirname` directory, and leave it
    as the context returns.
    """
    try:
        old_dirname = os.getcwd()
        os.chdir(dirname)

        # Joblib keeps the pool of workers alive, with their
        # currently defined active directory.

        # Since we chdir in temporary directories to run
        # tests and examples, if we run multiple examples
        # sequentially as in the tests, we might have
        # workers with an invalid current directory.
        # This is why, whenever we enter a context
        # with a new directory, we force the shutdown
        # of the workers.
        # https://github.com/joblib/joblib/issues/945

        get_reusable_executor().shutdown(wait=True)

        yield dirname
    finally:
        os.chdir(old_dirname)
