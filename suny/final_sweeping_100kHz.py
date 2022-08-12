#!/usr/bin/env python3

from spectrum_analyser.anritsuData import AnritsuData
import os

import numpy as np

from matplotlib.ticker import AutoMinorLocator

from plotter import Plotter

# LOAD FILES
base_dir = os.path.dirname(os.path.realpath(__file__))
spc_data_dir   = os.path.join(base_dir, "spectrum_analyser", "2022-08-05_High Frequency Painting", "zoomed_in")
spc_data_dir_2 = os.path.join(base_dir, "spectrum_analyser", "2022-08-11_High Frequency Painting_zoomed")

original_spectrum   = AnritsuData(os.path.join(spc_data_dir, "2022-08-05-100kHz-Ramp_1.csv"))
new_spectrum_100khz = AnritsuData(os.path.join(spc_data_dir_2, "2022-08-11-100kHz-Ramp-1_1.csv"))
new_spectrum_1khz   = AnritsuData(os.path.join(spc_data_dir_2, "2022-08-11-100kHz-Ramp-1_1kHzBW.csv"))

DATA_ORG = {
    "O_3.4 MHz": AnritsuData(os.path.join(spc_data_dir, "2022-08-05-3.4MHz-Ramp_1.csv")),
    "O_2.1 MHz": AnritsuData(os.path.join(spc_data_dir, "2022-08-05-2.1MHz-Ramp_1.csv")),
    "O_100 kHz": AnritsuData(os.path.join(spc_data_dir, "2022-08-05-100kHz-Ramp_1.csv")),
    "BW_100 kHz" : AnritsuData(os.path.join(spc_data_dir_2, "2022-08-11-100kHz-Ramp-1_1.csv")),
    "BW_1 kHz"   : AnritsuData(os.path.join(spc_data_dir_2, "2022-08-11-100kHz-Ramp-1_1kHzBW.csv"))
}
# / LOAD FILES

# CONVERT UNITS
data_plt = {}

for key in DATA_ORG:
    data_plt[key] = { "FREQ": DATA_ORG[key].DATA["A"]["FREQ"], "POWER": AnritsuData.dBmToWatt(DATA_ORG[key].DATA["A"]["POWER"]) }
# / CONVERT UNITS

# SCALING
allOriginalPowers = np.concatenate((data_plt["O_3.4 MHz"]["POWER"], data_plt["O_2.1 MHz"]["POWER"], data_plt["O_100 kHz"]["POWER"]))
maxOriginalPower = np.max(allOriginalPowers)

for key in DATA_ORG:
    data_plt[key]["POWER"] = data_plt[key]["POWER"] / maxOriginalPower

max_power_O_100kHz = np.max(data_plt["O_100 kHz"]["POWER"])
maxNewPower = np.max(data_plt["BW_1 kHz"]["POWER"])

for key in ["BW_1 kHz"]: # "BW_100 kHz"
    data_plt[key]["POWER"] = data_plt[key]["POWER"] * (max_power_O_100kHz / maxNewPower)
# / SCALING

# https://matplotlib.org/stable/gallery/subplots_axes_and_figures/zoom_inset_axes.html
# PLOTTING
PLOTTER = Plotter(figsize = (8, 3.5))

PLOTTER.ax.plot(data_plt["O_100 kHz"]["FREQ"], data_plt["O_100 kHz"]["POWER"], color = "firebrick", linewidth = 1)

PLOTTER.ax.set_xlim([72.5,87.5])
PLOTTER.ax.set_title("$100$ kHz Resolution Bandwidth (RBW)")
PLOTTER.ax.set_xlabel("Frequency (MHz)")
PLOTTER.ax.set_ylabel("Normalized Power")

# axins = PLOTTER.ax.inset_axes([1.2, 0.25, 0.5, 0.5]) # [x0, y0, width, height]
axins = PLOTTER.ax.inset_axes([1.2, 0.15, 0.5, 0.75]) # [x0, y0, width, height]
axins.plot(data_plt["BW_1 kHz"]["FREQ"], data_plt["BW_1 kHz"]["POWER"], color = "firebrick", linewidth = 1)
axins.set_title("$1$ kHz RBW")
axins.tick_params(axis = 'both', which = 'both', direction = 'out')
axins.tick_params(axis = 'both', which = 'minor', colors = PLOTTER.MINORTICK_COLOR)
axins.xaxis.set_minor_locator(AutoMinorLocator())
axins.yaxis.set_minor_locator(AutoMinorLocator())
axins.set_ylim([-0.005, 0.07])
axins.set_xlabel("Frequency (MHz)")
axins.set_ylabel("Normalized Power")
PLOTTER.ax.indicate_inset_zoom(axins, edgecolor="#222222")

PLOTTER.fig.subplots_adjust(top= 0.82, right=0.6)
PLOTTER.fig.suptitle("RF Spectrum at $100$ kHz Modulation Frequency")

# PLOTTER.show()
PLOTTER.savefig(os.path.join(base_dir, "0_allplots", "high-freq-sweeping-100kHz.pdf"), backend = "pdf")
# / PLOTTING

# https://www.everythingrf.com/community/what-is-rbw-and-vbw-in-a-spectrum-analyzer
