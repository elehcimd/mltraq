from mltraq import Sequence


def test_sequence():
    """
    Test: We can create a sequence, append values to it, and flush it to its pandas Dataframe representation.
    """
    s = Sequence()
    s.append(a=2)
    s.append(b=2)
    s.flush()

    assert s.df().dtypes.astype(str).tolist() == ["datetime64[ns]", "float64", "float64"]
    assert s.df().columns.tolist() == ["timestamp", "a", "b"]
    assert s.df().iloc[0].a == 2
