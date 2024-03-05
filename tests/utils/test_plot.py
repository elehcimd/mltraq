import matplotlib
import pandas as pd
from mltraq.utils.plot import bar_plot


def test_bar_plot():
    """
    Test: We can request to plot a simple data frame.
    """

    df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 3, 4]})

    # Disable interactivity and make sure that
    # matplotlib doesn't create new windows.
    with matplotlib.pyplot.ioff():
        matplotlib.use("PS")
        bar_plot(df, x="x", y="y")


def test_bar_plot_group():
    """
    Test: We can request to plot a simple data frame, with groups.
    """

    df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 3, 4], "z": [0, 0, 1, 1]})

    # Disable interactivity and make sure that
    # matplotlib doesn't create new windows.
    with matplotlib.pyplot.ioff():
        matplotlib.use("PS")
        bar_plot(df, x="x", y="y", group="z")
