#!/usr/bin/env python3

import __init__
import os, sys

from plotter import Plotter
import pandas as pd
import numpy as np

datafile = os.path.join(__init__.base_dir, "data", "AOM_DE_complete_data.dat")
figsize = (8,4)
PLOT3D = False

DATAF = pd.read_csv(datafile, sep = '\t', skiprows = 2, header = 0)

DATA = DATAF.sort_values(by = ["# RF Freq/MHz", "RF Input/dBm"])

freqs = DATA["# RF Freq/MHz"].unique()
powers = DATA["RF Input/dBm"].unique()
output = (DATA["Power/uW"].to_numpy() * 100) / 611.09

X, Y = np.meshgrid(freqs, powers)
C    = output.reshape((len(freqs), len(powers))).T

if not PLOT3D:
    plotter = Plotter(figsize = figsize)
    p1 = plotter.ax.pcolormesh(X, Y, C, cmap=plotter.COLORMAP, vmin=0, vmax=C.max(), rasterized = True)
    # plotter.ax.contour(Z, X, potentials_for_contour_plotting, colours = 'white', vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), linestyles = "dashed")
    cb = plotter.fig.colorbar(p1, ax = plotter.axs)

    plotter.ax.set_title('AOM Diffraction Efficiency')
    plotter.ax.set_xlabel("RF Input Frequency (MHz)")
    plotter.ax.set_ylabel("RF Input Power (dBm)")
    plotter.fig.tight_layout()
    # plotter.fig.subplots_adjust(right=0.9)
    plotter.fig.text(0.92, 0.52, "\\% Transmitted in the first order", rotation = "vertical", va = "center", ha = "center")
    # plotter.show()
    plotter.savefig(os.path.join(__init__.base_dir, "generated", f"aom-de.pdf"), backend = "PDF")
else:
    from matplotlib.ticker import LinearLocator

    plotter = Plotter(subplot_kw={"projection": "3d"})
        
    # Plot the surface.
    surf = plotter.axs.plot_surface(X = X, Y = Y, Z = C, cmap=plotter.COLORMAP,
                        linewidth=0, antialiased=True, rasterized = True)

    plotter.axs.view_init(azim = 121, elev = 50)

    # Customize the z axis.
    # ax.set_zlim(-1.01, 1.01)
    plotter.axs.zaxis.set_major_locator(LinearLocator(10))
    # A StrMethodFormatter is used automatically
    plotter.axs.zaxis.set_major_formatter('${x:.02f}$')

    # DO LABELS
    # plotter.fig.suptitle(f'Sweeping Beam Trap Depth (Beam Separation ${angle_between_beams}^\\circ$, Power ${power}$ W)\n{modulation_function_name}', y = 0.95)
    # plotter.axs.set_xlabel('$x$ ($\\mu$m)')
    # plotter.axs.set_ylabel('Propagation direction $z$ (mm)')
    # plotter.axs.set_zlabel('Trap Depth (mK $\\cdot k_B$)', linespacing=5)
    # plotter.axs.invert_zaxis()
    # END DO LABELS

    # Add a color bar which maps values to colors.
    plotter.fig.colorbar(surf, shrink=0.5, aspect=5, orientation="vertical", pad=0.2)

    # plt.tight_layout()
    plotter.fig.set_size_inches(7, 4.8)

    plotter.show()