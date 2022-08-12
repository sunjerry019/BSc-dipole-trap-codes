#!/usr/bin/env python3

import __init__

from plotter import Plotter

import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

wavelength = 1070
def hori(x: np.ndarray | float) -> np.ndarray | float:
    return 23.79708627 * np.sqrt(1 + ((x - (7.73953974))**2)*(((1.03252135 * wavelength)/(np.pi * (23.79708627**2)))**2))

def vert(x: np.ndarray | float) -> np.ndarray | float:
    return 24.25144646 * np.sqrt(1 + ((x - (7.27852809))**2)*(((1.06551593 * wavelength)/(np.pi * (24.25144646**2)))**2))

DATA = np.loadtxt(os.path.join(base_dir, "2022-07-12_IPG_m2.dat"))

scatter_params = {
     "marker": 'x', 
     "markersize": 6, 
     "capsize" : 4, 
     "capthick" : 0.5, 
     "fmt" : ' '
}

colours = ["mediumvioletred", "darkcyan"]

plot_x = np.linspace(start = np.min(DATA[:, 0]), stop = np.max(DATA[:, 0]), endpoint = True, num = 1000)
plot_h = hori(plot_x)
plot_v = vert(plot_x)

plotter = Plotter(figsize = (10, 5))
plotter.ax.errorbar(DATA[:, 0], DATA[:, 2]/2, 0.1, label = "Horizontal", color = colours[0], **scatter_params)
plotter.ax.plot(plot_x, plot_h, label = "Horizontal-Fit, $M^2 = 1.033$", color = colours[0])
plotter.ax.errorbar(DATA[:, 0], DATA[:, 1]/2, 0.1, label = "Vertical", color = colours[1], **scatter_params)
plotter.ax.plot(plot_x, plot_v, label = "Vertical-Fit, $M^2 = 1.066$", color = colours[1])

plotter.ax.set_title("\\shortstack{IPG-YLR-200-LP-WC Beam Caustic Measurement\\\\Wavelength 1070 nm}")
plotter.ax.set_xlabel("Position (mm)")
plotter.ax.set_ylabel("Beam Radius ($\\mu$m)")

plotter.ax.legend(loc = "upper right")
Plotter.reorderLegend(ax = plotter.ax, order = ["Horizontal", "Horizontal-Fit, $M^2 = 1.033$", "Vertical", "Vertical-Fit, $M^2 = 1.066$"])

plotter.show()