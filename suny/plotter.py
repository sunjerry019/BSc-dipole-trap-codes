#!/usr/bin/env python3

# PLOTTER CLASS

from matplotlib import rc
import matplotlib.pyplot as plt

import matplotlib.patches as mpl_p
import matplotlib.legend as mpl_l

from matplotlib.axes._axes import Axes
from matplotlib.ticker import AutoMinorLocator

from typing import Any, Iterable, List, Tuple, Union

import numpy as np

class Plotter():
    COLORMAP = "inferno"
    COLORMAP_R = "inferno_r"

    MINORTICK_COLOR = "black"

    def __init__(self, *args, **kwargs) -> None:
        Plotter.initMPLSettings()

        self.fig, self.axs = plt.subplots(*args, **kwargs)
        self.ax = self.axs

        if isinstance(self.axs, np.ndarray):
            _vert, _horz = self.axs.shape

            for i in range(_vert):
                for j in range(_horz):
                    ax = self.axs[i, j]
                    ax.tick_params(axis = 'both', which = 'both', direction = 'out')
                    ax.tick_params(axis = 'both', which = 'minor', colors = self.MINORTICK_COLOR)
                    ax.xaxis.set_minor_locator(AutoMinorLocator())
                    ax.yaxis.set_minor_locator(AutoMinorLocator())
        else:
            self.ax.tick_params(axis = 'both', which = 'both', direction = 'out')
            self.ax.tick_params(axis = 'both', which = 'minor', colors = self.MINORTICK_COLOR)
            self.ax.xaxis.set_minor_locator(AutoMinorLocator())
            self.ax.yaxis.set_minor_locator(AutoMinorLocator())
    

    #  Returns tuple of handles, labels for axis ax, after reordering them to conform to the label order `order`, and if unique is True, after removing entries with duplicate labels.
    # https://stackoverflow.com/a/35926913
    @staticmethod
    def reorderLegend(ax: Union[Axes, None] = None, order: Union[list, None] = None, unique: bool = False) -> Tuple[Tuple, Tuple]:
        if ax is None: 
            ax = plt.gca()

        handles, labels = ax.get_legend_handles_labels()
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0])) # sort both labels and handles by labels
        if order is not None: # Sort according to a given list (not necessarily complete)
            keys=dict(zip(order,range(len(order))))
            labels, handles = zip(*sorted(zip(labels, handles), key=lambda t,keys=keys: keys.get(t[0], np.inf)))
        
        if unique:  
            labels, handles= zip(*Plotter.unique_everseen(zip(labels,handles), key = labels)) # Keep only the first of each handle
        
        legendProp = { "handles": handles, "labels": labels}

        # Check if legend already exists
        oldLegend = ax.get_legend()
        # if old legend exists, update
        if oldLegend is not None:
            legendProp = Plotter.updateLegend(oldLegend = oldLegend, **legendProp)
        
        ax.legend(**legendProp)
        return (handles, labels)

    @staticmethod
    def updateLegend(oldLegend: mpl_l.Legend, **kwargs) -> dict:
        # https://stackoverflow.com/a/28089529

        defaults = dict(
            loc = oldLegend._loc,
            numpoints = oldLegend.numpoints,
            markerscale = oldLegend.markerscale,
            scatterpoints = oldLegend.scatterpoints,
            scatteryoffsets = oldLegend._scatteryoffsets,
            prop = oldLegend.prop,
            # fontsize = None,
            borderpad = oldLegend.borderpad,
            labelspacing = oldLegend.labelspacing,
            handlelength = oldLegend.handlelength,
            handleheight = oldLegend.handleheight,
            handletextpad = oldLegend.handletextpad,
            borderaxespad = oldLegend.borderaxespad,
            columnspacing = oldLegend.columnspacing,
            ncol = oldLegend._ncol,
            mode = oldLegend._mode,
            fancybox = type(oldLegend.legendPatch.get_boxstyle()) == mpl_p.BoxStyle.Round,
            shadow = oldLegend.shadow,
            title = oldLegend.get_title().get_text() if oldLegend._legend_title_box.get_visible() else None,
            framealpha = oldLegend.get_frame().get_alpha(),
            bbox_to_anchor = oldLegend.get_bbox_to_anchor()._bbox,
            bbox_transform = oldLegend.get_bbox_to_anchor()._transform,
            frameon = oldLegend.draw_frame,
            handler_map = oldLegend._custom_handler_map,
        )

        if "fontsize" in kwargs and "prop" not in kwargs:
            defaults["prop"].set_size(kwargs["fontsize"])

        return defaults | kwargs # merge the two dictionaries

    @staticmethod
    def unique_everseen(seq: Iterable, key: Union[Iterable, None] = None) -> List[Any]:
        seen = set()
        seen_add = seen.add
        return [x for x,k in zip(seq,key) if not (k in seen or seen_add(k))]

    @staticmethod
    def initMPLSettings():
        rc('text', usetex = True)
        rc('text.latex', preamble = r"\usepackage{libertine}\usepackage{nicefrac}")
        rc('font', size = 11, family = "Sans-Serif")

    # MAPPING FUNCS
    def xlim(self, *args, **kwargs) -> Tuple[float, float]:
        return plt.xlim(*args, **kwargs)

    def ylim(self, *args, **kwargs) -> Tuple[float, float]:
        return plt.xlim(*args, **kwargs)

    def clf(self) -> None:
        return plt.clf()

    def savefig(self, *args, **kwargs) -> None:
        return plt.savefig(*args, **kwargs)

    def show(self) -> None:
        return plt.show()

    def gca(self) -> Axes:
        return plt.gca()