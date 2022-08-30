#!/usr/bin/env python3

import __init__
from beamprofilerData import BeamprofilerImageData
from plotter import Plotter

import matplotlib_scalebar.scalebar

import numpy as np

import os, glob

## Settings
figsize = (2.5, 2)
data_dir = os.path.join(__init__.base_dir, "2022-08-05_High Frequency Painting", "AM Modulation")
onepixel = 5.2e-6 # in metres
## / Settings

images = {}

max_horz, max_vert = 0, 0
for fn in glob.glob(os.path.join(data_dir, "*.csv")):
    basename = fn.split(os.path.sep)[-1][:-4]
    
    images[basename] = BeamprofilerImageData(datafile = fn)

    _horz, _vert = np.shape(images[basename].DATA)

    max_horz = max(_horz, max_horz)
    max_vert = max(_vert, max_vert)

for basename in images:
    images[basename].padToSize(shape = (max_horz, max_vert))

    plotter = Plotter(figsize = figsize)
    plotter.ax.imshow(images[basename].DATA, cmap = plotter.COLORMAP)
    scalebar = matplotlib_scalebar.scalebar.ScaleBar(onepixel, location = "lower left") # 1 pixel = 5.2 micrometer
    plotter.ax.add_artist(scalebar)
    plotter.ax.axes.xaxis.set_visible(False)
    plotter.ax.axes.yaxis.set_visible(False)
    plotter.fig.tight_layout()
    # plotter.show()
    plotter.savefig(os.path.join(__init__.base_dir, "generated", f"AM_{basename}.pdf"), backend = "pdf", bbox_inches='tight', pad_inches = 0)
