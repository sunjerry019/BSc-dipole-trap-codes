#!/usr/bin/env python3

import wave
import __init__
import numpy as np
from plotter import Plotter
from spectrum_analyser.anritsuData import AnritsuData

import os

#   SETTINGS 
figsize = (5.5, 3.5)
datafile = os.path.join(__init__.base_dir, "VCO_Freq_power.dat")
# / SETTINGS

DATA = np.loadtxt(datafile)
PLOTTER = Plotter(figsize = figsize)

wavelengths = DATA[:, 0]
power       = AnritsuData.dBmToWatt(DATA[:, 1] + 20)

PLOTTER.ax.scatter(wavelengths, power, marker = "x", label = "RF Output", color = "tab:red")
PLOTTER.ax.set_title("\\shortstack{Change in POS-150+ AOM Driver RF Output Power\\\\with Measured Frequency}")
PLOTTER.fig.subplots_adjust(top = 0.85, bottom = 0.2)
PLOTTER.ax.set_xlabel("Measured Output Frequency (MHz)")
PLOTTER.ax.set_ylabel("RF Output Power (W)")
PLOTTER.ax.set_ylim([2.3, 5.7])
PLOTTER.ax.legend()
# PLOTTER.show()
PLOTTER.savefig(os.path.join(__init__.base_dir, "generated", "VCO_Freq_power.pdf"), backend = "PDF")