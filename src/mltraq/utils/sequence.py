import datetime
from typing import List

import numpy as np
import pandas as pd

from mltraq.utils.exceptions import ExceptionWithMessage
from mltraq.utils.frames import reorder_columns


class InvalidKey(ExceptionWithMessage):
    pass


class Sequence:
    """
    Class representing a growing sequence of tracked attributes, with `timestamp`.
    """

    __slots__ = ["data", "frame"]

    def __init__(self, frame: pd.DataFrame | None = None):
        """
        Initialize the sequence to the empty sequence, or with `data` if not None.
        """

        self.data: List[dict] = []
        if frame is None:
            self.frame = pd.DataFrame(columns=["timestamp"], dtype="datetime64[ns]")
        else:
            self.frame = frame

    def append(self, **kwargs):
        """
        Append a new dictionary of tracked values.
        """

        if "timestamp" in kwargs.keys():
            raise InvalidKey("Key 'timestamp' is reserved")

        current = np.datetime64(datetime.datetime.now())

        self.data.append(kwargs | {"timestamp": current})

    def size(self) -> int:
        """
        Flush and return number of rows in Pandas dataframe.
        """
        self.flush()
        return len(self.frame)

    def clear(self):
        """
        Clear the sequence.
        """
        self.data = []

    def flush(self):
        """
        Flush .data contents to .frame, concatenating existing and new dataframes.
        """

        # Create new dataframe
        if len(self.data) == 0:
            df = pd.DataFrame(columns=["timestamp"], dtype="datetime64[ns]")
        else:
            df = pd.DataFrame(self.data)

        # Concatenate dataframes, and clear data
        self.frame = pd.concat([self.frame, df], ignore_index=True)
        self.frame = reorder_columns(self.frame, ["timestamp"])
        self.clear()
        return self

    def df(self) -> pd.DataFrame:
        """
        Convert the sequence to a Pandas dataframe, with `timestamp` column.
        """
        self.flush()
        return self.frame
