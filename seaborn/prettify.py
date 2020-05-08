"""
(c) Matthias Christenson

function to create scalebar
"""

import string
import matplotlib as mpl

import numpy as np
import seaborn as sns


def scalebar(
        ax, xsize=None, ysize=None, xunits=None, yunits=None,
        xleft=-0.01, ybottom=-0.01, bottom=False, right=True,
        left=False, top=True, ylim=None, xlim=None,
        infer_sizes=False, infer_units=False, offset=None,
        xformat=False, yformat=False, digits=2,
        **kwargs
        ):
    """
    Create scalebars for a particular matplotlib.pyplot.axis object.

    Parameters
    ----------
    ax : matplotlib.pyplot.axis
        Axis instance.
    xsize, ysize : float, optional
        Size of x/y scale. If None and infer_sizes is False or
        "infer_y"/"infer_x", the x/y-axis will not be converted into
        a scalebar. Defaults to None.
    xunits, yunits : str, optional
        String of x/y unit name (e.g. "s") or formattable string
        to include xsize/ysize (e.g. "{}s"). Defaults to None.
    xleft, ybottom: float, optional
        Position of x/y scale bar relative to axis object. Defaults to -0.01.
    bottom, right, left, top: bool, optional
        Arguments passed to `sns.despine`. `trim=True` and `ax=ax` will
        also be passed to despine.
    xlim, ylim : two-tuple of floats, optional
        Two tuple of x/y axis limits. If None, limits will be inferred.
        Defaults to None.
    infer_sizes : bool or str, optional
        If True, infer xsize and ysize when not given. If "infer_x" or
        "infer_y" only infer xsize or ysize respectively.
    offset : float, optional
        Offset is passed to `sns.despine`.
    xformat, yformat : bool, optional
        Set to True, if xunits/yunits is a formattable string.
        See xunits/yunits.
    digits : int, optional
        If infer_sizes is True, the number of significant digits to show
        for each scale bar.
    kwargs : dict, optional
        Passed to ax.text for each scalebar label.
    """
    if ylim is None:
        ylim = ax.get_ylim()
    else:
        ax.set_ylim(*ylim)

    if xlim is None:
        xlim = ax.get_xlim()
    else:
        ax.set_xlim(*xlim)

    # infer xsize and ysize from ticks
    xsize, ysize = _infer_sizes(
        ax, infer_sizes, xsize, ysize, digits)
    xunits, yunits = _infer_units(
        ax, infer_units, xunits, yunits, xformat, yformat)

    xleft, ybottom = axis_data_coords_sys_transform(ax, xleft, ybottom)

    if xsize is not None:

        ax.set_xticks([xlim[0], xlim[0]+xsize])
        half = (xlim[0]*2+xsize)/2
        if xunits is not None:
            if xformat:
                ax.text(
                    half, ybottom,
                    xunits.format(xsize),
                    verticalalignment='top',
                    horizontalalignment='center',
                    **kwargs
                )
            else:
                ax.text(
                    half, ybottom,
                    '{} {}'.format(xsize, xunits),
                    verticalalignment='top',
                    horizontalalignment='center',
                    **kwargs
                )
        else:
            ax.text(
                half, ybottom,
                '{}'.format(xsize),
                verticalalignment='top',
                horizontalalignment='center',
                **kwargs
            )

    if ysize is not None:

        ax.set_yticks([ylim[0], ylim[0]+ysize])
        half = (ylim[0]*2+ysize)/2
        if yunits is not None:
            if yformat:
                ax.text(
                    xleft, half,
                    yunits.format(ysize),
                    verticalalignment='center',
                    horizontalalignment='right',
                    rotation=90,
                    **kwargs
                )
            else:
                ax.text(
                    xleft, half,
                    '{} {}'.format(ysize, yunits),
                    verticalalignment='center',
                    horizontalalignment='right',
                    rotation=90,
                    **kwargs
                )
        else:
            ax.text(
                xleft, half,
                '{}'.format(ysize),
                verticalalignment='center',
                horizontalalignment='right',
                rotation=90,
                **kwargs
            )
    sns.despine(
        ax=ax, trim=True, offset=offset,
        bottom=bottom, top=top, left=left, right=right
    )

    if xsize is not None:
        ax.set_xticks([])
    if ysize is not None:
        ax.set_yticks([])
    if xunits is not None:
        ax.set_xlabel('')
    if yunits is not None:
        ax.set_ylabel('')
    return ax


def _infer_sizes(ax, infer_sizes, xsize, ysize, digits):
    # infer xsize and ysize from ticks
    if infer_sizes:
        if xsize is None and infer_sizes != 'infer_y':
            xticks = ax.get_xticks()
            xsize = xticks[1] - xticks[0]
            xsize = siground(xsize, digits=digits)
        if ysize is None and infer_sizes != 'infer_x':
            yticks = ax.get_yticks()
            ysize = yticks[1] - yticks[0]
            ysize = siground(ysize, digits=digits)

    return xsize, ysize


def _infer_units(ax, infer_units, xunits, yunits, xformat, yformat):
    # infer yunits and xunits from labels
    if infer_units:
        if xunits is None and infer_units != 'infer_y':
            xunits = ax.get_xlabel()
            if xformat:
                xunits = '{}' + xunits
        if yunits is None and infer_units != 'infer_x':
            yunits = ax.get_ylabel()
            if yformat:
                yunits = '{}' + yunits

    return xunits, yunits


def axis_data_coords_sys_transform(ax, xin, yin, inverse=False):
    """ inverse = False : Axis => Data
                = True  : Data => Axis
    """
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xdelta = xlim[1] - xlim[0]
    ydelta = ylim[1] - ylim[0]
    if not inverse:
        xout = xlim[0] + xin * xdelta
        yout = ylim[0] + yin * ydelta
    else:
        xdelta2 = xin - xlim[0]
        ydelta2 = yin - ylim[0]
        xout = xdelta2 / xdelta
        yout = ydelta2 / ydelta
    return xout, yout


def panel_letter(
    ax, letter, xpos=-0.1, ypos=1.1,
    weight='bold', font_scale=1.5, size=None,
    transform='axes', **kwargs
):
    """
    Add a panel letter to a matplotlib.pyplot.axis object.
    """
    if size is None:
        size = mpl.rcParams['font.size'] * font_scale
    if transform == 'axes':
        transform = ax.transAxes
    ax.text(
        xpos, ypos, letter, size=size, weight=weight,
        transform=transform, **kwargs
    )
    return ax


def get_letter(idx, lower=False):

    if lower:
        letters = string.ascii_lowercase
    else:
        letters = string.ascii_uppercase

    letter_idx = idx % 26
    repeats = (idx // 26) + 1

    return letters[letter_idx] * repeats


def siground(x, digits):
    """round number up to significant digit
    """

    if x == 0:
        return x

    def digits_to_decimals(x, digits):
        return -np.floor(np.log10(np.abs(x))) + digits - 1

    decimals = int(digits_to_decimals(x, digits))

    return np.ceil(x*10**decimals) / (10**decimals)
