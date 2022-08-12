#!/usr/bin/env python3

# PLOTTER CLASS

from matplotlib import rc
import matplotlib.pyplot as plt

from matplotlib.axes._axes import Axes
from matplotlib.ticker import AutoMinorLocator

from typing import Tuple

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
            

    @staticmethod
    def initMPLSettings():
        rc('text', usetex = True)
        rc('text.latex', preamble = r"\usepackage{libertine}\usepackage{nicefrac}")
        rc('font', size = 11, family = "Sans-Serif")

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