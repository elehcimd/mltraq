from mltraq.job import ProgressParallel
import joblib
from functools import partial
import time


def test_parallel():
    """
    Test: We can parallelize the execution of N tasks, retaining their order.
    n_jobs=1 by default, so setting it to 4 to have 4 processes-parallelization.
    """

    def simple_task(x):
        return x

    tasks = [partial(simple_task, i) for i in range(10)]

    # TODO
    # Specifying n_jobs different than -1 (the default for other tests from config),
    # there's a segmentation fault in several parallel tests. It might be related
    # to the handling of workers in joblib.
    p = ProgressParallel(n_jobs=-1, total=len(tasks), prefer="processes")
    rets = p(joblib.delayed(func)() for func in tasks)

    assert rets == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_parallel_generator():
    """
    Test: We can return a generator instead a list.
    """

    def simple_task(x):
        return x

    tasks = [partial(simple_task, i) for i in range(10)]

    p = ProgressParallel(n_jobs=-1, total=len(tasks), prefer="processes", return_as="generator")
    gen = p(joblib.delayed(func)() for func in tasks)

    rets = [next(gen) for _ in range(10)]

    assert rets == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_parallel_generator_unordered():
    """
    Test: We can return a generator instead a list. Tasks that complete faster return earlier
    with option "generator_unordered".
    """

    def simple_task(x):
        return x

    tasks = [partial(simple_task, i) for i in range(4)]

    p = ProgressParallel(n_jobs=-1, total=len(tasks), prefer="processes", return_as="generator_unordered")
    gen = p(joblib.delayed(func)() for func in tasks)

    rets = [next(gen) for _ in range(4)]

    # 2 will be the last one (slower task to complete).
    # Depending on timing of tests, order might change.
    assert set(rets) == {0, 1, 3, 2}


def test_parallel_generator_unordered_faster_fail():
    """
    Test: We can return a generator instead a list. Tasks that complete faster return earlier
    with option "generator_unordered", including failing ones.
    """

    def simple_task(x):
        if x == 2:
            return None
        return x

    tasks = [partial(simple_task, i) for i in range(4)]  # 0 1 2 3

    p = ProgressParallel(n_jobs=-1, total=len(tasks), prefer="processes", return_as="generator_unordered")
    gen = p(joblib.delayed(func)() for func in tasks)

    rets = []

    while True:
        try:
            rets.append(next(gen))
        except StopIteration:
            # No more jobs, interrupting
            print("StopIteration")
            break

    # 0,1,3 completed, 2 failed.
    # Depending on timing of tests, order might change.
    assert set(rets) == {0, 1, None, 3}


def test_job_cls_exception():
    """
    Test: We can run tasks with the Job class interface,
    which might raise exceptions triggered by the tasks.
    """

    class TestException(Exception):
        pass

    def simple_task(x):
        if x == 2:
            raise TestException("test error")
        return x

    tasks = [partial(simple_task, i) for i in range(4)]  # 0 1 2 3

    job = Job(tasks)

    with pytest.raises(TestException):
        job.execute()


def test_job_cls_simple():
    """
    Test: We can run tasks with the Job class interface.
    """

    def simple_task(x):
        return x

    tasks = [partial(simple_task, i) for i in range(4)]  # 0 1 2 3

    job = Job(tasks)

    assert job.execute() == [0, 1, 2, 3]
