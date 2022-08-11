#!/usr/bin/env python3

from spectrum_analyser.anritsuData import AnritsuData
from beamprofiler_data.beamprofilerData import BeamprofilerImageData
import os

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib_scalebar.scalebar

import numpy as np

# SETTINGS
plotting_order = ["100 kHz", "2.1 MHz", "3.4 MHz"]
fig, axs = plt.subplots(nrows = 3, ncols = 3, sharex = "col", squeeze = False, figsize = (10, 5))
onepixel = 5.2e-6 # in meters
# / SETTINGS

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}\usepackage{nicefrac}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

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
for img in image_files_paths:
    # LOAD DATA
    image_files[img] = BeamprofilerImageData(datafile = image_files_paths[img])
    spect_files[img] = AnritsuData(datafile = spect_files_paths[img])

    _vert, _horz = image_files[img].DATA.shape

    max_vert = _vert if _vert > max_vert else max_vert
    max_horz = _horz if _horz > max_horz else max_horz

for i, key in enumerate(plotting_order):
    image_files[key].padToSize(shape = (max_vert, max_horz + 30))

    # PLOT THE SPECTRUM
    # Convert to Watts?
    axs[i, 0].plot(spect_files[key].DATA["A"]["FREQ"], spect_files[key].DATA["A"]["POWER"], label = key)

    # PLOT THE IMAGE
    axs[i, 1].imshow(image_files[key].DATA)
    scalebar = matplotlib_scalebar.scalebar.ScaleBar(onepixel, location = "lower right") # 1 pixel = 5.2 micrometer
    axs[i, 1].add_artist(scalebar)
    axs[i, 1].axes.xaxis.set_visible(False)
    axs[i, 1].axes.yaxis.set_visible(False)

    # PLOT THE HORIZONTAL CUT
    height, width = image_files[key].DATA.shape
    # PLOT THE MIDDLE
    mid = int(np.around(height/2))
    schnitt_y = image_files[key].DATA[mid,:]
    schnitt_x = np.arange(width) * onepixel * 1e6

    # TODO QUESTION: SHOULD I FIT SOMETHING OVER THIS?
    axs[i, 2].plot(schnitt_x, schnitt_y)

plt.show()