import numpy as np
from mltraq import Sequence


def test_sequence():
    """
    Test: We can create a sequence, append values to it, and flush it to its pandas Dataframe representation.
    """
    s = Sequence()
    s.append(a=2)
    s.append(b=3)
    s.flush()

    assert s.df().dtypes.astype(str).tolist() == ["int64", "datetime64[ns]", "float64", "float64"]
    assert s.df().columns.tolist() == ["idx", "timestamp", "a", "b"]
    assert s.df().iloc[0].idx == 0
    assert s.df().iloc[1].idx == 1
    assert s.df().iloc[0].a == 2
    assert np.isnan(s.df().iloc[0].b)
    assert np.isnan(s.df().iloc[1].a)
    assert s.df().iloc[1].b == 3
