import datetime
from typing import List

import numpy as np
import pandas as pd

from mltraq.utils.exceptions import ExceptionWithMessage
from mltraq.utils.frames import reorder_columns


class InvalidKey(ExceptionWithMessage):
    """
    Triggered in case a column with a reserved key is used.
    """

    pass


class Sequence:
    """
    Class representing a growing sequence of tracked attributes, with `idx` and `timestamp` (microsecond precision).

    In case of data streams:
    - There might be missing records, which can be identified by gaps in the `idx` values
    - Rows are not guaranteed to be in ascending `idx` order
    """

    __slots__ = ["data", "frame", "next_idx", "stream_send"]
    __state__ = ["data", "frame", "next_idx"]

    def __init__(self, frame: pd.DataFrame | None = None):
        """
        Initialize the sequence to the empty sequence, or with `data` if not None.
        """

        self.data: List[dict] = []
        if frame is None:
            self.frame = pd.DataFrame(columns=["idx", "timestamp"])
            # It is not possible to specify different dtypes via `dtype`, so doing it separately.
            self.frame["idx"] = self.frame["idx"].astype(np.int64)
            self.frame["timestamp"] = self.frame["timestamp"].astype("datetime64[us]")
            self.next_idx = 0
        else:
            self.frame = frame
            if self.frame.shape[0] > 0:
                # Rows are not guaranteed to be in order.
                self.next_idx = max(frame["idx"]) + 1
            else:
                self.next_idx = 0

        self.stream_send = None

    def __len__(self):
        """
        Return the number of rows of the sequence.
        """
        return len(self.frame) + len(self.data)

    def set_stream(self, name, callback):
        if callback is None:
            self.stream_send = None
        else:
            self.stream_send = lambda record: callback({"field_name": name, "record": record})

    def __getstate__(self):
        """
        Create state of the Sequence for pickling. Only attributes in `__state__` are considered.
        """
        state = {key: getattr(self, key) for key in self.__state__}
        return state

    def __setstate__(self, state):
        """
        Set state of the Sequence for unpickling.

        Note: __init__() is not called when unpickling an instance, this is why we need
        to initialise other attributes which are not part of __state__.
        """
        # Set state
        for k, v in state.items():
            self.__setattr__(k, v)
        # Set defaults
        self.stream_send = None

    def append(self, **kwargs):
        """
        Append a new dictionary of tracked values.
        """

        if "timestamp" in kwargs.keys() or "idx" in kwargs.keys():
            raise InvalidKey("Keys 'idx' and 'timestamp' are reserved")

        timestamp = np.datetime64(datetime.datetime.now())
        idx = self.next_idx
        self.next_idx += 1
        record = {"idx": idx, "timestamp": timestamp} | kwargs

        if self.stream_send:
            self.stream_send(record)

        self.append_record(record)

    def stream_recv(self, record: dict):
        """
        Add `record` as received by the stream.
        The record must contain keys `idx`, `timestamp`,
        as set by .stream_send(...).
        """
        self.append_record(record)

    def append_record(self, record: dict):
        self.data.append(record)

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
            df = pd.DataFrame(columns=["idx", "timestamp"])
            df["idx"] = df["idx"].astype(np.int64)
            df["timestamp"] = df["timestamp"].astype("datetime64[us]")
        else:
            df = pd.DataFrame(self.data)

        # Concatenate dataframes, and clear data
        self.frame = pd.concat([self.frame, df], ignore_index=True)
        self.frame = reorder_columns(self.frame, ["idx", "timestamp"])
        self.clear()
        return self

    def df(self) -> pd.DataFrame:
        """
        Convert the sequence to a Pandas dataframe, with `timestamp` column.
        """
        self.flush()
        return self.frame
