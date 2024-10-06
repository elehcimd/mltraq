import contextlib
import random
from typing import Union

import numpy as np

from mltraq.opts import options


@contextlib.contextmanager
def seed_ctx(seed: Union[int, None] = None):
    """
    Context with a randomness seed for both NumPy and random module.
    If a `seed` is not provided, the default from options is used.
    """

    if seed is None:
        seed = options().get("reproducibility.random_seed")
    state_np = np.random.get_state()
    state_random = random.getstate()
    np.random.seed(seed)
    random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state_np)
        random.setstate(state_random)
