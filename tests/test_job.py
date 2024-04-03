from functools import partial

import joblib
from mltraq.job import ProgressParallel


def test_parallel():
    """
    Test: We can parallelize the execution of N tasks, retaining their order.
    """

    def simple_task(x):
        return 2 * x

    tasks = [partial(simple_task, i) for i in range(10)]

    p = ProgressParallel(n_jobs=2, total=len(tasks), prefer="processes")
    rets = p(joblib.delayed(func)() for func in tasks)

    assert rets == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


def test_parallel_generator():
    """
    Test: We can return a generator instead a list. By itself, not useful. However, this is work
    in preparation for joblib 1.4, which will provide "generator_unordered", very useful to make
    jobs fail faster.
    """

    def simple_task(x):
        return 2 * x

    tasks = [partial(simple_task, i) for i in range(10)]

    p = ProgressParallel(n_jobs=2, total=len(tasks), prefer="processes", return_as="generator")
    gen = p(joblib.delayed(func)() for func in tasks)

    rets = [next(gen) for _ in range(10)]

    assert rets == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
