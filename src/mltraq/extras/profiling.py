import contextlib
import cProfile
import io
import pstats


@contextlib.contextmanager
def profiled(print_callers: bool = False):
    """
    Profile the execution of a function, copied from
    https://docs.sqlalchemy.org/en/14/faq/performance.html

    Args:
        print_callers (bool, optional): IF true, print who's calling waht.
        Defaults to False.
    """
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats()
    if print_callers:
        ps.print_callers()
    print(s.getvalue())  # noqa
