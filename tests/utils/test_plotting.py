import pandas as pd
from mltraq.utils.plotting import plot_ctx


def test_plot_ctx():
    """
    Test: We can use the context to generate a plot.
    """

    with plot_ctx(
        interactive_mode=False,
        backend="PS",
        show=False,
        x_label="X",
        y_label="Y",
        legend=["line"],
        title="test",
        facecolor="red",
        x_lim={"left": 0, "right": 1},
        y_lim={"bottom": 0, "top": 1},
        x_minor_locator=0.1,
        x_major_locator=1,
        y_minor_locator=0.1,
        y_major_locator=1,
        y_grid=True,
        hatches=True,
    ) as ax:
        pd.Series([1, 2, 3]).rename("sample1").plot(ax=ax)
