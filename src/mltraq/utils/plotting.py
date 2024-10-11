from contextlib import contextmanager
from typing import Any, Dict, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from mltraq.opts import options


@contextmanager
def plot_ctx(  # noqa: C901
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    legend: Optional[Any] = None,
    interactive_mode: Optional[bool] = None,
    backend: Optional[str] = None,
    title: Optional[str] = None,
    facecolor: Optional[str] = None,
    x_lim: Optional[Dict] = None,
    y_lim: Optional[Dict] = None,
    spines_bottomleft: bool = False,
    x_minor_locator: Optional[float] = None,
    x_major_locator: Optional[float] = None,
    y_minor_locator: Optional[float] = None,
    y_major_locator: Optional[float] = None,
    y_grid: bool = False,
    hatches: bool = False,
    ax: Optional[Any] = None,
    figsize: Optional[tuple[int, int]] = None,
    show_axes: bool = True,
    show: bool = True,
    savefig_svg: Optional[str] = None,
    close: bool = True,
):
    """
    Prepare a matplotlib plot (single sub-plot):

    `x_label`: X label
    `y_label`: Y label
    `legend`: Dictionary passed to ax.legend(...)
    `title`: Title of the plot
    `interactive_mode`: set plt.ioff() or plt.ion()
    `backend`: Backend to use
    `facecolor`: Color of drawing area
    `yerr`: If true, report Y error bars
    `x_lim`: X limits, passed to ax.set_xlim(...)
    `y_lim`: Y limits, passed to ax.set_ylim(...)
    `spines_bottomleft`: Show only left,bottom spines
    `x_minor_locator`: X Minor locator
    `x_major_locator`: X Major locator
    `y_minor_locator`: Y Minor locator
    `y_major_locator`: Y Major locator
    `y_logscale`: If true, set logscale for Y
    `y_grid`: If true, show grid on Y
    `hatches`: Show hatches on bars
    `ax`: If not None, use it as axis object to draw on
    `fixsize`: size (x,y) of the subplot
    `show`: If true, call plt.show()
    `show_axes`: If false, empty white canvas without axes
    `savefig_svg`: Save figure to pathname in SVG format
    `close`: If true, close figure as last step
    """

    rc = options().get("matplotlib.rc", otherwise=None)
    style = options().get("matplotlib.style", otherwise="default")

    current_backend = mpl.get_backend()
    current_interactive_mode = plt.isinteractive()

    if savefig_svg:
        # If saving figure to file, don't display it (we cannot render to both.)
        show = False

    if backend:
        plt.switch_backend(backend)

    if interactive_mode is not None:
        if interactive_mode is True:
            plt.ion()
        else:
            plt.ioff()

    with plt.rc_context(rc), plt.style.context(style):

        if ax is None:
            # Note: You can retrieve the figure with ax.get_figure().
            fig, ax = plt.subplots(figsize=figsize if figsize else (3, 3))

        try:
            yield ax
        finally:

            if facecolor:
                ax.set_facecolor(facecolor)

            if spines_bottomleft:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

            if not show_axes:
                ax.set_axis_off()

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

            if hatches:
                hatches = ("./O\o*" * len(ax.patches))[: len(ax.patches)]
                for idx, bar in enumerate(ax.patches):
                    bar.set_hatch(hatches[idx])

            if x_lim:
                ax.set_xlim(**x_lim)
            if y_lim:
                ax.set_ylim(**y_lim)

            if y_grid:
                ax.grid(axis="y", which="major")

            if title is not None:
                ax.set_title(title, fontsize=plt.rcParams["font.size"] * 1)

            if legend:
                if isinstance(legend, dict):
                    ax.legend(**legend)
                else:
                    ax.legend()

            if show:
                plt.show()

            if backend:
                plt.switch_backend(current_backend)

            if interactive_mode is not None:
                if current_interactive_mode is True:
                    plt.ion()
                else:
                    plt.ioff()

            if savefig_svg is not None:
                plt.savefig(savefig_svg, format="svg", bbox_inches="tight")

            if close:
                plt.close(fig)
