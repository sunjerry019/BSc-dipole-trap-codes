#!/usr/bin/env python3

# PLOTTER CLASS

from matplotlib import rc
import matplotlib.pyplot as plt

class Plotter():
    COLORMAP = "inferno"
    COLORMAP_R = "inferno_r"
    
    def __init__(self, *args, **kwargs) -> None:
        Plotter.initMPLSettings()

        self.fig, self.axs = plt.subplots(*args, **kwargs)

    @staticmethod
    def initMPLSettings():
        rc('text', usetex = True)
        rc('text.latex', preamble = r"\usepackage{libertine}\usepackage{nicefrac}")
        rc('font', size = 11, family = "Sans-Serif")

    def savefig(self, *args, **kwargs) -> None:
        return plt.savefig(*args, **kwargs)

    def show(self) -> None:
        return plt.show()