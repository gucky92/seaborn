"""
FacetFigure
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

import seaborn as sns


class FacetFigure:
    """
    Construct a figure with single plots and sns.FacetGrid in it.
    """

    def __init__(
        self,
        nrows=1,
        ncols=1,
        figsize=None,
        dpi=None,
        facecolor=None,
        edgecolor=None,
        frameon=True,
        clear=False,
        **kwargs
    ):

        self._fig = plt.figure(
            figsize=figsize,
            dpi=dpi,
            facecolor=facecolor,
            edgecolor=edgecolor,
            frameon=frameon,
            clear=clear
        )

        self._grid = gridspec.GridSpec(
            nrows, ncols,
            figure=self.fig, **kwargs
        )

        self._reserved_keys = {}

    def __getitem__(self, key):
        subplot_spec = self._grid[key]

        if isinstance(key, slice):
            key = key.__reduce__()
        elif isinstance(key, tuple):
            _key = []
            for ikey in key:
                if isinstance(ikey, slice):
                    ikey = ikey.__reduce__()

                _key.append(ikey)
            key = tuple(_key)

        if key in self._reserved_keys:
            return self._reserved_keys[key]

        subplot_spec_handler = _SubplotSpecHandler(self._fig, subplot_spec)
        self._reserved_keys[key] = subplot_spec_handler
        return subplot_spec_handler


class _SubplotSpecHandler:

    def __init__(self, fig, subplot_spec):

        self._fig = fig
        self._subplot_spec = subplot_spec

        self._reserved = False
        self._g = None

    def __getattr__(self, name):
        if hasattr(self._g, name):
            return getattr(self._g, name)
        else:
            raise AttributeError(
                '{} does not have attribute {}'.format(type(self._g), name)
            )

    def add_facetgrid(self, *args, **kwargs):
        """
        Returns
        -------
        g
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = sns.FacetGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g

        return g

    def add_pairgrid(self, *args, **kwargs):
        """
        Returns
        -------
        g
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = sns.PairGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g

        return g

    def add_jointgrid(self, *args, **kwargs):
        """
        Returns
        -------
        g
        """

        if self._reserved:
            raise RuntimeError(
                'grid or plot for selected figure subplot already created.'
            )

        g = sns.JointGrid(
            *args,
            fig=self._fig,
            subplot_spec=self._subplot_spec,
            **kwargs
        )

        self._reserved = True
        self._g = g

        return g

    def add_subplot(self, **subplot_kws):
        """
        Returns
        -------
        ax : matplotlib.pyplot.Axis
        """

        g = gridspec.GridSpecFromSubplotSpec(
            1, 1,
            subplot_spec=self._subplot_spec
        )
        ax = plt.Subplot(self._fig, g[0, 0], **subplot_kws)
        self._fig.add_subplot(ax)

        self._reserved = True
        self._g = ax

        return ax

    def add_grid(
        self, nrows=1, ncols=1,
        sharex=False, sharey=False, squeeze=True,
        wspace=None, hspace=None,
        height_ratios=None, width_ratios=None,
        **subplot_kws
    ):
        """
        Returns
        -------
        axes : array of matplotlib.pyplot.Axis
        """

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

        if squeeze:
            axes = np.squeeze(axes)

        self._reserved = True
        self._g = axes

        return axes
