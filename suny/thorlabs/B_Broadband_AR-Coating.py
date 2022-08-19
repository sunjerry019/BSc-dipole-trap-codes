#!/usr/bin/env python3

from textwrap import fill
import __init__
from plotter import Plotter

import os, sys
import numpy as np
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))

# SETTINGS
data_file_R = os.path.join(base_dir, "B_Broadband_AR-Coating.dat")
data_file_N = os.path.join(base_dir, "N-BK7_RefractiveIndexINFO.csv")
colours = ["tab:red", "tab:cyan", 'cornsilk', 'tab:purple', "darkgoldenrod"]
PLOTTER = Plotter(figsize = (5, 3))
# / SETTINGS

DATA_R  = np.loadtxt(data_file_R)
DATA_N  = pd.read_csv(data_file_N, header = 0).drop("k", axis = 1).dropna()

DATA_N['# "Wavelength (µm)"'] *= 1e3

wavelength  = DATA_R[:,0]
reflectance = DATA_R[:,1]
wavelength2    = DATA_N['# "Wavelength (µm)"'].to_numpy()
refractive_idx = DATA_N["n"].to_numpy()

fill_x = np.linspace(start = 650, stop = 1050, num = 100)
fill_y = np.zeros_like(fill_x)

# PLOTTING
PLOTTER.ax.plot(wavelength, reflectance, color = colours[0], label = "Thorlabs B-Coating")
ax2 = PLOTTER.ax.twinx()
PLOTTER.addMinorTicks(ax2)
ax2.plot(wavelength2, refractive_idx, color = colours[1])

PLOTTER.ax.fill_between(fill_x, fill_y, fill_y + 3.5, color = colours[2])
PLOTTER.ax.text(x = 850, y = 2.5, s = "\\shortstack[c]{Specified Working Range\\\\($650$ - $1050$) nm}", ha = "center", va = "center", color = colours[4])
PLOTTER.ax.vlines([1064], ymin = 0, ymax = 3.5, color = colours[3], linestyles = "dashed")
PLOTTER.ax.text(x = 1075, y = 2.5, s = "$1064$ nm", ha = "left", va = "center", color = colours[3])

PLOTTER.ax.set_title("Properties of Thorlabs B-Coated N-BK7 Lenses")

PLOTTER.ax.set_xlabel("Wavelength (nm)")

PLOTTER.ax.set_ylim([0, 3])
PLOTTER.ax.set_xlim([500, 1200])

PLOTTER.ax.set_ylabel("Reflectance (\\si{\\percent})", color = colours[0])
ax2.set_ylabel("Refractive index $n$", color = colours[1])

# PLOTTER.fig.legend()
PLOTTER.fig.tight_layout()

PLOTTER.savefig(os.path.join(base_dir, "generated", "thorlabs_BK7_B.pdf"), backend = "PDF")