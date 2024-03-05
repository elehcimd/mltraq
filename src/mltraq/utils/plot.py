import logging
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from scipy.stats import sem

from mltraq.opts import options

log = logging.getLogger(__name__)


def stderr(a):
    if a.nunique() == 1:
        return 0
    else:
        return sem(a, nan_policy="omit")


def bar_plot(  # noqa
    df: pd.DataFrame,
    x: str,
    y: str,
    group: list[str] | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    legend: dict | None = None,
    title: str | None = None,
    yerr: bool = False,
    x_lim: float | None = None,
    y_lim: float | None = None,
    x_minor_locator: float | None = None,
    x_major_locator: float | None = None,
    y_minor_locator: float | None = None,
    y_major_locator: float | None = None,
    y_logscale: bool = False,
    y_grid: bool = False,
    ax: Any | None = None,
    hatches: bool = False,
):
    """
    Bar plot results of an experiment:

    `df`: Pandas dataframe, as returned by experiment.df()
    `x`: Column name to be used for X values (numerical)
    `y`: Column name to be used for Y values (numerical)
    `group`: Column name to group results by
    `x_label`: X label
    `y_label`: Y label
    `legend`: Dictionary passed to ax.legend(...)
    `title`: Title of the plot, optional
    `yerr`: If true, report Y error bars
    `x_lim`: X limits, passed to ax.set_xlim(...)
    `y_lim`: Y limits, passed to ax.set_ylim(...)
    `x_minor_locator`: X Minor locator
    `x_major_locator`: X Major locator
    `y_minor_locator`: Y Minor locator
    `y_major_locator`: Y Major locator
    `y_logscale`: If true, set logscale for Y
    `y_grid`: If true, show grid on Y
    `ax`: If not none, use it as axis object to draw on
    `hatches`: Show hatches on bars
    """

    x_label = x if not x_label else x_label
    y_label = y if not y_label else y_label

    rc = options().get("matplotlib.rc", null_if_missing=True)
    style = options().get("matplotlib.style", null_if_missing=True) or "default"

    with plt.rc_context(rc), plt.style.context(style):

        if ax is None:
            _, ax = plt.subplots(figsize=options().get("matplotlib.figsize", null_if_missing=True) or (5, 5))

        aggfunc = ["mean", "median", stderr]

        if group is None:

            # Sort bars in ascending average value

            df = df.groupby(x, dropna=False).agg({y: aggfunc})

            # Sort bars in ascending mean order
            df = df.sort_values(by=(y, "mean"))

            df[y]["mean"].plot(
                kind="bar",
                yerr=df[y]["stderr"] if yerr else None,
                error_kw={"elinewidth": 1, "capthick": 1, "capsize": 3},
                ax=ax,
            )
        else:
            df = df.pivot_table(index=x, columns=group, values=y, aggfunc=aggfunc, dropna=False)

            # Sort bars in ascending average value
            df = df.reindex(df.mean().sort_values().index, axis=1)

            df.plot(
                kind="bar",
                y="mean",
                yerr="stderr" if yerr else None,
                error_kw={"elinewidth": 1, "capthick": 1, "capsize": 3},
                ax=ax,
            )

        if x_minor_locator:
            ax.yaxis.set_minor_locator(mtick.MultipleLocator(x_minor_locator))
        if x_major_locator:
            ax.yaxis.set_major_locator(mtick.MultipleLocator(x_major_locator))
        if y_minor_locator:
            ax.yaxis.set_minor_locator(mtick.MultipleLocator(y_minor_locator))
        if y_major_locator:
            ax.yaxis.set_major_locator(mtick.MultipleLocator(y_major_locator))

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.tick_params(axis="x", labelrotation=0)
        if y_logscale:
            ax.set_yscale("log")
            ax.tick_params(axis="y", which="minor")
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f"))
            ax.yaxis.set_minor_formatter(mtick.FormatStrFormatter("%.1f"))
            ax.yaxis.set_minor_locator(mtick.LogLocator(base=10.0, subs=[2, 4, 6, 8]))
            if y_grid:
                ax.grid(axis="y", which="both")
        else:
            if y_grid:
                ax.grid(axis="y", which="major")

        if hatches:
            hatches = ("./O\o*" * len(ax.patches))[: len(ax.patches)]
            for idx, bar in enumerate(ax.patches):
                bar.set_hatch(hatches[idx])

        if x_lim:
            ax.set_xlim(**x_lim)
        if y_lim:
            ax.set_ylim(**y_lim)

        if title is not None:
            ax.set_title(title, fontsize=plt.rcParams["font.size"] * 1.2, fontweight="bold")

        if group is not None:
            if not legend:
                legend = {}
            ax.legend(**legend)
