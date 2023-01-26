import pandas as pd
from mltraq.run import Run


class RunAssertion(Exception):
    """Raise this exception if an assertion on the runs state fails."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def assert_keys(name, keys, missing=False):
    """Ensure that a list of keys is either present or missing in a run attribute dict

    Args:
        name (_type_): Attribute name of the run
        keys (_type_): keys to check in run.name
        missing (bool, optional): If true, check keys to be missing. If false, check for keys
            to be present. Defaults to False.

    Raises:
        RunAssertion: Keys are either missing or present.

    Returns:
        __type__: step function
    """

    if isinstance(keys, str):
        keys = [keys]

    def func(run: Run):
        for key in keys:
            if not missing and (key not in getattr(run, name)):
                raise RunAssertion(f"run.{name}['{key}'] missing.")
            if missing and (key in run[name]):
                raise RunAssertion(f"run.{name}['{key}'] present.")

    return func


def assert_types(name, key_types):
    """Ensure that keys are present, with a certain type.

    Args:
        name (_type_): Attribute name of the run
        key_types (_type_): Dictionary of field names and their types

    Raises:
        RunAssertion: Keys missing or with wrong type.

    Returns:
        __type__: step function
    """

    def func(run: Run):
        for key, key_type in key_types:
            assert_keys(name, key)
            if not isinstance(getattr(run, name)[key], key_type):
                raise RunAssertion(f"type(run.{name}) != {key_type}")

    return func


def assert_df(name, key, columns=None, n_rows=None):
    """Ensure that the run contains a dataframe with certain columns and number of rows.

    Args:
        name (_type_): Run attribute name
        key (_type_): Field in run attribute
        columns (_type_, optional): List of expected columns in the Pandas dataframe. Defaults to None.
        n_rows (_type_, optional): Number of rows expected in the Pandas dataframe. Defaults to None.
    """

    def func(run: Run):
        assert_types(name, {key: pd.DataFrame})
        if columns is not None:
            cols_df = list(getattr(run, name)[key].columns)
            cols_expected = list(columns)
            if set(cols_df) != set(cols_expected):
                raise RunAssertion(f"run.{name}['{key}'].columns == {cols_df} != {cols_expected}")
        if n_rows is not None:
            n_rows_df = len(getattr(run, name)[key])
            if n_rows_df != n_rows:
                raise RunAssertion(f"len(run.{name}['{key}']) == {n_rows_df} != {n_rows}")

    return func
