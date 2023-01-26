import numpy as np
import pandas as pd
from mltraq import Sequence


def test_sequence():
    seq = Sequence()

    seq.log(c=3, a=1, b=2)
    seq.log(d=5)

    # create dataframe from sequence, and sequence from dataframe.
    df = pd.DataFrame(seq)
    seq = Sequence(df=df)

    # We expect two rows, first one with values for col c,a,b (and nan for col d),
    # and second one with a non-nan value only for d.
    assert len(seq) == 2
    assert list(seq.columns) == ["timestamp", "c", "a", "b", "d"]
    assert np.isnan(seq["d"].iloc[0])
    assert seq["d"].iloc[1] == 5
    assert seq["a"].iloc[0] == 1

    # Also, timestamp's type is datetime64[ns].
    assert str(seq.timestamp.dtype) == "datetime64[ns]"
