#!/usr/bin/env python3

import __init__

from plotter import Plotter
import fitting

from beamprofiler_data.beamprofilerData import BeamprofilerTimeseriesData
from helpers import findIntersection

import numpy as np
import os, sys
import glob

from uncertainties import ufloat

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(base_dir, "..", "beamprofiler_data", "2022-07-13_Caustic after 200mm Lens"))

wavelength = 1064
labels = ["Horizontal, x", "Vertical, y"]

def positionFromFileName(filename: str) -> float:
    _x = filename.split(os.path.sep)[-1][:-4] # Get basename using .csv ext
    assert _x.endswith("mm")

    return float(_x[:-2])

dtpts = []
x = []; y = []; z = []
x_err = []; y_err = []
for path in glob.glob(os.path.join(data_dir, "*.csv")):
    _dtpt = BeamprofilerTimeseriesData(path, autostats = True)
    _z = positionFromFileName(path) # mm
    _x = _dtpt.DATA["v_width_mum"] # um
    _y = _dtpt.DATA["h_width_mum"] # um
    
    z.append(_z)
    x.append(_x.nominal_value)
    x_err.append(_x.std_dev)
    y.append(_y.nominal_value)
    y_err.append(_y.std_dev)

x = np.array(x)/2; y = np.array(y)/2 # convert to radius
z = np.array(z)
x_err = np.array(x_err); y_err = np.array(y_err)


fitters = [
    fitting.fitter.MsqOCFFitter(x = z, y = x, yerror = x_err, wavelength = wavelength, mode = 1), 
    fitting.fitter.MsqOCFFitter(x = z, y = y, yerror = y_err, wavelength = wavelength, mode = 1)
]


i = 0
for f in fitters:
    # array([w_0, z_0, M_sq])

    print("\n\n ========= ", labels[i], " =========")
    f.estimateAndFit()
    f.printOutput()
    i += 1

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

plot_x = np.linspace(start = np.min(z), stop = np.max(z), endpoint = True, num = 1000)

plot_h = fitters[0].predict(x = plot_x)
plot_v = fitters[1].predict(x = plot_x)

errors_h = fitters[0].conf_interval(z = plot_x)
errors_v = fitters[1].conf_interval(z = plot_x)

plotter = Plotter(figsize = (9, 5))

# Best Fits
plotter.ax.plot(plot_x, plot_h, label = f"Horizontal-Fit, $M^2 = {np.around(fitters[0].m_squared[0], decimals = 3)}$", color = colours[0], **plot_params)
plotter.ax.fill_between(plot_x, plot_h - errors_h, plot_h + errors_h, color=colours_error[0])
plotter.ax.plot(plot_x, plot_v, label = f"Vertical-Fit, $M^2 = {np.around(fitters[1].m_squared[0], decimals = 3)}$", color = colours[1], **plot_params)
plotter.ax.fill_between(plot_x, plot_v - errors_v, plot_v + errors_v, color=colours_error[1])

# Data points
plotter.ax.errorbar(z, x, x_err, label = "Horizontal", color = colours[0], **err_params)
plotter.ax.scatter(z, x, color = colours[0], **scatter_params)
plotter.ax.errorbar(z, y, y_err, label = "Vertical", color = colours[1], **err_params)
plotter.ax.scatter(z, y, color = colours[1], **scatter_params)

plotter.ax.set_title("\\shortstack{Beam Caustic after 200 mm Lens\\\\Wavelength 1064 nm (Laser-export LCS-T-12 DPSS Laser)}")
plotter.ax.set_xlabel("Position (mm)")
plotter.ax.set_ylabel("Beam Radius ($\\mu$m)")

plotter.fig.text(0.5, 0.4, f"\\begin{{align}}w_{{0\\text{{, horz}}}} &= ({np.around(fitters[0].output.beta[0], decimals = 2)} \\pm {np.around(fitters[0].output.sd_beta[0], decimals = 2)}) ~\\si{{\\micro\\meter}}\\\\w_{{0\\text{{, vert}}}} &= ({np.around(fitters[1].output.beta[0], decimals = 2)} \\pm {np.around(fitters[1].output.sd_beta[0], decimals = 2)}) ~\\si{{\\micro\\meter}}\\end{{align}}", fontsize = "large")
# plotter.ax.arrow(7, 37, 0.3, -5) # data units
                        # end              # begin
plotter.ax.annotate("", xy=(7.3, 27), xytext=(7, 51), arrowprops=dict(arrowstyle="->"))

plotter.ax.legend(loc = "upper right")
Plotter.reorderLegend(ax = plotter.ax, order = ["Horizontal", f"Horizontal-Fit, $M^2 = {np.around(fitters[0].m_squared[0], decimals = 3)}$", "Vertical", f"Vertical-Fit, $M^2 = {np.around(fitters[1].m_squared[0], decimals = 3)}$"])

z0_x = ufloat(fitters[0].output.beta[1], fitters[0].output.sd_beta[1])
z0_y = ufloat(fitters[1].output.beta[1], fitters[1].output.sd_beta[1])

delta = z0_x - z0_y
print("====================================")
print("Astigmatism: ", delta.nominal_value, "+/-", delta.std_dev, "mm")

print("====================================")

# FIND THE INTERSECTION
def horz(x: float | np.ndarray) -> float | np.ndarray:
    return fitters[0].predict(x = x)

def vert(x: float | np.ndarray) -> float | np.ndarray:
    return fitters[1].predict(x = x)

intersection_z = findIntersection(func1 = horz, func2 = vert, initialGuess = 7)
intersection_waist = horz(intersection_z)

if not isinstance(intersection_z, float):
    intersection_z = intersection_z[0]

if not isinstance(intersection_waist, float):
    intersection_waist = intersection_waist[0]

print(intersection_z, "mm:", intersection_waist, "um")

plotter.fig.text(0.2, 0.2, f"\\shortstack[l]{{Point of round beam\\\\$({np.around(intersection_z, decimals = 2)} \\si{{\\milli\\meter}}, {np.around(intersection_waist, decimals = 2)} \\si{{\\micro\\meter}})$}}", fontsize = "large")
                        # end                                          # begin
plotter.ax.annotate("", xy=(intersection_z - 0.5, intersection_waist), xytext=(4, 30), arrowprops=dict(arrowstyle="->"))

# plotter.show()
plotter.savefig(os.path.join(base_dir, "generated", "2022-07-13_caustic_after_200mm_lens.pdf"), backend = "pdf")