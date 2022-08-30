#!/usr/bin/env python3

import __init__

from plotter import Plotter
import fitting

import numpy as np
import os, sys

from uncertainties import ufloat

base_dir = os.path.dirname(os.path.abspath(__file__))

wavelength = 1070
labels = ["Horizontal, x", "Vertical, y"]

DATA = np.loadtxt(os.path.join(base_dir, "2022-07-12_IPG_m2.dat"))


z = DATA[:,0]   # mm
x = DATA[:,2]/2 # radius, horizontal, um
y = DATA[:,1]/2 # radius, vertical,   um

fitters = [
    fitting.fitter.MsqOCFFitter(x = z, y = x, yerror = 0.1, wavelength = wavelength, mode = 1), 
    fitting.fitter.MsqOCFFitter(x = z, y = y, yerror = 0.1, wavelength = wavelength, mode = 1)
]


i = 0
for f in fitters:
    # array([w_0, z_0, M_sq])

    print("\n\n ========= ", labels[i], " =========")
    f.estimateAndFit()
    f.printOutput()

err_params = {
     "marker": ' ', 
    #  "markersize": 6, 
     "capsize" : 4, 
     "fmt" : ' ',
     "capthick" : 0.6, 
     "linewidth": 0.6
}
scatter_params = {
    "linewidth": 0.6,
    "marker": "x"
}
plot_params = {
    "linewidth": 1
}

colours = ["mediumvioletred", "darkcyan"]
colours_error = ["lightpink", "paleturquoise"]

plot_x = np.linspace(start = np.min(DATA[:, 0]), stop = np.max(DATA[:, 0]), endpoint = True, num = 1000)

plot_h = fitters[0].predict(x = plot_x)
plot_v = fitters[1].predict(x = plot_x)

errors_h = fitters[0].conf_interval(z = plot_x)
errors_v = fitters[1].conf_interval(z = plot_x)

plotter = Plotter(figsize = (9, 5))

# Best Fits
plotter.ax.plot(plot_x, plot_h, label = "Horizontal-Fit, $M^2 = 1.033$", color = colours[0], **plot_params)
plotter.ax.fill_between(plot_x, plot_h - errors_h, plot_h + errors_h, color=colours_error[0])
plotter.ax.plot(plot_x, plot_v, label = "Vertical-Fit, $M^2 = 1.066$", color = colours[1], **plot_params)
plotter.ax.fill_between(plot_x, plot_v - errors_v, plot_v + errors_v, color=colours_error[1])

# Data points
plotter.ax.errorbar(DATA[:, 0], DATA[:, 2]/2, 0.1, label = "Horizontal", color = colours[0], **err_params)
plotter.ax.scatter(DATA[:, 0], DATA[:, 2]/2, color = colours[0], **scatter_params)
plotter.ax.errorbar(DATA[:, 0], DATA[:, 1]/2, 0.1, label = "Vertical", color = colours[1], **err_params)
plotter.ax.scatter(DATA[:, 0], DATA[:, 1]/2, color = colours[1], **scatter_params)

plotter.ax.set_title("\\shortstack{IPG-YLR-200-LP-WC Beam Caustic Measurement\\\\Wavelength 1070 nm}")
plotter.ax.set_xlabel("Position (mm)")
plotter.ax.set_ylabel("Beam Radius ($\\mu$m)")

plotter.ax.legend(loc = "upper right")
Plotter.reorderLegend(ax = plotter.ax, order = ["Horizontal", f"Horizontal-Fit, $M^2 = {np.around(fitters[0].m_squared[0], decimals = 3)}$", "Vertical", f"Vertical-Fit, $M^2 = {np.around(fitters[1].m_squared[0], decimals = 3)}$"])

plotter.fig.text(0.3, 0.8, "\\shortstack[l]{Measurement Lens:\\\\Thorlabs LA1433-B Lens\\\\$f = 150$ mm}", va='center', ha='center', rotation='horizontal', fontsize='medium')

# plotter.show()
plotter.savefig(os.path.join(base_dir, "generated", "2022-07-12_IPG_m2.pdf"), backend = "pdf")