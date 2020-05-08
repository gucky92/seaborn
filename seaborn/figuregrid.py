"""
(c) Matthias Christenson

FacetFigure
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from .axisgrid import FacetGrid, PairGrid, JointGrid
from .prettify import get_letter, panel_letter
from . import utils


# TODO better padding between subplots
# TODO better padding within subplot grid
class Figure:
    """
    Construct a figure with single plots, subplots,
    `FacetGrid` plots, `PairGrid` plots, and `JointGrid` plots.

    Parameters
    ----------
    nrows : int, optional
        Number of rows in the figure grid.
    ncols : int, optional
        Number of columns in the figure grid.
    figsize : two-tuple, optional
        Size of complete figure.
    gridspec_kws : dict, optional
        Arguments passed to `gridspec.GridSpec`.
    fig_kws: dict, optional
        Arguments passed to `plt.figure`.
    """

    def __init__(
        self,
        nrows=1,
        ncols=1,
        figsize=None,
        gridspec_kws=None,
        **fig_kws
    ):

        gridspec_kws = {} if gridspec_kws is None else gridspec_kws

        self._fig = plt.figure(
            figsize=figsize,
            **fig_kws
        )

        self._grid = gridspec.GridSpec(
            nrows, ncols,
            figure=self._fig, **gridspec_kws
        )

        self._reserved = np.zeros((nrows, ncols)).astype(bool)

        self._keys = []
        self._handlers = []

    def __getitem__(self, key):

        if key in self._keys:
            index = self._keys.index(key)
            return self._handlers[index]
        if np.any(self._reserved[key]):
            raise KeyError("Indices in key '{}' already in use.".format(key))
        # create instance of subplot_spec_handler
        subplot_spec_handler = _SubplotSpecHandler(self._fig, self._grid[key])
        # append subplot_spec_handler and reserve key
        self._handlers.append(subplot_spec_handler)
        self._keys.append(key)
        self._reserved[key] = True
        # return
        return subplot_spec_handler

    @property
    def axes(self):
        """all matplotlib.pyplot.Axis objects in a flattened array
        """

        return np.concatenate([
            handler.axes
            for handler in self._handlers
        ])

    def add_panel_letters(self, lower=False, **kwargs):
        """
        Add panel letters to each axis

        Parameters
        ----------
        lower : bool, optional
            Whether panel letters are lowercase. Defaults to False.
        kwargs : dict, optional
            Arguments passed to `panel_letter` function.
        """

        for idx, ax in enumerate(self.axes):
            letter = get_letter(idx, lower)
            panel_letter(ax, letter, **kwargs)


class _SubplotSpecHandler:

    def __init__(self, fig, subplot_spec):

        self._fig = fig
        self._subplot_spec = subplot_spec

        self._reserved = False
        self._g = None
        self._axes = None
        self._subplot_grid = None

    @property
    def axes(self):
        """matplotlib.pyplot.Axis objects in a flattened array
        """
        return np.array([]) if self._axes is None else self._axes

    def __getattr__(self, name):
        if hasattr(self._g, name):
            return getattr(self._g, name)
        else:
            raise AttributeError(
                '{} does not have attribute {}'.format(type(self._g), name)
            )

    def add_facetgrid(self, *args, **kwargs):
        """
        Parameters
        ----------
        args, kwargs : tuple, dict
            Arguments passed to `FacetGrid`.

        Returns
        -------
        g : `FacetGrid` object
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = FacetGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g
        self._subplot_grid = g._gridspec
        self._axes = g.axes.flatten()

        return g

    def add_pairgrid(self, *args, **kwargs):
        """
        Parameters
        ----------
        args, kwargs : tuple, dict
            Arguments passed to `PairGrid`.

        Returns
        -------
        g : `PairGrid` object
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = PairGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g
        self._subplot_grid = g._gridspec
        self._axes = g.axes.flatten()

        return g

    def add_jointgrid(self, *args, **kwargs):
        """
        Parameters
        ----------
        args, kwargs : tuple, dict
            Arguments passed to `JointGrid`.

        Returns
        -------
        g : `JointGrid` object
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = JointGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g
        self._subplot_grid = g._gridspec
        self._axes = np.array([self.ax_joint, self.ax_marg_x, self.ax_marg_y])

        return g

    def add_subplot(self, despine=True, **subplot_kws):
        """
        Parameters
        ----------
        despine : bool
            Whether to apply `despine` to axis.
        subplot_kws : dict
            Arguments passed to `plt.Subplot`.

        Returns
        -------
        ax : matplotlib.pyplot.Axis
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = gridspec.GridSpecFromSubplotSpec(
            1, 1,
            subplot_spec=self._subplot_spec
        )
        ax = plt.Subplot(self._fig, g[0, 0], **subplot_kws)
        self._fig.add_subplot(ax)

        if despine:
            utils.despine(ax=ax)

        self._reserved = True
        self._g = ax
        self._subplot_grid = g
        self._axes = np.array([ax])

        return ax

    def add_grid(
        self, nrows=1, ncols=1,
        sharex=False, sharey=False, squeeze=True,
        wspace=None, hspace=None,
        height_ratios=None, width_ratios=None,
        despine=True,
        **subplot_kws
    ):
        """
        Parameters
        ----------
        nrows, ncols, sharex, sharey, squeeze : various
            Same as those passed to `plt.subplots`
        wspace, hspace, height_ratios, width_ratios : various
            Same as those passed to `gridspec.GridSpec`
        despine : bool
            Whether to apply `despine` to axis.
        subplot_kws : dict
            Arguments passed to each subplot instance.

        Returns
        -------
        axes : array of matplotlib.pyplot.Axis
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = gridspec.GridSpecFromSubplotSpec(
            nrows=nrows, ncols=ncols,
            subplot_spec=self._subplot_spec,
            wspace=wspace,
            hspace=hspace,
            height_ratios=height_ratios,
            width_ratios=width_ratios
        )

        axes = np.empty((nrows, ncols), object)

        for irow in range(nrows):
            for icol in range(ncols):

                # sharex
                if sharex == 'row' and icol > 0:
                    subplot_kws['sharex'] = axes[irow, 0]
                elif sharex == 'col' and irow > 0:
                    subplot_kws['sharex'] = axes[0, icol]
                elif sharex and ((irow > 0) or (icol > 0)):
                    subplot_kws['sharex'] = axes[0, 0]
                else:
                    subplot_kws['sharex'] = None

                # sharey
                if sharey == 'row' and icol > 0:
                    subplot_kws['sharey'] = axes[irow, 0]
                elif sharey == 'col' and irow > 0:
                    subplot_kws['sharey'] = axes[0, icol]
                elif sharey and ((irow > 0) or (icol > 0)):
                    subplot_kws['sharey'] = axes[0, 0]
                else:
                    subplot_kws['sharey'] = None

                axes[irow, icol] = plt.Subplot(
                    self._fig, g[irow, icol], **subplot_kws)

                self._fig.add_subplot(axes[irow, icol])

        # Now we turn off labels on the inner axes
        if sharex and not sharex == 'row':
            for ax in axes[:-1, :].flat:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
                ax.xaxis.offsetText.set_visible(False)

        if sharey and not sharey == 'col':
            for ax in axes[:, 1:].flat:
                for label in ax.get_yticklabels():
                    label.set_visible(False)
                ax.yaxis.offsetText.set_visible(False)

        if squeeze:
            axes = np.squeeze(axes)

        if despine:
            for ax in axes.flat:
                utils.despine(ax=ax)

        self._reserved = True
        self._g = axes
        self._subplot_grid = g
        self._axes = axes.flatten()

        return axes
