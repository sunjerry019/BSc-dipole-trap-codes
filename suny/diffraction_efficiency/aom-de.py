#!/usr/bin/env python3

import __init__
import os, sys

from plotter import Plotter
import pandas as pd
import numpy as np

datafile = os.path.join(__init__.base_dir, "data", "AOM_DE_complete_data.dat")
figsize = (8,4)

DATAF = pd.read_csv(datafile, sep = '\t', skiprows = 2, header = 0)

DATA = DATAF.sort_values(by = ["# RF Freq/MHz", "RF Input/dBm"])

freqs = DATA["# RF Freq/MHz"].unique()
powers = DATA["RF Input/dBm"].unique()
output = (DATA["Power/uW"].to_numpy() * 100) / 611.09

X, Y = np.meshgrid(freqs, powers)
C    = output.reshape((len(freqs), len(powers))).T

plotter = Plotter(figsize = figsize)
p1 = plotter.ax.pcolormesh(X, Y, C, cmap=plotter.COLORMAP, vmin=C.min(), vmax=C.max(), rasterized = True)
# plotter.ax.contour(Z, X, potentials_for_contour_plotting, colours = 'white', vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), linestyles = "dashed")
cb = plotter.fig.colorbar(p1, ax = plotter.axs)

plotter.ax.set_title('AOM Diffraction Efficiency')
plotter.ax.set_xlabel("RF Input Frequency (MHz)")
plotter.ax.set_ylabel("RF Input Power (dBm)")
plotter.fig.tight_layout()
# plotter.fig.subplots_adjust(right=0.9)
plotter.fig.text(0.92, 0.52, "\\% Transmitted in the first order ($\\mu$W)", rotation = "vertical", va = "center", ha = "center")
# plotter.show()
plotter.savefig(os.path.join(__init__.base_dir, "generated", f"aom-de.pdf"), backend = "PDF")