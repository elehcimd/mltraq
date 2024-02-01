from typing import List

import pandas as pd


def reorder_columns(df: pd.DataFrame, ordered_columns: List[str]) -> pd.DataFrame:
    """Given a dataframe, enforce the initial columns in the order
    `ordered_columns`, appending the remaining ones after sorting them.
    Why sorting: this ensures that, with queries like *, the order of returned columns is consistent.
    """

    remaining_columns = [col_name for col_name in df.columns if col_name not in ordered_columns]
    return df[ordered_columns + sorted(remaining_columns)]
