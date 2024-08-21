import random

import numpy as np
from mltraq.utils.reproducibility import seed_ctx


def test_seed_ctx_random():
    """
    Test: We can set a temporary seed for randomness in random module.
    """

    with seed_ctx():
        v1 = random.randint(0, 1000)

    random.randint(0, 10)

    with seed_ctx():
        v2 = random.randint(0, 1000)

    assert v1 == v2


def test_seed_ctx_numpy():
    """
    Test: We can set a temporary seed for randomness in NumPy package.
    """

    with seed_ctx():
        v1 = np.random.randint(0, 1000)

    np.random.randint(0, 10)

    with seed_ctx():
        v2 = np.random.randint(0, 1000)

    assert v1 == v2
