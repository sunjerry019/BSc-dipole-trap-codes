#!/usr/bin/env python3

from spectrum_analyser.anritsuData import AnritsuData
from beamprofiler_data.beamprofilerData import BeamprofilerImageData
import os

from plotter import Plotter
import matplotlib_scalebar.scalebar

import numpy as np

# SETTINGS
plotting_order = ["100 kHz", "2.1 MHz", "3.4 MHz"]
plotter = Plotter(nrows = 3, ncols = 3, sharex = "col", squeeze = False, figsize = (10, 5))
onepixel = 5.2e-6 # in meters
# / SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))
img_data_dir = os.path.join(base_dir, "beamprofiler_data", "2022-08-05_High Frequency Painting")
spc_data_dir = os.path.join(base_dir, "spectrum_analyser", "2022-08-05_High Frequency Painting", "zoomed_in")

image_files_paths = {
    "3.4 MHz": os.path.join(img_data_dir, "3.4MHz_1.250.0V_10MHzModulation.csv"),
    "2.1 MHz": os.path.join(img_data_dir, "2.1MHz_1.250.0V_10MHzModulation.csv"),
    "100 kHz": os.path.join(img_data_dir, "100kHz_1.250.0V_10MHzModulation.csv")
}

spect_files_paths = {
    "3.4 MHz": os.path.join(spc_data_dir, "2022-08-05-3.4MHz-Ramp_1.csv"),
    "2.1 MHz": os.path.join(spc_data_dir, "2022-08-05-2.1MHz-Ramp_1.csv"),
    "100 kHz": os.path.join(spc_data_dir, "2022-08-05-100kHz-Ramp_1.csv")
}

image_files = {}
spect_files = {}

max_vert, max_horz = 0, 0
max_intensity      = 0
max_specpower      = - np.inf
for img in image_files_paths:
    # LOAD DATA
    image_files[img] = BeamprofilerImageData(datafile = image_files_paths[img])
    spect_files[img] = AnritsuData(datafile = spect_files_paths[img])

    _vert, _horz = image_files[img].DATA.shape

    max_vert = _vert if _vert > max_vert else max_vert
    max_horz = _horz if _horz > max_horz else max_horz

    max_intensity = max(max_intensity, np.max(image_files[img].DATA))
    max_specpower = max(max_specpower, np.max(spect_files[img].DATA["A"]["POWER"]))

max_specpower = AnritsuData.dBmToWatt(max_specpower)

for i, key in enumerate(plotting_order):
    image_files[key].padToSize(shape = (max_vert, max_horz + 5))

    # PLOT THE SPECTRUM
    _y = AnritsuData.dBmToWatt(data = spect_files[key].DATA["A"]["POWER"])
    _y = _y / max_specpower
    plotter.axs[i, 0].plot(spect_files[key].DATA["A"]["FREQ"], _y, label = key, color = "firebrick", linewidth = 1)
    plotter.axs[i, 0].set_xlim([60,100])
    # axs[i, 0].set_ylim([0, 1])
    # axs[i, 0].plot(spect_files[key].DATA["A"]["FREQ"], spect_files[key].DATA["A"]["POWER"], label = key)

    # PLOT THE IMAGE
    plotter.axs[i, 1].imshow(image_files[key].DATA, cmap = plotter.COLORMAP)
    scalebar = matplotlib_scalebar.scalebar.ScaleBar(onepixel, location = "lower left") # 1 pixel = 5.2 micrometer
    plotter.axs[i, 1].add_artist(scalebar)
    plotter.axs[i, 1].axes.xaxis.set_visible(False)
    plotter.axs[i, 1].axes.yaxis.set_visible(False)

    # PLOT THE HORIZONTAL CUT
    height, width = image_files[key].DATA.shape
    # PLOT THE MIDDLE
    mid = int(np.around(height/2))
    schnitt_y = image_files[key].DATA[mid,:]
    schnitt_x = (np.arange(width) - ((width - 1)/2) )* onepixel * 1e6

    schnitt_y = schnitt_y / max_intensity

    # TODO QUESTION: SHOULD I FIT SOMETHING OVER THIS?
    plotter.axs[i, 2].plot(schnitt_x, schnitt_y, color = "teal", linewidth = 1)
    plotter.axs[i, 2].set_ylim([0,1.1])

plotter.axs[0,2].set_title("Horizontal Cut")
plotter.axs[2,2].set_xlabel("$x$-Position ($\\mu$m)")
plotter.axs[1,2].set_ylabel("Normalised Intensity")

plotter.axs[0,1].set_title("CCD Image")
# plotter.axs[2,1].set_xlabel("$x$-Position")
# plotter.axs[1,1].set_ylabel("$y$ Position")

plotter.axs[0,0].set_title("Output Spectrum")
plotter.axs[2,0].set_xlabel("Frequency $f$ (MHz)")
plotter.axs[1,0].set_ylabel("Normalised Power")

plotter.fig.text(0.945, 0.76, "\\shortstack{$0.1$ MHz\\\\Modulation}", va='center', ha='center', rotation='horizontal', fontsize='large')
plotter.fig.text(0.945, 0.5, "\\shortstack{$2.1$ MHz\\\\Modulation}", va='center', ha='center', rotation='horizontal', fontsize='large')
plotter.fig.text(0.945, 0.23, "\\shortstack{$3.4$ MHz\\\\Modulation}", va='center', ha='center', rotation='horizontal', fontsize='large')
plotter.fig.subplots_adjust(right=0.89) # Anchor of the right side

plotter.fig.suptitle("High Frequency Modulated Painting Dipole Trap")

# plotter.show()
plotter.savefig(os.path.join(base_dir, "0_allplots", "high-freq-sweeping.eps"), backend = "eps")