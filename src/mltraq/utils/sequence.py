import pandas as pd


class Sequence(pd.DataFrame):
    def __init__(self, df=None):
        """Initialize sequence, using df contents if not None.

        Args:
            df (_type_, optional): If not None, initialize sequence using dataframe. Defaults to None.
        """
        if df is None:
            super().__init__(columns=["timestamp"])
            self["timestamp"] = self["timestamp"].astype("datetime64[ns]")
            # We cannot set a dtype for columns, Pandas will convert the column to float
            # at the first call to .track(value) to make sure that the column type can
            # contain missing values (nans).

        else:
            # We load a previously generated Sequence
            super().__init__(df)
            self["timestamp"] = self["timestamp"].astype("datetime64[ns]")

    def log(self, **kwargs):
        """Append values to dataframe"""

        self.loc[len(self), ["timestamp"] + list(kwargs.keys())] = [
            pd.Timestamp.now().to_datetime64(),
            *kwargs.values(),
        ]
