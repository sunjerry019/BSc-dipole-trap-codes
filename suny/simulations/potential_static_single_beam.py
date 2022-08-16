#!/usr/bin/env python3

import numpy as np
from dipoletrapli import DipoleTrapLi, cartesian_product 

import __init__
from plotter import Plotter
from matplotlib.ticker import LinearLocator

beam_params = {
    "w_0": [25e-6  , 25e-6 ], # m
    "z_0": [0   , 0  ], # m
    "Msq": [1.1 , 1.1],
}

wavelength = 1070e-9  #nm
# We generate in the x-z plane

# BEG SETTINGS
power = 100                       # W
PLOT3D = False
# END SETTINGS

import os
base_dir = os.path.dirname(os.path.realpath(__file__))

x = np.linspace(start = -100, stop = 100, num = 3000, endpoint = True) * 1e-6
z = np.linspace(start = -6, stop = 6, num = 3000, endpoint = True) * 1e-3
y = np.array([0])

points = cartesian_product(x, y, z)

intensities = DipoleTrapLi.intensity(
    x = points[:,0], y = points[:,1], z = points[:,2], 
    power = power, wavelength = wavelength,
    **beam_params
)

potential = DipoleTrapLi.potential(intensity = intensities, wavelength = wavelength)*1e27 # Turn into reasonable units

assert isinstance(potential, np.ndarray)

potentials_mk = DipoleTrapLi.trap_temperature(trap_depth = potential*1e-27)*1e3

# https://matplotlib.org/stable/gallery/images_contours_and_fields/contour_demo.html
potentials_for_contour_plotting = potentials_mk.reshape((len(x), len(z))).T
X, Z = np.meshgrid(x * 1e6, z * 1e3)

# fig, ax = plt.subplots()
# cs      = ax.contour(x, z, potentials_for_contour_plotting, levels = 15)
# # ax.clabel(cs, inline=True, fontsize=10)
# ax.set_title('Simplest default with labels')

if PLOT3D:
    plotter = Plotter(subplot_kw={"projection": "3d"})
    
    # Plot the surface.
    surf = plotter.axs.plot_surface(X = X, Y = Z, Z = potentials_for_contour_plotting, cmap=plotter.COLORMAP_R,
                        linewidth=0, antialiased=True, rasterized = True)

    plotter.axs.view_init(elev = 31., azim = -50)

    # Customize the z axis.
    # ax.set_zlim(-1.01, 1.01)
    plotter.axs.zaxis.set_major_locator(LinearLocator(10))
    # A StrMethodFormatter is used automatically
    plotter.axs.zaxis.set_major_formatter('${x:.02f}$')

    # DO LABELS
    plotter.fig.suptitle(f'Static Beam Trap Depth (Beam Separation ${angle_between_beams}^\\circ$, Power ${power}$ W)', y = 0.9)
    plotter.axs.set_xlabel('$x$ ($\\mu$m)')
    plotter.axs.set_ylabel('Propagation direction $z$ (mm)')
    plotter.axs.set_zlabel('Trap Depth (mK $\\cdot k_B$)', linespacing=5)
    plotter.axs.invert_zaxis()
    # END DO LABELS

    # Add a color bar which maps values to colors.
    plotter.fig.colorbar(surf, shrink=0.5, aspect=5, orientation="vertical", pad=0.2)

    # plt.tight_layout()
    plotter.fig.set_size_inches(8, 4.8)

    plotter.savefig(os.path.join(base_dir, "generated", "static_potential_3D_single_beam.pdf"), backend = "pdf", dpi = 600)
else:
    # Plot 2D colour map
    # http://www.peterbeerli.com/classes/images/2/26/Isc4304matplotlib6.pdf

    plotter = Plotter()
    p1 = plotter.ax.pcolormesh(Z, X, potentials_for_contour_plotting, cmap=plotter.COLORMAP_R, vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), rasterized = True)
    # plotter.ax.contour(Z, X, potentials_for_contour_plotting, colours = 'white', vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), linestyles = "dashed")
    cb = plotter.fig.colorbar(p1, ax = plotter.axs)

    plotter.ax.set_title(f'Static Beam Trap Depth (Power ${power}$ W)')
    plotter.ax.set_ylabel('$x$ ($\\mu$m)')
    plotter.ax.set_xlabel('Propagation direction $z$ (mm)')
    plotter.fig.text(0.92, 0.52,'Trap Depth (mK $\\cdot k_B$)', rotation = "vertical", va = "center", ha = "center")
    plotter.fig.set_size_inches(8, 2.7)
    plotter.fig.tight_layout()

    # plotter.show()
    plotter.savefig(os.path.join(base_dir, "generated", "static_potential_2D_single_beam.pdf"), backend = "pdf", dpi = 600)

min_point = np.argmin(potential)
print("Min Potential at =", points[min_point] * 1e6, "um")
print("Trap Depth =", DipoleTrapLi.trap_temperature(trap_depth = potential[min_point]*1e-27)*1e3, "mK")