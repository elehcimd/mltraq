from typing import List

import pandas as pd


def reorder_columns(df: pd.DataFrame, ordered_columns: List[str]) -> List[str]:
    """Given a dataframe, enforce a partial ordering of some columns, appending
    the remaining ones in sorted order.

    Args:
        df (pd.DataFrame): Consider the columns from thsi dataframe.
        ordered_columns (List[str]): Consider this partial ordering of the columns.

    Returns:
        List[str]: New ordering of all columns for the {df} dataframe.
    """
    remaining_columns = sorted([col_name for col_name in df.columns if col_name not in ordered_columns])
    return df[ordered_columns + remaining_columns]


def json_normalize(data, max_level=0, sep="."):
    """Convert JSON object to dataframe.

    Args:
        data (_type_): JSON object
        max_level (int, optional): Max level to normalize. Defaults to 0.
        sep (str, optional): Separator for nested values. Defaults to ".".

    Returns:
        _type_: _description_
    """
    df = pd.json_normalize(
        data,
        max_level=max_level,
        sep=sep,
    )

    return df
